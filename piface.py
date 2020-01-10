import sys
# Ugly hack because script launches using sudo, pythonpath is broken
# sys.path.append("/home/pi/.local/lib/python3.7/site-packages/")

import pifacedigitalio as p
import keyboard as k
board = p.PiFaceDigital()

listener = p.InputEventListener(chip=board)
listener.register(0, p.IODIR_FALLING_EDGE, lambda e: e.chip.leds[1].toggle()) # toggle relay
listener.register(1, p.IODIR_FALLING_EDGE, lambda _: k.send('left')) # send left key
listener.register(2, p.IODIR_FALLING_EDGE, lambda _: k.send('right')) # send right key
listener.activate()
