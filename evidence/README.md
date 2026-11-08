# Blood-stage retraining evidence

On 27 October 2026 all 12 blood-stage fits (RGB at learning rates 0.001 and 0.01, grayscale and RGB + occlusion at 0.01; seeds 0–2) were retrained from the prepared training inputs on a Colab Tesla T4, with checkpoints selected on validation data. The training log runs from 23:16:58 to 23:21:38 UTC. The run then executed the default analysis, which reuses saved predictions, so it is a reproducibility check rather than a new test experiment.

- `summary.json`: run completion and confirmation that saved artifacts were not modified.
- `rgb_*.json`, `gray_*.json`, `rgb_occlusion_*.json`: per-fit receipts with full-precision validation loss and model SHA-256.
- `validation_comparison.json`: reproduced versus saved validation losses (all 12 identical).
- `execution_log.txt`, `reproduction_training_log_*.txt`: raw logs, kept unedited. They name the notebook file as it was called at the time.

The model binaries are not in the repository, so these files document the check; they cannot replace the binaries. The training cell does not evaluate the test split; later analysis cells reuse the saved test predictions.
