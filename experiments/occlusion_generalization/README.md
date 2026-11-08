# Occlusion generalisation (planned run)

**Status: code and tests ready; not yet run on the real data. No results yet.**

The occlusion-augmented Handiprint heads were trained and tested with the same white-rectangle generator, where they gained +41.25 pp at 80% masking. This experiment asks whether that benefit carries over to occluders and degradations the heads never saw in training.

| Family | What it simulates | Levels |
|---|---|---|
| `rect_white` | training family (reference) | 40 / 60 / 80% of impression box |
| `blob_white` | irregular missing regions | 40 / 60 / 80% |
| `stripes_white` | banded missing contact | 40 / 60 / 80% |
| `partial_contact` | toe or heel end missing | 40 / 60 / 80% |
| `rect_dark` | dark occluder, not paper-coloured | 40 / 60 / 80% |
| `rect_texture` | substrate-like texture patch | 40 / 60 / 80% |
| `fade` | faint impression | 50 / 30 / 15% of ink contrast kept |
| `noise` | Gaussian noise | sd 0.1 / 0.2 / 0.3 |
| `blur` | Gaussian blur | sigma 1 / 2 / 4 px |

Each level uses 5 mask draws per image, shared by both models. The primary estimate is the augmented-minus-original balanced accuracy per family and level on the test split, with a 95% bootstrap interval that resamples whole shoe pairs within class. The run also records the realised fraction of ink removed, so accuracy can be plotted against tread actually lost. All results will be exploratory, because the test pairs were examined earlier.

## Files

- `occlusion_families.py`: corruption families, pair bootstrap and evaluation loop (NumPy/SciPy only).
- `Occlusion_Generalization_Colab.ipynb`: Colab GPU notebook. It locks the evaluation plan, re-runs the Handiprint stage to rebuild canvases and models, checks that the models match the published hashes and the published 80% result, runs every family on validation and test, and packages the outputs as a zip.
- `../../tests/test_occlusion_families.py`: unit tests on synthetic images, including a check that `rect_white` reproduces the training mask rule exactly.

## Run

1. Open the notebook in Colab with a GPU runtime.
2. Edit `PROJECT_ROOT` (and optionally `SAVED_RESULTS_DIR`) in Step 1. The data layout is in [docs/DATA_ACCESS.md](../../docs/DATA_ACCESS.md).
3. Run all cells (about 20–40 minutes). The last cell downloads a results zip.
