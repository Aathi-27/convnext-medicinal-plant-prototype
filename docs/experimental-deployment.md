# Experimental deployment readiness

Local end-to-end test: real v3 ONNX prediction, explicit uncertain research candidates, manual candidate choice, source-linked plant-use notes. Notes do not establish identity or recommend consuming the photographed plant. Experimental mode cannot report a confident identification and requires ALLOW_EXPERIMENTAL_MODEL=1. Public preview has not changed.

Artifact: 111395786 bytes; SHA256 4f6ea859eab720f0dc6b8daaccfe6f85aaec61a422bae57f3b9a68b3a76b5eed. Checksum pinning is integrity, not scientific validation. Current artifact remains local. No public download URL is promised. scripts/install_model.py can install an explicitly provided HTTPS artifact and rejects changed bytes, unexpected filenames or excess size. It has no default remote model.

Hosting choice changed to AWS at the user's request. No new resources have been created for this version. Actual account credits, applicable services, rates and limits must be verified before a deployment plan is approved. Existing Render preview is retained. Inference requires CPU only, one worker and serialized model calls. Start capacity planning at1GiB RAM including OS headroom, then measure actual peak memory/latency. Earlier local ONNX-only memory measurements are not AWS benchmarks. No GPU or training host is required for serving.

Scientific blocker: development validation70/85does not override the failed57/99new-observer audit, which covers9species and lacks Stevia. All results remain research-only. A different host cannot fix accuracy.

Rights review: TorchVision code is BSD-3-Clause, but its official documentation explicitly says pretrained models may carry their own dataset-derived terms. This prototype initializes from ConvNeXt_Tiny_Weights.IMAGENET1K_V1, not SWAG or ConvNeXt V2. Do not imply the code license clears weights or apply a blanket permissive license to the checkpoint. No commercial-use clearance has been established. Review any redistribution against the educational research purpose and preserve upstream notices before publishing a model asset.

Sources checked:
- https://github.com/pytorch/vision
- https://docs.pytorch.org/vision/stable/models.html
- https://docs.pytorch.org/vision/stable/models/generated/torchvision.models.convnext_tiny.html
- https://github.com/facebookresearch/ConvNeXt
