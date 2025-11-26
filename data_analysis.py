import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm
from statsmodels.formula.api import ols


RESULTS_FILE = "experiment_results.csv"

def analyze_results():
    try:
        df = pd.read_csv(RESULTS_FILE)
    except FileNotFoundError:
        print(f"Error: {RESULTS_FILE} not found. Run experiment_runner.py first.")
        return

    import warnings
    warnings.filterwarnings("ignore")

    # Calculate descriptive stats
    # Group by Algorithm and Type
    grouped = df.groupby(['Algorithm', 'Type'])
    
    print("\n--- Descriptive Statistics with 95% CI ---")
    summary = grouped.agg({
        'Time': ['mean', 'std', 'count', 'sem'],
        'HausdorffDist': ['mean', 'std', 'count', 'sem']
    })
    print("Summary Table:")
    print(summary)
    
    # Calculate 95% CI
    # We use t-distribution because n is small (15)
    from scipy import stats
    
    def get_ci(row, col):
        mean = row[(col, 'mean')]
        sem = row[(col, 'sem')]
        count = row[(col, 'count')]
        return stats.t.interval(0.95, count-1, loc=mean, scale=sem)

    # Print formatted table
    print(f"{'Algorithm':<15} {'Type':<20} {'Time Mean':<10} {'Time 95% CI':<25} {'HD Mean':<10} {'HD 95% CI':<25}")
    print("-" * 110)
    
    for idx, row in summary.iterrows():
        algo, mtype = idx
        
        time_mean = row[('Time', 'mean')]
        time_ci = get_ci(row, 'Time')
        
        hd_mean = row[('HausdorffDist', 'mean')]
        hd_ci = get_ci(row, 'HausdorffDist')
        
        print(f"{algo:<15} {mtype:<20} {time_mean:<10.4f} ({time_ci[0]:.4f}, {time_ci[1]:.4f})    {hd_mean:<10.4f} ({hd_ci[0]:.4f}, {hd_ci[1]:.4f})")
        
    print("-" * 110)

    # Note: Shapiro-Wilk is sensitive to sample size.
    print("Shapiro-Wilk Test for Normality (p-value < 0.05 indicates non-normality):")
    for algo in df['Algorithm'].unique():
        for mtype in df['Type'].unique():
            subset = df[(df['Algorithm'] == algo) & (df['Type'] == mtype)]
            if len(subset) > 3: # Need at least 3 data points
                _, p_time = stats.shapiro(subset['Time'])
                _, p_hd = stats.shapiro(subset['HausdorffDist'])
                print(f"  {algo} - {mtype}: Time p={p_time:.4f}, HD p={p_hd:.4f}")
    
    # Homogeneity of Variance (Levene's Test)
    print("\nLevene's Test for Homogeneity of Variance (p-value < 0.05 indicates unequal variances):")
    # We test across the 6 groups (3 algos * 2 types)
    groups_time = [df[(df['Algorithm'] == a) & (df['Type'] == t)]['Time'] for a in df['Algorithm'].unique() for t in df['Type'].unique()]
    groups_hd = [df[(df['Algorithm'] == a) & (df['Type'] == t)]['HausdorffDist'] for a in df['Algorithm'].unique() for t in df['Type'].unique()]
    
    _, p_levene_time = stats.levene(*groups_time)
    _, p_levene_hd = stats.levene(*groups_hd)
    print(f"  Time: p={p_levene_time:.4f}")
    print(f"  Hausdorff Distance: p={p_levene_hd:.4f}")
    print("\n")
    # --- Three-Way ANOVA ---
    print("--- Three-Way ANOVA Results ---")
    
    # Model for Time
    print("Dependent Variable: Execution Time")
    model_time = ols('Time ~ C(Algorithm) * C(Type) * C(Decimation)', data=df).fit()
    anova_time = sm.stats.anova_lm(model_time, typ=2)
    print(anova_time)
    print("\n")

    # Model for Hausdorff Distance
    print("Dependent Variable: Hausdorff Distance")
    model_hd = ols('HausdorffDist ~ C(Algorithm) * C(Type) * C(Decimation)', data=df).fit()
    anova_hd = sm.stats.anova_lm(model_hd, typ=2)
    print(anova_hd)
    print("\n")
    
    
    # --- Post-Hoc Analysis (Tukey's HSD) ---
    print("--- Post-Hoc Analysis (Tukey's HSD) ---")
    print("Performing pairwise comparisons to control for Type 1 error.\n")
    
    # Create a combined group column for interaction analysis
    df['Group'] = df['Algorithm'] + "_" + df['Type'] + "_" + df['Decimation']
    
    from statsmodels.stats.multicomp import pairwise_tukeyhsd
    
    print("1. Tukey HSD for Execution Time:")
    tukey_time = pairwise_tukeyhsd(endog=df['Time'], groups=df['Group'], alpha=0.05)
    print(tukey_time)
    print("\n")
    
    print("2. Tukey HSD for Hausdorff Distance:")
    tukey_hd = pairwise_tukeyhsd(endog=df['HausdorffDist'], groups=df['Group'], alpha=0.05)
    print(tukey_hd)
    print("\n")

    print("=== Analysis Complete ===")
    print("\nInterpretation Guide:")
    print("- If Levene's test p < 0.05: Variances are unequal, T-test results may be affected.")

if __name__ == "__main__":
    import sys
    
    # Redirect stdout to file
    with open("analysis_summary.txt", "w", encoding="utf-8") as f:
        original_stdout = sys.stdout
        sys.stdout = f
        
        try:
            analyze_results()
        finally:
            sys.stdout = original_stdout
            
    print("Analysis complete. Results saved to analysis_summary.txt")
