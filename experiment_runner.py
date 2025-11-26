import pymeshlab
import os
import glob
import time
import csv
import shutil

# Setup paths
DATASET_DIRS = {
    "clean_cad": "./dataset/clean_cad",
    "organic_scanned": "./dataset/organic_scanned"
}
RESULTS_FILE = "experiment_results.csv"
DECIMATED_DIR = "decimated_meshes"

# Target reduction (e.g., 50% of original face count)
# Target reductions (Percentage of original face count to KEEP)
# 50% decimation -> keep 0.5
# 90% decimation -> keep 0.1
TARGET_PERCENTAGES = [0.5, 0.1]

def get_face_count(ms):
    return ms.current_mesh().face_number()

def tune_clustering_threshold(filepath, target_faces):
    min_t = 0.001
    max_t = 20.0
    best_t = 0.1
    best_diff = float('inf')
    
    # Binary search (approximate)
    for _ in range(25):
        mid_t = (min_t + max_t) / 2
        
        # Test this threshold
        ms_test = pymeshlab.MeshSet()
        ms_test.load_new_mesh(filepath)
        ms_test.meshing_decimation_clustering(threshold=pymeshlab.PercentageValue(mid_t))
        
        res_faces = ms_test.current_mesh().face_number()
        diff = abs(res_faces - target_faces)
        
        if diff < best_diff:
            best_diff = diff
            best_t = mid_t
        
        if res_faces < target_faces:
            # Too aggressive (too few faces) -> Reduce threshold (smaller cells)
            max_t = mid_t
        else:
            # Too many faces -> Increase threshold (larger cells)
            min_t = mid_t
            
    return best_t

def apply_algorithm(ms, algo_name, target_faces, clustering_threshold=None):
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
        # Use provided threshold or default to 0.1% if not tuned (shouldn't happen in exp)
        t = clustering_threshold if clustering_threshold is not None else 0.1
        ms.meshing_decimation_clustering(threshold=pymeshlab.PercentageValue(t))

def run_experiment():
    results = []
    
    # Clear decimated_meshes directory
    if os.path.exists(DECIMATED_DIR):
        print("Clearing decimated_meshes directory...")
        for filename in os.listdir(DECIMATED_DIR):
            file_path = os.path.join(DECIMATED_DIR, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')
    else:
        os.makedirs(DECIMATED_DIR)

    # Prepare CSV
    with open(RESULTS_FILE, 'w', newline='') as csvfile:
        fieldnames = ['Model', 'Type', 'Algorithm', 'Decimation', 'Time', 'HausdorffDist', 'InitialFaces', 'FinalFaces']
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
                
                for target_pct in TARGET_PERCENTAGES:
                    target_faces = int(initial_faces * target_pct)
                    decimation_label = f"{int((1-target_pct)*100)}pct"
                    print(f"  Target: {decimation_label} Decimation ({target_faces} faces)")
                    
                    # Algorithms to test
                    algorithms = ["QEM", "Clustering"]
                    
                    for algo in algorithms:
                        try:
                            # Tune parameters if needed
                            clustering_threshold = None
                            if algo == "Clustering":
                                clustering_threshold = tune_clustering_threshold(filepath, target_faces)
                            
                            # Warm-up run (if needed, to load libraries/caches)
                            # For simple scripts, this might be overkill, but good practice.
                            # We'll run once without timing.
                            print(f"    Running {algo}...", end='', flush=True)
                            ms = pymeshlab.MeshSet()
                            ms.load_new_mesh(filepath)
                            apply_algorithm(ms, algo, target_faces, clustering_threshold)
                        
                        # Measure Time (Average of N runs)
                            NUM_REPEATS = 1
                            total_time = 0
                            
                            for _ in range(NUM_REPEATS):
                                # Reload mesh for each run to ensure identical starting state
                                ms_timing = pymeshlab.MeshSet()
                                ms_timing.load_new_mesh(filepath)
                                
                                start_time = time.perf_counter_ns()
                                apply_algorithm(ms_timing, algo, target_faces, clustering_threshold)
                                end_time = time.perf_counter_ns()
                                total_time += (end_time - start_time)
                            
                            # Convert nanoseconds to seconds for consistency with analysis
                            execution_time = (total_time / NUM_REPEATS) / 1e9
                            
                            # Final application for geometric analysis (using the last run's result)
                            # We can just use the ms from the last iteration or reload one last time.
                            # Let's reload to be safe and consistent with the "FinalFaces" count.
                            ms = pymeshlab.MeshSet()
                            ms.load_new_mesh(filepath)
                            apply_algorithm(ms, algo, target_faces, clustering_threshold)
                            
                            final_faces = get_face_count(ms)
                            final_verts = ms.current_mesh().vertex_number()
                            
                            # Save the decimated mesh
                            output_dir = "./decimated_meshes"
                            os.makedirs(output_dir, exist_ok=True)
                            name_only = os.path.splitext(filename)[0]
                            save_path = os.path.join(output_dir, f"{name_only}_{algo}_{decimation_label}.obj")
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
                                'Decimation': decimation_label,
                                'Time': execution_time,
                                'HausdorffDist': hausdorff_dist,
                                'InitialFaces': initial_faces,
                                'FinalFaces': final_faces
                            }
                            writer.writerow(row)
                            results.append(row)
                            print(f"    {algo}: Time={execution_time:.4f}s, HD={hausdorff_dist:.6f}, Faces={final_faces}")
                        
                        except Exception as e:
                            # Print error in RED
                            print(f"\033[91m    Failed {algo} on {filename}: {e}\033[0m")

    print(f"Experiment complete. Results saved to {RESULTS_FILE}")

if __name__ == "__main__":
    run_experiment()
