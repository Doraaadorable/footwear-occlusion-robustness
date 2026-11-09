# Dataset attribution and modifications

Source: Tibben, A., Carriquiry, A., & McGuire, M. (2023). *ShoeCase: A data set of mock crime scene footwear impressions*. Iowa State University. https://doi.org/10.25380/iastate.22814438.v1

Dataset license: Creative Commons Attribution 4.0 International (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/, as listed on the dataset record (checked 27 October 2026).

Changes to the selected blood-on-tile images: manually selected RGB crops, EXIF orientation handling, aspect-preserving resizing to 224 pixels and centred white padding. Grayscale versions are generated from the same crops. Image hashes and pair mappings are kept in the blood-stage input bundle.

The blood subset has 308 images of 77 pairs (180 training, 64 validation, 64 test), with pair 81 excluded.

`splits/split_manifest_final.csv` is derived from the ShoeCase metadata (file names, dates, shoe sizes and image hashes) with this project's pair audit and train/validation/test assignment added. It is shared under CC BY 4.0 with the attribution above.

Redistributed derivatives carry this attribution, the DOI, the license link and this list of changes. The repository itself contains code, aggregate results, training receipts and the split manifest, and no images or model weights.
