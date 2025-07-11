import freenect
import numpy as np
import cv2
import json
import time

# -----------------------------
# CONFIGURATION
# -----------------------------
ROWS, COLS = 4, 4
FRAME_HEIGHT, FRAME_WIDTH = 480, 640
CELL_H = FRAME_HEIGHT // ROWS
CELL_W = FRAME_WIDTH // COLS
PRINT_INTERVAL = 1.0  # seconds

ZONES = {
    "left": ['R1C1', 'R2C1', 'R3C1', 'R4C1'],
    "right": ['R1C4', 'R2C4', 'R3C4', 'R4C4'],
    "front": ['R1C2', 'R1C3', 'R2C2', 'R2C3', 'R3C2', 'R3C3', 'R4C2', 'R4C3']
}

# -----------------------------
# SENSOR INPUT FUNCTIONS
# -----------------------------
def get_video():
    video, _ = freenect.sync_get_video()
    return cv2.cvtColor(video, cv2.COLOR_RGB2BGR)

def get_depth():
    depth, _ = freenect.sync_get_depth(format=freenect.DEPTH_MM)
    return depth

# -----------------------------
# GRID ANALYSIS FUNCTION
# -----------------------------
def analyze_grid(depth):
    grid_distances = {}
    labels = {}

    for i in range(ROWS):
        for j in range(COLS):
            x1, y1 = j * CELL_W, i * CELL_H
            x2, y2 = (j + 1) * CELL_W, (i + 1) * CELL_H

            region = depth[y1:y2, x1:x2]
            valid = region[region != 2047]

            key = f"R{i+1}C{j+1}"

            if valid.size > 0:
                avg_distance = int(np.mean(valid))
                label = f"{(avg_distance + 150)/1000:.2f}m" if avg_distance >= 150 else "<=0.15m"
                grid_distances[key] = avg_distance / 1000
            else:
                label = "no data"
                grid_distances[key] = None

            labels[key] = (x1, y1, x2, y2, label)

    return grid_distances, labels

# -----------------------------
# DISPLAY FRAME FUNCTION
# -----------------------------
def draw_grid(frame, labels):
    for key, (x1, y1, x2, y2, label) in labels.items():
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 1)
        cv2.putText(frame, label, (x1 + 5, y1 + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
    return frame

# -----------------------------
# DECISION LOGIC
# -----------------------------
def control_logic(grid_distances):
    status = {
        zone: any(grid_distances[pos] is not None and grid_distances[pos] < 1.0 for pos in positions)
        for zone, positions in ZONES.items()
    }

    if status["front"]:
        print("🔴 STOP")
        # send_pixhawk_cmd("stop")
    elif status["left"]:
        print("↪️ Move Right")
        # send_pixhawk_cmd("right")
    elif status["right"]:
        print("↩️ Move Left")
        # send_pixhawk_cmd("left")
    else:
        print("✅ CLEAR")
        # send_pixhawk_cmd("forward")

# Placeholder for future Pixhawk integration
def send_pixhawk_cmd(command):
    print(f"[PIXHAWK] Execute: {command}")
    # Implement MAVLink commands here using pymavlink

# -----------------------------
# MAIN LOOP
# -----------------------------
def main():
    last_print_time = 0

    while True:
        frame = cv2.resize(get_video(), (FRAME_WIDTH, FRAME_HEIGHT))
        depth = cv2.resize(get_depth(), (FRAME_WIDTH, FRAME_HEIGHT))

        grid_distances, labels = analyze_grid(depth)
        frame = draw_grid(frame, labels)
        cv2.imshow("Kinect Feed + Grid", frame)

        current_time = time.time()
        if current_time - last_print_time >= PRINT_INTERVAL:
            print(json.dumps(grid_distances, indent=2))
            control_logic(grid_distances)
            last_print_time = current_time

        if cv2.waitKey(1) == 27:  # ESC key
            break

    cv2.destroyAllWindows()

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    main()
