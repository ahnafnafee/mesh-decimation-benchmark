# Mesh Simplification Experiment

This project compares three mesh simplification algorithms:

1.  **QEM (Quadric Error Metrics)**: Standard high-quality simplification.
2.  **Clustering**: Fast, vertex clustering approach.

## Setup

1.  **Install Dependencies**:

    ```bash
    uv pip install -r requirements.txt
    ```

    (Or ensure `pymeshlab`, `pandas`, `matplotlib`, `scipy`, `statsmodels` are installed).

2.  **Prepare Data**:
    -   Place raw ModelNet40 `.off` files in `raw_downloads/modelnet40`.
    -   Place raw Thingi10k `.stl` files in `raw_downloads/thingi10k`.
    -   Run the preprocessor:
        ```bash
        uv run model_preprocessor.py
        ```
        This cleans, re-orients, and converts models to `.obj` in `dataset/`.

## Running Experiments

1.  **Run the Experiment**:

    ```bash
    uv run experiment_runner.py
    ```

    This will:

    -   Apply all 3 algorithms to the models.
    -   Measure execution time (Wall-clock) and Geometric Error (Hausdorff Distance).
    -   Save results to `experiment_results.csv`.
    -   Save decimated meshes to `decimated_meshes/`.

2.  **Analyze Results**:
    ```bash
    uv run data_analysis.py
    ```
    This generates statistical analysis (ANOVA) and descriptive statistics.

## Generating Figures

To visualize the results and compare the wireframes/meshes:

```bash
uv run generate_figures.py
```

This will create composite comparison images in the `figures/` directory, showing the Original mesh alongside the output of QEM, Clustering, and Simple algorithms, with vertex counts.

### Custom Rotation

If you want to manually adjust the rotation angle for a specific model:

```bash
uv run custom_figure.py airplane_0004 --rot_x -30 --rot_y 45 --rot_z 0
```

-   `model`: Name of the model (e.g., `airplane_0004`).
-   `--rot_x`, `--rot_y`, `--rot_z`: Rotation angles in degrees.

This generates `figures/airplane_0004_custom.png`.

## Results

See `RESULTS.md` for the detailed report and findings.
