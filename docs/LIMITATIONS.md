# Interpretation and limitations

- **Two shoe styles.** Each class is one style (Adidas Seeley, Nike Zoom Winflo 4), so class is tied to style, shoe size distribution and collection conditions. Nothing here measures general brand recognition or forensic identification.
- **Small test set.** 16 test pairs (8 per class). One misclassified pair moves balanced accuracy by several points; intervals resample pairs, not images.
- **Test exposure.** The test pairs were examined before the severe-occlusion extension, the blood-stage models and the shortcut controls were designed. These results are exploratory, not confirmatory.
- **Matched train/test corruption.** The occlusion-augmented Handiprint heads were trained and evaluated with the same white-rectangle generator. The 80% level is only slightly beyond the 10–70% training range. The +41.25 pp gain shows benefit on that corruption; [held-out families](../experiments/occlusion_generalization/) test other occluders.
- **Mask size is not tread removed.** Mask percentages are the share of the impression box covered, not the share of tread removed. The occlusion-generalisation run also records ink coverage.
- **Shortcuts.** Crop geometry (93.75% on Handiprint), collection suffix (100% on blood), shoe size and brightness all predict the class. Aspect-preserving resizing keeps outsole shape visible. A successful nuisance baseline shows the information is available; it does not show which features the CNN uses.
- **Collection confounding in the blood data.** Because the collection suffix alone predicts the class perfectly, within-blood accuracy cannot be attributed to tread pattern. The Handiprint-to-blood transfer result (71.88%) is the more informative blood-stage number.
- **Different crop workflows.** Blood training crops were manually reviewed regions of interest; validation and test crops were prepared by a separate workflow.
- **Inferred identities.** Seven pair identities are inferred from metadata rather than verified: 9, 70, 76, 79, 114, 120 and 158. `tables/metrics.csv` reports results with and without them.
- **Perfect scores.** 64/64 correct with a degenerate bootstrap interval does not imply perfect population performance.
- **Archived Handiprint values.** The blood notebook reports the Handiprint severe-occlusion results from the Handiprint stage; the augmented Handiprint checkpoint was not transferred to blood.
- **Reproducibility.** Images, weights and the split manifest are not in the repository, so the results cannot be reproduced from this repository alone.
