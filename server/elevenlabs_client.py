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
        # "Rachel" - warm female voice
        self.voice_id = "21m00Tcm4TlvDq8ikWAM"
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
