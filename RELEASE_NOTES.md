# It Takes Two Android port — alpha13 (verified build)

This release is the latest verified It Takes Two port build, plus the 30 fps and 60 fps logs,
the source snapshot and the profile package.

## Verified build

- **APK:** `nx2android-v0.4.1-alpha13-it2-srgb.apk`
- **versionCode / versionName:** `32` / `0.4.1-alpha13`
- **SHA-256:** `3886fc7e95a04ce50a3c60ffd0b311c64dc6685174843a5c58a32afdc1cd5622`
- **Package:** `com.gjr.nx2androidx` (same signer as alpha12; installs over it)
- **No game data / keys included.**

## Test logs

- `IT2-30fps-alpha11-log.zip`: 467 s, 14,100 frames; frame p50 33.14 ms, GPU p50 12.71 ms.
- `IT2-60fps-alpha12-log.zip`: 373 s, 20,399 presents; frame p50 16.65 ms, GPU 8–12 ms.
- `IT2-60fps-alpha13-srgb-log.zip`: 417 s, ~21,200 frames; frame p50 16.6–16.7 ms, GPU p50
  10.2–11.1 ms; no `[RED]`, `VK_ERROR`, device lost or OOM. Application pool reached
  `3.00 GB / 3.21 GB`.

## Profile package

`nx2a-profiles-r2-it2.zip` — 185 profiles (184 original + `010092A0172E4000`), revision 2,
SHA-256 `1061681ded85736b64ceae635866004df1088926d30d72c9dd2ca685b6f28e6c`. Import it in the
app's Profiles environment; it is metadata only and does not raise the 3.21 GB `app_pool`.

## Known issue carried by this build

The alpha13 sRGB present shader is **not confirmed active**. The log line
`the surface offers no format 0 ...` shows `g_want == 0`; `present_thread` calls `present_one()`
without setting `im_meta_srgb`, so the new path falls back to the old blit. A follow-up build
needs to set `im_meta_srgb` from the image format (or call `present_window()`) before using the
shader. The port otherwise runs; this release does not claim sRGB correctness.

The source for all changes is in the repository tree; the upstream readme is preserved under
`docs/README-upstream.md`.
