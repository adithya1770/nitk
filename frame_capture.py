import freenect
import cv2
import numpy as np
import open3d as o3d

print("Starting Kinect-based 3D reconstruction... Press Q to quit.")

# Set up camera intrinsics (Kinect v1)
width, height = 640, 480
intrinsics = o3d.camera.PinholeCameraIntrinsic(
    width=width,
    height=height,
    fx=525.0,
    fy=525.0,
    cx=width / 2,
    cy=height / 2
)

# Initialize
pose = np.identity(4)
global_pcd = o3d.geometry.PointCloud()
prev_rgbd = None
frame_count = 0

while True:
    # Get RGB and depth from Kinect
    rgb, _ = freenect.sync_get_video()
    depth, _ = freenect.sync_get_depth()

    if rgb is None or depth is None:
        print("Failed to read from Kinect.")
        break

    # Convert to proper formats
    rgb = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    depth = depth.astype(np.uint16)

    # Display preview
    cv2.imshow("RGB", rgb)
    cv2.imshow("Depth", depth)

    # Convert to Open3D image formats
    color_o3d = o3d.geometry.Image(cv2.cvtColor(rgb, cv2.COLOR_BGR2RGB))
    depth_o3d = o3d.geometry.Image(depth)
    rgbd = o3d.geometry.RGBDImage.create_from_color_and_depth(
        color_o3d, depth_o3d,
        depth_scale=1000.0,
        depth_trunc=3.0,
        convert_rgb_to_intensity=False
    )

    # Odometry
    if prev_rgbd is None:
        prev_rgbd = rgbd
        continue

    success, trans, _ = o3d.pipelines.odometry.compute_rgbd_odometry(
        prev_rgbd, rgbd, intrinsics,
        np.identity(4),
        o3d.pipelines.odometry.RGBDOdometryJacobianFromColorTerm()
    )

    if success:
        pose = np.dot(pose, trans)
        pcd = o3d.geometry.PointCloud.create_from_rgbd_image(rgbd, intrinsics)
        pcd.transform(pose)
        global_pcd += pcd
        global_pcd = global_pcd.voxel_down_sample(voxel_size=0.01)

        o3d.io.write_point_cloud(f"frame_{frame_count:04d}.ply", pcd)
        print(f"Saved frame {frame_count}")
        frame_count += 1
        prev_rgbd = rgbd

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
o3d.io.write_point_cloud("merged_pointcloud.ply", global_pcd)
print("Saved final point cloud as merged_pointcloud.ply")
