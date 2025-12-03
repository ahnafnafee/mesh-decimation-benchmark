import pymeshlab
import os
import glob
import time
import csv
import pandas as pd
import math

# Setup paths
DATASET_DIRS = {
    "clean_cad": "./dataset/clean_cad",
    "organic_scanned": "./dataset/organic_scanned"
}
RESULTS_FILE = "experiment_results.csv"

# Target reduction (e.g., 50% of original face count)
TARGET_PERCENTAGE = 0.5

def get_face_count(ms):
    return ms.current_mesh().face_number()

def apply_algorithm(ms, algo_name, target_faces):
    if algo_name == "QEM":
        ms.meshing_decimation_quadric_edge_collapse(
            targetfacenum=target_faces,
            preservenormal=True,
            preserveboundary=True,
            preservetopology=True,
            qualitythr=0.3,
            optimalplacement=True
        )
    elif algo_name == "Clustering":
        # Vertex Clustering
        ms.meshing_decimation_clustering(threshold=pymeshlab.PercentageValue(1.0))

def run_experiment():
    results = []
    
    # Prepare CSV
    with open(RESULTS_FILE, 'w', newline='') as csvfile:
        fieldnames = ['Model', 'Type', 'Algorithm', 'Time', 'HausdorffDist', 'InitialFaces', 'FinalFaces']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for mesh_type, dir_path in DATASET_DIRS.items():
            files = glob.glob(os.path.join(dir_path, "*.obj"))
            print(f"--- Processing {mesh_type} ({len(files)} files) ---")
            
            for filepath in files:
                filename = os.path.basename(filepath)
                print(f"Processing {filename}...")
                
                # Load original mesh to get baseline
                ms_orig = pymeshlab.MeshSet()
                ms_orig.load_new_mesh(filepath)
                initial_faces = get_face_count(ms_orig)
                target_faces = int(initial_faces * TARGET_PERCENTAGE)
                
                # Algorithms to test
                algorithms = ["QEM", "Clustering"]
                
                for algo in algorithms:
                    try:
                        # Warm-up run (if needed, to load libraries/caches)
                        # For simple scripts, this might be overkill, but good practice.
                        # We'll run once without timing.
                        print(f"  Running {algo}...", end='', flush=True)
                        ms = pymeshlab.MeshSet()
                        ms.load_new_mesh(filepath)
                        apply_algorithm(ms, algo, target_faces)
                        
                        # Measure Time (Average of N runs)
                        NUM_REPEATS = 5
                        total_time = 0
                        
                        for _ in range(NUM_REPEATS):
                            # Reload mesh for each run to ensure identical starting state
                            ms_timing = pymeshlab.MeshSet()
                            ms_timing.load_new_mesh(filepath)
                            
                            start_time = time.perf_counter_ns()
                            apply_algorithm(ms_timing, algo, target_faces)
                            end_time = time.perf_counter_ns()
                            total_time += (end_time - start_time)
                        
                        # Convert nanoseconds to seconds for consistency with analysis
                        execution_time = (total_time / NUM_REPEATS) / 1e9
                        
                        # Final application for geometric analysis (using the last run's result)
                        # We can just use the ms from the last iteration or reload one last time.
                        # Let's reload to be safe and consistent with the "FinalFaces" count.
                        ms = pymeshlab.MeshSet()
                        ms.load_new_mesh(filepath)
                        apply_algorithm(ms, algo, target_faces)
                        
                        final_faces = get_face_count(ms)
                        final_verts = ms.current_mesh().vertex_number()
                        
                        # Save the decimated mesh
                        output_dir = "./decimated_meshes"
                        os.makedirs(output_dir, exist_ok=True)
                        name_only = os.path.splitext(filename)[0]
                        save_path = os.path.join(output_dir, f"{name_only}_{algo}.obj")
                        ms.save_current_mesh(save_path)
                        
                        # Measure Hausdorff Distance (Two-Sided)
                        # Create a clean MeshSet to ensure correct layer indices
                        ms_hd = pymeshlab.MeshSet()
                        ms_hd.load_new_mesh(save_path)  # Layer 0: Decimated
                        ms_hd.load_new_mesh(filepath)   # Layer 1: Original
                        
                        # 1. Processed -> Original
                        res1 = ms_hd.get_hausdorff_distance(sampledmesh=0, targetmesh=1)
                        hd1 = res1['max']
                        
                        # 2. Original -> Processed
                        res2 = ms_hd.get_hausdorff_distance(sampledmesh=1, targetmesh=0)
                        hd2 = res2['max']
                        
                        hausdorff_dist = max(hd1, hd2)
                        
                        # Record result
                        row = {
                            'Model': filename,
                            'Type': mesh_type,
                            'Algorithm': algo,
                            'Time': execution_time,
                            'HausdorffDist': hausdorff_dist,
                            'InitialFaces': initial_faces,
                            'FinalFaces': final_faces
                        }
                        writer.writerow(row)
                        results.append(row)
                        print(f"  {algo}: Time={execution_time:.4f}s, HD={hausdorff_dist:.6f}, Faces={final_faces}")
                        
                    except Exception as e:
                        # Print error in RED
                        print(f"\033[91m  Failed {algo} on {filename}: {e}\033[0m")

    print(f"Experiment complete. Results saved to {RESULTS_FILE}")

if __name__ == "__main__":
    run_experiment()
