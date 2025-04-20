# SPDX-FileCopyrightText: 2021 Jeff Epler for Adafruit Industries
# SPDX-FileCopyrightText: 2021 therealdaniel
# SPDX-License-Identifier: MIT

import keypad
import board
import usb_hid
from adafruit_hid.keyboard import Keyboard, find_device
from adafruit_hid.keycode import Keycode as K
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS

NUM_ROWS = 5
NUM_COLS = 12

print("running")

row_pins = (board.GP9, board.GP10, board.GP11, board.GP12, board.GP13)
column_pins = (
    board.GP14, board.GP15, board.GP26, board.GP27, board.GP28, board.GP29,
    board.GP3, board.GP4, board.GP5, board.GP6, board.GP7, board.GP8
    )

keys = keypad.KeyMatrix(
    row_pins=row_pins,
    column_pins=column_pins,
    columns_to_anodes=True)

class BitmapKeyboard(Keyboard):
    def __init__(self, devices):
        device = find_device(devices, usage_page=0x1, usage=0x6)

        try:
            device.send_report(b'\0' * 16)
        except ValueError:
            print("found keyboard, but it did not accept a 16-byte report. check that boot.py is installed properly")

        self._keyboard_device = device

        # report[0] modifiers
        # report[1:16] regular key presses bitmask
        self.report = bytearray(16)

        self.report_modifier = memoryview(self.report)[0:1]
        self.report_bitmap = memoryview(self.report)[1:]

    def _add_keycode_to_report(self, keycode):
        modifier = K.modifier_bit(keycode)
        if modifier:
            # Set bit for this modifier.
            self.report_modifier[0] |= modifier
        else:
            self.report_bitmap[keycode >> 3] |= 1 << (keycode & 0x7)

    def _remove_keycode_from_report(self, keycode):
        modifier = K.modifier_bit(keycode)
        if modifier:
            # Set bit for this modifier.
            self.report_modifier[0] &= ~modifier
        else:
            self.report_bitmap[keycode >> 3] &= ~(1 << (keycode & 0x7))

    def release_all(self):
        for i in range(len(self.report)):
            self.report[i] = 0
        self._keyboard_device.send_report(self.report)

kbd = BitmapKeyboard(usb_hid.devices)
layout = KeyboardLayoutUS(kbd)

keymap = {
    0: [
        [K.ESCAPE, K.ONE, K.TWO, K.THREE, K.FOUR, K.FIVE, K.SIX, K.SEVEN, K.EIGHT, K.NINE, K.ZERO, K.BACKSPACE],  # row 1
        [K.GRAVE_ACCENT, K.Q, K.W, K.E, K.R, K.T, K.Y, K.U, K.I, K.O, K.P, K.BACKSPACE],
        [K.TAB, K.A, K.S, K.D, K.F, K.G, K.H, K.J, K.K, K.L, K.SEMICOLON, K.QUOTE],
        [K.LEFT_SHIFT, K.Z, K.X, K.C, K.V, K.B, K.N, K.M, K.COMMA, K.PERIOD, K.UP_ARROW, K.RETURN],
        [K.LEFT_CONTROL, K.GUI, K.ALT, K.DELETE, 'lower', K.SPACEBAR, K.SPACEBAR, 'raise', K.FORWARD_SLASH, K.LEFT_ARROW, K.DOWN_ARROW, K.RIGHT_ARROW]
        ],
    1: [
        [None, None, None, None, None, None, None, None, None, None, None, None],  # row 1
        [K.GRAVE_ACCENT, K.ONE, K.TWO, K.THREE, K.FOUR, K.FIVE, K.SIX, K.SEVEN, K.EIGHT, K.NINE, K.ZERO, None],
        [None, K.F1, K.F2, K.F3, K.F4, K.F5, K.F6, K.MINUS, K.EQUALS, K.LEFT_BRACKET, K.RIGHT_BRACKET, K.BACKSLASH],
        [K.LEFT_SHIFT, K.F7, K.F8, K.F9, K.F10, K.F11, K.F12, K.M, K.COMMA, K.PERIOD, None, None],
        [K.LEFT_CONTROL, K.GUI, K.ALT, None, 'lower', K.SPACEBAR, K.SPACEBAR, 'raise', None, None, None, None]
        ],
    2: [
        [None, None, None, None, None, None, None, None, None, None, None, None],  # row 1
        [None, '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', None],
        [None, K.F1, K.F2, K.F3, K.F4, K.F5, K.F6, '_', '+', '{', '}', '|'],
        [K.LEFT_SHIFT, K.F7, K.F8, K.F9, K.F10, K.F11, K.F12, None, None, None, None, None],
        [K.LEFT_CONTROL, K.GUI, K.ALT, K.DELETE, 'lower', K.SPACEBAR, K.SPACEBAR, 'raise', None, None, None, None]
        ],
    3: [
        [None, None, None, None, None, None, None, None, None, None, None, None],  # row 1
        [None, None, None, None, None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None, None, None, None, None],
        [None, None, None, None, 'lower', None, None, 'raise', None, None, None, None],
        ]    
    }

#validate shape of keymap
for k, v in keymap.items():
    assert len(v) == NUM_ROWS, f"incorrect number of rows in layer {k}.\nExpecting {NUM_ROWS}, got {len(v)}"
    for row in v:
        assert len(row) == NUM_COLS, f"incorrect number of columns in layer {k}, row: {row}.\nExpecting {NUM_COLS}, got {len(row)}"

# layer logic------------------------------------------------------------------/
# layer_state is 2 bits comprised of whether raise and lower are active
# bit 0 = raise, bit 1 = lower
# we can then use layer state directly.
# 0 = both off, 1 = raised, 2 = lowered, 3 = both.
layer_state = 0b00  #initialise layer state to both off
#bit masks
RAISE = 0b01
LOWER = 0b10

def press_lower():
    global layer_state
    layer_state |= LOWER

def release_lower():
    global layer_state
    layer_state &= ~LOWER

def press_raise():
    global layer_state
    layer_state |= RAISE

def release_raise():
    global layer_state
    layer_state &= ~RAISE
#------------------------------------------------------------------------------/

while True:
    ev = keys.events.get()

    if ev is not None:
        row = ev.key_number // len(column_pins)
        col = ev.key_number % len(column_pins)
        key = keymap[layer_state][row][col]

        if ev.pressed and key is not None:
            print(key)
            if key == 'raise':
                press_raise()
                continue
            elif key == 'lower':
                press_lower()
                continue
            #check if it's a string and not a keycode
            if isinstance(key, str):
                for k in layout.keycodes(key): kbd.press(k)
                continue
            kbd.press(key)

        else:
            if key == 'raise':
                release_raise()
                continue
            elif key == 'lower':
                release_lower()
                continue
            else:
                #release all keys at the same row/col across all layers
                for l in keymap:
                    key = keymap[l][row][col]
                    if key is not None:
                        #check if it's a string and not a keycode
                        #release all the keycodes in the string
                        if isinstance(key, str):
                            for k in layout.keycodes(key): kbd.release(k)
                            continue
                        kbd.release(key)
