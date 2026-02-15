import os
import sys
import time
import threading
from dotenv import load_dotenv

# Load .env before any other imports that read env vars
load_dotenv()

# Fix sys.path so `from vision.mediapipe_tracker` works when running from server/
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO
from flask_cors import CORS

# Import our modules
from sync_engine import SyncEngine
from gemini_client import GeminiCommentary
from elevenlabs_client import VoiceNarrator
from mongo_client import SessionLogger
from music_controller import MusicController
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
music = MusicController()

# Try to load music stems
audio_dir = os.path.join(project_root, "audio")
harmony_path = os.path.join(audio_dir, "harmony.wav")
neutral_path = os.path.join(audio_dir, "neutral.wav")
tension_path = os.path.join(audio_dir, "tension.wav")
if os.path.exists(harmony_path) and os.path.exists(neutral_path) and os.path.exists(tension_path):
    music.load_stems(harmony_path, neutral_path, tension_path)
    print("Music stems loaded successfully")
else:
    print("Warning: Audio stems not found in audio/ directory, music disabled")

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
    music.start()
    return jsonify({"status": "started"})

@app.route('/api/session/stop', methods=['POST'])
def stop_session():
    """Stop the current session."""
    global session_active
    session_active = False
    mongo.end_session()
    music.stop()
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
    5. Updates music crossfade
    6. Logs to MongoDB (throttled to every ~5 seconds)
    """
    global last_commentary_time, last_sync_score

    tick = 0

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

        # 4. Update music crossfade
        music.update_sync(sync_result["score"])

        # 5. Commentary trigger (every 30s or on big sync change)
        now = time.time()
        sync_changed_a_lot = abs(sync_result["score"] - last_sync_score) > 0.2
        time_for_new = (now - last_commentary_time) > 30

        if (sync_changed_a_lot or time_for_new) and last_commentary_time > 0:
            _trigger_commentary(sync_result, vision_state)
            last_commentary_time = now
        elif last_commentary_time == 0:
            last_commentary_time = now  # First tick

        last_sync_score = sync_result["score"]

        # 6. Log to MongoDB (every ~5 seconds = every 10th tick at 500ms)
        tick += 1
        if tick % 10 == 0:
            mongo.log_snapshot(dict(state))

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
    camera_index = int(os.environ.get("CAMERA_INDEX", "0"))
    vision_tracker.start(camera_index=camera_index)

    # Start update loop in background thread
    update_thread = threading.Thread(target=update_loop, daemon=True)
    update_thread.start()

    host = os.environ.get("FLASK_HOST", "0.0.0.0")
    port = int(os.environ.get("FLASK_PORT", "5000"))

    print(f"\n HeartSync Server running on http://{host}:{port}")
    print("   Open browser to see the display")
    print("   Waiting for phone connections...\n")

    socketio.run(app, host=host, port=port, debug=False)
