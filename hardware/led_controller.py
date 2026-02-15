"""
LED Strip Controller for HeartSync.
Drives a WS2812B (NeoPixel) strip via Raspberry Pi GPIO.

Wiring:
- LED Data -> GPIO 18 (Pin 12)
- LED 5V   -> 5V power (Pin 2 or external supply for long strips)
- LED GND  -> GND (Pin 6)

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
    print("HeartSync LED Controller started")

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
