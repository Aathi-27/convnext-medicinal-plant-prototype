# Dataset v0.4 EXPERIMENTAL development revision

690community-labeled, visually content-screened photos, not expert-certified or the original Phase I report dataset. Preserves all627v0.3rows and splits; adds63new mint-family photos,50train and13mint_dev_val. The frozen99-photo audit and every candidate/contributor in its collection pool were excluded from these additions. One proposed extra photo was excluded on a cross-species contributor split conflict, leaving63not64. At most one photo per new contributor, exact hashes and conservative dHash checks reduce leakage, not a guarantee. Cross-platform photographer aliases are unresolved.

Splits:471train,85reusedval,13mint_dev_val,65already-readnew_test,56already-usedtest. All validation now development feedback. No split here is a new final benchmark. Labels retain community attribution, no silent relabeling. All63accepted additions had live per-photo license/research-grade/exact-taxon/observer checks. Leaf visibility screening is not expert label verification. Some images include flowers/backgrounds. Source-shift bias remains.

Photos retain their individual CC0/CC-BY4.0/CC-BY-SA4.0 terms; see ATTRIBUTION.csv, LICENSES.md and manifest. Exact downloaded medium-resolution bytes, no pixel edits. The code license does not apply to photos. No medical identification, ingestion, treatment, endorsement or copyright clearance beyond the identified licenses is claimed.

Provenance sources: Pl@ntNet exact-species leaf galleries and iNaturalist research-grade observations, with per-photo source URLs and credits. New development URLs and observer groups are preserved in the manifest.

Training outcome: continuing v3for8epochs failed to improve the13-photo mint slice (4/13); a fresh frozen-pretrained-feature linear head reached8/13on reused development data, with Lemon balm1/4. Neither is independent test accuracy or release evidence. No final reliable model or final dataset completion is claimed.
