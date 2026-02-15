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
            max_num_hands=4,  # Up to 4 hands (2 people x 2 hands)
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

                    # Eye contact detection
                    new_state["eye_contact"] = self._detect_eye_contact(
                        faces[0], faces[1], w, h
                    )

                    # Face distance
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
        # Left ear: 234, Right ear: 454, Nose: 1
        face1_direction = lm1[1].x - (lm1[234].x + lm1[454].x) / 2
        face2_direction = lm2[1].x - (lm2[234].x + lm2[454].x) / 2

        # If face1 is left of face2
        if nose1_x < nose2_x:
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
