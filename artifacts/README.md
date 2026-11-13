No trained model is included yet. The API returns 503 instead of fake predictions.
The architecture-benchmark.onnx sizing artifact is UNTRAINED and must never be deployed.
A deployment model needs model.json with architecture, trained=true, file, sha256,
species_ids in registry order, a validation-derived confidence_threshold and version.
Store approved weights as an eligible GitHub Release asset, retain a SHA-256 manifest,
and test ONNX/PyTorch output parity before release. No benchmark-only artifact is valid.
