# Data access and reproduction

Source dataset: Tibben, Carriquiry & McGuire (2023), *ShoeCase*, https://doi.org/10.25380/iastate.22814438.v1 (CC BY 4.0; see [DATA_PROVENANCE.md](DATA_PROVENANCE.md)).

This repository contains code, aggregate result tables and run receipts. It does not contain images, model weights or the canonical split manifest.

## Handiprint stage and occlusion generalisation

Download the Handiprint scans and `Handiprint_database.xlsx` from the dataset record, and arrange them as:

```
YOUR_PROJECT/
  data/
    Handiprint_database.xlsx
    split_manifest_final.csv     # canonical pair split, SHA-256 20f94282…3d11d
    Handiprint_images/           # paths must match matched_path in the manifest
```

The canonical split manifest is kept by the author; the notebooks check its SHA-256 and never draw a new split. Run instructions:

- Handiprint stage: [experiments/handiprint_gpu/README.md](../experiments/handiprint_gpu/README.md)
- Held-out occlusion families: [experiments/occlusion_generalization/README.md](../experiments/occlusion_generalization/README.md)

## Blood stage

`notebooks/blood_stage.ipynb` reads a prepared-input bundle with this layout:

```
BLOOD_BUNDLE/
  input/
    gpu/                 # saved GPU model heads, manifests and training receipts
    locked/              # split, crop annotations, audit table and preprocessing lock
    inputs/train/        # 180 prepared RGB224 PNGs
    inputs/val/          # 64 prepared RGB224 PNGs
    inputs/test/         # 64 prepared RGB224 PNGs
    train_canvas_statistics.csv
  legacy/results_to_share.zip   # earlier Handiprint weights used for the transfer test
  histories/            # crop-review archives, checked for record continuity
```

Point the notebook at it before starting Jupyter:

```bash
export FOOTWEAR_ANALYSIS_BUNDLE=/absolute/path/to/BLOOD_BUNDLE
jupyter notebook notebooks/blood_stage.ipynb
```

The notebook checks the locked hashes and stops with a clear message if an input is missing. Default execution reuses the saved heads. Setting `FOOTWEAR_RUN_TRAINING=1` refits all heads into `results/blood_reproduction_v1` without replacing the saved models; run that on a copy of the bundle. The 27 October 2026 GPU retraining check is recorded in [evidence/reproduction_check/](../evidence/reproduction_check/).
