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
