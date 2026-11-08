# Dataset attribution and modifications

Source: Tibben, A., Carriquiry, A., & McGuire, M. (2023). *ShoeCase: A data set of mock crime scene footwear impressions*. Iowa State University. https://doi.org/10.25380/iastate.22814438.v1

Dataset license: Creative Commons Attribution 4.0 International (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/, as listed in the License field of the dataset record (checked 27 October 2026). Re-check the record before redistributing any data.

Changes to the selected blood-on-tile images: manually selected RGB crops; EXIF orientation handling; aspect-preserving resizing to 224 pixels and centered white padding. Grayscale is generated from the same RGB crops for a controlled experiment. No perspective correction or color enhancement is claimed. Existing image hashes and pair mappings are retained in the private reproduction bundle.

Any derivative-data distribution must carry the source attribution, dataset DOI, license link and modification notice; retain applicable upstream notices and previous modification notices, and do not imply endorsement or impose additional restrictions inconsistent with the license.

The eligible subset consists of 308 images from 77 pairs (180 training, 64 validation, 64 test), after exclusion of pair 81 under the original split. These are related observations, not 308 independent shoes.

`splits/split_manifest_final.csv` is derived from the ShoeCase metadata (file names, dates, shoe sizes and image hashes) with this project's pair audit and train/validation/test assignment added. It is shared under CC BY 4.0 with the attribution above.

This notice concerns ShoeCase data. It does not grant a code license, relicense third-party model weights, or claim endorsement by the creators. The repository contains code, aggregate results, training receipts and the split manifest; it contains no images or model weights.
