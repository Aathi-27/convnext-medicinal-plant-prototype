# Data audit, 13 November 2026
The old public project contains ten originals per class and a MobileNetV2 model.
It lacks Turmeric, Ashwagandha and Bacopa/Brahmi, substituting Aloe, Amla and mint.
Its image downloader lacks photo-license filtering and provenance. Do not reuse or
redistribute its images until independently cleared.

Current exact-taxon iNaturalist metadata query, research grade + photo CC0/CC-BY:
Tulsi 72; Neem 672; Turmeric 19; Ashwagandha 94; Brahmi 1,386; Bael 49;
Peppermint (hybrid taxon 181525) 89; Lemon Balm 1,176; Stevia 2; Catnip 1,969.
These are candidate OBSERVATION counts, not approved leaf images. Query total may
include descendant taxa or mixed photos; exact photo/taxon/content checks still apply.
Records fetched are marked pending and are not a training manifest.

Stevia also has 13 casual and 1 needs-ID photo-license-filtered observations;
Turmeric has 65 casual and 54 needs-ID. These weaker labels need independent botanical
review, not automatic promotion. Do not silently weaken training-label quality.

Candidate alternatives: Mendeley Medicinal Leaf, MED117, BDMediLeaves, Wikimedia.
MED117 has video-derived frames and cannot be split randomly across related frames.
Commons and NC State offer some Stevia references but no adequate independent
leaf-training set is established. Do not claim 500-800 images/class are available.

Sources:
https://github.com/Aathi-27/Medicinal-Plant-Classification-Project
https://www.inaturalist.org/api
https://api.inaturalist.org/v1/observations
https://meta-album.github.io/datasets/MED_LF.html
https://pmc.ncbi.nlm.nih.gov/articles/PMC9974419/
https://pmc.ncbi.nlm.nih.gov/articles/PMC10450835/
https://commons.wikimedia.org/wiki/Stevia_rebaudiana
https://plants.ces.ncsu.edu/plants/stevia-rebaudiana/
