import cv2
import numpy as np
import open3d as o3d
import os

# Save in current directory
output_dir = "."
# No need to create directory since "." is current directory

# Open webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Failed to open camera.")
    exit()

print("Starting 3D Reconstruction... Press Q to quit.")

# Read one frame to get camera parameters
ret, frame = cap.read()
if not ret:
    print("Failed to read from camera.")
    cap.release()
    exit()

height, width = frame.shape[:2]

# Intrinsics (fx, fy may be tuned)
intrinsics = o3d.camera.PinholeCameraIntrinsic(
    width, height, 525.0, 525.0, width // 2, height // 2
)

# Setup
pose = np.identity(4)
global_pcd = o3d.geometry.PointCloud()
prev_rgbd = None
frame_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert to RGB and fake depth
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    depth_fake = gray.astype(np.uint16)

    # Convert to Open3D format
    color_o3d = o3d.geometry.Image(rgb)
    depth_o3d = o3d.geometry.Image(depth_fake)
    rgbd = o3d.geometry.RGBDImage.create_from_color_and_depth(
        color_o3d, depth_o3d, depth_scale=1000.0, convert_rgb_to_intensity=False
    )

    if prev_rgbd is None:
        prev_rgbd = rgbd
        continue

    # Estimate transformation
    success, trans, info = o3d.pipelines.odometry.compute_rgbd_odometry(
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

        # Save current point cloud frame in current directory
        o3d.io.write_point_cloud(f"{output_dir}/frame_{frame_count:04d}.ply", pcd)
        print(f"Saved frame {frame_count}")
        frame_count += 1

        prev_rgbd = rgbd

    # Exit on Q
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
print("Reconstruction complete.")

# Save final merged point cloud
o3d.io.write_point_cloud("merged_pointcloud.ply", global_pcd)
print("Saved final merged point cloud as merged_pointcloud.ply")
