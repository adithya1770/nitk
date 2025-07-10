import freenect
import time

while True:
    depth, _ = freenect.sync_get_depth(format=freenect.DEPTH_MM)
    center = depth[240, 320]
    print(f"{center/1000} m")
    time.sleep(1)
