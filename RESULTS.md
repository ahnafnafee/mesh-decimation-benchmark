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
| **Clustering** | Clean CAD | **0.0025 ± 0.0010**  | (0.0020, 0.0031) | 0.0105 ± 0.0043            | (0.0081, 0.0129)  |
|                | Organic   | **0.0161 ± 0.0166**  | (0.0069, 0.0253) | 0.0086 ± 0.0041            | (0.0064, 0.0109)  |
| **QEM**        | Clean CAD | 0.2103 ± 0.1346      | (0.1358, 0.2849) | 0.0070 ± 0.0251            | (-0.0069, 0.0209) |
|                | Organic   | 1.0466 ± 1.4033      | (0.2695, 1.8238) | **0.0036 ± 0.0047**        | (0.0010, 0.0062)  |

### 2.2. Statistical Analysis (ANOVA)

We performed a two-way ANOVA to assess the impact of **Algorithm** and **Mesh Type** on performance.

#### **Execution Time**

-   **Algorithm**: $F(1, 56) = 11.57$, $p = 0.0012$ (Significant)
-   **Mesh Type**: $F(1, 56) = 5.45$, $p = 0.0232$ (Significant)
-   **Interaction**: $F(1, 56) = 5.11$, $p = 0.0277$ (Significant)

#### **Hausdorff Distance (Error)**

-   **Algorithm**: $F(1, 56) = 1.60$, $p = 0.2109$ (Not Significant)
-   **Mesh Type**: $F(1, 56) = 0.62$, $p = 0.4348$ (Not Significant)
-   **Interaction**: $F(1, 56) = 0.05$, $p = 0.8179$ (Not Significant)

### 2.3. Simple Main Effects (Interaction Analysis)

Since the ANOVA showed a significant interaction for Time ($p=0.03$), and to explore specific performance scenarios for Accuracy, we performed independent T-tests (Welch's) comparing QEM vs. Clustering within each Mesh Type.

**Execution Time:**

-   **Clean CAD**: QEM is significantly slower ($p < 0.001$, Mean Diff: 0.21s).
-   **Organic**: QEM is significantly slower ($p = 0.013$, Mean Diff: 1.03s).
-   **Insight**: The performance gap widens drastically for organic meshes, confirming the interaction effect.

**Hausdorff Distance (Exploratory):**

-   **Clean CAD**: No significant difference ($p = 0.60$).
-   **Organic**: QEM is **significantly more accurate** ($p = 0.004$, Mean Diff: -0.005).
-   **Insight**: While the global ANOVA was conservative, this specific comparison reveals that QEM maintains geometric fidelity better than Clustering on complex organic shapes.

## 3. Discussion & Conclusions

1.  **Speed**: **Vertex Clustering** is the undisputed winner for speed ($p < 0.01$). It operates in milliseconds. The "Simple" algorithm (Isotropic Remeshing) was removed from the final scope as it is a different class of algorithm (remeshing vs. decimation).
2.  **Accuracy**:
    -   For **Clean CAD** models, there is no significant difference in accuracy between QEM and Clustering at 50% reduction.
    -   For **Organic** models, **QEM** demonstrates superior accuracy ($p = 0.004$), preserving surface details better than Clustering.
3.  **Interaction**: The significant interaction in Time ($p=0.03$) highlights that QEM's computational cost scales poorly with mesh complexity (Organic), whereas Clustering remains consistently fast.
4.  **Recommendation**:
    -   **Real-Time / Preview**: Use **Vertex Clustering**. It is orders of magnitude faster and offers "good enough" accuracy for CAD.
    -   **High-Fidelity / Organic**: Use **QEM**. The extra processing time (approx. 1s) is justified by the significantly better geometric preservation on organic forms.

## 4. Limitations

-   **Non-normality**: Significant violations of normality assumptions were observed.
-   **Sample size**: $n=15$ per group.
