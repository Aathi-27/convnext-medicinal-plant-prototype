# ConvNeXt medicinal plant prototype
Status: development scaffold, not a completed classifier. No trained or validated
checkpoint yet. Three medicinal records have partial source checks; remaining records and regional names are pending curation. The UI/API preview is deployed; identification remains unavailable until a trained and evaluated checkpoint passes the release gate.

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
