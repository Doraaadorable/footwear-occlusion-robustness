# Optional integrated two-stage submission builder

This utility assembles one notebook and one report from the exact verified blood submission and Handiprint GPU result archives. It preserves existing experiments and never retrains by default. It does not modify the earlier frozen course submission.

## Exact source versions

- Blood source: `MGSC673_Portable_Submission.zip` (download suffixes such as `(1)` do not matter), SHA256 `9254b2f258b1d72bdc7dc9b090a96b415ca24c11bcd3efa4b3afca3a08ee3620`.
- Handiprint source: `Handiprint_GPU_Reproduction_Results.zip`, SHA256 `eacbdcec1872a6b6c6420cc7af86ee74ed152927600dd94a19a3b77994a3bc3d`.

Both complete file inventories are verified before assembly. These source artifacts are not hosted in this public repository; the author retains them locally/privately.

## Use

Install the repository requirements in a compatible environment, retaining a matched torch/torchvision pair. Then:

```bash
python scripts/build_integrated_submission.py \
  --blood-zip /path/to/MGSC673_Portable_Submission.zip \
  --handiprint-zip /path/to/Handiprint_GPU_Reproduction_Results.zip \
  --output-dir /path/to/NEW_OUTPUT_FOLDER \
  --execute
```

The output directory may exist, but must not already contain `MGSC673_Integrated_Project`. Existing source archives, project directories and final ZIPs are not overwritten. Omitting `--execute` creates a candidate with cleared outputs, not a finished submission.

Default execution checks models, preserves the canonical split, recomputes Handiprint metrics and paired intervals from saved scores, and reuses locked blood predictions. No CNN fits are made. ImageNet ResNet18 weights may need an initial network download; exact SHA256 is checked. The output is `MGSC673_Integrated_Submission.zip` (about 20.6 MiB).

## Contents and limits

The merged notebook has 33 cells, including 18 code cells. It contains the full original Handiprint GPU implementation in a readable multiline source block with an isolated optional-training wrapper, the complete blood implementation, saved-artifact analysis, plots and an integrated report. The source-string approach prevents Handiprint global variables from overwriting blood-stage variables; its hash is checked before use. It is not an external API performing training.

The package contains all 308 processed blood images and the recorded Handiprint heads, predictions and GPU evidence. It does not contain the roughly 3.49 GiB original Handiprint TIFFs. Source DOI, exact manifest, filename identities, hashes and raw-data setup instructions are supplied for optional fresh Handiprint training. New wrapper assembly is not misrepresented as another completed training experiment; the original Handiprint GPU source was actually run, while integrated default execution reuses its artifacts.

Six report body pages plus one references page cover both stages. Masks, cross-medium provenance, CPU tasks, repeated test exposure, inferred links, collection confounding, ethics and AI assistance remain disclosed. The historical Handiprint transfer heads are not silently replaced by GPU reproduction heads.

## Validation

The builder was executed locally on the two original uploaded archives. All 18 code cells completed, the resulting ZIP inventory had 482 checked entries plus the inventory itself, and the exact ZIP was extracted into a separate directory and executed again. Immutable models, image bytes, manifests and review records remained unchanged. No new CNN training was done in these integration checks. The assembled optional wrapper has not itself undergone another real-data retraining run; the underlying original GPU implementation and earlier blood retraining adapter retain their completed-run evidence.

After the author generates the integrated version in Colab, inspect and retain that result before replacing an earlier submission. Instructor topic approval and permitted AI use remain governed by course policy.


## Review correction: provenance and descriptor controls
The reviewed builder replaces the obsolete archived-curve/checkpoint wording with the actual GPU-reproduction provenance, describes Handiprint grayscale conversion, brightness normalization, contrast stretching, cropping, padding and synthetic masks, and distinguishes these changes from blood RGB preparation.

The Stage 1 notebook displays the recorded S1 descriptor probes, and the report interprets geometry 93.75%, scan/session 78.13%, and combined 96.88% on unmodified images. The text does not infer CNN feature use from those baselines, does not assume the probes perform equally under heavy masking, and describes 80% masking only as nominal-severity extrapolation within a white-rectangle family. The author-facing notebook packaging reminder is removed.

For the exact previously generated integrated ZIP (SHA256 `fa4c9f522cd0e6a29de139485080fa473513d4a047b28add14e1781eb5606d77`), use `scripts/revise_integrated_submission.py --source-zip /path/to/MGSC673_Integrated_Submission.zip --output-dir /path/to/NEW_REVIEW_FOLDER --execute`. Keep that helper beside the updated builder. It extracts a new clone, verifies the source inventory, applies narrowly scoped corrections and runs default analysis without training. The original source ZIP is preserved; a new ZIP is written in the review output directory. Models, inputs, manifests and source prediction tables are checked unchanged. The revised archive has 483 checked entries plus its inventory, including revision notes, with 18 ordered code cells and seven report pages.
