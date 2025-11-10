import open3d as o3d
import os

input_dir = "src/qbert_description/meshes/merged_original"
output_dir = "src/qbert_description/meshes/merged"
os.makedirs(output_dir, exist_ok=True)

for fname in os.listdir(input_dir):
    if not fname.lower().endswith(".stl"):
        continue
    
    target_ratio = 0.1

    if fname.startswith("tooling_disc"):
        target_ratio = 0.2

    in_path = os.path.join(input_dir, fname)
    out_path = os.path.join(output_dir, fname)

    print(f"Processing {fname} ...", end=" ")

    mesh = o3d.io.read_triangle_mesh(in_path)
    if mesh.is_empty():
        print("could not load mesh")
        continue

    # Compute normals before simplification
    mesh.compute_vertex_normals()
    mesh.compute_triangle_normals()

    n_triangles = len(mesh.triangles)
    target = max(500, int(n_triangles * target_ratio))  # don’t go below 500
    simplified = mesh.simplify_quadric_decimation(target)

    # Recompute normals for smoother shading
    simplified.compute_vertex_normals()
    simplified.compute_triangle_normals()

    o3d.io.write_triangle_mesh(out_path, simplified)
    print(f"reduced {n_triangles} → {len(simplified.triangles)} triangles")
