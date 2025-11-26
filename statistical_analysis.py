import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
import statsmodels.api as sm
import os

# Create figures directory if it doesn't exist
os.makedirs('Report/figures', exist_ok=True)

# Read the data
df = pd.read_csv('experiment_results.csv')

# Prepare data for ANOVA residuals (Time)
# Model: Time ~ Algorithm + Type + Decimation + Interactions
# We can just get residuals from the group means for a simple check
df['Time_Group_Mean'] = df.groupby(['Algorithm', 'Type', 'Decimation'])['Time'].transform('mean')
df['Time_Residuals'] = df['Time'] - df['Time_Group_Mean']

# Prepare data for ANOVA residuals (HausdorffDist)
df['HD_Group_Mean'] = df.groupby(['Algorithm', 'Type', 'Decimation'])['HausdorffDist'].transform('mean')
df['HD_Residuals'] = df['HausdorffDist'] - df['HD_Group_Mean']

# 1. Shapiro-Wilk Test
w_time, p_time = stats.shapiro(df['Time_Residuals'])
w_hd, p_hd = stats.shapiro(df['HD_Residuals'])

print(f"Shapiro-Wilk Test for Time Residuals: W={w_time:.4f}, p={p_time:.4e}")
print(f"Shapiro-Wilk Test for HD Residuals:   W={w_hd:.4f}, p={p_hd:.4e}")

# Save results to a text file for inclusion in report (optional, but good for record)
with open('Report/statistical_summary.txt', 'w') as f:
    f.write(f"Shapiro-Wilk Test for Time Residuals: W={w_time:.4f}, p={p_time:.4e}\n")
    f.write(f"Shapiro-Wilk Test for HD Residuals:   W={w_hd:.4f}, p={p_hd:.4e}\n")

# 2. Q-Q Plot for Time
plt.figure(figsize=(6, 6))
sm.qqplot(df['Time_Residuals'], line='45', fit=True)
plt.title('Q-Q Plot of Execution Time Residuals')
plt.savefig('Report/figures/qq_plot_time.pdf')
plt.close()

# 3. Q-Q Plot for Hausdorff Distance
plt.figure(figsize=(6, 6))
sm.qqplot(df['HD_Residuals'], line='45', fit=True)
plt.title('Q-Q Plot of Hausdorff Distance Residuals')
plt.savefig('Report/figures/qq_plot_hd.pdf')
plt.close()

print("Q-Q plots generated in Report/figures/")
