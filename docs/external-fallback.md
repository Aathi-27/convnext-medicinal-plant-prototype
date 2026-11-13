# Optional photo check

The research prototype retains the local ConvNeXt result and offers a second photo check. A top local score below0.70 makes the offer more prominent. This is a demo routing heuristic, not a calibrated confidence cutoff. A high local score can also be wrong, so the option remains available for every local result. The visitor must explicitly consent before each selected photo is forwarded. No photo is sent automatically.

The same Possible matches layout displays either result. An external result does not change the local model or combine its scores with an external AI self-rating. Notes are available only for an exact scientific-name match to the ten-species registry. Selecting notes never confirms the uploaded plant's identity.

External processing details identify Groq as the processor. The account was verified on the Free plan and inference-only Zero Data Retention was enabled with the owner's approval on2026-11-14IST. Usage metadata remains retained. This is not a blanket claim about every provider feature or future account settings. The general vision model is a preview, not a validated plant classifier. A single public turmeric-image smoke test succeeded; no accuracy claim follows.

## Safety and privacy

- Key is read from a server-only readonly mounted file, never frontend code or GitHub.
- POST `/api/external-suggestion` requires `consent=true`. Invalid images fail before a transfer.
- JPEG/PNG/WebP only,10MB/10megapixel limits; EXIF orientation applied, resized to at most1280x1280 and clean JPEG re-encoded. No EXIF/GPS, original filename, public photo URL or account identity is sent.
-3attempts/minute and60attempts/rolling24hours for the whole demo; SQLite stores timestamps only. Mount persistent state to avoid losing limits across restarts. Failed calls count.
-25second provider timeout, fixed model, bounded response, strict output parsing, safe generic errors. No provider response-body/request/secret logging. Failed external checks preserve the local result.
- Visitor photos and external responses are not saved to disk by the app. Reverse proxy access logs must not log request bodies.
- Model output is untrusted text, rendered as text by React, never executed or treated as authority. No treatment/ingestion guidance is requested.
- Public endpoint caps limit abuse, not production-grade authentication or capacity. Keep this short-lived demo low traffic.

Use `deploy/fallback-compose.yaml` with the existing compose file. Obtain the existing key through secure credential handling, place it outside the source tree with0600permissions, and set `GROQ_KEY_PATH` to that host path. Do not type or paste the value into a command, transcript, repository or message. Keep the original model mount and HTTPS proxy unchanged. Rollback: disable EXTERNAL_FALLBACK_ENABLED and restart the prior image; local predictions continue.

Sources: https://console.groq.com/docs/vision ; https://console.groq.com/docs/your-data ; https://console.groq.com/docs/rate-limits .
