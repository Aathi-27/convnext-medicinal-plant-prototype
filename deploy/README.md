# Portable host preparation, not an AWS launch

This directory creates no AWS resources. Instance/product/region, credits, charges, storage, public IPv4, transfer, DNS/TLS and shut-down responsibilities must be approved against current account facts before provisioning. Do not use EKS, a NAT gateway, load balancer or a GPU for this small single-worker demo without a separate reason and cost approval. This is a proposed low-footprint layout, not a price quote.

Prerequisites: a suitable x86-64 Linux host with Docker Compose, at least1GiB total memory as a planning starting point, and the privately supplied verified model directory. Actual host memory/latency must be measured. Keep the existing working preview until the new full flow passes checks.

1. Clone the public source at the reviewed commit. Build with `docker compose -f deploy/compose.yaml build`.
2. Transfer the verified artifact and model.json using the chosen private authenticated route. Do not open an unauthenticated model-upload endpoint. Check the SHA256 on the host. No public checkpoint download exists by default.
3. Set MODEL_PATH to that local directory and run `docker compose -f deploy/compose.yaml up -d`. It binds localhost only. A separately configured HTTPS reverse proxy is required for public access. Do not open port8000 to the world.
4. Verify health reports model_ready=true and experimental=true. Upload a valid photo, confirm uncertain ranked candidates, and confirm no use notes are automatically attached before choosing a candidate. Check invalid/corrupt/oversized inputs and the phone layout. Confirm logs do not retain uploaded photos.
5. Measure real RSS, CPU, disk, start-up and sequential response times on the chosen host. Check the one-worker memory cap does not kill it. Keep traffic low; no production capacity claim is established.
6. Pin the reviewed image/artifact checksums. Document the public URL only after it resolves to the correct app over HTTPS. Roll back by stopping the new container and retaining the earlier preview; do not delete unrelated resources.
7. Track service running hours, storage/IP charges and credit expiry. Set an approved end time and clean-up route. Stopping a VM may not remove storage or IP charges. No credits are spent by these files alone.

Experimental mode is deliberately uncertain for every result. It is not calibrated rejection or reliable identification. A candidate click only selects educational notes; it does not authenticate the photographed plant. Never recommend use or ingestion based on the image. The failed generalization audit and weight-license caveats still apply.

The Compose proposal is source-inspected but has not been run with Docker or on AWS in this environment. It is not deployment proof. Provisioning remains pending the account/cost decision.
