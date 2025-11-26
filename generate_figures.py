import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Create figures directory if it doesn't exist
os.makedirs('Report/figures', exist_ok=True)

# Read the data
df = pd.read_csv('experiment_results.csv')

# Helper function to compute stats
def get_stats(data, group_col, value_col):
    grouped = data.groupby([group_col, 'Algorithm'])[value_col].agg(['mean', 'std', 'count', 'sem'])
    grouped['ci95'] = 1.96 * grouped['sem']
    return grouped.unstack()

# 1. Execution Time Bar Chart
stats_time = get_stats(df, 'Type', 'Time')
means = stats_time['mean']
errs = stats_time['ci95']

fig, ax = plt.subplots(figsize=(10, 6))
means.plot(kind='bar', yerr=errs, capsize=4, ax=ax, rot=0)
ax.set_yscale('log') # Use log scale for huge time differences
plt.title('Execution Time by Mesh Type and Algorithm')
plt.ylabel('Time (s) - Log Scale')
plt.xlabel('Mesh Type')
plt.legend(title='Algorithm')
plt.tight_layout()
plt.savefig('Report/figures/time_bar_chart.pdf')
plt.close()

# 2. Hausdorff Distance Bar Chart
stats_hd = get_stats(df, 'Type', 'HausdorffDist')
means_hd = stats_hd['mean']
errs_hd = stats_hd['ci95']

fig, ax = plt.subplots(figsize=(10, 6))
means_hd.plot(kind='bar', yerr=errs_hd, capsize=4, ax=ax, rot=0)
plt.title('Hausdorff Distance by Mesh Type and Algorithm')
plt.ylabel('Hausdorff Distance')
plt.xlabel('Mesh Type')
plt.legend(title='Algorithm')
plt.tight_layout()
plt.savefig('Report/figures/hd_bar_chart.pdf')
plt.close()

# 3. Interaction Plots (Manual implementation for Matplotlib)
def plot_interaction(df, y_col, filename, title):
    fig, ax = plt.subplots(figsize=(8, 6))
    
    algorithms = df['Algorithm'].unique()
    mesh_types = df['Type'].unique()
    
    for alg in algorithms:
        subset = df[df['Algorithm'] == alg]
        stats = subset.groupby('Type')[y_col].agg(['mean', 'sem'])
        stats['ci95'] = 1.96 * stats['sem']
        
        ax.errorbar(stats.index, stats['mean'], yerr=stats['ci95'], label=alg, capsize=5, marker='o' if alg == 'QEM' else 's')
    
    ax.set_title(title)
    ax.set_ylabel(y_col)
    if y_col == 'Time':
        ax.set_yscale('log') # Log scale for time plots
    ax.set_xlabel('Mesh Type')
    ax.legend(title='Algorithm')
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

plot_interaction(df, 'Time', 'Report/figures/time_interaction.pdf', 'Interaction Plot: Time vs. Mesh Type & Algorithm')
plot_interaction(df, 'HausdorffDist', 'Report/figures/hd_interaction.pdf', 'Interaction Plot: Geometric Error vs. Mesh Type & Algorithm')

# 4. Decimation Faceted plots (Simplified to Interaction-like plots per decimation level or just simple bars)
# Just creating separate plots for 50% vs 90% might be clearer or just Algorithm x Decimation
# Let's do Algorithm x Decimation for each Type

def plot_decimation_effect(df, mesh_type, y_col, filename_suffix, title_prefix):
    fig, ax = plt.subplots(figsize=(8, 6))
    subset = df[df['Type'] == mesh_type]
    
    algorithms = subset['Algorithm'].unique()
    
    # Organize data for bar plot
    stats = subset.groupby(['Decimation', 'Algorithm'])[y_col].agg(['mean', 'sem'])
    stats['ci95'] = 1.96 * stats['sem']
    means = stats['mean'].unstack()
    errs = stats['ci95'].unstack()
    
    means.plot(kind='bar', yerr=errs, capsize=4, ax=ax, rot=0)
    ax.set_title(f'{title_prefix} - {mesh_type}')
    ax.set_ylabel(y_col)
    if y_col == 'Time':
        ax.set_yscale('log')
    ax.set_xlabel('Decimation Level')
    plt.tight_layout()
    plt.savefig(f'Report/figures/{filename_suffix}_{mesh_type}.pdf')
    plt.close()

plot_decimation_effect(df, 'clean_cad', 'Time', 'time_dec', 'Execution Time')
plot_decimation_effect(df, 'organic_scanned', 'Time', 'time_dec', 'Execution Time')
plot_decimation_effect(df, 'clean_cad', 'HausdorffDist', 'hd_dec', 'Hausdorff Dist')
plot_decimation_effect(df, 'organic_scanned', 'HausdorffDist', 'hd_dec', 'Hausdorff Dist')

print("Figures generated successfully.")
