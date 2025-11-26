import pymeshlab
import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pandas as pd
from matplotlib.lines import Line2D

# Configuration
MODELS_TO_VISUALIZE = ["airplane_0004", "airplane_0009", "190698-frog_statue", "208741-sheep"]
DECIMATED_DIR = "./decimated_meshes"
ORIGINAL_DIRS = {
    "airplane_0004": "./dataset/clean_cad/airplane_0004.obj",
    "airplane_0009": "./dataset/clean_cad/airplane_0009.obj",
    "190698-frog_statue": "./dataset/organic_scanned/190698-frog_statue.obj",
    "208741-sheep": "./dataset/organic_scanned/208741-sheep.obj"
}
ALGORITHMS = ["QEM", "Clustering", "Simple"]
RESULTS_FILE = "experiment_results.csv"

def load_results():
    """Load experiment results into a dictionary for easy lookup."""
    df = pd.read_csv(RESULTS_FILE)
    results = {}
    for _, row in df.iterrows():
        # Key: (ModelName, Algorithm)
        # Remove .obj extension for matching
        model_name = os.path.splitext(str(row['Model']))[0]
        key = (model_name, row['Algorithm'])
        results[key] = {
            'HausdorffDist': row['HausdorffDist'],
            'FinalFaces': int(row['FinalFaces']),
            'InitialFaces': int(row['InitialFaces'])
        }
    return results

def take_snapshot(mesh_path, output_image):
    """Generate a high-quality snapshot of the mesh."""
    ms = pymeshlab.MeshSet()
    ms.load_new_mesh(mesh_path)
    
def take_snapshot(mesh_path, output_image):
    """Generate a high-quality snapshot of the mesh."""
    ms = pymeshlab.MeshSet()
    ms.load_new_mesh(mesh_path)
    vertex_count = ms.current_mesh().vertex_number()
    
    # 1. Base Mesh Style: Ambient Occlusion + Smooth Shading
    ms.set_current_mesh(0)
    
    # Compute Normals for smooth shading
    ms.compute_normal_per_vertex()
    
    # Compute Ambient Occlusion (AO)
    # Using defaults for robustness
    ms.compute_scalar_ambient_occlusion()
    
    # Map AO scalar to Color (Grayscale)
    # 0 (Occluded) -> Dark, 1 (Exposed) -> White
    # We use a custom transfer function or just standard grayscale?
    # 'compute_color_from_scalar_per_vertex' with default might use rainbow.
    # We want grayscale.
    # There isn't a simple "grayscale" enum exposed easily without checking docs.
    # Workaround: Use 'colorize_by_vertex_quality' equivalent if available, or:
    # We can manually set color if we can't control the ramp easily.
    # Actually, let's try 'compute_color_from_scalar_per_vertex' and hope for a good default or check if we can specify color.
    # If not, we can stick to a solid light grey but with lighting enabled, it should look okay.
    # But the user specifically mentioned "rendered" which implies AO.
    # Let's try to map it.
    # Alternative: 'apply_color_equalization_per_vertex' might help?
    # Let's stick to simple shading first: Light Grey + Lighting.
    # The previous issue was likely transparency due to only rendering the wireframe.
    # So let's fix the flattening first.
    
    gray = pymeshlab.Color(200, 200, 200, 255)
    ms.set_color_per_vertex(color1=gray)
    
    # 2. Wireframe: Generate solid wireframe as a new layer
    # Radius 0.05% (thinner for cleaner look)
    ms.generate_solid_wireframe(edgecylradius=pymeshlab.PercentageValue(0.05), 
                                vertsphflag=False)
    
    # 3. Style Wireframe: Dark Grey/Black
    # The wireframe is now the current mesh (Layer 1)
    dark_line = pymeshlab.Color(20, 20, 20, 255)
    ms.set_color_per_vertex(color1=dark_line)
    
    # 4. Prevent Z-Fighting: Scale Wireframe slightly
    # This pushes the wireframe just outside the base mesh
    ms.compute_matrix_from_translation_rotation_scale(scalex=1.001, scaley=1.001, scalez=1.001)
    ms.apply_matrix_freeze()
    
    # 5. Better Angle: Isometric-ish view
    # Apply to ALL meshes (Layer 0 and Layer 1)
    # We need to apply the rotation to both, or set the camera.
    # compute_matrix_from_rotation applies to the CURRENT mesh.
    # We need to apply it to both.
    
    # Apply to Wireframe (Current, Layer 1)
    ms.compute_matrix_from_rotation(rotaxis=0, angle=-20) 
    ms.compute_matrix_from_rotation(rotaxis=1, angle=45)
    ms.apply_matrix_freeze()
    
    # Apply to Base (Layer 0)
    ms.set_current_mesh(0)
    ms.compute_matrix_from_rotation(rotaxis=0, angle=-20) 
    ms.compute_matrix_from_rotation(rotaxis=1, angle=45)
    ms.apply_matrix_freeze()
    
    # 6. High Resolution Snapshot with White Background
    ms.save_snapshot(imagewidth=1024, imageheight=1024,
                     imagebackgroundcolor=pymeshlab.Color(255, 255, 255, 255))
    if os.path.exists("gpu_generated_image.png"):
        if os.path.exists(output_image):
            os.remove(output_image)
        os.rename("gpu_generated_image.png", output_image)
    
    return vertex_count

def create_figure(model_name, results_data):
    os.makedirs("figures", exist_ok=True)
    
    # Layout: 1 row, 4 columns (Input + 3 Algos)
    fig, axes = plt.subplots(1, 4, figsize=(20, 6))
    
    # Titles for columns
    titles = ["Input", "QEM", "Clustering", "Simple (Naive)"]
    
    # 1. Original
    orig_path = ORIGINAL_DIRS[model_name]
    orig_img = f"temp_{model_name}_orig.png"
    take_snapshot(orig_path, orig_img)
    
    # Get initial face count from any result entry for this model (they all have InitialFaces)
    # Just grab the first one found
    initial_faces = 0
    for algo in ALGORITHMS:
        if (model_name, algo) in results_data:
            initial_faces = results_data[(model_name, algo)]['InitialFaces']
            break
            
    if os.path.exists(orig_img):
        img = mpimg.imread(orig_img)
        axes[0].imshow(img)
        axes[0].axis('off')
        
        # Text labels
        axes[0].set_title(titles[0], fontsize=16, pad=20)
        axes[0].text(0.5, -0.1, f"Faces: {initial_faces}", 
                     transform=axes[0].transAxes, ha='center', fontsize=12)
        os.remove(orig_img)
    
    # 2. Algorithms
    for i, algo in enumerate(ALGORITHMS):
        ax = axes[i+1]
        mesh_path = os.path.join(DECIMATED_DIR, f"{model_name}_{algo}.obj")
        
        if not os.path.exists(mesh_path):
            ax.axis('off')
            continue
            
        algo_img = f"temp_{model_name}_{algo}.png"
        take_snapshot(mesh_path, algo_img)
        
        # Get stats
        stats = results_data.get((model_name, algo), None)
        faces = stats['FinalFaces'] if stats else "?"
        hd = stats['HausdorffDist'] if stats else 0.0
        
        if os.path.exists(algo_img):
            img = mpimg.imread(algo_img)
            ax.imshow(img)
            ax.axis('off')
            
            # Title
            ax.set_title(titles[i+1], fontsize=16, pad=20)
            
            # Stats text
            # Format: Faces: X (Y%)
            #         HD: Z
            if isinstance(faces, int) and initial_faces > 0:
                percent = (faces / initial_faces * 100)
            else:
                percent = 0.0
            
            stats_text = f"Faces: {faces} ({percent:.1f}%)\nHD: {hd:.2e}"
            
            # Bold the best HD? (Optional, but nice)
            # For now, just standard text
            ax.text(0.5, -0.1, stats_text, 
                    transform=ax.transAxes, ha='center', fontsize=12, linespacing=1.5)
            
            os.remove(algo_img)
            
        # Add vertical separator line to the left of this plot
        line = Line2D([0, 0], [0.2, 0.8], transform=ax.transAxes, color='black', linewidth=1)
        ax.add_line(line)

    plt.tight_layout()
    # Adjust spacing to make room for text
    plt.subplots_adjust(bottom=0.2, wspace=0.1)
    
    output_path = os.path.join("figures", f"{model_name}_comparison_v2.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved {output_path}")

if __name__ == "__main__":
    results = load_results()
    for model in MODELS_TO_VISUALIZE:
        print(f"Generating figure for {model}...")
        create_figure(model, results)
