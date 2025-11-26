import pymeshlab
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os
import argparse

# Configuration
DECIMATED_DIR = "./decimated_meshes"
ORIGINAL_DIRS = {
    # Clean CAD
    "airplane_0004": "./dataset/clean_cad/airplane_0004.obj",
    "airplane_0009": "./dataset/clean_cad/airplane_0009.obj",
    "airplane_0019": "./dataset/clean_cad/airplane_0019.obj",
    "airplane_0263": "./dataset/clean_cad/airplane_0263.obj",
    "airplane_0352": "./dataset/clean_cad/airplane_0352.obj",
    "chair_0187": "./dataset/clean_cad/chair_0187.obj",
    "chair_0230": "./dataset/clean_cad/chair_0230.obj",
    "chair_0303": "./dataset/clean_cad/chair_0303.obj",
    "chair_0590": "./dataset/clean_cad/chair_0590.obj",
    "chair_0889": "./dataset/clean_cad/chair_0889.obj",
    "guitar_0019": "./dataset/clean_cad/guitar_0019.obj",
    "guitar_0028": "./dataset/clean_cad/guitar_0028.obj",
    "guitar_0050": "./dataset/clean_cad/guitar_0050.obj",
    "guitar_0079": "./dataset/clean_cad/guitar_0079.obj",
    "guitar_0125": "./dataset/clean_cad/guitar_0125.obj",
    
    # Organic
    "190698-frog_statue": "./dataset/organic_scanned/190698-frog_statue.obj",
    "208741-sheep": "./dataset/organic_scanned/208741-sheep.obj",
    "286162-dragon": "./dataset/organic_scanned/286162-dragon.obj",
    "313444-neko": "./dataset/organic_scanned/313444-neko.obj",
    "321050-skull": "./dataset/organic_scanned/321050-skull.obj",
    "357854-gnome": "./dataset/organic_scanned/357854-gnome.obj",
    "38157-face": "./dataset/organic_scanned/38157-face.obj",
    "451870-fish": "./dataset/organic_scanned/451870-fish.obj",
    "49316-face": "./dataset/organic_scanned/49316-face.obj",
    "64957-duo_rabbit": "./dataset/organic_scanned/64957-duo_rabbit.obj",
    "73192-statue": "./dataset/organic_scanned/73192-statue.obj",
    "73877-pharaoh": "./dataset/organic_scanned/73877-pharaoh.obj",
    "80757-dragon_head": "./dataset/organic_scanned/80757-dragon_head.obj",
    "859652-skull": "./dataset/organic_scanned/859652-skull.obj",
    "86250-minion": "./dataset/organic_scanned/86250-minion.obj"
}
ALGORITHMS = ["QEM", "Clustering", "Simple"]

def take_snapshot(mesh_path, output_image, rot_x, rot_y, rot_z):
    ms = pymeshlab.MeshSet()
    ms.load_new_mesh(mesh_path)
    
    # 1. Base Mesh Style: Light Grey
    ms.set_current_mesh(0) # Ensure we are on the base mesh
    gray = pymeshlab.Color(220, 220, 220, 255)
    ms.set_color_per_vertex(color1=gray)
    # ms.set_color_per_face(color1=gray) # Not available
    ms.compute_normal_per_face()
    
    # 2. Wireframe: Generate solid wireframe as a new layer
    # Radius 0.1% (thinner for dense meshes)
    ms.generate_solid_wireframe(edgecylradius=pymeshlab.PercentageValue(0.1), 
                                vertsphflag=False)
    
    # 3. Style Wireframe: Dark Blue
    # generate_solid_wireframe makes the new mesh current
    dark_blue = pymeshlab.Color(0, 50, 150, 255)
    ms.set_color_per_vertex(color1=dark_blue)
    # ms.set_color_per_face(color1=dark_blue) # Not available
    
    # 4. Custom Rotation
    if rot_x != 0:
        ms.compute_matrix_from_rotation(rotaxis=0, angle=rot_x)
    if rot_y != 0:
        ms.compute_matrix_from_rotation(rotaxis=1, angle=rot_y)
    if rot_z != 0:
        ms.compute_matrix_from_rotation(rotaxis=2, angle=rot_z)
    
    # 5. High Resolution Snapshot with White Background
    ms.save_snapshot(imagewidth=2048, imageheight=2048,
                     imagebackgroundcolor=pymeshlab.Color(255, 255, 255, 255))
    if os.path.exists("gpu_generated_image.png"):
        if os.path.exists(output_image):
            os.remove(output_image)
        os.rename("gpu_generated_image.png", output_image)
    return ms.current_mesh().vertex_number()

def create_figure(model_name, rot_x, rot_y, rot_z):
    os.makedirs("figures", exist_ok=True)
    fig, axes = plt.subplots(1, 4, figsize=(24, 6)) # Wider figure
    
    # 1. Original
    if model_name not in ORIGINAL_DIRS:
        print(f"Error: Model '{model_name}' not found in ORIGINAL_DIRS.")
        return

    orig_path = ORIGINAL_DIRS[model_name]
    orig_img = f"temp_{model_name}_orig.png"
    orig_verts = take_snapshot(orig_path, orig_img, rot_x, rot_y, rot_z)
    
    if os.path.exists(orig_img):
        img = mpimg.imread(orig_img)
        axes[0].imshow(img)
        axes[0].set_title(f"Original\n{orig_verts} vertices", fontsize=14)
        axes[0].axis('off')
        os.remove(orig_img)
    
    # 2. Algorithms
    for i, algo in enumerate(ALGORITHMS):
        mesh_path = os.path.join(DECIMATED_DIR, f"{model_name}_{algo}.obj")
        if not os.path.exists(mesh_path):
            print(f"Warning: {mesh_path} not found.")
            axes[i+1].axis('off')
            continue
            
        algo_img = f"temp_{model_name}_{algo}.png"
        verts = take_snapshot(mesh_path, algo_img, rot_x, rot_y, rot_z)
        
        if os.path.exists(algo_img):
            img = mpimg.imread(algo_img)
            axes[i+1].imshow(img)
            axes[i+1].set_title(f"{algo}\n{verts} vertices", fontsize=14)
            axes[i+1].axis('off')
            os.remove(algo_img)
    
    plt.tight_layout()
    plt.subplots_adjust(wspace=0.02) # Reduce whitespace between subplots
    output_path = os.path.join("figures", f"{model_name}_custom.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate mesh comparison figure with custom rotation.")
    parser.add_argument("model", help="Name of the model (e.g., airplane_0004)")
    parser.add_argument("--rot_x", type=float, default=-30, help="Rotation around X axis (degrees)")
    parser.add_argument("--rot_y", type=float, default=45, help="Rotation around Y axis (degrees)")
    parser.add_argument("--rot_z", type=float, default=0, help="Rotation around Z axis (degrees)")
    
    args = parser.parse_args()
    
    create_figure(args.model, args.rot_x, args.rot_y, args.rot_z)
