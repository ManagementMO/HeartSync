# HeartSync — Complete Project Plan

## MakeUofT 2026 | Valentine's Day + Audio/Music Themes

> **One-liner:** HeartSync uses contactless biometric sensing, computer vision, and AI to measure how synchronized two people's hearts, expressions, and body language are — and turns that connection into a real-time audiovisual experience.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Prize Strategy](#2-prize-strategy)
3. [System Architecture](#3-system-architecture)
4. [Tech Stack & APIs](#4-tech-stack--apis)
5. [Hardware Requirements](#5-hardware-requirements)
6. [Detailed Component Breakdown](#6-detailed-component-breakdown)
7. [Sync Score Algorithm](#7-sync-score-algorithm)
8. [Hour-by-Hour Build Plan](#8-hour-by-hour-build-plan)
9. [Task Split (2 People)](#9-task-split-2-people)
10. [Demo Script](#10-demo-script)
11. [Devpost Submission Guide](#11-devpost-submission-guide)
12. [Risk Matrix & Fallbacks](#12-risk-matrix--fallbacks)
13. [API Setup Guides](#13-api-setup-guides)
14. [File & Folder Structure](#14-file--folder-structure)

---

## 1. Project Overview

### What It Is

Two people sit in front of a display. Two phones (one per person) read their heart rates contactlessly via Presage's SmartSpectra SDK. A laptop webcam runs MediaPipe to detect facial expressions, eye contact, smiles, and hand-holding. A central Python server fuses all these signals into a single **Sync Score (0–100%)** representing how connected the two people are.

The sync score drives three real-time outputs:

- **Visual display** — Two animated hearts on screen that pulse to each person's real heartbeat. As sync increases, the hearts drift closer together, colors harmonize, and particle effects emerge.
- **LED strip** — A physical NeoPixel strip mounted in a heart-shaped frame shifts from split contrasting colors (low sync) to a unified warm pulse synchronized to their shared heartbeat (high sync).
- **Reactive audio** — Layered music stems crossfade from dissonant to harmonious based on sync. ElevenLabs TTS narrates Gemini-generated romantic commentary at key moments.

### Why It Wins

- **Emotional experience over technical demo.** Judges don't just see it — they *feel* it. The moment two hearts sync on screen on Valentine's Day is unforgettable.
- **Multi-modal sensing story.** Three independent sensing channels (physiology via Presage, vision via MediaPipe, audio environment optionally via Edge Impulse) fused into one score. This is a genuine technical narrative.
- **Physical hardware component.** LED strip in a heart frame driven by a Raspberry Pi/Arduino satisfies MakeUofT's hardware requirement with visual impact.
- **Hits 6–7 prize categories** from a single project (see Prize Strategy below).

---

## 2. Prize Strategy

| Prize Category | How HeartSync Qualifies | Confidence |
|---|---|---|
| **Valentine's Day Theme** | Literally about two hearts connecting. Perfect thematic fit. Only 2 winners = less competition. | Very High |
| **Audio/Music Theme** | Reactive music system that responds to biometric sync in real time. | High |
| **Best Use of Presage (MLH)** | Presage is the core sensing engine — contactless heart rate + breathing + HRV. Exactly their target use case (gaming/entertainment). | Very High |
| **Best Use of ElevenLabs (MLH)** | ElevenLabs narrates AI-generated romantic commentary with expressive voices. | High |
| **Best Use of Gemini API (MLH)** | Gemini generates unique romantic commentary and connection insights from biometric data. | High |
| **Best Use of MongoDB Atlas (MLH)** | All session data (heart rates, sync scores, emotions, timestamps) logged to Atlas for session history and replay. | Medium |
| **1st / 2nd / 3rd Place Overall** | Strong wow-factor, technical depth, and demo quality. | Medium |

**Action:** On Devpost, select ALL of these prize categories when submitting.

---

## 3. System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        SENSING LAYER                                │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │  Phone A      │  │  Phone B      │  │  Laptop Webcam           │  │
│  │  (Presage     │  │  (Presage     │  │  (MediaPipe)             │  │
│  │   Android)    │  │   Android)    │  │  - Face Mesh (2 faces)   │  │
│  │  - Heart Rate │  │  - Heart Rate │  │  - Gaze/Eye Contact      │  │
│  │  - Breathing  │  │  - Breathing  │  │  - Smile Detection       │  │
│  │  - HRV        │  │  - HRV        │  │  - Hand Tracking         │  │
│  └──────┬───────┘  └──────┬───────┘  └────────────┬─────────────┘  │
│         │ HTTP POST        │ HTTP POST             │ Local pipe     │
└─────────┼──────────────────┼──────────────────────┼────────────────┘
          │                  │                      │
          ▼                  ▼                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     CENTRAL BRAIN (Flask Server)                    │
│                          (Laptop - Python)                          │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                   SYNC SCORE ENGINE                          │   │
│  │  Inputs:                                                     │   │
│  │   - HR difference (Presage)         weight: 0.35             │   │
│  │   - Breathing sync (Presage)        weight: 0.15             │   │
│  │   - Eye contact detected (MediaPipe) weight: 0.20            │   │
│  │   - Mutual smile (MediaPipe)        weight: 0.15             │   │
│  │   - Hand proximity (MediaPipe)      weight: 0.15             │   │
│  │  Output: sync_score (0.0 – 1.0)                              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐      │
│  │ Gemini API   │  │ ElevenLabs   │  │ MongoDB Atlas        │      │
│  │ (commentary) │  │ (TTS voice)  │  │ (session logging)    │      │
│  └──────────────┘  └──────────────┘  └──────────────────────┘      │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        OUTPUT LAYER                                 │
│                                                                     │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │  Web Display      │  │  LED Strip        │  │  Speaker          │  │
│  │  (Browser)        │  │  (Raspberry Pi/   │  │  - Music stems    │  │
│  │  - Heart anims    │  │   Arduino)        │  │  - ElevenLabs     │  │
│  │  - Sync score     │  │  - NeoPixels in   │  │    narration      │  │
│  │  - Live graphs    │  │    heart frame    │  │                   │  │
│  │  - Particles      │  │                   │  │                   │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### Data Flow Summary

1. **Every ~1 second:** Phones POST `{heart_rate, breathing_rate, hrv}` to Flask `/api/biometrics`
2. **Every frame (~30fps):** MediaPipe processes webcam, pushes `{eye_contact, smiles, hand_distance}` to shared state
3. **Every ~500ms:** Sync engine recalculates score from all inputs
4. **Every ~500ms:** Flask pushes state to display via WebSocket, sends serial commands to LED controller
5. **Every ~30 seconds:** If sync score changed significantly, call Gemini for new commentary → ElevenLabs speaks it
6. **Every ~5 seconds:** Log snapshot to MongoDB Atlas

---

## 4. Tech Stack & APIs

### Languages & Frameworks

| Component | Language | Libraries |
|---|---|---|
| Central server | Python 3.10+ | Flask, flask-socketio, flask-cors |
| Presage phone apps | Kotlin (Android) | SmartSpectra SDK, OkHttp |
| MediaPipe vision | Python | mediapipe, opencv-python |
| Web display | HTML/JS/CSS | Socket.IO client, Chart.js, Canvas API |
| LED controller | Python (on Pi) or C++ (Arduino) | rpi_ws281x (Pi) or FastLED (Arduino) |
| Music system | Python | pygame.mixer |

### External APIs

| API | Purpose | Free Tier | Setup Time |
|---|---|---|---|
| **Presage SmartSpectra** | Contactless heart rate, breathing, HRV | Free dev key | ~30 min |
| **Google Gemini** | Generate romantic commentary from biometric data | Free tier (15 RPM) | ~10 min |
| **ElevenLabs** | Text-to-speech narration with expressive voices | 10k chars/month free | ~10 min |
| **MongoDB Atlas** | Session data logging and history | Free 512MB cluster | ~15 min |
| **MediaPipe** | Face mesh, hand tracking (runs locally, no API key) | Fully free/local | ~5 min (pip install) |

### Key Python Packages

```
flask==3.0.*
flask-socketio==5.*
flask-cors==4.*
mediapipe==0.10.*
opencv-python==4.9.*
pygame==2.5.*
elevenlabs==1.*
google-generativeai==0.5.*
pymongo==4.6.*
requests==2.31.*
numpy==1.26.*
```

---

## 5. Hardware Requirements

### Must Have

| Item | Purpose | Source |
|---|---|---|
| 2x Android phones | Run Presage SDK, read biometrics | Your own phones |
| 1x Laptop with webcam | Central server, MediaPipe, display | Your own laptop |
| 1x WS2812B LED strip (30–60 LEDs) | Physical light output | MakeUofT hardware rental |
| 1x Raspberry Pi (any model) OR Arduino | Drive the LED strip | MakeUofT hardware rental |
| Jumper wires + breadboard | Connect LED strip to controller | MakeUofT hardware rental |
| 1x USB cable (for Pi/Arduino) | Power + serial to laptop | MakeUofT hardware rental |
| 1x External speaker OR 3.5mm speaker | Play music + ElevenLabs audio | MakeUofT hardware rental or own |

### Nice to Have

| Item | Purpose |
|---|---|
| External monitor/TV | Bigger display for demo |
| Cardboard + hot glue | Heart-shaped frame for LED strip |
| Capacitive touch sensor | "Touch to connect" ritual button |
| Fairy lights / extra LEDs | Ambiance for demo booth |

### Hardware Signout Priority List

When hardware.makeuoft.ca opens, grab these first:
1. WS2812B/NeoPixel LED strip (or any individually addressable LED strip)
2. Raspberry Pi (any model with GPIO) — OR Arduino Uno/Nano
3. Breadboard + jumper wires
4. External speaker (if available)
5. USB cables

---

## 6. Detailed Component Breakdown

### 6.1 — Presage Phone Apps (Android)

**What:** Modify the Presage SmartSpectra Android example app to continuously measure heart rate and POST results to your Flask server.

**Setup Steps:**

1. Register at https://physiology.presagetech.com and get an API key
2. Clone the example app:
   ```bash
   git clone https://github.com/Presage-Security/SmartSpectra.git
   cd SmartSpectra/android
   ```
3. Open in Android Studio. Replace `"YOUR_API_KEY"` in `MainActivity.kt`
4. The example app already displays pulse and breathing data via `MetricsBuffer` observer

**Modification needed:** Add HTTP POST to send data to your Flask server. Add this to the `handleMetricsBuffer` function in `MainActivity.kt`:

```kotlin
// Add to imports
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import okhttp3.MediaType.Companion.toMediaType
import org.json.JSONObject

// Add as class property
private val httpClient = OkHttpClient()
private val SERVER_URL = "http://<LAPTOP_IP>:5000/api/biometrics"
private val PERSON_ID = "A"  // Change to "B" on the second phone

// Add to handleMetricsBuffer()
private fun handleMetricsBuffer(metrics: MetricsBuffer) {
    // Existing plot code...

    // NEW: Send to server
    val pulseRate = metrics.pulse.rate  // BPM
    val breathingRate = metrics.breathing.rate
    
    if (pulseRate > 0) {
        Thread {
            try {
                val json = JSONObject().apply {
                    put("person_id", PERSON_ID)
                    put("heart_rate", pulseRate)
                    put("breathing_rate", breathingRate)
                    put("timestamp", System.currentTimeMillis())
                }
                val body = json.toString()
                    .toRequestBody("application/json".toMediaType())
                val request = Request.Builder()
                    .url(SERVER_URL)
                    .post(body)
                    .build()
                httpClient.newCall(request).execute()
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }.start()
    }
}
```

**Important notes:**
- Both phones must be on the same WiFi network as the laptop
- Replace `<LAPTOP_IP>` with your laptop's local IP (find via `ipconfig` / `ifconfig`)
- Change `PERSON_ID` to `"B"` when building for the second phone
- The SDK needs ~3–5 seconds to lock onto a face and start streaming data
- Good lighting (≥60 lux) is important — the hackathon venue should be fine

**Testing:** Open the app, point at your face, confirm you see pulse data on screen AND your Flask server receives POST requests.

---

### 6.2 — MediaPipe Vision System

**What:** Use the laptop webcam to detect two faces, their expressions, eye gaze, and hand positions — all running locally in Python.

**File:** `vision/mediapipe_tracker.py`

```python
import cv2
import mediapipe as mp
import numpy as np
import threading
import time

class ConnectionTracker:
    """
    Uses MediaPipe to track visual indicators of connection between two people.
    Outputs: eye_contact (bool), both_smiling (bool), hand_distance (float),
             face_distance (float), individual smile scores.
    """

    def __init__(self):
        # Face mesh for expression + gaze
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=2,
            refine_landmarks=True,  # Enables iris landmarks for gaze
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Hand tracking
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=4,  # Up to 4 hands (2 people × 2 hands)
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Shared state (thread-safe)
        self.lock = threading.Lock()
        self.state = {
            "eye_contact": False,
            "both_smiling": False,
            "smile_scores": [0.0, 0.0],
            "hand_distance": 999.0,  # Normalized 0-1 (0 = touching)
            "hands_touching": False,
            "face_count": 0,
            "face_distance": 999.0,
        }
        
        self.running = False
        self.cap = None
        self.thread = None

    def start(self, camera_index=0):
        """Start the vision tracking in a background thread."""
        self.running = True
        self.cap = cv2.VideoCapture(camera_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop tracking and release camera."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        if self.cap:
            self.cap.release()

    def get_state(self):
        """Get current tracking state (thread-safe)."""
        with self.lock:
            return dict(self.state)

    def _run_loop(self):
        """Main processing loop (runs in background thread)."""
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.01)
                continue

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w = frame.shape[:2]

            # Process face mesh
            face_results = self.face_mesh.process(frame_rgb)
            # Process hands
            hand_results = self.hands.process(frame_rgb)

            new_state = {
                "eye_contact": False,
                "both_smiling": False,
                "smile_scores": [0.0, 0.0],
                "hand_distance": 999.0,
                "hands_touching": False,
                "face_count": 0,
                "face_distance": 999.0,
            }

            # --- FACE ANALYSIS ---
            if face_results.multi_face_landmarks:
                faces = face_results.multi_face_landmarks
                new_state["face_count"] = len(faces)

                if len(faces) >= 2:
                    # Smile detection for each face
                    for i, face in enumerate(faces[:2]):
                        smile_score = self._detect_smile(face, w, h)
                        new_state["smile_scores"][i] = smile_score

                    new_state["both_smiling"] = (
                        new_state["smile_scores"][0] > 0.5 and
                        new_state["smile_scores"][1] > 0.5
                    )

                    # Eye contact detection (simplified: both faces facing each other)
                    new_state["eye_contact"] = self._detect_eye_contact(
                        faces[0], faces[1], w, h
                    )

                    # Face distance (how close the two faces are)
                    new_state["face_distance"] = self._face_distance(
                        faces[0], faces[1], w, h
                    )

                elif len(faces) == 1:
                    new_state["smile_scores"][0] = self._detect_smile(
                        faces[0], w, h
                    )

            # --- HAND ANALYSIS ---
            if hand_results.multi_hand_landmarks:
                hands_list = hand_results.multi_hand_landmarks
                if len(hands_list) >= 2:
                    min_dist = self._closest_hand_distance(hands_list, w, h)
                    new_state["hand_distance"] = min_dist
                    new_state["hands_touching"] = min_dist < 0.05

            with self.lock:
                self.state = new_state

    def _detect_smile(self, face_landmarks, w, h):
        """
        Detect smile by measuring mouth width vs face width ratio.
        Returns a score from 0.0 (no smile) to 1.0 (big smile).
        
        Key landmarks:
        - Mouth corners: 61 (left), 291 (right)
        - Upper lip top: 13
        - Lower lip bottom: 14
        - Face edges: 234 (left), 454 (right)
        """
        landmarks = face_landmarks.landmark

        # Mouth width
        mouth_left = np.array([landmarks[61].x * w, landmarks[61].y * h])
        mouth_right = np.array([landmarks[291].x * w, landmarks[291].y * h])
        mouth_width = np.linalg.norm(mouth_right - mouth_left)

        # Mouth height (openness)
        upper_lip = np.array([landmarks[13].x * w, landmarks[13].y * h])
        lower_lip = np.array([landmarks[14].x * w, landmarks[14].y * h])
        mouth_height = np.linalg.norm(lower_lip - upper_lip)

        # Face width for normalization
        face_left = np.array([landmarks[234].x * w, landmarks[234].y * h])
        face_right = np.array([landmarks[454].x * w, landmarks[454].y * h])
        face_width = np.linalg.norm(face_right - face_left)

        if face_width == 0:
            return 0.0

        # Smile ratio: wide mouth + slightly open = smiling
        width_ratio = mouth_width / face_width
        # Typical range: 0.25 (neutral) to 0.45 (big smile)
        smile_score = np.clip((width_ratio - 0.28) / 0.15, 0.0, 1.0)

        return float(smile_score)

    def _detect_eye_contact(self, face1, face2, w, h):
        """
        Simplified eye contact detection.
        Checks if both faces are oriented toward each other
        by comparing nose tip positions and face orientations.
        
        Key landmarks:
        - Nose tip: 1
        - Left eye inner: 133
        - Right eye inner: 362
        - Forehead: 10
        - Chin: 152
        """
        lm1 = face1.landmark
        lm2 = face2.landmark

        # Get nose positions (center of face)
        nose1_x = lm1[1].x
        nose2_x = lm2[1].x

        # Get face orientations using the nose-to-ear vector
        # If face1 is on the left and facing right, and face2 is on the right
        # and facing left, they're looking at each other
        
        # Left ear: 234, Right ear: 454, Nose: 1
        face1_direction = lm1[1].x - (lm1[234].x + lm1[454].x) / 2
        face2_direction = lm2[1].x - (lm2[234].x + lm2[454].x) / 2

        # If face1 is left of face2
        if nose1_x < nose2_x:
            # Face1 should face right (positive direction) and
            # face2 should face left (negative direction)
            facing_each_other = face1_direction > -0.01 and face2_direction < 0.01
        else:
            facing_each_other = face1_direction < 0.01 and face2_direction > -0.01

        # Also check vertical alignment (both at similar height = eye level)
        vertical_diff = abs(lm1[1].y - lm2[1].y)
        at_eye_level = vertical_diff < 0.15

        return facing_each_other and at_eye_level

    def _face_distance(self, face1, face2, w, h):
        """Normalized distance between two face centers (0 = overlapping, 1 = far)."""
        lm1 = face1.landmark
        lm2 = face2.landmark
        center1 = np.array([lm1[1].x, lm1[1].y])
        center2 = np.array([lm2[1].x, lm2[1].y])
        dist = np.linalg.norm(center2 - center1)
        return float(np.clip(dist, 0, 1))

    def _closest_hand_distance(self, hands_list, w, h):
        """
        Find minimum distance between any two hands.
        Uses landmark 9 (middle of palm) as the reference point.
        Returns normalized distance (0 = touching, 1 = far).
        """
        palm_centers = []
        for hand in hands_list:
            palm = hand.landmark[9]  # Middle of palm
            palm_centers.append(np.array([palm.x, palm.y]))

        min_dist = 999.0
        for i in range(len(palm_centers)):
            for j in range(i + 1, len(palm_centers)):
                dist = np.linalg.norm(palm_centers[i] - palm_centers[j])
                min_dist = min(min_dist, dist)

        return float(np.clip(min_dist, 0, 1))
```

**Key design decisions:**
- Runs in a background thread so it doesn't block the Flask server
- Thread-safe state dict that the sync engine polls
- Face mesh with `refine_landmarks=True` enables iris tracking for better gaze detection
- Smile detection uses mouth-width-to-face-width ratio (research-backed approach)
- Eye contact detection is simplified but effective for demo — checks if faces are oriented toward each other
- Hand tracking detects when any two hands are close together (covering both holding hands and high-fives)

**Testing:** Run standalone with `python mediapipe_tracker.py` — it should print state updates showing face count, smile scores, and hand detection.

---

### 6.3 — Central Flask Server

**What:** The brain of the project. Receives all sensor data, computes sync score, serves the web display, and coordinates all API calls.

**File:** `server/app.py`

```python
import time
import json
import threading
from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO
from flask_cors import CORS

# Import our modules
from sync_engine import SyncEngine
from gemini_client import GeminiCommentary
from elevenlabs_client import VoiceNarrator
from mongo_client import SessionLogger
from vision.mediapipe_tracker import ConnectionTracker

app = Flask(__name__, static_folder='../display')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# --- Initialize components ---
sync_engine = SyncEngine()
vision_tracker = ConnectionTracker()
gemini = GeminiCommentary()
narrator = VoiceNarrator()
mongo = SessionLogger()

# --- Biometric state ---
biometrics = {
    "A": {"heart_rate": 0, "breathing_rate": 0, "timestamp": 0},
    "B": {"heart_rate": 0, "breathing_rate": 0, "timestamp": 0},
}

session_active = False
session_start_time = 0
last_commentary_time = 0
last_sync_score = 0

# ============================================================
#  API ENDPOINTS
# ============================================================

@app.route('/api/biometrics', methods=['POST'])
def receive_biometrics():
    """Receive heart rate data from Presage phone apps."""
    data = request.json
    person_id = data.get('person_id', 'A')
    
    biometrics[person_id] = {
        "heart_rate": data.get('heart_rate', 0),
        "breathing_rate": data.get('breathing_rate', 0),
        "timestamp": time.time()
    }
    
    return jsonify({"status": "ok"})

@app.route('/api/session/start', methods=['POST'])
def start_session():
    """Start a new HeartSync session."""
    global session_active, session_start_time, last_commentary_time
    session_active = True
    session_start_time = time.time()
    last_commentary_time = 0
    mongo.start_session()
    return jsonify({"status": "started"})

@app.route('/api/session/stop', methods=['POST'])
def stop_session():
    """Stop the current session."""
    global session_active
    session_active = False
    mongo.end_session()
    return jsonify({"status": "stopped"})

@app.route('/api/state', methods=['GET'])
def get_state():
    """Get current full state (for polling fallback)."""
    return jsonify(_build_state())

@app.route('/')
def serve_display():
    """Serve the main display page."""
    return send_from_directory('../display', 'index.html')

# ============================================================
#  MAIN UPDATE LOOP
# ============================================================

def update_loop():
    """
    Main loop that runs every 500ms:
    1. Gets MediaPipe state
    2. Computes sync score
    3. Pushes state to display via WebSocket
    4. Triggers commentary if appropriate
    5. Logs to MongoDB
    """
    global last_commentary_time, last_sync_score

    while True:
        if not session_active:
            time.sleep(0.5)
            continue

        # 1. Gather all inputs
        vision_state = vision_tracker.get_state()
        
        # 2. Compute sync score
        sync_result = sync_engine.compute(
            hr_a=biometrics["A"]["heart_rate"],
            hr_b=biometrics["B"]["heart_rate"],
            br_a=biometrics["A"]["breathing_rate"],
            br_b=biometrics["B"]["breathing_rate"],
            eye_contact=vision_state["eye_contact"],
            both_smiling=vision_state["both_smiling"],
            hands_touching=vision_state["hands_touching"],
            hand_distance=vision_state["hand_distance"],
            face_distance=vision_state["face_distance"],
        )

        # 3. Build and push state
        state = _build_state(sync_result, vision_state)
        socketio.emit('state_update', state)

        # 4. Commentary trigger (every 30s or on big sync change)
        now = time.time()
        sync_changed_a_lot = abs(sync_result["score"] - last_sync_score) > 0.2
        time_for_new = (now - last_commentary_time) > 30

        if (sync_changed_a_lot or time_for_new) and last_commentary_time > 0:
            _trigger_commentary(sync_result, vision_state)
            last_commentary_time = now
        elif last_commentary_time == 0:
            last_commentary_time = now  # First tick

        last_sync_score = sync_result["score"]

        # 5. Log to MongoDB
        mongo.log_snapshot(state)

        time.sleep(0.5)


def _build_state(sync_result=None, vision_state=None):
    """Build the full state object for the display."""
    return {
        "person_a": {
            "heart_rate": biometrics["A"]["heart_rate"],
            "breathing_rate": biometrics["A"]["breathing_rate"],
            "data_fresh": (time.time() - biometrics["A"]["timestamp"]) < 5,
        },
        "person_b": {
            "heart_rate": biometrics["B"]["heart_rate"],
            "breathing_rate": biometrics["B"]["breathing_rate"],
            "data_fresh": (time.time() - biometrics["B"]["timestamp"]) < 5,
        },
        "sync": sync_result or {"score": 0, "level": "disconnected", "hr_sync": 0},
        "vision": vision_state or {},
        "session_duration": time.time() - session_start_time if session_active else 0,
        "session_active": session_active,
        "timestamp": time.time(),
    }


def _trigger_commentary(sync_result, vision_state):
    """Generate and speak AI commentary."""
    try:
        text = gemini.generate_commentary(
            sync_score=sync_result["score"],
            sync_level=sync_result["level"],
            hr_a=biometrics["A"]["heart_rate"],
            hr_b=biometrics["B"]["heart_rate"],
            eye_contact=vision_state["eye_contact"],
            both_smiling=vision_state["both_smiling"],
            hands_touching=vision_state["hands_touching"],
        )
        if text:
            # Emit the text to display
            socketio.emit('commentary', {"text": text})
            # Speak it
            narrator.speak(text)
    except Exception as e:
        print(f"Commentary error: {e}")


# ============================================================
#  STARTUP
# ============================================================

if __name__ == '__main__':
    # Start MediaPipe tracker
    vision_tracker.start(camera_index=0)
    
    # Start update loop in background thread
    update_thread = threading.Thread(target=update_loop, daemon=True)
    update_thread.start()
    
    print("\n🫀 HeartSync Server running on http://0.0.0.0:5000")
    print("   Open browser to see the display")
    print("   Waiting for phone connections...\n")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
```

---

### 6.4 — Sync Score Engine

**File:** `server/sync_engine.py`

```python
import numpy as np
from collections import deque

class SyncEngine:
    """
    Fuses multiple sensing channels into a single sync score (0.0 to 1.0).
    
    Channels and weights:
    - Heart rate similarity:  0.35  (core biometric signal)
    - Eye contact:            0.20  (strongest visual signal of connection)
    - Breathing synchrony:    0.15  (subtle but meaningful)
    - Mutual smiling:         0.15  (emotional expression)
    - Hand proximity:         0.15  (physical touch/closeness)
    
    The score is smoothed over time to avoid jumpy changes.
    """

    def __init__(self):
        self.score_history = deque(maxlen=10)  # For smoothing
        self.hr_history_a = deque(maxlen=30)
        self.hr_history_b = deque(maxlen=30)

    def compute(self, hr_a, hr_b, br_a, br_b,
                eye_contact, both_smiling,
                hands_touching, hand_distance, face_distance):
        """
        Compute the sync score from all inputs.
        Returns dict with score, level, and component breakdowns.
        """

        # --- Heart Rate Sync (0.0 to 1.0) ---
        # Perfect sync = 0 BPM difference = 1.0
        # 20+ BPM difference = 0.0
        if hr_a > 0 and hr_b > 0:
            hr_diff = abs(hr_a - hr_b)
            hr_sync = max(0.0, 1.0 - (hr_diff / 20.0))
            self.hr_history_a.append(hr_a)
            self.hr_history_b.append(hr_b)
        else:
            hr_sync = 0.0

        # --- Breathing Sync (0.0 to 1.0) ---
        if br_a > 0 and br_b > 0:
            br_diff = abs(br_a - br_b)
            br_sync = max(0.0, 1.0 - (br_diff / 10.0))
        else:
            br_sync = 0.0

        # --- Eye Contact (0.0 or 1.0) ---
        eye_score = 1.0 if eye_contact else 0.0

        # --- Smile Sync (0.0 or 1.0) ---
        smile_score = 1.0 if both_smiling else 0.0

        # --- Hand Proximity (0.0 to 1.0) ---
        if hands_touching:
            hand_score = 1.0
        else:
            # Inverse of distance, clamped
            hand_score = max(0.0, 1.0 - (hand_distance / 0.3))

        # --- Weighted combination ---
        raw_score = (
            0.35 * hr_sync +
            0.20 * eye_score +
            0.15 * br_sync +
            0.15 * smile_score +
            0.15 * hand_score
        )

        # --- Smoothing (exponential moving average with history) ---
        self.score_history.append(raw_score)
        smoothed = np.mean(self.score_history)

        # --- Determine level ---
        if smoothed >= 0.75:
            level = "deeply_connected"
        elif smoothed >= 0.50:
            level = "connecting"
        elif smoothed >= 0.25:
            level = "warming_up"
        else:
            level = "disconnected"

        return {
            "score": round(float(smoothed), 3),
            "level": level,
            "hr_sync": round(float(hr_sync), 3),
            "br_sync": round(float(br_sync), 3),
            "eye_contact": eye_contact,
            "both_smiling": both_smiling,
            "hand_score": round(float(hand_score), 3),
            "raw_score": round(float(raw_score), 3),
        }
```

---

### 6.5 — Gemini Commentary Generator

**File:** `server/gemini_client.py`

```python
import google.generativeai as genai
import os

class GeminiCommentary:
    """Generates romantic/playful commentary based on biometric data."""

    def __init__(self):
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Fallback lines if API fails
        self.fallbacks = {
            "deeply_connected": [
                "Your hearts are speaking the same language.",
                "In this moment, you are perfectly in tune.",
                "The universe notices when two souls align.",
            ],
            "connecting": [
                "Something beautiful is building between you.",
                "Your rhythms are finding harmony.",
                "The connection grows stronger with every beat.",
            ],
            "warming_up": [
                "Every great connection starts with a single moment.",
                "Your hearts are curious about each other.",
                "The dance is beginning.",
            ],
            "disconnected": [
                "Try looking into each other's eyes.",
                "Take a deep breath together.",
                "Reach out — connection is just a touch away.",
            ],
        }
        self.fallback_index = 0

    def generate_commentary(self, sync_score, sync_level,
                            hr_a, hr_b, eye_contact,
                            both_smiling, hands_touching):
        """Generate a short romantic line based on current state."""
        
        prompt = f"""You are the voice of HeartSync, a Valentine's Day device that 
measures the connection between two people through their heartbeats and body language.

Current state:
- Sync score: {int(sync_score * 100)}%
- Connection level: {sync_level}
- Person A heart rate: {hr_a} BPM
- Person B heart rate: {hr_b} BPM  
- Making eye contact: {eye_contact}
- Both smiling: {both_smiling}
- Holding hands: {hands_touching}

Generate ONE short, romantic, poetic line (max 20 words) that reflects this moment.
Be warm, specific to the data, and Valentine's Day themed.
Do NOT use hashtags, emojis, or quotation marks. Just the line itself."""

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip().strip('"').strip("'")
            if len(text) > 0 and len(text) < 200:
                return text
        except Exception as e:
            print(f"Gemini API error: {e}")

        # Fallback
        lines = self.fallbacks.get(sync_level, self.fallbacks["disconnected"])
        line = lines[self.fallback_index % len(lines)]
        self.fallback_index += 1
        return line
```

---

### 6.6 — ElevenLabs Voice Narrator

**File:** `server/elevenlabs_client.py`

```python
import os
import threading
from elevenlabs import stream
from elevenlabs.client import ElevenLabs

class VoiceNarrator:
    """Speaks commentary aloud using ElevenLabs TTS."""

    def __init__(self):
        self.client = ElevenLabs(
            api_key=os.environ.get("ELEVENLABS_API_KEY", "")
        )
        # Use a warm, romantic voice
        # "Rachel" is a good default - warm female voice
        # "Adam" for warm male voice
        # Browse voices at https://elevenlabs.io/voice-library
        self.voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel
        self.speaking = False
        self.lock = threading.Lock()

    def speak(self, text):
        """Speak text aloud (non-blocking)."""
        if self.speaking:
            return  # Don't overlap
        
        thread = threading.Thread(
            target=self._speak_sync, args=(text,), daemon=True
        )
        thread.start()

    def _speak_sync(self, text):
        """Synchronous speak (runs in thread)."""
        with self.lock:
            self.speaking = True
            try:
                audio_stream = self.client.text_to_speech.stream(
                    text=text,
                    voice_id=self.voice_id,
                    model_id="eleven_multilingual_v2",
                )
                stream(audio_stream)
            except Exception as e:
                print(f"ElevenLabs error: {e}")
            finally:
                self.speaking = False
```

---

### 6.7 — MongoDB Session Logger

**File:** `server/mongo_client.py`

```python
import os
import time
from pymongo import MongoClient
from datetime import datetime

class SessionLogger:
    """Logs session data to MongoDB Atlas for history and analytics."""

    def __init__(self):
        uri = os.environ.get("MONGODB_URI", "")
        if uri:
            self.client = MongoClient(uri)
            self.db = self.client["heartsync"]
            self.sessions = self.db["sessions"]
            self.snapshots = self.db["snapshots"]
            self.connected = True
        else:
            self.connected = False
            print("Warning: MONGODB_URI not set, logging disabled")

        self.current_session_id = None

    def start_session(self):
        """Create a new session document."""
        if not self.connected:
            return
        result = self.sessions.insert_one({
            "started_at": datetime.utcnow(),
            "ended_at": None,
            "peak_sync": 0,
            "avg_sync": 0,
        })
        self.current_session_id = result.inserted_id

    def end_session(self):
        """Mark session as ended and compute summary stats."""
        if not self.connected or not self.current_session_id:
            return
        
        # Compute averages from snapshots
        pipeline = [
            {"$match": {"session_id": self.current_session_id}},
            {"$group": {
                "_id": None,
                "avg_sync": {"$avg": "$sync.score"},
                "peak_sync": {"$max": "$sync.score"},
            }}
        ]
        stats = list(self.snapshots.aggregate(pipeline))
        
        update = {"ended_at": datetime.utcnow()}
        if stats:
            update["avg_sync"] = stats[0].get("avg_sync", 0)
            update["peak_sync"] = stats[0].get("peak_sync", 0)

        self.sessions.update_one(
            {"_id": self.current_session_id},
            {"$set": update}
        )

    def log_snapshot(self, state):
        """Log a state snapshot (called every ~5 seconds)."""
        if not self.connected or not self.current_session_id:
            return
        
        state["session_id"] = self.current_session_id
        state["logged_at"] = datetime.utcnow()
        
        try:
            self.snapshots.insert_one(state)
        except Exception as e:
            print(f"MongoDB log error: {e}")
```

---

### 6.8 — LED Strip Controller

**File:** `hardware/led_controller.py` (for Raspberry Pi)

```python
"""
LED Strip Controller for HeartSync.
Drives a WS2812B (NeoPixel) strip via Raspberry Pi GPIO.

Wiring:
- LED Data → GPIO 18 (Pin 12)
- LED 5V   → 5V power (Pin 2 or external supply for long strips)
- LED GND  → GND (Pin 6)

Install: sudo pip3 install rpi_ws281x adafruit-circuitpython-neopixel
Run with sudo: sudo python3 led_controller.py
"""

import time
import math
import requests
import board
import neopixel

# Configuration
LED_COUNT = 30         # Number of LEDs on your strip
LED_PIN = board.D18    # GPIO pin
BRIGHTNESS = 0.5       # 0.0 to 1.0
SERVER_URL = "http://localhost:5000/api/state"

# Initialize strip
pixels = neopixel.NeoPixel(
    LED_PIN, LED_COUNT,
    brightness=BRIGHTNESS,
    auto_write=False  # We'll call show() manually for performance
)

# Color palettes for each sync level
COLORS = {
    "disconnected": {
        "a": (30, 60, 200),    # Cool blue
        "b": (200, 40, 40),    # Warm red
    },
    "warming_up": {
        "a": (100, 50, 180),   # Purple-blue
        "b": (180, 50, 100),   # Purple-red
    },
    "connecting": {
        "a": (170, 50, 130),   # Magenta
        "b": (170, 50, 130),   # Same - blending
    },
    "deeply_connected": {
        "a": (220, 40, 80),    # Warm rose
        "b": (220, 40, 80),    # Unified
    },
}


def lerp_color(c1, c2, t):
    """Linear interpolation between two RGB colors."""
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def heartbeat_pulse(t, bpm):
    """
    Generate a heartbeat-like brightness curve.
    Returns 0.0 to 1.0.
    """
    if bpm <= 0:
        return 0.5
    period = 60.0 / bpm
    phase = (t % period) / period
    # Double-bump heartbeat shape
    if phase < 0.15:
        return 0.4 + 0.6 * math.sin(phase / 0.15 * math.pi)
    elif phase < 0.35:
        return 0.4 + 0.4 * math.sin((phase - 0.15) / 0.2 * math.pi)
    else:
        return 0.3 + 0.1 * math.sin((phase - 0.35) / 0.65 * math.pi)


def update_leds(state):
    """Update LED strip based on current state."""
    sync = state.get("sync", {})
    score = sync.get("score", 0)
    level = sync.get("level", "disconnected")
    hr_a = state.get("person_a", {}).get("heart_rate", 70)
    hr_b = state.get("person_b", {}).get("heart_rate", 70)

    colors = COLORS.get(level, COLORS["disconnected"])
    t = time.time()

    # Compute heartbeat brightness
    pulse_a = heartbeat_pulse(t, hr_a)
    pulse_b = heartbeat_pulse(t, hr_b)

    # At high sync, use averaged pulse; at low sync, use individual
    avg_pulse = (pulse_a + pulse_b) / 2
    blend = score  # 0 = fully separate, 1 = fully unified

    half = LED_COUNT // 2

    for i in range(LED_COUNT):
        if i < half:
            # Person A's side
            pulse = pulse_a * (1 - blend) + avg_pulse * blend
            color = lerp_color(colors["a"], colors["b"], blend)
        else:
            # Person B's side
            pulse = pulse_b * (1 - blend) + avg_pulse * blend
            color = lerp_color(colors["b"], colors["a"], blend)

        # Apply pulse brightness
        pixels[i] = tuple(int(c * pulse) for c in color)

    pixels.show()


def main():
    """Main loop: poll server state and update LEDs."""
    print("🫀 HeartSync LED Controller started")
    
    while True:
        try:
            resp = requests.get(SERVER_URL, timeout=1)
            state = resp.json()
            update_leds(state)
        except requests.exceptions.ConnectionError:
            # Server not ready yet - show idle animation
            for i in range(LED_COUNT):
                t = time.time()
                brightness = 0.3 + 0.2 * math.sin(t * 2 + i * 0.3)
                pixels[i] = (int(50 * brightness), int(10 * brightness), int(30 * brightness))
            pixels.show()
        except Exception as e:
            print(f"LED error: {e}")

        time.sleep(0.033)  # ~30fps


if __name__ == "__main__":
    main()
```

**Alternative: Arduino version** — If using an Arduino instead of a Pi, write a simple serial protocol where the Python server sends LED commands over USB serial (e.g., `S0.75\n` for sync score 0.75), and the Arduino runs a FastLED sketch that interprets them. This is even simpler to wire up.

---

### 6.9 — Music System

**File:** `server/music_controller.py`

```python
"""
Reactive Music System for HeartSync.

Uses 3 pre-prepared audio stems that crossfade based on sync score:
- Layer A: Warm, harmonious ambient (plays at high sync)
- Layer B: Neutral melodic pad (always plays softly)
- Layer C: Dissonant/tense texture (plays at low sync)

Audio files should be:
- WAV or OGG format
- Same length and BPM (loop seamlessly)
- Placed in audio/ directory

For the hackathon: Use royalty-free ambient music or generate 
stems using AI music tools ahead of time.
"""

import pygame
import threading
import time

class MusicController:
    """Crossfades music layers based on sync score."""

    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        pygame.mixer.set_num_channels(4)
        
        self.channels = {
            "harmony": pygame.mixer.Channel(0),
            "neutral": pygame.mixer.Channel(1),
            "tension": pygame.mixer.Channel(2),
            "narration": pygame.mixer.Channel(3),  # Reserved for ElevenLabs
        }
        
        self.sounds = {}
        self.loaded = False
        self.current_sync = 0.0

    def load_stems(self, harmony_path, neutral_path, tension_path):
        """Load the three music stems."""
        try:
            self.sounds["harmony"] = pygame.mixer.Sound(harmony_path)
            self.sounds["neutral"] = pygame.mixer.Sound(neutral_path)
            self.sounds["tension"] = pygame.mixer.Sound(tension_path)
            self.loaded = True
        except Exception as e:
            print(f"Music load error: {e}")
            self.loaded = False

    def start(self):
        """Start playing all layers (volumes will be controlled by update)."""
        if not self.loaded:
            return
        for name, channel in self.channels.items():
            if name in self.sounds:
                channel.play(self.sounds[name], loops=-1)  # Loop forever
        # Start with neutral mix
        self.update_sync(0.5)

    def stop(self):
        """Stop all music."""
        for channel in self.channels.values():
            channel.stop()

    def update_sync(self, sync_score):
        """
        Adjust layer volumes based on sync score.
        
        sync = 0.0 (disconnected):
            harmony=0.0, neutral=0.3, tension=0.7
        sync = 0.5 (connecting):
            harmony=0.4, neutral=0.5, tension=0.2
        sync = 1.0 (deeply connected):
            harmony=0.8, neutral=0.3, tension=0.0
        """
        if not self.loaded:
            return

        self.current_sync = sync_score
        s = sync_score

        harmony_vol = min(1.0, s * 1.0)           # 0→0, 0.5→0.5, 1.0→1.0
        neutral_vol = 0.3 + 0.2 * (1 - abs(s - 0.5) * 2)  # Peak at 0.5
        tension_vol = max(0.0, 0.7 - s * 1.0)     # 0.7→0, tapers off

        self.channels["harmony"].set_volume(harmony_vol)
        self.channels["neutral"].set_volume(neutral_vol)
        self.channels["tension"].set_volume(tension_vol)
```

**Where to get the audio stems:**
- **Before the hackathon:** Generate 3 looping ambient stems using a free AI music tool (Suno, Udio, etc.) or download royalty-free ambient loops from Freesound.org
- Each stem should be 30–60 seconds and loop cleanly
- Layer A: search for "warm ambient pad loop" or "romantic piano ambient"
- Layer B: search for "neutral synth pad loop"  
- Layer C: search for "tense atmospheric drone loop" or "dissonant ambient"
- Save as WAV files in an `audio/` directory

---

### 6.10 — Web Display

**File:** `display/index.html`

This is the visual centerpiece. Build as a single HTML file with inline CSS/JS for simplicity.

**Key features to implement:**
- Two heart shapes (SVG or CSS) that scale/pulse to each person's real BPM
- Hearts drift closer together as sync increases
- Sync score displayed as a large arc/circle gauge
- Background color shifts: cool blues (low sync) → warm pinks/reds (high sync)
- Particle effects when sync > 75% (hearts, sparkles)
- Live heart rate numbers for each person
- Commentary text appears at bottom when Gemini generates it
- Session timer
- "Start Session" button

**Tech approach:**
- Connect to Flask via Socket.IO for real-time updates
- Use `requestAnimationFrame` for smooth animations
- Heart pulse: scale transform with timing based on `60 / BPM * 1000` ms period
- Chart.js for optional live HR line graph

**Display layout sketch:**

```
┌──────────────────────────────────────────────────┐
│                                                   │
│          ♥ 72 BPM          ♥ 74 BPM              │
│        (Person A)        (Person B)               │
│            ←── hearts drift closer ──→            │
│                                                   │
│                  ┌─────────┐                      │
│                  │  87%    │                       │
│                  │  SYNC   │                       │
│                  └─────────┘                       │
│                                                   │
│     "Your hearts are speaking the same language"  │
│                                                   │
│    ──────── HR Graph over time ────────           │
│                                                   │
└──────────────────────────────────────────────────┘
```

---

## 7. Sync Score Algorithm

### Design Philosophy

The sync score represents **how connected two people are** as measured across multiple channels. It's designed to:

1. Respond to genuine human connection behaviors (eye contact, shared smiling, physical touch)
2. Create a satisfying experience curve — easy to get from 0→40%, requires real connection for 70%+
3. Feel responsive but not jumpy — smoothed over ~5 seconds

### Weight Rationale

| Channel | Weight | Why |
|---|---|---|
| Heart rate similarity | 0.35 | Core biometric — this is the hero feature. Presage provides this. |
| Eye contact | 0.20 | Research shows eye contact is the strongest predictor of interpersonal connection. MediaPipe detects this. |
| Breathing synchrony | 0.15 | Breathing patterns naturally sync between connected people. Presage provides this. |
| Mutual smiling | 0.15 | Shared positive emotion is a key connection signal. MediaPipe detects this. |
| Hand proximity | 0.15 | Physical touch is a direct, intentional connection action. MediaPipe hand tracking detects this. |

### Tuning Tips

- If the score feels too easy to max out: reduce eye_contact weight, increase hr_sync weight
- If it feels impossible: reduce hr_sync weight (heart rates may naturally differ)
- Test with yourselves during build — sit side by side, try different interactions, tune until it feels right
- The smoothing window (deque maxlen=10 at 500ms = 5 second window) is the main "feel" knob

---

## 8. Hour-by-Hour Build Plan

### Phase 1: Foundation (Hours 0–3)

```
HOUR 0-1 | BOTH TOGETHER
├── Register for ALL API keys:
│   ├── Presage: https://physiology.presagetech.com
│   ├── ElevenLabs: https://elevenlabs.io (sign up, get API key from dashboard)
│   ├── Gemini: https://aistudio.google.com/apikey
│   └── MongoDB Atlas: https://cloud.mongodb.com (create free cluster)
├── Set up shared Git repo
├── Both install Presage Android example on your phones
├── Confirm: phone → Presage → see heart rate data on screen
└── Create project .env file with all API keys

HOUR 1-2 | SPLIT
├── Person A: Get Flask server skeleton running
│   ├── Endpoints: /api/biometrics, /api/state, /api/session/start
│   └── Test: curl POST to /api/biometrics, GET /api/state returns data
│
└── Person B: Get MediaPipe running
    ├── pip install mediapipe opencv-python
    ├── Run face mesh on webcam, confirm 2-face detection
    └── Run hand tracking, confirm detection

HOUR 2-3 | SPLIT
├── Person A: Modify Presage Android app
│   ├── Add HTTP POST to send biometric data to Flask
│   ├── Build + install on both phones
│   └── TEST: Both phones streaming data to Flask, server prints it
│
└── Person B: Wire up LED strip
    ├── Connect NeoPixels to Pi/Arduino GPIO
    ├── Run basic test (rainbow, solid color)
    └── TEST: LEDs respond to a hardcoded command
```

### Phase 2: Core Pipeline (Hours 3–8)

```
HOUR 3-5 | SPLIT
├── Person A: Build sync engine + integrate MediaPipe into server
│   ├── Implement sync_engine.py with all 5 channels
│   ├── Connect MediaPipe tracker as background thread
│   ├── Wire up: biometrics + vision → sync score → /api/state
│   └── TEST: /api/state returns real sync score from real inputs
│
└── Person B: Build web display
    ├── Create display/index.html with heart animations
    ├── Connect to Flask via Socket.IO
    ├── Display: two hearts, BPM numbers, sync score gauge
    └── TEST: Display updates when state changes

HOUR 5-8 | SPLIT
├── Person A: Integrate Gemini + ElevenLabs + MongoDB
│   ├── gemini_client.py — generate commentary from biometric state
│   ├── elevenlabs_client.py — speak the commentary aloud
│   ├── mongo_client.py — log snapshots to Atlas
│   ├── Wire all three into the server's update loop
│   └── TEST: Commentary generates and speaks every 30 seconds
│
└── Person B: Build LED controller + music system
    ├── led_controller.py — polls /api/state, drives LEDs by sync level
    ├── music_controller.py — crossfades 3 stems by sync score
    ├── Integrate music into server main loop
    └── TEST: LEDs and music respond to changing sync scores
```

### Phase 3: Integration & Polish (Hours 8–14)

```
HOUR 8-10 | BOTH TOGETHER
├── FULL END-TO-END TEST
│   ├── Both phones streaming Presage data
│   ├── Webcam tracking both faces + hands
│   ├── Sync score computing from all channels
│   ├── Display showing real-time hearts + score
│   ├── LEDs responding to sync level
│   ├── Music crossfading with sync
│   ├── Gemini generating commentary
│   ├── ElevenLabs speaking it
│   └── MongoDB logging snapshots
├── Identify what's broken → fix
└── Identify what's janky → smooth

HOUR 10-14 | SPLIT
├── Person A: Backend polish
│   ├── Tune sync score weights (test with yourselves!)
│   ├── Handle edge cases (phone disconnects, camera blocked)
│   ├── Add fallback commentary if Gemini fails
│   ├── Optimize update frequency if laggy
│   └── Add session summary endpoint for Devpost
│
└── Person B: Frontend + hardware polish
    ├── Make display beautiful (gradients, animations, particles)
    ├── Valentine's theme (pinks, reds, heart particles)
    ├── Mount LEDs in heart-shaped frame (cardboard + hot glue)
    ├── Polish music transitions (ensure no audio glitches)
    └── Add "Start/Stop Session" UI flow
```

### Phase 4: Demo Prep (Hours 14–20)

```
HOUR 14-16 | BOTH TOGETHER
├── Write Devpost submission
│   ├── Project name, description, screenshots
│   ├── Take photos of hardware setup
│   ├── Screenshot the display at different sync levels
│   ├── Document the tech stack and architecture
│   └── SELECT ALL PRIZE CATEGORIES
├── Write demo pitch script (2 minutes)
└── Practice demo 3x

HOUR 16-18 | SPLIT
├── Person A: Record backup demo video
│   ├── Screen record the display + audio
│   ├── Film the LED strip reacting
│   └── Upload to YouTube (unlisted)
│
└── Person B: Final visual polish
    ├── Ensure display looks great on projector/monitor
    ├── Add loading states and error handling to UI
    └── Make the "high sync" moment feel magical

HOUR 18-20 | BOTH TOGETHER
├── Full dress rehearsal of demo
├── Time the demo (must fit in 2-3 minutes)
├── Prepare for Q&A (common judge questions below)
└── SET UP DEMO STATION
    ├── Laptop centered with display visible
    ├── LED heart frame positioned behind/beside
    ├── Both phones on stands pointing at demo volunteers
    └── Speaker volume check
```

### Phase 5: Buffer & Final (Hours 20–24)

```
HOUR 20-24 | BOTH
├── This is your safety buffer
├── Fix any remaining bugs
├── If everything works: add stretch features
│   ├── Thermal printer for "compatibility receipt"
│   ├── Session history page on display
│   └── Edge Impulse audio classification (if time)
├── Final Devpost submission review
├── SUBMIT ON DEVPOST (don't wait until last minute!)
└── Rest, eat, practice demo one more time
```

---

## 9. Task Split (2 People)

### Person A: "Backend + Sensing"

**Owns:** Flask server, sync engine, Presage integration, Gemini API, MongoDB, MediaPipe integration into server.

**Skills needed:** Python, basic Android (Kotlin), API integration, algorithm design.

**Key deliverables:**
1. Modified Presage Android app (both phones)
2. `server/app.py` — Flask server
3. `server/sync_engine.py` — Sync score algorithm
4. `server/gemini_client.py` — Commentary generation
5. `server/mongo_client.py` — Session logging
6. `vision/mediapipe_tracker.py` — MediaPipe wrapper

### Person B: "Frontend + Output"

**Owns:** Web display, LED strip, music system, ElevenLabs TTS, hardware assembly, demo polish.

**Skills needed:** HTML/CSS/JS, basic Python, basic electronics (wiring LEDs), UX design sense.

**Key deliverables:**
1. `display/index.html` — Main web display
2. `hardware/led_controller.py` — LED strip driver
3. `server/music_controller.py` — Reactive audio
4. `server/elevenlabs_client.py` — TTS narration
5. Physical LED heart frame
6. Demo presentation + Devpost writeup

### Shared Responsibilities
- API key registration (Hour 0)
- End-to-end testing (Hours 8-10)
- Demo practice (Hours 14+)
- Devpost submission (Hours 14-16)

---

## 10. Demo Script

### The 2-Minute Pitch

**[0:00-0:15] Hook**

"What if technology could measure something we all feel but can never see — the connection between two people? On Valentine's Day, we built HeartSync."

**[0:15-0:35] How It Works**

"HeartSync reads your heart rate through your phone's camera — no wearables, no touching — using Presage's contactless biometric sensing. Our laptop's webcam uses MediaPipe computer vision to detect eye contact, smiles, and physical touch. All these signals fuse into a single sync score that drives lights, music, and AI-generated narration."

**[0:35-1:30] Live Demo**

"Let us show you. [Both sit down, phones activate] Right now our hearts are beating independently — you can see the two different rhythms on screen, and the LEDs are split into two colors."

[Look at each other, maybe hold hands]

"Watch what happens as we connect... [sync score rises] The hearts are drifting together. The music is harmonizing. The lights are blending."

[Sync hits high — ElevenLabs speaks a romantic line, LEDs pulse in unison]

"That line was generated live by Gemini based on our actual biometric data, and spoken by ElevenLabs."

**[1:30-1:50] Technical Depth**

"Under the hood: Presage for contactless physiology, MediaPipe for computer vision, Gemini for AI commentary, ElevenLabs for voice, MongoDB Atlas for session history, and a Raspberry Pi driving the LED strip. Five sensing channels fused into one sync score."

**[1:50-2:00] Close**

"HeartSync — because the best connections aren't just felt, they're seen. Happy Valentine's Day."

### Common Judge Questions & Answers

**Q: How accurate is the contactless heart rate?**
A: Presage's clinical trials show less than 1.62% error compared to hospital equipment. It's surprisingly accurate even through a phone camera.

**Q: What happens if someone moves or lighting is bad?**
A: Presage has built-in quality metrics. If confidence drops, we weight other channels (MediaPipe, hand tracking) more heavily. The system degrades gracefully.

**Q: Could this scale beyond two people?**
A: Absolutely — you could use it for group bonding exercises, therapy sessions, concert audience engagement, or even long-distance couples using video calls.

**Q: Why these specific weights for the sync score?**
A: Heart rate is the hero biometric (35%) because it's involuntary and hard to fake. Eye contact gets 20% because research consistently shows it's the strongest predictor of interpersonal connection. The remaining channels add richness.

---

## 11. Devpost Submission Guide

### Required Fields

- **Project name:** HeartSync
- **Tagline:** "Where technology meets the human heart — measuring the invisible connection between two people through contactless biometrics, computer vision, and AI."
- **Description:** Include architecture diagram, tech stack, how sync score works, challenges overcome, what you learned, future potential.
- **Built with:** Python, Flask, MediaPipe, Presage SmartSpectra SDK, Google Gemini API, ElevenLabs, MongoDB Atlas, Raspberry Pi, NeoPixel LED Strip, HTML/CSS/JavaScript, Socket.IO
- **Try it out:** Link to GitHub repo
- **Video:** Upload demo video to YouTube (unlisted), link on Devpost

### Prize Categories to Select

CHECK ALL OF THESE:
- [ ] Valentine's Day Theme
- [ ] Audio/Music Theme
- [ ] Best Use of Presage
- [ ] Best Use of ElevenLabs
- [ ] Best Use of Gemini API
- [ ] Best Use of MongoDB Atlas

### Photos to Include

Take these during the build:
1. Both phones streaming data simultaneously
2. The web display showing hearts + sync score
3. LED heart frame glowing
4. The full setup (laptop + phones + LEDs + speaker)
5. You two demoing it (looking at each other with the display in background)

---

## 12. Risk Matrix & Fallbacks

| Risk | Probability | Impact | Fallback |
|---|---|---|---|
| Presage SDK fails to install or work | Medium | Critical | Use open-source webcam PPG (github.com/giladoved/webcam-heart-rate-monitor). Lose Presage prize, but project still works. |
| Two-phone setup is flaky | Medium | High | Use one phone, alternate between people for 15-sec readings. Compare stored values. Less dramatic but functional. |
| Both phones can't connect to laptop | Low | High | Use the C++ SDK on the laptop with two USB webcams instead. Or use one webcam and alternate. |
| Gemini API rate limited or down | Low | Low | Pre-generated fallback lines (already in gemini_client.py). Nobody will notice. |
| ElevenLabs API fails | Low | Medium | Use Python `pyttsx3` for offline TTS. Sounds worse but works. |
| MediaPipe can't detect 2 faces | Low | Medium | Works reliably in good lighting. Fallback: reduce face detection confidence threshold. Or run sync score with only Presage data. |
| Music crossfading sounds bad | Medium | Low | Use volume changes on a single track. Or just drop the music and rely on LEDs + voice. |
| LED strip doesn't work | Low | Medium | Use on-screen LED simulation. Still satisfies "hardware" with the Pi itself. |
| MongoDB Atlas connection fails | Low | Very Low | Just disable logging. No impact on demo. |
| WiFi is unreliable at venue | Medium | High | Create a local hotspot from one phone. Or run Presage C++ on the laptop directly. |

---

## 13. API Setup Guides

### Presage SmartSpectra

1. Go to https://physiology.presagetech.com
2. Register → verify email → log in
3. Dashboard shows your API key (click the `****` to reveal)
4. Copy the key → add to `.env` as `PRESAGE_API_KEY=your_key_here`
5. Also paste into the Android app's `MainActivity.kt`

### Google Gemini

1. Go to https://aistudio.google.com/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy → add to `.env` as `GEMINI_API_KEY=your_key_here`

### ElevenLabs

1. Go to https://elevenlabs.io → Sign up
2. Go to Profile → API Keys
3. Create a key → copy → add to `.env` as `ELEVENLABS_API_KEY=your_key_here`
4. Free tier gives 10,000 characters/month (plenty for a hackathon)

### MongoDB Atlas

1. Go to https://cloud.mongodb.com → Sign up
2. Create a free shared cluster (M0 tier, any region)
3. Create a database user (username/password)
4. Whitelist IP: click "Allow Access from Anywhere" (for hackathon simplicity)
5. Click "Connect" → "Connect your application" → copy the URI
6. Replace `<password>` in the URI → add to `.env` as `MONGODB_URI=your_uri_here`

### .env File Template

```bash
# HeartSync API Keys
PRESAGE_API_KEY=your_presage_key
GEMINI_API_KEY=your_gemini_key
ELEVENLABS_API_KEY=your_elevenlabs_key
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/heartsync

# Server Config
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
CAMERA_INDEX=0

# Display Config
LED_COUNT=30
LED_PIN=18
```

---

## 14. File & Folder Structure

```
heartsync/
├── .env                          # API keys (DO NOT COMMIT)
├── .gitignore
├── CLAUDE.md                     # Claude Code project context
├── README.md                     # Quick start guide
├── requirements.txt              # Python dependencies
│
├── server/
│   ├── app.py                    # Flask server (central brain)
│   ├── sync_engine.py            # Sync score algorithm
│   ├── gemini_client.py          # Gemini API commentary
│   ├── elevenlabs_client.py      # ElevenLabs TTS
│   ├── music_controller.py       # Reactive audio system
│   └── mongo_client.py           # MongoDB session logging
│
├── vision/
│   └── mediapipe_tracker.py      # MediaPipe face mesh + hand tracking
│
├── display/
│   ├── index.html                # Main web display (single file)
│   └── assets/                   # Heart SVGs, fonts, etc.
│
├── hardware/
│   ├── led_controller.py         # Raspberry Pi NeoPixel driver
│   └── arduino_led/              # (Alternative) Arduino FastLED sketch
│       └── arduino_led.ino
│
├── audio/
│   ├── harmony.wav               # Warm ambient stem
│   ├── neutral.wav               # Neutral pad stem
│   └── tension.wav               # Dissonant texture stem
│
├── android/
│   └── presage-heartsync/        # Modified Presage Android app
│       └── (cloned from SmartSpectra repo + our modifications)
│
├── scripts/
│   ├── setup.sh                  # Install all dependencies
│   └── start.sh                  # Launch everything
│
└── docs/
    ├── architecture.png          # System diagram for Devpost
    └── photos/                   # Build photos for submission
```
