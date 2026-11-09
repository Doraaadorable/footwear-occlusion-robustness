# Limitations

- **Two shoe styles.** Each class is a single style (Adidas Seeley, Nike Zoom Winflo 4), so the task is to tell two sole designs apart. Results say nothing about recognising brands or individual shoes.
- **Small, reused test set.** 16 test pairs, 8 per class; one misclassified pair moves balanced accuracy by several points. These pairs were examined before the occlusion experiments and shortcut controls were designed. The occlusion-generalisation families and levels were fixed before that run.
- **Occluder-specific augmentation.** The +41.25 pp gain at 80% masking holds for the white rectangles used in training. It disappears for blobs and stripes and reverses under heavy noise (−35.0 pp); see [occlusion generalisation](../experiments/occlusion_generalization/).
- **Mask level versus tread removed.** At the 80% level, rectangles remove about 91% of the impression's ink and blobs, stripes and partial-contact masks 80–83%, so families are compared at equal box coverage, not equal ink loss.
- **Shape cues.** Crop geometry predicts the class at 93.75% on Handiprint, because aspect-preserving resizing keeps the outsole's shape. Moving a toe or heel fragment does not change accuracy, so fragment position is not the cue; fragment width was not varied.
- **Blood-stage confounding.** The collection suffix alone predicts the class perfectly in the blood data, so within-blood accuracy (64/64) cannot be credited to tread. Handiprint-to-blood transfer (71.88%) is the informative blood-stage result.
- **Blood-stage crops.** Training crops were manually reviewed regions of interest; validation and test crops came from a separate workflow.
- **Inferred identities.** Seven blood pair identities (9, 70, 76, 79, 114, 120, 158) are inferred from metadata; `tables/metrics.csv` reports results with and without them.
- **Synthetic corruption.** Every occluder and degradation is simulated; none reproduces crime-scene conditions.
- **Reproducibility.** The Handiprint stage reproduces from public sources. The blood stage needs a prepared-input bundle that is not public.
