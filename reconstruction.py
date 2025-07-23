import open3d as o3d
import numpy as np

# Load point cloud
pcd = o3d.io.read_point_cloud("merged.ply")
print("Original point cloud loaded:", pcd)

# Downsample to reduce noise
pcd = pcd.voxel_down_sample(voxel_size=0.01)
print("Downsampled point cloud.")

# Remove outliers (statistical)
pcd, ind = pcd.remove_statistical_outlier(nb_neighbors=20, std_ratio=2.0)
print("Outliers removed.")

# Estimate normals
pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
pcd.orient_normals_consistent_tangent_plane(k=30)
print("Normals estimated and oriented.")

# Poisson reconstruction
print("Running Poisson reconstruction...")
mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd, depth=9)
print("Poisson reconstruction completed.")

# Density-based filtering to crop mesh
densities = np.asarray(densities)
density_threshold = np.quantile(densities, 0.02)  # remove bottom 2% of low-density vertices
vertices_to_keep = densities > density_threshold
mesh = mesh.select_by_index(np.where(vertices_to_keep)[0])
print("Low-density vertices removed.")

# Optional mesh cleanup
mesh.remove_degenerate_triangles()
mesh.remove_duplicated_triangles()
mesh.remove_duplicated_vertices()
mesh.remove_non_manifold_edges()
print("Cleaned mesh geometry.")

# Save final mesh
o3d.io.write_triangle_mesh("reconstructed_mesh_clean.ply", mesh)
print("✅ Cleaned mesh saved as 'reconstructed_mesh_clean.ply'")
