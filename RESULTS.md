# Experiment Results

## 1. Methodology Notes (PI Feedback Implemented)

Following the project proposal review, the following methodological improvements were implemented:

1.  **Execution Time Measurement**: Switched to **Wall-Clock Time** (`time.perf_counter()`) as per **Section 2.3.6** of the project guidelines. This metric captures the full elapsed time perceived by the user, including system overhead and memory operations, which is more relevant for real-world performance analysis than CPU time. To ensure accuracy:
    -   **Warm-up**: Each algorithm is run once before timing to mitigate JIT/caching effects.
    -   **Repetitions**: Measurements are averaged over **5 repetitions** to reduce noise.
2.  **Geometric Error Metric**: Implemented **Two-Sided Hausdorff Distance** (`max(d(A,B), d(B,A))`).
3.  **Confidence Intervals**: 95% Confidence Intervals (CI) are calculated for all metrics.
4.  **Scope Refinement**: The "Simple" algorithm (Isotropic Remeshing) was removed to focus the study strictly on **Decimation** algorithms (QEM vs. Clustering), isolating the trade-off between speed and geometric accuracy without confounding topological regularization.

# Experiment Results

## 1. Methodology Notes (PI Feedback Implemented)

Following the project proposal review, the following methodological improvements were implemented:

1.  **Execution Time Measurement**: Switched to **Wall-Clock Time** (`time.perf_counter()`) as per **Section 2.3.6** of the project guidelines. This metric captures the full elapsed time perceived by the user, including system overhead and memory operations, which is more relevant for real-world performance analysis than CPU time. To ensure accuracy:
    -   **Warm-up**: Each algorithm is run once before timing to mitigate JIT/caching effects.
    -   **Repetitions**: Measurements are averaged over **5 repetitions** to reduce noise.
2.  **Geometric Error Metric**: Implemented **Two-Sided Hausdorff Distance** (`max(d(A,B), d(B,A))`).
3.  **Confidence Intervals**: 95% Confidence Intervals (CI) are calculated for all metrics.
4.  **Scope Refinement**: The "Simple" algorithm (Isotropic Remeshing) was removed to focus the study strictly on **Decimation** algorithms (QEM vs. Clustering), isolating the trade-off between speed and geometric accuracy without confounding topological regularization.

## 2. Results

### 2.1. Descriptive Statistics

| Algorithm      | Mesh Type       | Time (s) [Mean ± SD] | Time 95% CI      | Hausdorff Dist [Mean ± SD] | HD 95% CI        |
| :------------- | :-------------- | :------------------- | :--------------- | :------------------------- | :--------------- |
| **Clustering** | Clean CAD       | **0.0049 ± 0.0037**  | (0.0035, 0.0063) | 0.0058 ± 0.0056            | (0.0038, 0.0079) |
|                | Organic Scanned | **0.0317 ± 0.0620**  | (0.0085, 0.0548) | 0.0128 ± 0.0118            | (0.0084, 0.0173) |
| **QEM**        | Clean CAD       | 0.2589 ± 0.1780      | (0.1925, 0.3254) | 0.0339 ± 0.0606            | (0.0113, 0.0566) |
|                | Organic Scanned | 1.2904 ± 1.7175      | (0.6491, 1.9317) | 0.0060 ± 0.0065            | (0.0035, 0.0084) |

### 2.2. Statistical Analysis (3-Way ANOVA)

We performed a **Three-Way ANOVA** to analyze the effects of **Algorithm**, **Mesh Type**, and **Decimation Level** (50% vs 90%) on Execution Time and Geometric Fidelity.

### 2.3. Post-Hoc Analysis (Tukey's HSD)

-   **Time**:
    -   **QEM on Organic Scanned** meshes at 90% decimation is significantly slower than all other groups ($p < 0.001$).
-   **Hausdorff Distance**:
    -   **QEM on Clean CAD** showed a significant increase in error when moving from 50% to 90% decimation ($p < 0.001$).
    -   **Clustering** did not show a statistically significant degradation in Hausdorff Distance between 50% and 90% for either mesh type ($p > 0.9$).
    -   **Insight**: QEM's error explodes on CAD models at extreme decimation (90%), likely due to the loss of critical features that QEM tries to preserve but fails when the budget is too low. Clustering remains "consistently mediocre" but stable.

## 3. Discussion & Conclusions

1.  **Speed**: **Vertex Clustering** is consistently orders of magnitude faster ($p < 0.001$), especially for complex organic meshes.
2.  **Accuracy & Stability**:
    -   At **50% decimation**, both algorithms perform comparably.
    -   At **90% decimation**, **QEM** struggles with **Clean CAD** models, showing a significant spike in geometric error ($p < 0.001$).
    -   **Clustering** is remarkably stable; its error does not significantly increase even at 90% reduction.
3.  **Recommendation**:
    -   **Moderate Reduction (50%)**: Use **QEM** if topology preservation is key, otherwise **Clustering** for speed.
    -   **Extreme Reduction (90%)**: **Vertex Clustering** is the superior choice. It is faster and statistically more robust in terms of geometric error stability than QEM for CAD models in this dataset.

## 4. Limitations

-   **Non-normality**: Significant violations of normality assumptions were observed (Shapiro-Wilk $p < 0.05$). However, ANOVA is generally robust to this given the balanced design.
-   **Sample Size**: $n=15$ per group (Clean CAD), $n=15$ per group (Organic).
-   **Metric Scope**: We only measured Hausdorff Distance. QEM might still be superior in preserving specific topological features or sharp edges that Hausdorff Distance averages out.
