# Dataset sourcing status - 13 November 2026

No reviewed training manifest or trained classifier is complete. No report accuracy is reproduced.

## Stevia

The live Pl@ntNet gallery showed 563 observations, 727 images, and 573 tagged leaf images. These are source totals, not independent, approved leaf examples. A first batch contains 65 leaf-tagged images from 59 observations and 54 named authors. Photos include per-image CC BY-SA 4.0 links, author, observation ID and community vote count. Visual review finds some images unsuitable or ambiguous; community votes do not replace an expert botanical identification.

Source: https://identify.plantnet.org/es/prosea/species/Stevia%20rebaudiana%20(Bertoni)%20Bertoni/data/galleries
License: https://creativecommons.org/licenses/by-sa/4.0/

Keep image derivatives under their supplied licenses with attribution. Keep data separate from code. Do not publish an unrestricted model or image bundle without reviewing applicable licensing conditions. A larger source pool does not establish generalization.

GBIF returned 105 image-bearing Stevia records: 98 preserved specimens, five human observations, one material sample and one living specimen. Herbarium-sheet photos are not substitutes for phone leaf photographs and must not be mixed into a phone-image test set. GBIF also republishes some iNaturalist/Pl@ntNet records, so cross-source deduplication is required.

## Turmeric

PhilMedic provides an exact Curcuma longa folder with 100 image files under CC BY 4.0. Sample viewed shows a leaf on a plain background. The source captures front/back views of leaves; grouping and near-duplicate checks must precede any split. File count is not independent specimen count.

https://data.mendeley.com/datasets/tsvdyhbphs/1

## All classes

The iNaturalist collector retrieves photo-specific licenses and observation groups. First-photo selection often returns flowers, fruits, distant whole plants or mixed scenes. Research-grade labels alone do not establish leaf suitability or exclude misidentification. Downloaded candidates remain outside the public repository and are not approved just because they downloaded.

Next gates: content and label review, retain source/author/license, exact and perceptual duplicate checks, capture/observer-aware group split, class coverage, untouched external phone-image evaluation, rejection calibration, ONNX parity, measured hosted inference memory. Do not count augmentation as new original data.
