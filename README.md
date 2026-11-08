# Footwear Occlusion Robustness

**Research focus:** How robust is footwear-impression classification when part of an impression is missing or the recording medium changes—and can collection artifacts explain high scores?

This two-stage study uses related [ShoeCase](https://doi.org/10.25380/iastate.22814438.v1) Handiprint and synthetic-blood impressions to examine **occlusion robustness, cross-medium transfer, and shortcut learning**. It compares two specific shoe styles (Adidas Seeley and Nike Zoom Winflo 4); it is **not** a general brand-recognition or forensic-identification system.

### Key findings at a glance

| Investigation | Observed result | Interpretation |
| --- | --- | --- |
| **Severe occlusion (Handiprint)** | At 80% crop-area masking, original CNN balanced accuracy: **53.75%**; occlusion-augmented model: **95.00%** (**+41.25 percentage points**) | Exploratory evidence that augmentation improved robustness under the tested synthetic masking setup |
| **Blood-on-tile classification** | Three blood-trained ResNet18 variants each classified **64/64** held-out images correctly | High performance on this particular, previously examined test set—not evidence of reliable generalization |
| **Collection-artifact controls** | Collection-suffix baseline: **100%** balanced accuracy; area-and-brightness baseline: **79.69%** | Nuisance information can be predictive; perfect CNN accuracy alone does not establish tread-specific learning |
| **Cross-medium transfer** | Original Handiprint model on blood impressions: **71.88%** balanced accuracy | A change in recording medium remains an important evaluation challenge |

**Main takeaway:** Accuracy is only part of the story. Pair-aware splitting, stress tests, and nuisance-feature baselines are necessary to interpret what a classifier may have learned. These are exploratory results from related shoe pairs with repeated test exposure, not confirmatory forensic evidence.

### Explore the project

- [Handiprint GPU experiment and robustness curve](experiments/handiprint_gpu/)
- [Blood-stage result figure](assets/test_balanced_accuracy.svg) · [Full metrics](tables/metrics.csv) · [Experiment decision log](tables/experiment_decision_log.csv)
- [Data access and reproducibility](docs/DATA_ACCESS.md) · [Limitations](docs/LIMITATIONS.md) · [Public verification checks](#public-verification-no-private-data-required)
- [Integrated course-submission workflow](docs/INTEGRATED_SUBMISSION.md) (private package; not distributed here)

### Research stages

1. **Handiprint occlusion robustness:** completed GPU reproduction, masking-severity evaluation, and an occlusion-augmentation comparison. [Experiment details](experiments/handiprint_gpu/).
2. **Synthetic-blood cross-medium extension:** frozen-feature ResNet18 variants and comparison baselines, with attention to collection confounds. The public repository separates the stages; the reviewed course submission integrates them.

The two stages use **related shoe pairs, not independent populations**.

## Data and experimental design
- 312 downloaded blood-on-tile images, representing 78 candidate shoe pairs rather than 312 independent shoes.
- Pair 81 excluded under the original split: 308 eligible images, 77 pairs.
- Training: 180 images / 45 pairs; validation and test: 64 images / 16 pairs each.
- Both sides, full/partial impressions and related media from a pair stay in one split.
- Frozen ImageNet ResNet18 with a trained linear head: RGB, grayscale and RGB with occlusion augmentation; seeds 0, 1 and 2. HOG and legacy Handiprint models provide comparisons.

## Blood-stage findings

![Observed test balanced accuracy](assets/test_balanced_accuracy.svg)

The three blood-trained ResNet variants each classified all 64 test images correctly. HOG achieved 92.19% balanced accuracy; the original Handiprint model transferred to blood achieved 71.88%. A collection-suffix baseline also achieved 100%, and an area-plus-brightness baseline achieved 79.69%.

These are exploratory results from a small, previously examined test population. Perfect scores do not demonstrate tread-specific learning, equivalence between methods, or reliability on new collection conditions. See [limitations](docs/LIMITATIONS.md).

Detailed numbers: [aggregate result tables](tables/metrics.csv). Experiment history: [decision log](tables/experiment_decision_log.csv).

## Current course-submission version

The current frozen submission is the **reviewed two-stage `MGSC673_Integrated_Submission.zip`**, including the provenance correction and qualified Handiprint descriptor-probe interpretation. It supersedes the earlier blood-only Portable ZIP and the first integrated ZIP.

The reviewed package contains one notebook (33 cells, including 18 sequentially executed code cells), a six-page report body plus one references page, 308 processed blood inputs, recorded Handiprint GPU artifacts, both stages' evidence, and `REVISION_NOTES.json`. Its checksum inventory has 483 entries, plus the inventory file itself. The report preserves the geometry-probe caveat and limited mask-severity extrapolation; original models, predictions and pair splits are unchanged.

The submission notebook is `MGSC673_Integrated_Project/MGSC673_Project.ipynb`; its report is `MGSC673_Integrated_Project/reproduced_analysis/report/MGSC673_Footwear_Report.pdf`. Raw Handiprint TIFFs remain external, with access and identity-verification instructions. The final ZIP is retained privately and is not hosted here. See the [integration and review workflow](docs/INTEGRATED_SUBMISSION.md).

## Public blood-stage notebook and legacy reproduction bundle

The following instructions apply to the earlier blood-stage public notebook and Portable bundle. For the current two-stage submission, follow the integrated package's own README.
This is the code-and-results repository intended for public presentation, not the self-contained course submission. Source and derivative images, model weights, review archives, private manifests and image-bearing outputs are not included in the current code-and-results release. The author supplied the ShoeCase dataset record’s Licence field as CC BY 4.0; see [data provenance](docs/DATA_PROVENANCE.md). Public code alone cannot reproduce the numerical results without the private artifacts. No missing images are downloaded automatically.

1. Install `requirements.txt` in a compatible Python environment. GPU is recommended for optional fresh training; default execution reuses saved formal models.
2. Obtain the private reproduction bundle through an authorized channel. Its required layout is documented in [DATA_ACCESS.md](docs/DATA_ACCESS.md).
3. Set `FOOTWEAR_ANALYSIS_BUNDLE` to the extracted `MGSC673_Portable_Project` directory before running the notebook. Start Jupyter from the configured environment.
4. Open `notebooks/MGSC673_Project.ipynb` and run all. Keep the environment variable `FOOTWEAR_RUN_TRAINING` unset for the default mode. A first run can download the approximately 45 MB public ImageNet backbone and verifies its hash.

The final bundle adapter was independently exercised on the real prepared data using a Tesla T4 on 27 October 2026. All 12 fits were freshly trained; the validation losses and model SHA256 values matched the archived formal receipts exactly. The executed run completed 14 code cells. See the [full training log and receipts](evidence/reproduction_check/) and [validation comparison](evidence/reproduction_check/validation_comparison.json). This is a reproducibility check, not a new independent experiment or evidence of generalization across hardware. Fresh fits write separately and do not replace formal models.

## Status
- Completed: original GPU experiments; portable-bundle verification; timestamped stdout/stderr logs; real-data GPU retraining verification; final default execution and package-integrity checks.
- The reviewed two-stage Integrated ZIP is the current frozen course submission. Earlier Portable and first-integrated ZIPs are backups, not additional submission versions.
- Completed additionally: [Handiprint GPU reproduction](experiments/handiprint_gpu/), including severe-mask results and occlusion-augmented heads.
- Not implemented: a new **blood-stage** occlusion-strength scan, unfreezing comparison or Grad-CAM study.

## Public verification (no private data required)

From the repository root, run the following checks with Python 3. These use standard-library modules only and do **not** require installing the ML dependencies:

```bash
python scripts/check_notebook.py
python scripts/check_evidence.py
python scripts/check_handiprint_gpu.py
```

| Check | What it verifies | What it does not verify |
| --- | --- | --- |
| `check_notebook.py` | Public blood-stage notebook code parses and code-cell outputs are cleared | Notebook execution, data availability, or model accuracy |
| `check_evidence.py` | Published blood-stage training receipts and validation-loss comparison metadata agree | Fresh training, binary checkpoint integrity, or independent test performance |
| `check_handiprint_gpu.py` | Published Handiprint metadata, paired-difference table arithmetic, and public notebook syntax/output hygiene | Fresh GPU execution, source-data identity, or generalization |

The published receipt checks use assertions over archived records, not cryptographic verification of unavailable model binaries. The private course submission retains executed outputs and the full report. To rerun the underlying experiments, follow [data access](docs/DATA_ACCESS.md) and the [Handiprint GPU stage](experiments/handiprint_gpu/); CUDA and the authorized inputs are required for the latter.

## Dataset attribution
Dataset: Tibben, Carriquiry & McGuire (2023), *ShoeCase: A data set of mock crime scene footwear impressions*, https://doi.org/10.25380/iastate.22814438.v1.

No open-source license is assigned in this initial repository; upstream data and model rights are separate.
