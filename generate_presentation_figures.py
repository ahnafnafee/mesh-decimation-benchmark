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
    """Slide 5: Execution Time Results (Faceted by Decimation)"""
    # Use catplot for faceting
    g = sns.catplot(
        data=df, x="Type", y="Time", hue="Algorithm", col="Decimation",
        kind="bar", errorbar=('ci', 95), capsize=0.1, 
        palette=["#9b59b6", "#e67e22"], height=6, aspect=0.8,
        hue_order=["QEM", "Clustering"], order=["clean_cad", "organic_scanned"]
    )
    
    g.set_axis_labels("Mesh Type", "Execution Time (s) [Log Scale]")
    g.set_titles("{col_name} Decimation")
    
    # Set log scale for all axes
    for ax in g.axes.flat:
        ax.set_yscale('log')
        ax.grid(True, which="minor", ls="--", alpha=0.3)
    
    # Adjust title
    g.fig.suptitle("Execution Time: Clustering vs QEM", fontsize=16, y=1.05)
    
    plt.savefig(os.path.join(OUTPUT_DIR, "slide5_execution_time.png"), dpi=300, bbox_inches='tight')
    plt.close()

def create_geometric_fidelity_chart(df):
    """Slide 6: Geometric Fidelity (Faceted by Decimation)"""
    g = sns.catplot(
        data=df, x="Type", y="HausdorffDist", hue="Algorithm", col="Decimation",
        kind="bar", errorbar=('ci', 95), capsize=0.1, 
        palette=["#9b59b6", "#e67e22"], height=6, aspect=0.8,
        hue_order=["QEM", "Clustering"], order=["clean_cad", "organic_scanned"]
    )
    
    g.set_axis_labels("Mesh Type", "Hausdorff Distance (Lower is Better)")
    g.set_titles("{col_name} Decimation")
    
    g.fig.suptitle("Geometric Fidelity: Clustering vs QEM", fontsize=16, y=1.05)
    
    plt.savefig(os.path.join(OUTPUT_DIR, "slide6_geometric_fidelity.png"), dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    df = load_data()
    create_execution_time_chart(df)
    create_geometric_fidelity_chart(df)
    print("Figures generated in 'presentation/' directory.")
