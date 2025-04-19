# fixed-split-ergo-64
5x12 key handwired ortholinear keyboard with ergonomic split. Imagine a Microsoft Natural Keyboard and a Preonic had a baby.

### Instructions
- Cut case and plate out of 4.5mm stock using the DXF files in [cutting files](./cutting_files/). I used white acrylic.
- Press heat set threads into the bottom pieces - they have slightly bigger holes than the rest
- Hot glue switches into the plate
- Wire it (more details to come...)
- Flash the Waveshare RP2040-Zero with the Circuit Python firmware from here: https://circuitpython.org/board/waveshare_rp2040_zero/
- Copy the contents of the [MCU folder](./MCU/) to the device

### BOM
- Waveshare RP2040-Zero
- 4.5mm acrylic
- 9 x 16mm M2 bolts - with a flat top, not countersunk
- 9 x M2 heat set threads, 4.5mm tall
- Wire
- Hot glue gun
- 60 x key switches - I like Gazzew Boba U4T
- Keycaps

### Included Libraries
This project is developed on circuitpython and includes:
- the [`adafruit_hid`](https://github.com/adafruit/Adafruit_CircuitPython_HID) library
- custom NKRO boot.py file from adafruit 
