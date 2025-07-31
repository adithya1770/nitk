import open3d as o3d
import numpy as np
import glob

def preprocess_point_cloud(pcd, voxel_size):
    pcd_down = pcd.voxel_down_sample(voxel_size)
    pcd_down.estimate_normals(
        o3d.geometry.KDTreeSearchParamHybrid(radius=voxel_size * 2, max_nn=30)
    )
    return pcd_down

def pairwise_icp(source, target, voxel_size):
    source_down = preprocess_point_cloud(source, voxel_size)
    target_down = preprocess_point_cloud(target, voxel_size)

    print("[INFO] Running ICP...")
    icp_result = o3d.pipelines.registration.registration_icp(
        source_down, target_down, max_correspondence_distance=voxel_size * 2,
        estimation_method=o3d.pipelines.registration.TransformationEstimationPointToPlane(),
        init=np.identity(4)
    )
    return icp_result.transformation

def stitch_point_clouds(ply_files, voxel_size=0.01):
    if len(ply_files) < 2:
        print("[!] Need at least two point clouds to stitch.")
        return None

    print(f"[INFO] Stitching {len(ply_files)} point clouds...")
    pcd_combined = o3d.io.read_point_cloud(ply_files[0])

    for i in range(1, len(ply_files)):
        pcd_next = o3d.io.read_point_cloud(ply_files[i])
        transformation = pairwise_icp(pcd_next, pcd_combined, voxel_size)
        pcd_next.transform(transformation)
        pcd_combined += pcd_next

    pcd_combined = pcd_combined.voxel_down_sample(voxel_size)
    return pcd_combined

def main():
    ply_files = sorted(glob.glob("left_new/frame_000*.ply"))  # Adjust path as needed
    result = stitch_point_clouds(ply_files, voxel_size=0.02)

    if result:
        o3d.io.write_point_cloud("stitched_pointcloud.ply", result)
        print("[✓] Saved: stitched_pointcloud.ply")
        o3d.visualization.draw_geometries([result])

if __name__ == "__main__":
    main()
