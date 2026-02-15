/*
 * HeartSync LED Controller — Arduino FastLED Version
 *
 * Drives a WS2812B strip of 30 LEDs on pin 6.
 * Receives sync score and heart rate data over Serial from a host
 * (e.g., a Python bridge script that polls the Flask server).
 *
 * Serial Protocol (9600 baud):
 *   S0.75\n   — Set sync score (0.00 to 1.00)
 *   HA72\n    — Set Person A heart rate (BPM)
 *   HB74\n    — Set Person B heart rate (BPM)
 *
 * Wiring:
 *   - LED Data  -> Pin 6 (through a 330-ohm resistor)
 *   - LED 5V    -> 5V (external supply for >10 LEDs)
 *   - LED GND   -> GND (shared with Arduino GND)
 *   - 1000uF capacitor across LED 5V and GND recommended
 */

#include <FastLED.h>

// ---------- Configuration ----------
#define LED_PIN     6
#define NUM_LEDS    30
#define BRIGHTNESS  128    // 0-255
#define LED_TYPE    WS2812B
#define COLOR_ORDER GRB

// ---------- Global State ----------
CRGB leds[NUM_LEDS];

float syncScore  = 0.0;   // 0.0 to 1.0
float hrA        = 70.0;  // Person A BPM
float hrB        = 70.0;  // Person B BPM

// Serial input buffer
char serialBuf[32];
int  serialIdx = 0;

// Idle detection: switch to idle animation if no serial data for 5 seconds
unsigned long lastSerialTime = 0;
const unsigned long IDLE_TIMEOUT_MS = 5000;

// ---------- Color Palettes ----------
// Each sync level has a color for Person A's half and Person B's half.
// Format: {R, G, B}

// disconnected (score < 0.25): cool blue / warm red
const CRGB COLOR_DISC_A = CRGB(30, 60, 200);
const CRGB COLOR_DISC_B = CRGB(200, 40, 40);

// warming_up (0.25 <= score < 0.50): purple-blue / purple-red
const CRGB COLOR_WARM_A = CRGB(100, 50, 180);
const CRGB COLOR_WARM_B = CRGB(180, 50, 100);

// connecting (0.50 <= score < 0.75): magenta (same both sides)
const CRGB COLOR_CONN_A = CRGB(170, 50, 130);
const CRGB COLOR_CONN_B = CRGB(170, 50, 130);

// deeply_connected (score >= 0.75): warm rose (unified)
const CRGB COLOR_DEEP_A = CRGB(220, 40, 80);
const CRGB COLOR_DEEP_B = CRGB(220, 40, 80);


// ---------- Utility Functions ----------

/**
 * Linear interpolation between two CRGB colors.
 * t = 0.0 returns c1, t = 1.0 returns c2.
 */
CRGB lerpColor(CRGB c1, CRGB c2, float t) {
    t = constrain(t, 0.0, 1.0);
    return CRGB(
        c1.r + (int)((c2.r - c1.r) * t),
        c1.g + (int)((c2.g - c1.g) * t),
        c1.b + (int)((c2.b - c1.b) * t)
    );
}

/**
 * Scale a color's brightness by a factor (0.0 to 1.0).
 */
CRGB scaleColor(CRGB c, float factor) {
    factor = constrain(factor, 0.0, 1.0);
    return CRGB(
        (uint8_t)(c.r * factor),
        (uint8_t)(c.g * factor),
        (uint8_t)(c.b * factor)
    );
}

/**
 * Generate a heartbeat-like brightness curve (0.0 to 1.0).
 * Uses millis() as the time base and BPM as the rate.
 * Produces a double-bump pattern mimicking a real heartbeat.
 */
float heartbeatPulse(float bpm) {
    if (bpm <= 0) return 0.5;

    float periodMs = 60000.0 / bpm;            // One beat period in ms
    float phase = fmod(millis(), periodMs) / periodMs;  // 0.0 to 1.0

    // Double-bump heartbeat shape:
    //   First bump  (systolic):  0.00 - 0.15 of the cycle
    //   Second bump (diastolic): 0.15 - 0.35 of the cycle
    //   Resting:                 0.35 - 1.00 of the cycle
    if (phase < 0.15) {
        return 0.4 + 0.6 * sin(phase / 0.15 * PI);
    } else if (phase < 0.35) {
        return 0.4 + 0.4 * sin((phase - 0.15) / 0.2 * PI);
    } else {
        return 0.3 + 0.1 * sin((phase - 0.35) / 0.65 * PI);
    }
}

/**
 * Get the color pair for the current sync level.
 */
void getSyncColors(CRGB &colorA, CRGB &colorB) {
    if (syncScore >= 0.75) {
        colorA = COLOR_DEEP_A;
        colorB = COLOR_DEEP_B;
    } else if (syncScore >= 0.50) {
        colorA = COLOR_CONN_A;
        colorB = COLOR_CONN_B;
    } else if (syncScore >= 0.25) {
        colorA = COLOR_WARM_A;
        colorB = COLOR_WARM_B;
    } else {
        colorA = COLOR_DISC_A;
        colorB = COLOR_DISC_B;
    }
}


// ---------- Serial Parsing ----------

/**
 * Process a complete line received over Serial.
 * Supported commands:
 *   S<float>   — sync score (e.g., "S0.75")
 *   HA<float>  — Person A heart rate (e.g., "HA72")
 *   HB<float>  — Person B heart rate (e.g., "HB74")
 */
void processSerialLine(const char *line) {
    lastSerialTime = millis();
    if (line[0] == 'S') {
        syncScore = constrain(atof(line + 1), 0.0, 1.0);
    } else if (line[0] == 'H' && line[1] == 'A') {
        hrA = constrain(atof(line + 2), 0.0, 250.0);
    } else if (line[0] == 'H' && line[1] == 'B') {
        hrB = constrain(atof(line + 2), 0.0, 250.0);
    }
}

/**
 * Read all available Serial data and process complete lines.
 */
void readSerial() {
    while (Serial.available() > 0) {
        char c = Serial.read();
        if (c == '\n' || c == '\r') {
            if (serialIdx > 0) {
                serialBuf[serialIdx] = '\0';
                processSerialLine(serialBuf);
                serialIdx = 0;
            }
        } else if (serialIdx < (int)(sizeof(serialBuf) - 1)) {
            serialBuf[serialIdx++] = c;
        }
    }
}


// ---------- LED Update ----------

/**
 * Update the entire LED strip based on current sync score and heart rates.
 *
 * Behavior:
 *   - Strip is split in half: left = Person A, right = Person B.
 *   - Each half gets a color based on the sync level.
 *   - Each half pulses at the corresponding person's BPM.
 *   - As sync score rises, both halves blend toward a unified color
 *     and their pulse timing merges toward an averaged heartbeat.
 */
void updateLEDs() {
    CRGB colorA, colorB;
    getSyncColors(colorA, colorB);

    float pulseA   = heartbeatPulse(hrA);
    float pulseB   = heartbeatPulse(hrB);
    float avgPulse = (pulseA + pulseB) / 2.0;

    // blend factor: 0 = fully separate, 1 = fully unified
    float blend = syncScore;

    int half = NUM_LEDS / 2;

    for (int i = 0; i < NUM_LEDS; i++) {
        float pulse;
        CRGB  color;

        if (i < half) {
            // Person A's side
            pulse = pulseA * (1.0 - blend) + avgPulse * blend;
            color = lerpColor(colorA, colorB, blend);
        } else {
            // Person B's side
            pulse = pulseB * (1.0 - blend) + avgPulse * blend;
            color = lerpColor(colorB, colorA, blend);
        }

        leds[i] = scaleColor(color, pulse);
    }

    FastLED.show();
}

/**
 * Show a gentle idle breathing animation when no data is being received.
 * Soft pink/purple glow that slowly breathes.
 */
void idleAnimation() {
    float t = millis() / 1000.0;
    for (int i = 0; i < NUM_LEDS; i++) {
        float brightness = 0.3 + 0.2 * sin(t * 2.0 + i * 0.3);
        leds[i] = CRGB(
            (uint8_t)(50 * brightness),
            (uint8_t)(10 * brightness),
            (uint8_t)(30 * brightness)
        );
    }
    FastLED.show();
}


// ---------- Arduino Entry Points ----------

void setup() {
    Serial.begin(9600);

    FastLED.addLeds<LED_TYPE, LED_PIN, COLOR_ORDER>(leds, NUM_LEDS)
        .setCorrection(TypicalLEDStrip);
    FastLED.setBrightness(BRIGHTNESS);

    // Clear strip on startup
    fill_solid(leds, NUM_LEDS, CRGB::Black);
    FastLED.show();

    Serial.println("HeartSync Arduino LED Controller ready");
    Serial.println("Commands: S<score> HA<bpm> HB<bpm>");
}

void loop() {
    readSerial();

    // Fall back to idle animation if no serial data for 5 seconds
    if (millis() - lastSerialTime > IDLE_TIMEOUT_MS) {
        idleAnimation();
    } else {
        updateLEDs();
    }

    // Run at roughly 30 FPS
    delay(33);
}
