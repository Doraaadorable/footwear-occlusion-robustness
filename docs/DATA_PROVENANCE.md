# Dataset attribution and modifications

Source: Tibben, A., Carriquiry, A., & McGuire, M. (2023). *ShoeCase: A data set of mock crime scene footwear impressions*. Iowa State University. https://doi.org/10.25380/iastate.22814438.v1

Dataset license: Creative Commons Attribution 4.0 International (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/ . Evidence: the project author supplied the dataset page’s Licence field in this project discussion on 2026-10-27. Automated retrieval of the dataset license field was unsuccessful; this records author-provided evidence, not a claim of independent retrieval. The Creative Commons license terms were checked directly.

Changes to the selected blood-on-tile images: manually selected RGB crops; EXIF orientation handling; aspect-preserving resizing to 224 pixels and centered white padding. Grayscale is generated from the same RGB crops for a controlled experiment. No perspective correction or color enhancement is claimed. Existing image hashes and pair mappings are retained in the private reproduction bundle.

Any derivative-data distribution must carry the source attribution, dataset DOI, license link and modification notice; retain applicable upstream notices and previous modification notices, and do not imply endorsement or impose additional restrictions inconsistent with the license.

The eligible subset consists of 308 images from 77 pairs (180 training, 64 validation, 64 test), after exclusion of pair 81 under the original split. These are related observations, not 308 independent shoes.

This notice concerns ShoeCase data. It does not grant a code license, relicense third-party model weights, or claim endorsement by the creators. The current repository release contains code, aggregate results and training receipts; no dataset or weights were added by this documentation update.
