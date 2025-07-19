import open3d as o3d
import numpy as np

# Load point cloud
pcd = o3d.io.read_point_cloud("frame_00.ply")

# Estimate normals (required for Poisson)
pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))

# Poisson reconstruction
mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd, depth=9)

# Optional: crop mesh using density filtering
vertices_to_keep = densities > np.quantile(densities, 0.02)
mesh = mesh.select_by_index(np.where(vertices_to_keep)[0])

# Save reconstructed mesh
o3d.io.write_triangle_mesh("reconstructed_mesh.ply", mesh)
print("Saved as reconstructed_mesh.ply")
