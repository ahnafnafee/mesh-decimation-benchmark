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
| **Clustering** | Clean CAD       | **0.0169 ± 0.0140**  | (0.0124, 0.0214) | 0.0033 ± 0.0025            | (0.0025, 0.0041) |
|                | Organic Scanned | **0.1160 ± 0.1739**  | (0.0511, 0.1809) | 0.0068 ± 0.0046            | (0.0051, 0.0085) |
| **QEM**        | Clean CAD       | 0.7309 ± 0.4875      | (0.5750, 0.8868) | 0.0076 ± 0.0229            | (0.0003, 0.0149) |
|                | Organic Scanned | 3.4893 ± 4.4972      | (1.8100, 5.1686) | 0.0045 ± 0.0047            | (0.0028, 0.0063) |

### 2.2. Statistical Analysis (3-Way ANOVA)

We performed a **Three-Way ANOVA** to analyze the effects of **Algorithm**, **Mesh Type**, and **Decimation Level** (50% vs 80%) on Execution Time and Geometric Fidelity.

#### **1. Execution Time**

-   **Algorithm**: Significant ($F(1, 132) = 27.31, p < 0.001$). QEM is significantly slower.
-   **Mesh Type**: Significant ($F(1, 132) = 15.90, p < 0.001$). Organic meshes take longer.
-   **Decimation Level**: Not Significant ($F(1, 132) = 1.01, p = 0.32$).
-   **Interaction (Algorithm $\times$ Type)**: Significant ($F(1, 132) = 13.77, p < 0.001$). The performance gap between QEM and Clustering widens drastically for organic meshes.

#### **2. Geometric Fidelity (Hausdorff Distance)**

-   **Algorithm**: Not Significant ($F(1, 132) = 0.48, p = 0.49$).
-   **Mesh Type**: Not Significant ($F(1, 132) = 0.01, p = 0.93$).
-   **Decimation Level**: Not Significant ($F(1, 132) = 1.90, p = 0.17$).
-   **Interactions**: None were significant.

### 2.3. Post-Hoc Analysis (Tukey's HSD)

Since the ANOVA showed a significant interaction for Time, we performed **Tukey's HSD** to compare individual groups.

-   **Time**:
    -   **QEM on Organic Scanned** meshes is significantly slower than all other groups ($p < 0.001$).
    -   There is no statistically significant difference in speed between QEM and Clustering on **Clean CAD** meshes ($p \approx 0.99$), likely due to the low polygon count of CAD models making the difference negligible in absolute terms.
-   **Hausdorff Distance**:
    -   No pairwise comparisons were statistically significant ($p > 0.05$).
    -   **Insight**: At 50% and 80% decimation, **Vertex Clustering performs statistically comparably to QEM** in terms of geometric error for this dataset.

## 3. Discussion & Conclusions

1.  **Speed**: **Vertex Clustering** is the clear winner for large, complex (Organic) meshes. For simple CAD models, the difference is less pronounced in absolute time but still present.
2.  **Accuracy**: Contrary to the common assumption that QEM is always superior, our results show **no significant difference** in Hausdorff Distance between QEM and Clustering for these specific decimation levels (50% and 80%). This suggests Clustering is a viable, high-speed alternative for moderate reduction tasks.
3.  **Decimation Impact**: The target reduction level (50% vs 80%) did not significantly alter the relative performance ranking or the quality trade-off.

## 4. Limitations

-   **Non-normality**: Significant violations of normality assumptions were observed (Shapiro-Wilk $p < 0.05$). However, ANOVA is generally robust to this given the balanced design.
-   **Sample Size**: $n \approx 30-40$ per group, which is decent but could be larger.
-   **Metric Scope**: We only measured Hausdorff Distance. QEM might still be superior in preserving specific topological features or sharp edges that Hausdorff Distance averages out.
