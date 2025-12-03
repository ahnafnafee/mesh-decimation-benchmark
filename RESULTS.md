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

| Algorithm      | Mesh Type | Time (s) [Mean ± SD] | Time 95% CI      | Hausdorff Dist [Mean ± SD] | HD 95% CI         |
| :------------- | :-------- | :------------------- | :--------------- | :------------------------- | :---------------- |
| **Clustering** | Clean CAD | **0.0232 ± 0.0150**  | (0.0149, 0.0315) | 0.0019 ± 0.0017            | (0.0009, 0.0028)  |
|                | Organic   | **0.1542 ± 0.2473**  | (0.0172, 0.2911) | 0.0058 ± 0.0039            | (0.0037, 0.0079)  |
| **QEM**        | Clean CAD | 0.6214 ± 0.3783      | (0.4119, 0.8309) | 0.0070 ± 0.0251            | (-0.0069, 0.0209) |
|                | Organic   | 3.0787 ± 3.9697      | (0.8803, 5.2770) | 0.0036 ± 0.0047            | (0.0010, 0.0062)  |

### 2.2. Statistical Analysis (ANOVA)

We performed a two-way ANOVA to assess the impact of **Algorithm** and **Mesh Type** on performance.

#### **Execution Time**

-   **Algorithm**: $F(1, 56) = 11.66$, $p = 0.0012$ (Significant)
-   **Mesh Type**: $F(1, 56) = 6.29$, $p = 0.0150$ (Significant)
-   **Interaction**: $F(1, 56) = 5.09$, $p = 0.0281$ (Significant)

#### **Hausdorff Distance (Error)**

-   **Algorithm**: $F(1, 56) = 0.19$, $p = 0.6661$ (Not Significant)
-   **Mesh Type**: $F(1, 56) = 0.01$, $p = 0.9400$ (Not Significant)
-   **Interaction**: $F(1, 56) = 1.23$, $p = 0.2731$ (Not Significant)

### 2.3. Simple Main Effects (Interaction Analysis)

Since the ANOVA showed a significant interaction for Time ($p=0.03$), we performed independent T-tests (Welch's) comparing QEM vs. Clustering within each Mesh Type.

**Execution Time:**

-   **Clean CAD**: QEM is significantly slower ($p < 0.001$, Mean Diff: 0.60s).
-   **Organic**: QEM is significantly slower ($p = 0.013$, Mean Diff: 2.92s).
-   **Insight**: The performance gap widens drastically for organic meshes, confirming the interaction effect.

**Hausdorff Distance (Exploratory):**

-   **Clean CAD**: No significant difference ($p = 0.44$).
-   **Organic**: No significant difference ($p = 0.16$).
-   **Insight**: When face counts are strictly controlled (approx. 50% reduction), **Clustering performs comparably to QEM** in terms of geometric error (Hausdorff Distance) for this dataset, contrary to the initial hypothesis that QEM would be superior for organic shapes.

## 3. Discussion & Conclusions

1.  **Speed**: **Vertex Clustering** is the undisputed winner for speed ($p < 0.01$). It operates in milliseconds (approx 20-150ms) compared to QEM's seconds (0.6-3.0s).
2.  **Accuracy**:
    -   For **Clean CAD** models, there is no significant difference in accuracy between QEM and Clustering at 50% reduction.
    -   For **Organic** models, contrary to expectations, **no significant difference** was found ($p = 0.16$) when face counts are strictly controlled. This suggests that for a 50% reduction, Clustering provides a competitive geometric approximation.
3.  **Interaction**: The significant interaction in Time ($p=0.03$) highlights that QEM's computational cost scales poorly with mesh complexity (Organic), whereas Clustering remains consistently fast.
4.  **Recommendation**:
    -   **General Use**: **Vertex Clustering** is recommended for most real-time applications. It offers a massive speed advantage with statistically comparable geometric accuracy to QEM at moderate reduction levels (50%).
    -   **High-Fidelity**: **QEM** may still be preferred for extreme reductions or where topological preservation (which Hausdorff doesn't measure) is critical, but for pure geometric error at 50%, the advantage is not statistically significant in this dataset.

## 4. Limitations

-   **Non-normality**: Significant violations of normality assumptions were observed.
-   **Sample size**: $n=15$ per group.
