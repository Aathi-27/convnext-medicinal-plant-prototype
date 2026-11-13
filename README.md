# ConvNeXt medicinal plant prototype
Status: development prototype, not a completed classifier. Experimental full ConvNeXt-Tiny fine-tuning completed locally, but class failures prevent a reliable release. All ten medicinal records have partial source checks; most regional names are pending. Source and tests are pushed. The updated ten-plant knowledge library is live and visually verified on desktop and phone; live identification remains unavailable. See the work log and release checklist below.


## Preview

https://convnext-medicinal-plant-prototype.onrender.com/

Render Free may sleep after inactivity and take about a minute to wake. This is a UI/API preview, not a working plant identifier.

## What works locally
Approved green/ivory React UI, upload/camera file selection, image validation,
status/error/loading/result components, ten-species registry, API, source-linked
knowledge schema and genuine ConvNeXt training code. Missing weights fail closed.
No uploaded images are persisted by the application.

## Setup (Windows PowerShell)
1. Install Python 3.10 and a current Node LTS release.
2. `py -3.10 -m venv .venv`
3. `.\.venv\Scripts\Activate.ps1`
4. `python -m pip install -r requirements.txt`
5. `cd web; npm ci; npm run build; cd ..`
6. `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`
7. Open http://127.0.0.1:8000

Development UI: `cd web; npm run dev` proxies /api to localhost:8000.
Tests: install pytest and httpx, then `python -m pytest -q`.

## Data and training gate
`python scripts/audit_inaturalist.py` only retrieves licensed-photo metadata.
Research grade is not confirmation that a picture shows a clear leaf. Every candidate
requires content/label review, attribution, grouping and duplicate checks before training.
The collector accepts photo-specific CC0/CC-BY only. Existing legacy images are NOT
approved just because their repository comments claim open licensing.

The report's classes are Tulsi, Neem, Turmeric, Ashwagandha, Bacopa monnieri/Brahmi,
Bael, Peppermint, Lemon Balm, Stevia and Catnip. No substitutions are approved.
Train after reviewed CSV exists: `python training/train.py --manifest data/reviewed.csv --out artifacts/training`.
GPU training environment: requirements-train.txt; install CPU/GPU torch wheels as appropriate.
No accuracy guarantee. Keep test data untouched until model/threshold selection is frozen.

## Hosting proposal
The UI/API preview is on Render Free. Trained ONNX inference has not yet been deployed or validated there.
512 MB memory and idle cold starts apply. See docs/runtime-benchmark.json for LOCAL
UNTRAINED architecture sizing only. Never use that benchmark model for identification.
No AWS is required. No paid upgrade is authorized.

## Known incomplete work
Dataset coverage/content review; trained checkpoint; held-out evaluation; ONNX parity;
calibration/rejection threshold; medicinal record curation; in-app crop control; production
security/load tests; deployment/account verification.
"Leaf study" remains a placeholder display name. Hero art is illustrative, not a specimen.

## Internal pilot, not released identification

A small frozen-feature ConvNeXt-Tiny baseline was trained to exercise the pipeline, not to reproduce report accuracy. See `docs/pilot-evaluation.json` for exact small-sample results and limits. It is not installed in the live service. The manifest uses community labels and provisional visual content screening, not expert botanical verification.

To reproduce from the repository root: install training dependencies; `python scripts/fetch_pilot_images.py`; then `python training/pilot_frozen_features.py --manifest data/pilot-manifest.json --out artifacts/pilot`. Images keep their individual CC BY-SA4.0 terms and attribution. No checkpoint is published. Full fine-tuning, more data and external validation remain pending.


## Expanded full-fine-tuning experiment (not deployed)
532 visually screened community-labeled originals, not expert-certified. Contributor-grouped splits: 326 train,85 validation,65 new internal test,56 previously used pilot test. Full pretrained ConvNeXt-Tiny,10 epochs, batch1, best validation-loss checkpoint epoch9. New internal test53/65; Tulsi0/3, Bael2/4 and Catnip2/4 expose serious limitations. This is not an external phone benchmark or report-accuracy reproduction. See docs/finetune-evaluation.json and docs/finetune-history.json. The old56-image test is not untouched. No checkpoint is installed in production.

Reproduce: `python scripts/fetch_experimental_images.py`, then `python training/finetune_experiment.py --manifest data/expanded-manifest.json --out experimental-run --epochs-this-run 1`. Repeat bounded runs for10epochs, then evaluate once with `python training/evaluate_experiment.py --manifest data/expanded-manifest.json --checkpoint-dir experimental-run`. Holdouts must not drive tuning.

All ten knowledge records now offer partial source-linked educational notes through the Plant library independently of predictions. Traditional uses are not clinical endorsements. No dosing instructions. Names not verified remain blank.


## Work log, problems and current limits
This log describes work actually performed, not a claim of project completion.

1. **Scope and architecture.** Matched the Phase I report's exact ten species. The older repository used a different model and lacked classes, so it was left untouched and a separate public repository was created. The architecture here is torchvision ConvNeXt-Tiny.
2. **Interface and API.** Built the approved green/ivory desktop/phone interface, upload/camera file selection, safe image decoding, status/error handling and knowledge endpoints. Inspected real desktop/phone renders, including the later knowledge library. Ten core/API tests and the TypeScript/Vite build pass locally.
3. **Free preview.** Deployed on an existing-account Render Free service in Singapore, not AWS. No paid compute or upgrade used. Tested public health/species endpoints and browser upload/Analyze/error flow. Free instances can sleep; the UI explains delays. Live model_ready=false until a defensible model release. Existing unrelated services were not changed.
4. **Missing original dataset.** The original report dataset was unavailable. Investigated open sources rather than treating old augmented images as clean originals. GBIF Stevia results were dominated by herbarium sheets, unsuitable as phone-photo test data. Pl@ntNet exact-species galleries supplied richer candidate pools; iNaturalist supplemented Bacopa. Candidate totals were never counted as reviewed training originals.
5. **Rights and review.** Retained per-photo authors, observation IDs, source URLs, licenses and SHA256 hashes. Visually excluded distant, flower-only or ambiguous photos. Initial346 candidates yielded258 provisional leaf-suitable photos. Expanded screening produced532 originals in the internal experiment. Screening is leaf-content review, not botanical expert certification. Images are not committed. Exact/dHash duplicate checks and contributor grouping reduce leakage but do not prove its absence.
6. **Pilot.** Trained a linear head on frozen genuine pretrained ConvNeXt features. The258-photo pilot had44/56 correct on a tiny internal test. This was not full fine-tuning or report-accuracy reproduction and was never installed as the public classifier.
7. **Full fine-tuning and memory failure.** Full ConvNeXt-Tiny training initially exceeded available memory at batch8 and was stopped. Batch1 completed10epochs locally. The best validation-loss checkpoint was epoch9. New65-image internal holdout:53correct. Tulsi0/3, Bael2/4, Catnip2/4 show serious failures despite the aggregate score. Old56-image test is already used and is not a fresh benchmark. Checkpoints remain private experimental artifacts. No external expert-labeled phone benchmark or calibrated confidence threshold exists yet.
8. **Knowledge safety.** Added partial source checks for all ten records with citations, traditional-use/evidence distinctions, plant-part/preparation caveats and safety notes. No dosing instructions or treatment promises. Brahmi naming ambiguity is explicit; unverified regional names remain blank. Added a browsable library so knowledge does not depend on a model prediction.
9. **Publishing route.** Browser root ZIP upload failed with HTTP400. A repository-scoped checksum-verified source-import workflow provided a working transfer route without new credentials. Replace this temporary source bundle with ordinary CI after source updates settle. Source import success is not the same as Render deployment success; each is checked separately.

### Release checklist still open
- Review weak-class labels and expand diverse original photos.
- Establish a new external phone-photo benchmark, not another tuned internal split.
- Re-train only after data changes are frozen; report class-level failures.
- Export ONNX, verify PyTorch/runtime parity and measure inference memory on the free-tier budget.
- Set and validate rejection/uncertainty behavior; closed-set softmax is not open-world identification.
- Verify model/media licensing before distributing weights.
- Deploy a justified checkpoint and test the full photo-to-result-to-knowledge flow.
- Complete regional-name/source review and optional crop controls. Automatic segmentation is not implemented.

The README is a running record and will be reconciled with the final live state. No93.2% accuracy,500-800images/class or2.5-hour training claim is reproduced here.


## Dataset snapshot delivery
`data/dataset-v0.3/` contains the627-photo experimental snapshot manifest, per-photo attribution/licenses and dataset card.95new training-only additions target weak classes; prior holdout rows stay unchanged. This snapshot is not the final expert-validated dataset. The versioned release packages exact medium-resolution source bytes with credits and SHA256 checksums; no paid LFS. `python scripts/package_dataset.py` rebuilds from public source URLs and fails if bytes change. Distribution uses three small ZIPs; extract all into one folder. Existing test/new_test splits are already-read development history, not a new final benchmark.

Live library verification: all10 partial records can be opened independently of prediction. ONNX engineering smoke:10validation photos had matching PyTorch/runtime top1 with worst absolute logit difference1.91e-6; runtime-only local peakRSS~224MiB. This is not test accuracy, calibration, or a Render memory/latency measurement.

Additional problems: the existing-file web editor duplicated a large source-transfer payload, causing a workflow failure. A fresh checksum-verified file transferred correctly, then removed the temporary files. Browser release asset upload did not accept files, so a reproducible manifest-only packaging workflow is used instead. Scientific release gates were not relaxed to hide publishing or class failures.


## Verified dataset release and additional generalization audit
The experimental dataset is now downloadable: https://github.com/Aathi-27/convnext-medicinal-plant-prototype/releases/tag/dataset-v0.3-experimental . All three public ZIPs and SHA256SUMS were downloaded again. Every archive checksum and all627image hashes matched. Each part includes attribution, licenses and the dataset card. Extract all three into one folder. See docs/dataset-v0.3-delivery-verification.json. This is an experimental research snapshot, not an expert-validated final dataset.

Development v3 used421training photos, frozen-feature head initialization followed by8epochs of full fine-tuning (backbone1e-6, head2e-5, batch2). Best development-validation-loss checkpoint was epoch8;70/85correct on reused validation. This is development feedback, not new test accuracy. See docs/development-v3-evaluation.json and history.

A subsequent new-observer audit exposed substantial generalization failure:57/99correct across9represented species. Selection was frozen before prediction inspection; contributors already present in the development dataset were excluded, and exact/conservative dHash checks found no accepted duplicates. However, cross-platform photographer aliases remain unresolved. iNaturalist is already represented in training, so this is not a fully independent source benchmark. No suitable new Stevia leaf photo was available in this eligible pool. Do not present57.6%as ten-class model accuracy. These99photos are kept out of training, but the audit is now read and must never be described as an untouched final benchmark.

Class outcomes: Tulsi5/7, Neem9/12, Turmeric7/8, Ashwagandha13/14, Brahmi11/11, Bael2/4, Peppermint2/13, Lemon balm4/17, Catnip4/13, Stevia not represented. All labels remain community labels, not independent expert botanical certification. Images include varied backgrounds and some flowers; this is not a user-phone benchmark. The poor mint-family outcomes block classifier release. Predictions remain disabled rather than exposing unreliable outputs. See docs/fresh-observer-audit.json and its frozen-manifest record.

Next scientific work: more varied leaf-centered training data and label review, mint-family error diagnosis, genuinely independent ten-class phone-photo evaluation, and calibrated rejection for unknown/poor-quality inputs. Training more epochs alone does not solve evidence gaps. No live classifier,93.2%accuracy or final dataset completion is claimed.


## Experimental full flow (local engineering check, not public release)
A real v3 ONNX checkpoint now supports local photo upload → ranked research candidates → explicitly selected species notes. Experimental mode is opt-in (ALLOW_EXPERIMENTAL_MODEL=1), always returns uncertain and never treats a softmax score as confirmed identity. Species notes remain hidden until the visitor selects a candidate; that choice is not botanical verification. No treatment or ingestion is recommended. Real API/browser tests passed and desktop/phone pixels were inspected without horizontal overflow.15tests pass locally and the frontend builds. Code publication does not change the existing live service. See docs/experimental-full-flow-smoke.json.

Hosting plan changed to AWS at the user's request. No new resources or charges have been approved or created by this implementation work. The existing Render preview is retained. Current local ONNX runtime-only peakRSS274032KiB (~268MiB), median inference0.078s over10sequential images. These are local engineering measurements, not accuracy or AWS measurements. Plan capacity with OS/container headroom and measure the actual host before commitment. See docs/experimental-deployment.md.

Checkpoint distribution is separate from source/data distribution. The model is initialized from TorchVision ImageNet-1K weights, whose official documentation warns that pretrained terms can differ from code licensing. No blanket commercial/redistribution clearance or permissive weight license is claimed. Current v3 artifact remains local. A checksum-pinned HTTPS installer is available for an explicitly supplied approved model source; it has no default public model.
