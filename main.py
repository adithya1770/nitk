import freenect
import numpy as np
import cv2
import json
import time
import re

def get_video():
    video, _ = freenect.sync_get_video()
    video = cv2.cvtColor(video, cv2.COLOR_RGB2BGR)
    return video

def get_depth():
    depth, _ = freenect.sync_get_depth(format=freenect.DEPTH_MM)
    return depth

last_print_time = 0 

rows, cols = 4, 4
frame_height, frame_width = 480, 640
cell_h = frame_height // rows
cell_w = frame_width // cols

zones = {
        "left":['R1C1', 'R2C1', 'R3C1', 'R4C1'],
        "right":['R1C4', 'R2C4', 'R3C4', 'R4C4'],
        "front":['R1C2','R1C3','R2C2','R2C3','R3C2','R3C3','R4C2','R4C3']
        }

while True:
    frame = get_video()
    frame = cv2.resize(frame, (frame_width, frame_height))
    depth = get_depth()
    depth = cv2.resize(depth, (frame_width, frame_height))

    grid_distances = {}

    for i in range(rows):
        for j in range(cols):
            x1 = j*cell_w
            y1 = i*cell_h
            x2 = (j+1)*cell_w
            y2 = (i+1)*cell_h

            region = depth[y1:y2, x1:x2]
            valid = region[region!=2047]

            key = f"R{i+1}C{j+1}"
            if valid.size > 0:
                avg_distance = int(np.mean(valid))
                # adjusted the first 150mm blind spot
                if avg_distance<150:
                    label = f"<=0.15m"
                else:
                    label = f"{(avg_distance+150)/1000}m"
                grid_distances[key] = avg_distance/1000
            else:
                label = "no data"
                grid_distances[key] = None

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 1)
            cv2.putText(frame, label, (x1+5, y1+20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255, 255), 1)

            cv2.imshow("Kinect RGB Feed + Depth Grid", frame)

    current_time = time.time()
    if current_time - last_print_time >= 1.0:
        print(json.dumps(grid_distances, indent=2))
        last_print_time = current_time


    status = {
            zone: any(grid_distances[pos] < 1.0 for pos in positions)
            for zone, positions in zones.items()
            }
    

    if status["front"]:
        print("stop")
        #pixhawk CMDS
    elif (status["front"] and status["right"]) or (status["front"] and status["left"]):
        print("stop")
        # PIXHAWK COMMANDS GO HERE
    elif (status["right"]):
        print("move left")
        #HERE AS WELL
    elif (status["left"]):
        print("move right")
        #HERE AS WELL

    if cv2.waitKey(1)==27:
        break

cv2.destroyAllWindows()
