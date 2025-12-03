import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import os

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_context("talk")
OUTPUT_DIR = "presentation"

def load_data():
    return pd.read_csv("experiment_results.csv")

def create_execution_time_chart(df):
    """Slide 5: Execution Time Results"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Calculate means and CIs for error bars
    # We'll let seaborn handle the aggregation and CI
    
    sns.barplot(data=df, x="Type", y="Time", hue="Algorithm", 
                errorbar=('ci', 95), capsize=0.1, palette=["#9b59b6", "#e67e22"], ax=ax)
    
    ax.set_yscale('log')
    ax.set_ylabel("Execution Time (s) [Log Scale]", fontsize=14)
    ax.set_xlabel("Mesh Type", fontsize=14)
    ax.set_title("Execution Time: Clustering vs QEM", fontsize=16, pad=20)
    ax.legend(title="Algorithm")
    
    # Add grid for log scale readability
    ax.grid(True, which="minor", ls="--", alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "slide5_execution_time.png"), dpi=300)
    plt.close()

def create_geometric_fidelity_chart(df):
    """Slide 6: Geometric Fidelity"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot with explicit order to ensure annotation alignment
    sns.barplot(data=df, x="Type", y="HausdorffDist", hue="Algorithm", 
                hue_order=["QEM", "Clustering"], order=["clean_cad", "organic_scanned"],
                errorbar=('ci', 95), capsize=0.1, palette=["#9b59b6", "#e67e22"], ax=ax)
    
    ax.set_ylabel("Hausdorff Distance (Lower is Better)", fontsize=14)
    ax.set_xlabel("Mesh Type", fontsize=14)
    ax.set_title("Geometric Fidelity: Clustering vs QEM", fontsize=16, pad=20)

    # Organic is index 1. QEM is bar 0 (left). Clustering is bar 1 (right).
    # We want to annotate the difference.
    # Get max height for placement
    y_max = df[df['Type']=='organic_scanned']['HausdorffDist'].max()
    
    # Draw bracket
    x1, x2 = 0.8, 1.2 # Approx positions for bars at x=1
    y, h = y_max + 0.002, 0.001
    ax.plot([x1, x1, x2, x2], [y, y+h, y+h, y], lw=1.5, c='k')
    ax.text((x1+x2)*.5, y+h, "p=0.16 (ns)", ha='center', va='bottom', color='k', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "slide6_geometric_fidelity.png"), dpi=300)
    plt.close()

if __name__ == "__main__":
    df = load_data()
    create_execution_time_chart(df)
    create_geometric_fidelity_chart(df)
    print("Figures generated in 'presentation/' directory.")
