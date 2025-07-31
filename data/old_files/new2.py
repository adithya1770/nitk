import open3d as o3d
import numpy as np
import os

frames_folder = "./pointclouds2/"
frame_files = sorted([f for f in os.listdir(frames_folder) if f.endswith(".ply")])

global_pcd = o3d.geometry.PointCloud()
pose = np.identity(4)

for i, fname in enumerate(frame_files):
    print(f"[INFO] Processing: {fname}")
    pcd = o3d.io.read_point_cloud(os.path.join(frames_folder, fname))
    pcd.estimate_normals()

    # Optional: align using ICP with the previous frame
    if i > 0:
        reg = o3d.pipelines.registration.registration_icp(
            pcd, prev_pcd, 0.05, np.identity(4),
            o3d.pipelines.registration.TransformationEstimationPointToPlane()
        )
        pose = pose @ reg.transformation
        pcd.transform(pose)

    global_pcd += pcd
    prev_pcd = pcd

# Downsample final merged point cloud
global_pcd = global_pcd.voxel_down_sample(0.005)

# Save final point cloud
o3d.io.write_point_cloud("stitched_pointcloud.ply", global_pcd)
print("✅ Merged point cloud saved as 'stitched_pointcloud.ply'")
