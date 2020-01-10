# stop screen blanking
xset s noblank
xset s off
xset -dpms

sdptool add SP
rfcomm connect hci0 [OBD MAC ADDRESS] &
sleep 10
python3 /home/pi/obd-gui/gui.py
