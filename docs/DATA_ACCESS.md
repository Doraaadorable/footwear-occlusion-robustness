# Data access and reproduction

Dataset record: https://doi.org/10.25380/iastate.22814438.v1

The author supplied the ShoeCase dataset record’s Licence field as CC BY 4.0. This permits sharing and adaptations subject to attribution and the other license terms; see DATA_PROVENANCE.md. The current code-and-results release still includes no images, third-party weights or review archives. Dataset licensing does not assign a license to project code or third-party model weights.

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

Keep formal artifacts read-only. Optional retraining belongs in a copy and produces `results/blood_reproduction_v1`. The final adapter completed a real-data Tesla T4 reproduction of all 12 fits. Logs, receipts and consistency checks are included in evidence/reproduction_check/. The frozen course submission contains the executed default notebook and report.
