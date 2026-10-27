# Real-data reproduction evidence

The separate Colab Tesla T4 check freshly trained all 12 fits on the prepared training inputs, selected checkpoints using validation data, and preserved the formal experiment. The training log runs from 23:16:58 to 23:21:38 UTC on 27 October 2026. The check also ran the default analysis, which reused existing predictions; it did not constitute a new independent test experiment.

`summary.json` records the runner's checks of code completion and protected artifacts. Receipts and `validation_comparison.json` retain full-precision losses. Reproduced receipt metadata and model SHA256 values match the formal source receipts. The public repository does not contain the corresponding model binaries; these evidence files are not a substitute for those binaries or the complete private submission.

The training cell correctly states that it does not evaluate the test split. Later analysis cells can reuse or reproduce formal test predictions according to the locked evaluation path. Do not interpret the training log as claiming that the whole notebook has never accessed test data.
