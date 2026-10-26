# Data access and reproduction

Dataset record: https://doi.org/10.25380/iastate.22814438.v1

The dataset redistribution license has not yet been independently verified. The associated paper's license is not sufficient evidence of dataset permissions. This repository distributes no source images, derivative crops, third-party weights or review archives.

The default notebook requires an authorized private bundle with:

```
MGSC673_Portable_Project/
  input/
    gpu/                 # original manifests, model heads and receipts
    locked/              # original split, audit, annotation and preprocessing lock
    inputs/train/        # 180 exact RGB224 PNGs
    inputs/val/          # 64 exact RGB224 PNGs
    inputs/test/         # 64 exact RGB224 PNGs
    train_canvas_statistics.csv
  legacy/results_to_share.zip
  histories/             # original review handoff archives
```

Configure `FOOTWEAR_ANALYSIS_BUNDLE` with this directory's absolute path before kernel startup. For example, on Linux/macOS:

```bash
export FOOTWEAR_ANALYSIS_BUNDLE=/absolute/path/to/MGSC673_Portable_Project
jupyter notebook
```

The notebook checks original hashes and resolves images relative to the private bundle; immutable manifests retain original provenance paths. Missing private artifacts cause a clear stop. This repository is not a substitute for the authorized private course-submission bundle.

Keep formal artifacts read-only. Optional retraining belongs in a copy and produces `results/blood_reproduction_v1`. The current adapter still needs a full real-data validation; do not describe it as already verified.
