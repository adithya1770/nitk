import open3d as o3d
import numpy as np
import os
import glob
from datetime import datetime

def load_point_clouds(ply_folder):
    print("[INFO] Loading point clouds from:", ply_folder)
    ply_files = glob.glob(os.path.join(ply_folder, "*.ply"))
    pcds = []
    for ply_file in ply_files:
        print(f"[INFO] Reading {ply_file}")
        pcd = o3d.io.read_point_cloud(ply_file)
        pcds.append(pcd)
    return pcds

def merge_point_clouds(pcds, voxel_size=0.01):
    print("[INFO] Merging point clouds...")
    combined = o3d.geometry.PointCloud()
    for pcd in pcds:
        combined += pcd
    print(f"[INFO] Merged {len(pcds)} point clouds. Total points: {len(combined.points)}")

    print("[INFO] Downsampling...")
    combined_down = combined.voxel_down_sample(voxel_size=voxel_size)

    print("[INFO] Estimating normals...")
    combined_down.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(
        radius=0.05, max_nn=30))

    return combined_down

if __name__ == "__main__":
    current_folder = os.getcwd()
    point_clouds = load_point_clouds(current_folder)
    
    if len(point_clouds) == 0:
        print("[ERROR] No PLY files found in the current directory.")
        exit()

    merged = merge_point_clouds(point_clouds)

    save_path = os.path.join(current_folder, "merged.ply")
    o3d.io.write_point_cloud(save_path, merged)
    print(f"[INFO] Merged point cloud saved to: {save_path}")
