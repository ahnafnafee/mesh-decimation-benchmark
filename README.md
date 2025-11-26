# Mesh Decimation Benchmark

![Python](https://img.shields.io/badge/python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![PyMeshLab](https://img.shields.io/badge/PyMeshLab-2022.2-orange?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Research_InProgress-yellow?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

> **A rigorous statistical comparison of mesh decimation algorithms (QEM vs. Vertex Clustering) using Python and PyMeshLab.**

## 🚀 Overview

This project provides a comprehensive benchmark of 3D mesh simplification algorithms. It automates the process of decimating dataset models, measuring performance metrics (Wall-clock time & Hausdorff Distance), and performing rigorous statistical analysis (ANOVA, Welch's T-test) to determine the optimal trade-off between speed and geometric fidelity.

**Key Findings:**

-   **Vertex Clustering**: ⚡ **100x Faster** and **Robust**. Best for real-time previews and extreme decimation (90%), where it maintains stable error rates compared to QEM.
-   **Quadric Error Metrics (QEM)**: 💎 **High Fidelity (at 50%)**. Preferred for moderate reduction, but geometric error spikes significantly on CAD models at 90% reduction.

## Clone the repository

```bash
git clone https://github.com/ahnafnafee/mesh-decimation-benchmark.git
cd mesh-decimation-benchmark
```

## Install dependencies using uv

```bash
uv sync
```

## 🚦 Usage

### 1. Prepare Dataset

Place your raw models in `raw_downloads/` or use the included script to fetch ModelNet40 samples.

```bash
uv run model_preprocessor.py
```

### 2. Run Benchmark

Execute the main experiment runner. This will decimate meshes and record metrics.

```bash
uv run experiment_runner.py
```

### 3. Analyze & Visualize

Generate the statistical report and plots.

```bash
uv run data_analysis.py
uv run generate_presentation_figures.py
```

## 📈 Statistical Methodology

We employ a **Three-Way ANOVA** to analyze the interaction between _Algorithm_, _Mesh Type_, and _Decimation Level_ (50% vs 90%).

-   **Significance Level**: $\alpha = 0.05$
-   **Post-Hoc**: Tukey's HSD for pairwise comparisons (controlling for Type 1 error).

See [RESULTS.md](RESULTS.md) for the experiment report.

## 📄 License

This project is licensed under the MIT License.
