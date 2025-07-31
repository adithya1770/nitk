import open3d as o3d

def clean_and_sharpen(pcd_file, output_file="sharpened_output.ply"):
    # Load the point cloud
    pcd = o3d.io.read_point_cloud(pcd_file)
    print(f"[INFO] Loaded {pcd_file} with {len(pcd.points)} points.")

    # Downsample to reduce noise
    voxel_size = 0.01
    pcd_down = pcd.voxel_down_sample(voxel_size=voxel_size)
    pcd_down.estimate_normals(
        search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.03, max_nn=30)
    )

    # Remove outliers
    pcd_clean, ind_stat = pcd_down.remove_statistical_outlier(nb_neighbors=20, std_ratio=2.0)
    print(f"[INFO] After statistical outlier removal: {len(pcd_clean.points)} points")

    pcd_clean_final, ind_rad = pcd_clean.remove_radius_outlier(nb_points=5, radius=0.03)
    print(f"[INFO] After radius outlier removal: {len(pcd_clean_final.points)} points")

    # Save final clean cloud
    if len(pcd_clean_final.points) > 0:
        o3d.io.write_point_cloud(output_file, pcd_clean_final)
        print(f"[✓] Cleaned and sharpened point cloud saved to: {output_file}")
        o3d.visualization.draw_geometries([pcd_clean_final])
    else:
        print("[✗] No points left after cleaning — try relaxing filter parameters.")

if __name__ == "__main__":
    clean_and_sharpen("stitched_pointcloud.ply")
