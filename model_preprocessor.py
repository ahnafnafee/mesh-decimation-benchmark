import glob
import os

import pymeshlab

# Setup paths
RAW_DIRS = {
    "modelnet40": "./raw_downloads/modelnet40",  # Put your 15 .off files here
    "thingi10k": "./raw_downloads/thingi10k",  # Put your 15 .stl files here
}
PROCESSED_DIRS = {"modelnet40": "./dataset/clean_cad", "thingi10k": "./dataset/organic_scanned"}

MIN_FACE_COUNT = 2000  # Threshold to reject too-simple models


def preprocess_models():
    for key, raw_path in RAW_DIRS.items():
        out_path = PROCESSED_DIRS[key]
        os.makedirs(out_path, exist_ok=True)

        files = glob.glob(os.path.join(raw_path, "*"))
        print(f"--- Processing {key} ({len(files)} files) ---")

        for filepath in files:
            filename = os.path.basename(filepath)
            name_only, ext = os.path.splitext(filename)

            if filename.startswith("."):
                continue

            ms = pymeshlab.MeshSet()
            ms.load_new_mesh(filepath)

            print(f"Processing: {filename}")

            # Check face count
            initial_face_count = ms.current_mesh().face_number()
            print(f"  Initial faces: {initial_face_count}")
            if initial_face_count < MIN_FACE_COUNT:
                print(f"Skipping {filename}: Too few faces.")
                continue

            # --- STEP 1: Basic Cleaning ---
            ms.meshing_merge_close_vertices()
            ms.meshing_remove_duplicate_faces()
            ms.meshing_remove_duplicate_vertices()

            # --- STEP 2: Geometric Repair (THE NEW FIX) ---
            # 1. Remove small floating disconnected pieces (noise often causes non-manifold errors)
            ms.meshing_remove_connected_component_by_face_number(mincomponentsize=50)

            # 2. Repair Non-Manifold Edges by removing faces sharing them
            # This makes the mesh "open" (holes) but "manifold" (valid for math)
            ms.meshing_repair_non_manifold_edges(method="Remove Faces")

            # 3. Repair Non-Manifold Vertices
            ms.meshing_repair_non_manifold_vertices(vertdispratio=0)

            # --- STEP 3: Re-orienting ---
            # Now that it is manifold, we can safely re-orient
            try:
                # Use geometric heuristic to orient faces (better for disconnected components?)
                ms.meshing_re_orient_faces_by_geometry()
            except Exception:
                # Fallback to coherent orientation if geometric fails
                try:
                    ms.meshing_re_orient_faces_coherently()
                except Exception:
                    print(f"Skipping {filename}: Geometry too broken to re-orient.")
                    continue

            # Fix for dark meshes (inverted normals) common in ModelNet40
            # We force flip to ensure outside is outside.
            # Note: re_orient_faces_coherently makes them consistent, but might be consistently wrong (inside out).
            # Checking volume or similar might be better, but for now, let's try flipping if it looks dark.
            # Actually, let's just ensure normals are computed correctly.
            # If the user says it looks like the picture (dark silhouette), it's likely inverted.
            # Let's add a step to invert.
            # ms.meshing_invert_face_orientation(forceflip=True) 
            
            # Fix for dark meshes (inverted normals) common in ModelNet40
            # Reverted unconditional flip as it broke other meshes.
            # We will rely on re_orient_faces_coherently for now.
            # If specific meshes are problematic, we might need a more sophisticated check.
            
            # Smooth shading
            ms.compute_normal_per_vertex()

            # --- STEP 4: Scaling ---
            ms.compute_matrix_from_scaling_or_normalization(axisx=1.0, axisy=1.0, axisz=1.0, unitflag=True, freeze=True)

            # Export
            final_face_count = ms.current_mesh().face_number()
            print(f"  Final faces: {final_face_count}")
            out_name = os.path.join(out_path, name_only + ".obj")
            ms.save_current_mesh(out_name)
            print(f"Fixed & Converted: {filename}\n")


if __name__ == "__main__":
    preprocess_models()
