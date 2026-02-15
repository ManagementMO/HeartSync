# CLAUDE.md — HeartSync Project Context

## Project Overview

HeartSync is a hardware hackathon project for MakeUofT 2026 (24-hour build). It measures the real-time connection between two people using contactless biometric sensing, computer vision, and AI — and transforms that data into a synchronized audiovisual experience with LEDs, reactive music, and AI narration.

**Team size:** 2 people
**Timeframe:** 24 hours
**Event themes:** Valentine's Day, Survival, Audio/Music (we target Valentine's Day + Audio)
**Hardware requirement:** All projects must include a physical component that is electrically powered or computer programmed.

## Architecture Summary

```
Phones (Presage SDK) ──→ Flask Server ──→ Web Display (browser)
Laptop Webcam (MediaPipe) ──↗    ↘──→ LED Strip (Raspberry Pi)
                                  ↘──→ Speaker (music + ElevenLabs TTS)
                                  ↘──→ MongoDB Atlas (logging)
```

**Data flow:** Two Android phones read heart rates via Presage SmartSpectra SDK and POST biometric data to a central Flask server every ~1 second. A laptop webcam runs MediaPipe to detect facial expressions, eye contact, smiles, and hand-holding between two people. The Flask server fuses all inputs into a Sync Score (0.0–1.0) using weighted combination of 5 channels: heart rate similarity (0.35), eye contact (0.20), breathing sync (0.15), mutual smiling (0.15), hand proximity (0.15). The sync score drives three outputs: a web-based display with animated hearts, an LED strip, and reactive audio with AI narration.

## Tech Stack

- **Language:** Python 3.10+ (server, MediaPipe, LEDs, music), Kotlin (Android app), HTML/CSS/JS (display)
- **Server:** Flask + flask-socketio + flask-cors
- **Computer Vision:** MediaPipe (face mesh with 2-face detection, hand tracking)
- **Biometrics:** Presage SmartSpectra SDK (Android, contactless heart rate + breathing via phone camera)
- **AI Commentary:** Google Gemini API (gemini-1.5-flash model)
- **Voice:** ElevenLabs TTS API (Python SDK, streaming)
- **Database:** MongoDB Atlas (free tier, pymongo)
- **Music:** pygame.mixer (3-stem crossfading)
- **LEDs:** rpi_ws281x / neopixel library (WS2812B strip on Raspberry Pi GPIO 18)
- **Real-time comms:** Socket.IO (server→display), HTTP POST (phones→server), HTTP GET (LED controller→server)

## File Structure

```
heartsync/
├── .env                          # API keys (never commit)
├── CLAUDE.md                     # This file
├── requirements.txt
├── server/
│   ├── app.py                    # Flask server — central brain, WebSocket, all endpoints
│   ├── sync_engine.py            # Sync score algorithm (5-channel weighted fusion + EMA smoothing)
│   ├── gemini_client.py          # Gemini API wrapper for romantic commentary generation
│   ├── elevenlabs_client.py      # ElevenLabs TTS wrapper (non-blocking, threaded)
│   ├── music_controller.py       # pygame.mixer 3-stem crossfader
│   └── mongo_client.py           # MongoDB Atlas session/snapshot logger
├── vision/
│   └── mediapipe_tracker.py      # MediaPipe face mesh + hand tracking (background thread)
├── display/
│   ├── index.html                # Single-file web display (hearts, sync gauge, graphs, particles)
│   └── assets/
├── hardware/
│   ├── led_controller.py         # Raspberry Pi NeoPixel driver (polls /api/state)
│   └── arduino_led/
│       └── arduino_led.ino       # Alternative Arduino FastLED sketch
├── audio/
│   ├── harmony.wav               # Warm ambient stem (high sync)
│   ├── neutral.wav               # Neutral pad stem (always soft)
│   └── tension.wav               # Dissonant texture (low sync)
├── android/
│   └── presage-heartsync/        # Modified Presage SmartSpectra Android app
└── scripts/
    ├── setup.sh
    └── start.sh
```

## Key API Endpoints (Flask Server)

- `POST /api/biometrics` — Receives `{person_id: "A"|"B", heart_rate: float, breathing_rate: float}` from phones
- `POST /api/session/start` — Starts a new HeartSync session
- `POST /api/session/stop` — Ends the session, computes summary stats in MongoDB
- `GET /api/state` — Returns full current state (biometrics, sync score, vision state, session info)
- `GET /` — Serves the display HTML page
- WebSocket event `state_update` — Pushes state to display at ~2Hz
- WebSocket event `commentary` — Pushes AI-generated text to display when spoken

## Sync Score Algorithm

The sync engine in `sync_engine.py` computes a score from 0.0 to 1.0:

```
score = 0.35 * hr_sync + 0.20 * eye_contact + 0.15 * br_sync + 0.15 * smile_sync + 0.15 * hand_score
```

Where:
- `hr_sync` = `max(0, 1 - abs(hr_a - hr_b) / 20)` — 0 BPM diff = 1.0, 20+ BPM diff = 0.0
- `eye_contact` = 1.0 if MediaPipe detects both faces oriented toward each other, else 0.0
- `br_sync` = `max(0, 1 - abs(br_a - br_b) / 10)` — breathing rate similarity
- `smile_sync` = 1.0 if both people's smile score > 0.5 (mouth width / face width ratio)
- `hand_score` = 1.0 if hands touching (distance < 0.05), else inverse of hand distance

The raw score is smoothed via exponential moving average (deque of last 10 values at 500ms intervals = 5-second window).

**Sync levels:** deeply_connected (≥0.75), connecting (≥0.50), warming_up (≥0.25), disconnected (<0.25)

## MediaPipe Details

`mediapipe_tracker.py` runs in a background thread, processing the laptop webcam at ~30fps.

**Face Mesh:**
- `max_num_faces=2`, `refine_landmarks=True` (enables iris landmarks)
- Smile detection: landmarks 61 (left mouth corner), 291 (right mouth corner), 234/454 (face edges). Score = normalized mouth-width-to-face-width ratio.
- Eye contact: Compare nose-tip X positions and face orientation vectors of both faces. If face1 is left and facing right, face2 is right and facing left = eye contact.
- Face distance: Euclidean distance between nose tips (landmark 1) of both faces, normalized.

**Hand Tracking:**
- `max_num_hands=4` (2 people × 2 hands each)
- Palm center = landmark 9 (middle of palm)
- hands_touching = minimum distance between any two palms < 0.05 (normalized)

## Environment Variables (.env)

```
PRESAGE_API_KEY=...
GEMINI_API_KEY=...
ELEVENLABS_API_KEY=...
MONGODB_URI=mongodb+srv://...
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
CAMERA_INDEX=0
LED_COUNT=30
LED_PIN=18
```

## Development Commands

```bash
# Install Python dependencies
pip install flask flask-socketio flask-cors mediapipe opencv-python pygame elevenlabs google-generativeai pymongo requests numpy python-dotenv

# Run the server (starts Flask + MediaPipe + update loop)
cd server && python app.py

# Run LED controller on Raspberry Pi (separate terminal/device)
sudo python3 hardware/led_controller.py

# Run everything via script
./scripts/start.sh
```

## Coding Guidelines

1. **Hackathon speed over production quality.** Working > clean. Hardcoding is fine for demo values. Comments are nice but not required on every line.
2. **Single-file preference.** The display should be one `index.html` with inline CSS/JS. Don't split into multiple frontend files.
3. **Thread safety matters.** The MediaPipe tracker, Flask server, sync engine, and music controller all run concurrently. Use threading.Lock for shared state. The `ConnectionTracker.state` dict is the main shared resource.
4. **Graceful degradation.** Every component should handle the case where its data source is unavailable. If Presage data stops flowing, sync score should still work with just MediaPipe. If Gemini fails, use fallback lines. If MongoDB is down, just skip logging.
5. **Demo-first development.** Build the impressive demo path first (two hearts syncing → score rising → LEDs changing → voice speaks). Edge cases and error handling come second.
6. **No authentication or security.** This is a hackathon running on a local network. No auth on endpoints. No HTTPS. No input validation beyond basic type checking.

## Important Constraints

- **MakeUofT hardware requirement:** Must have a physical hardware component. Our LED strip on Raspberry Pi/Arduino satisfies this.
- **No Arduino Uno Q available.** We cannot use Arduino Uno Q boards — they are no longer available at this hackathon. Use Raspberry Pi or standard Arduino.
- **Presage SDK is Android/iOS/C++.** No Python SDK. Phones run the SDK and POST data to our server. The C++ SDK works on Linux laptops but is more complex to set up.
- **MediaPipe runs locally.** No API key needed. No internet required for vision processing.
- **ElevenLabs free tier:** 10,000 characters/month. Each commentary line is ~100 chars. Budget for ~100 narrations during the hackathon (plenty).
- **Gemini free tier:** 15 requests per minute. We call every ~30 seconds = 2 RPM. Well within limits.
- **LED strip needs sudo on Raspberry Pi** due to GPIO access. Run led_controller.py with `sudo python3`.

## Display (index.html) Requirements

The display is the visual centerpiece shown to judges. It must:
- Show two heart shapes that pulse to each person's real BPM (scale animation with period = 60/BPM seconds)
- Hearts drift closer together as sync score increases
- Large sync score display (percentage in a circular gauge or arc)
- Background gradient shifts: cool blues (low sync) → warm pinks/reds (high sync)
- Particle effects (hearts, sparkles) when sync > 75%
- Show each person's BPM number
- Show AI commentary text when it arrives (fade in/out at bottom)
- "Start Session" / "Stop Session" button
- Connect to Flask via Socket.IO (`io('http://localhost:5000')`)
- Valentine's Day aesthetic: pinks, reds, warm tones, heart motifs
- Must look polished — judges associate visual quality with project quality

## Music System

Three audio stems loaded into pygame.mixer channels, looping infinitely. Volumes crossfade based on sync score:
- harmony channel: volume = sync_score (0→silent, 1→full)
- neutral channel: volume peaks at 0.5 sync, quieter at extremes
- tension channel: volume = 1 - sync_score (inverse of harmony)

Audio files should be pre-prepared WAV files, same length (30-60 seconds), loopable.

## LED Patterns

The LED strip (WS2812B, 30-60 LEDs) is split into two halves (Person A, Person B):

- **disconnected:** Left half = cool blue, right half = warm red, no pulse sync
- **warming_up:** Left = purple-blue, right = purple-red, slight pulse
- **connecting:** Both halves = magenta, pulsing begins to unify
- **deeply_connected:** Entire strip = warm rose, pulsing in unison to averaged heartbeat

Heartbeat pulse function: double-bump sinusoidal curve at the person's BPM. At high sync, both halves use an averaged pulse. The blend factor equals the sync score.

## Prize Categories We Target

1. Valentine's Day Theme (Lego Cherry Blossoms, 2 winners)
2. Audio/Music Theme (JBL Go4, 4 winners)
3. Best Use of Presage - MLH (SenseCAP Watcher + Presage credits)
4. Best Use of ElevenLabs - MLH (Wireless Earbuds)
5. Best Use of Gemini API - MLH (Google Swag Kit)
6. Best Use of MongoDB Atlas - MLH (M5Stack IoT Kit)
7. 1st/2nd/3rd Place Overall

## Quick Reference: External API Calls

### Presage (received, not called — phones POST to us)
```python
# Phone sends:
POST /api/biometrics
{"person_id": "A", "heart_rate": 72.5, "breathing_rate": 15.2, "timestamp": 1707900000}
```

### Gemini
```python
import google.generativeai as genai
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")
response = model.generate_content("Your prompt here")
text = response.text
```

### ElevenLabs
```python
from elevenlabs import stream
from elevenlabs.client import ElevenLabs
client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])
audio = client.text_to_speech.stream(text="Hello", voice_id="21m00Tcm4TlvDq8ikWAM", model_id="eleven_multilingual_v2")
stream(audio)  # Plays through speakers
```

### MongoDB Atlas
```python
from pymongo import MongoClient
client = MongoClient(os.environ["MONGODB_URI"])
db = client["heartsync"]
db["snapshots"].insert_one({"heart_rate_a": 72, "sync_score": 0.85, "timestamp": datetime.utcnow()})
```

## Testing Checklist

Before demo, verify each component independently:
- [ ] Phone A streams HR data to Flask (check server logs)
- [ ] Phone B streams HR data to Flask
- [ ] MediaPipe detects 2 faces (check face_count in state)
- [ ] MediaPipe detects smiles (smile at camera, check smile_scores)
- [ ] MediaPipe detects hands near each other
- [ ] Sync score changes when you interact (hold hands, look at each other)
- [ ] Display updates in real-time via WebSocket
- [ ] LEDs change color with sync level
- [ ] Music crossfades when sync changes
- [ ] Gemini generates commentary (check server logs)
- [ ] ElevenLabs speaks the commentary aloud
- [ ] MongoDB has snapshots (check Atlas dashboard)
- [ ] Full end-to-end: two people sit down → sync rises → lights change → voice speaks
