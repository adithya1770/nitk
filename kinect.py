import freenect
import cv2
import numpy as np

def get_video():
    rgb, _ = freenect.sync_get_video()
    rgb = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    return rgb

def get_depth():
    depth, _ = freenect.sync_get_depth()
    return depth.astype(np.uint8)

while True:
    frame = get_video()
    depth = get_depth()

    cv2.imshow('RGB', frame)
    cv2.imshow('Depth', depth)

    if cv2.waitKey(1) == ord('q'):
        break

cv2.destroyAllWindows()
