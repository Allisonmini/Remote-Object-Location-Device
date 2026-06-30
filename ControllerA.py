# =================================================================
# PROJECT R.O.L.D. - ROLE A: HANDHELD FLIGHT CONTROLLER (Functional)
# =================================================================
from microbit import *
import radio

# --- OLED DRIVER (now with a REAL character renderer) -----------------
# The original oled_print() only called print() (serial console) and never
# drew anything on the glass. Below adds a small 5x8 font + a renderer so
# text actually appears on the screen. oled_init() and oled_clear() are
# unchanged from the provided boilerplate.
OLED_ADDR = 0x3C
def oled_command(cmd):
    i2c.write(OLED_ADDR, bytes([0x00, cmd]))
def oled_init():
    i2c.init(freq=400000)
    for cmd in [0xAE, 0xD5, 0x80, 0xA8, 0x3F, 0xD3, 0x00, 0x40, 0x8D, 0x14,
                0x20, 0x02, 0xA1, 0xC8, 0xDA, 0x12, 0x81, 0xCF, 0xD9, 0xF1,
                0xDB, 0x40, 0xA4, 0xA6, 0xAF]:
        oled_command(cmd)
def oled_clear():
    for page in range(8):
        oled_command(0xB0 + page)
        oled_command(0x00)
        oled_command(0x10)
        i2c.write(OLED_ADDR, bytes([0x40] + [0] * 128))

# 5x8 bitmap font. Each char = 5 column-bytes; each byte's bits are the 8
# vertical pixels of that column (LSB = top row). Only the glyphs this
# project actually prints are included to keep memory small. Unknown
# characters render as a blank space.
_FONT = {
    ' ': (0x00, 0x00, 0x00, 0x00, 0x00),
    '-': (0x08, 0x08, 0x08, 0x08, 0x08),
    ':': (0x00, 0x36, 0x36, 0x00, 0x00),
    '.': (0x00, 0x60, 0x60, 0x00, 0x00),
    '(': (0x00, 0x1C, 0x22, 0x41, 0x00),
    ')': (0x00, 0x41, 0x22, 0x1C, 0x00),
    '0': (0x3E, 0x51, 0x49, 0x45, 0x3E),
    '1': (0x00, 0x42, 0x7F, 0x40, 0x00),
    '2': (0x42, 0x61, 0x51, 0x49, 0x46),
    '3': (0x21, 0x41, 0x45, 0x4B, 0x31),
    '4': (0x18, 0x14, 0x12, 0x7F, 0x10),
    '5': (0x27, 0x45, 0x45, 0x45, 0x39),
    '6': (0x3C, 0x4A, 0x49, 0x49, 0x30),
    '7': (0x01, 0x71, 0x09, 0x05, 0x03),
    '8': (0x36, 0x49, 0x49, 0x49, 0x36),
    '9': (0x06, 0x49, 0x49, 0x29, 0x1E),
    'A': (0x7E, 0x11, 0x11, 0x11, 0x7E),
    'B': (0x7F, 0x49, 0x49, 0x49, 0x36),
    'C': (0x3E, 0x41, 0x41, 0x41, 0x22),
    'D': (0x7F, 0x41, 0x41, 0x22, 0x1C),
    'E': (0x7F, 0x49, 0x49, 0x49, 0x41),
    'F': (0x7F, 0x09, 0x09, 0x09, 0x01),
    'G': (0x3E, 0x41, 0x49, 0x49, 0x7A),
    'L': (0x7F, 0x40, 0x40, 0x40, 0x40),
    'M': (0x7F, 0x02, 0x0C, 0x02, 0x7F),
    'N': (0x7F, 0x04, 0x08, 0x10, 0x7F),
    'O': (0x3E, 0x41, 0x41, 0x41, 0x3E),
    'P': (0x7F, 0x09, 0x09, 0x09, 0x06),
    'R': (0x7F, 0x09, 0x19, 0x29, 0x46),
    'T': (0x01, 0x01, 0x7F, 0x01, 0x01),
    'U': (0x3F, 0x40, 0x40, 0x40, 0x3F),
    'W': (0x3F, 0x40, 0x38, 0x40, 0x3F),
    'X': (0x63, 0x14, 0x08, 0x14, 0x63),
    'Y': (0x07, 0x08, 0x70, 0x08, 0x07),
    'Z': (0x61, 0x51, 0x49, 0x45, 0x43),
    'a': (0x20, 0x54, 0x54, 0x54, 0x78),
    'c': (0x38, 0x44, 0x44, 0x44, 0x20),
    'e': (0x38, 0x54, 0x54, 0x54, 0x18),
    'g': (0x0C, 0x52, 0x52, 0x52, 0x3E),
    'i': (0x00, 0x44, 0x7D, 0x40, 0x00),
    'l': (0x00, 0x41, 0x7F, 0x40, 0x00),
    'm': (0x7C, 0x04, 0x18, 0x04, 0x78),
    'n': (0x7C, 0x08, 0x04, 0x04, 0x78),
    'o': (0x38, 0x44, 0x44, 0x44, 0x38),
    'r': (0x7C, 0x08, 0x04, 0x04, 0x08),
    't': (0x04, 0x3F, 0x44, 0x40, 0x20),
}

def _oled_set_pos(col, page):
    """Move the OLED's internal cursor to a pixel column and 8px page row."""
    oled_command(0xB0 + page)
    oled_command(0x00 + (col & 0x0F))
    oled_command(0x10 + (col >> 4))

def oled_print(text_line, row=0):
    """Render text on the physical OLED at the given row (0-7).
    Each char is 6px wide (5 font + 1 gap), so ~21 chars fit per row."""
    print(text_line)  # keep serial output too, handy for debugging
    if row < 0 or row > 7:
        return
    # Clear this row first so old text doesn't bleed through
    _oled_set_pos(0, row)
    i2c.write(OLED_ADDR, bytes([0x40] + [0] * 128))
    # Draw each character's 5 columns, then a 1px blank spacer
    col = 0
    _oled_set_pos(0, row)
    for ch in text_line:
        glyph = _FONT.get(ch, _FONT[' '])
        if col + 6 > 128:
            break  # ran off the right edge of the screen
        i2c.write(OLED_ADDR, bytes([0x40]) + bytes(glyph) + bytes([0x00]))
        col += 6
# ---------------------------------------------------------------------

# --- RADIO COMPATIBILITY HELPERS (added — see note below) ---
# Real MicroPython's `radio` only has on()/off()/config()/send()/receive().
# set_group(), send_value(), and receive_value() are MakeCode block names and
# will raise AttributeError on a real micro:bit. These helpers reproduce the
# same behavior on top of plain string messages and MUST stay identical to
# the matching ones in Role B so the two boards understand each other.
def radio_send_value(name, value):
    radio.send("{}:{}".format(name, value))

def radio_receive_value():
    message = radio.receive()
    if message is None or ":" not in message:
        return None
    name, raw_value = message.split(":", 1)
    try:
        value = int(raw_value)
    except ValueError:
        try:
            value = float(raw_value)
        except ValueError:
            value = raw_value
    return (name, value)
# ---------------------------------------------------------------------

# Initialize the radio and display hardware
radio.on()
radio.config(group=10)   # was radio.set_group(10) — same group, real call
oled_init()
oled_clear()
oled_print("Remote Online", row=0)

# --- SYSTEM FUNCTIONS (Provided for Students) ---

def read_hardware_tilt():
    """Reads raw physical accelerometer data from the back of the board.
    Returns a tuple containing (raw_pitch, raw_roll) values from -1024 to 1024."""
    pitch = accelerometer.get_y()
    roll  = accelerometer.get_x()
    return pitch, roll

def transmit_steering_commands(pan, tilt):
    """Broadcasts calculated servo angles wirelessly into the room."""
    radio_send_value("pan", pan)    # was radio.send_value(...)
    radio_send_value("tilt", tilt)

def check_for_incoming_telemetry():
    """Listens to the radio network for data packets from the turret.
    Writes distance to its own dedicated rows (4-5) so it doesn't fight
    with the steering readout on rows 0-2."""
    packet = radio_receive_value()  # was radio.receive_value()
    if packet:
        name  = packet[0]
        value = packet[1]
        if name == "dist":
            oled_print("--- TELEMETRY ---", row=4)
            oled_print("Target: " + str(value) + " cm", row=5)


# --- STUDENTS' MATHEMATICAL CHALLENGE ---

def convert_tilt_to_servo_angle(raw_tilt_value):
    """
    Maps a raw accelerometer reading (-1024 to 1024) to a servo angle (0 to 180).

    Linear mapping formula:
        angle = (raw - raw_min) / (raw_max - raw_min) * (angle_max - angle_min) + angle_min

    Breakdown:
        raw_min  = -1024,  raw_max  = 1024   <- accelerometer range
        angle_min = 0,     angle_max = 180   <- servo range

    So:
        angle = (raw_tilt_value + 1024) / 2048 * 180

    We also clamp the result so hardware is never sent an out-of-range value.
    """
    RAW_MIN   = -1024
    RAW_MAX   =  1024
    ANGLE_MIN =     0
    ANGLE_MAX =   180

    # Clamp input so a sharp jerk never produces garbage angles
    clamped = max(RAW_MIN, min(RAW_MAX, raw_tilt_value))

    # Linear interpolation: shift range to 0-2048, then scale to 0-180
    calculated_angle = (clamped - RAW_MIN) / (RAW_MAX - RAW_MIN) * (ANGLE_MAX - ANGLE_MIN) + ANGLE_MIN

    return int(calculated_angle)


# --- Z-AXIS (GESTURE) DETECTION ---

# Threshold for what counts as a strong upward/downward flick (mg units)
Z_THRESHOLD = 700

def read_z_gesture():
    """
    Reads the Z-axis accelerometer (perpendicular to the board face).
    Returns:
        "UP"    if the board is flicked / tilted face-up strongly
        "DOWN"  if flicked face-down strongly
        "FLAT"  otherwise (normal holding position)

    Axis reference (micro:bit held horizontally, USB at top):
        +Z = face pointing UP   (away from the table)
        -Z = face pointing DOWN (toward the table)
    """
    z = accelerometer.get_z()

    if z > Z_THRESHOLD:
        return "UP"
    elif z < -Z_THRESHOLD:
        return "DOWN"
    else:
        return "FLAT"


# --- MAIN EXECUTION LOOP ---
while True:
    # 1. Gather raw data from all three axes
    raw_pitch, raw_roll = read_hardware_tilt()   # Y and X axes
    raw_z = accelerometer.get_z()                # Z axis (face up/down)
    z_gesture = read_z_gesture()

    # 2. Process tilt data through the mapping function
    target_pan  = convert_tilt_to_servo_angle(raw_roll)   # left/right → pan servo
    target_tilt = convert_tilt_to_servo_angle(raw_pitch)  # forward/back → tilt servo

    # 3. Transmit processed angles to the turret over radio
    transmit_steering_commands(target_pan, target_tilt)

    # 4. Also broadcast Z so the turret can react to gestures (e.g. fire/stop)
    radio_send_value("z_raw", raw_z)   # was radio.send_value("z_raw", raw_z)

    # 5. Display live axis readings on the OLED (rows 0-2). No full-screen
    #    clear here — oled_print() clears just its own row before drawing,
    #    so this no longer flickers or wipes the telemetry on rows 4-5.
    oled_print("X(pan):"  + str(target_pan),  row=0)
    oled_print("Y(tilt):" + str(target_tilt), row=1)
    oled_print("Z:" + str(raw_z) + " " + z_gesture, row=2)

    # 6. Handle any incoming telemetry from the turret
    check_for_incoming_telemetry()

    # Precise software throttle
    sleep(50)
