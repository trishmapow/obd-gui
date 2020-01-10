import sys
# Ugly hack because script launches using sudo, pythonpath is broken
# sys.path.append("/home/pi/.local/lib/python3.7/site-packages/")
# sys.path.append("/home/pi/obd-gui/")

import itertools
import obd
import PySimpleGUI as sg
import random
from utils import Buffer

DEBUG_MOCK = False # Testing without bluetooth connection
DEBUG_CONNECT = True # Show pythonOBD debug info
UPDATE_FREQ = 2.5 # wait 1/freq s each frame
PORT = "/dev/rfcomm0"

FONT = "Arial 20"
BUFFER_SIZE = 60 # buffer & graph last x measurements
GRAPH_Y_MAX = 100

watchlist = [["ELM_VOLTAGE", "RPM", "SPEED", "ENGINE_LOAD"],
             ["FUEL_LEVEL", "COOLANT_TEMP", "OIL_TEMP", "INTAKE_TEMP"],
             ["RUN_TIME", "THROTTLE_POS", "TIMING_ADVANCE", "BAROMETRIC_PRESSURE"]]
history = {k: Buffer(maxlen=BUFFER_SIZE) for k in itertools.chain.from_iterable(watchlist)}
labels = ("s1", "s2", "s3", "s4") # layout: sX_l for label, sX_d for data

layout = [
    [sg.Text("", size=(15, 1), key=f"{label}_l", font=FONT),
     sg.Text("", size=(15, 1), key=f"{label}_d", font=FONT, justification='left'),
     sg.Graph(canvas_size=(170, 120), graph_bottom_left=(-BUFFER_SIZE-1, -GRAPH_Y_MAX*1.05),
              graph_top_right=(1, GRAPH_Y_MAX*1.05), background_color="white", key=f"{label}_g")]
    for label in labels
]
layout.append([sg.Text("", size=(20, 1), key="page_num", font="Arial 14")])

def connect(port=PORT, watchlist=None, debug=False):
    if debug:
        obd.logger.setLevel(obd.logging.DEBUG)
    conn = obd.Async(port, fast=False)
    if watchlist is None:
        watchlist = []
    for command in watchlist:
        conn.watch(getattr(obd.commands, command))
    conn.start()
    return conn

def query(conn, param):
    return conn.query(getattr(obd.commands, param))

def format_name(name):
    return name.replace('_', ' ').title()

def main():
    window = sg.Window("Test", layout, return_keyboard_events=True).Finalize()
    window.Maximize()
    conn = connect(watchlist=list(itertools.chain.from_iterable(watchlist), debug=DEBUG_CONNECT))

    page = 0
    max_page = len(watchlist) - 1

    def update_labels():
        for label, item in zip(labels, watchlist[page]):
            window[label + "_l"].update(format_name(item))
        window["page_num"].update(
            f"{'<<<' if page > 0 else ''} page {page+1}/{max_page+1} {'>>>' if page < max_page else ''}"
        )

    def update_items():
        # always update all data
        for item in itertools.chain.from_iterable(watchlist):
            data = query(conn, item)
            history[item].push(data)

        # show only current page on screen
        for label, item in zip(labels, watchlist[page]):
            window[label + "_d"].update(str(history[item][0])[:15])

    def update_graphs():
        for label, item in zip(labels, watchlist[page]):
            label += "_g"
            data = [round(x.value.magnitude, 2) for x in history[item] if not x.is_null()]
            if len(data) == 0: continue

            min_y, max_y = min(data), max(data)
            avg_y, range_y = (min_y + max_y) / 2, max_y - min_y

            window[label].erase()   # clear previous draw

            # get scale and offset to autoscale graph
            scale = GRAPH_Y_MAX*2 / (range_y if range_y != 0 else 1)
            offset = -avg_y * scale

            # draw axes
            window[label].DrawLine((-BUFFER_SIZE, offset), (0, offset))
            window[label].DrawLine((0, -GRAPH_Y_MAX*1.05), (0, GRAPH_Y_MAX*1.05))

            # label y min & max
            window[label].DrawText(round(max_y, 1), (-BUFFER_SIZE*0.1, GRAPH_Y_MAX*0.75))
            window[label].DrawText(round(min_y, 1), (-BUFFER_SIZE*0.1, -GRAPH_Y_MAX*0.75))

            # draw points
            for x, point in enumerate(data, start=-BUFFER_SIZE):
                y = float(point) * scale + offset
                window[label].DrawCircle((x, y), 1, line_color="red", fill_color="red")

    update_labels()
    while True:
        event, values = window.read(timeout=UPDATE_FREQ*100)
        if event is None:
            break
        
        event = event[:event.find(":")]
        if event in ("Left", "Right"):
            if event == "Left" and page > 0:
                page -= 1
            elif event == "Right" and page < max_page:
                page += 1
            update_labels()
        
        update_items()
        update_graphs()

def query_mock(conn, param):
    return round(random.random() * 100, 2)

def connect_mock(port="/dev/rfcomm0", watchlist=None, debug=False):
    print(port, watchlist, debug)
    return None

if __name__ == "__main__":
    if DEBUG_MOCK:
        query = query_mock
        connect = connect_mock

    main()
