# Hosting, development status
AWS is out of scope for this prototype. Free one-day deployment is the target.
Preferred trial: Render Free, ONNX inference only, single worker and serialized image
preprocessing/inference. Server image limit 10 MB and 10 megapixels. No uploaded
image is persisted. This is not a production medical service.

Local UNTRAINED architecture-only benchmark: ONNX 106.0 MiB; model process peak
207.7 MiB RSS. API + ONNX + decode of a 3000x3000 JPEG peaked at 322.8 MiB.
These figures do not establish hosted latency or model accuracy. No trained model
is deployed. More comprehensive peak-memory/load testing remains required.

Render Free: 512 MB RAM; idle sleep after 15 minutes, about a minute to wake;
750 free workspace instance hours/month. Verify workspace usage before deployment.
Vercel Python: standard 500 MB uncompressed bundle, Hobby 2 GB memory; large function
beta exists. Cloudflare Workers Free: 128 MB memory / 10 ms CPU, not suitable for
this server-side ConvNeXt process. It can serve a separate static frontend.

https://render.com/docs/free
https://render.com/pricing
https://vercel.com/docs/functions/limitations
https://developers.cloudflare.com/workers/platform/limits/
