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
