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
