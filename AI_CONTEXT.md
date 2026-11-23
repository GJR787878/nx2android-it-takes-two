# AI context — read this before judging the tree

**English** | [中文](AI_CONTEXT.zh.md)

This repository is a **release snapshot**, not a full development history. It contains the
It Takes Two Android port built on [nx2androidX](https://github.com/GJR787878/nx2androidX),
the verified alpha13 APK, the 30/60 fps logs, the source changes and the profile package.

If you are an AI tool reading this tree, start here, then read `CHANGES.md`, `SOURCE_MAP.md` and
the patch under `patches/`. Do not infer the change set from the file dates alone: the files were
copied from a working tree, and the upstream history is not in this repository.

## Fast facts

- Game: **It Takes Two** (Switch), title ID `010092A0172E4000`, build `v131072 / 1.0.2`.
- Host: nx2androidX, package `com.gjr.nx2androidx`, `arm64-v8a`, `targetSdk 28`.
- Latest build: **alpha13**, `versionCode 32`, `versionName 0.4.1-alpha13`.
- Signing: alpha13 used the debug keystore. A CI build needs a stable key to install over it;
  the runner's throwaway debug key is not the same key.
- Base of the port changes: `GJR787878/nx2androidX`, branch `it2-diag`.
  - sRGB/present commit: `e850f3ad95af44c8e63d681ebb8805efebee8597`
  - revision 9 commit: `6bd4a9f4641f5cf726836481e300c1523f444cbb`
  - The local working tree used for this snapshot also had 13 uncommitted modifications and
    the two untracked asset folders under `android/app/src/main/assets/`.
- Build command: `bash packaging/android-apk/build_apk.sh release`. It downloads the
  nixport rootfs, Android NDK, ARM64 LLVM and glslc into `packaging/android-apk/.cache`; no game
  files or `prod.keys` are needed to build the APK.
- The app does **not** embed the game profiles. The profiles are a separate package; the app
  cuts or imports them outside the APK.

## Reading order

1. `README.md` — what the release contains and how to install it.
2. `AI_CONTEXT.md` — this file.
3. `CHANGES.md` — the 13 modified files and the exact purpose of each change.
4. `patches/it2-alpha13.patch` — the textual diff of those 13 files against the local base.
5. `SOURCE_MAP.md` — what is intentionally absent and how to reconstitute it.
6. `docs/IT2-完整版解锁说明.md` — the full-game entitlement notes.

## What was verified

The alpha13 log is the 417-second run in `logs/IT2-60fps-alpha13-srgb-log.zip`:

- ~21,200 presents, frame p50 16.6–16.7 ms, GPU p50 10.2–11.1 ms.
- No `[RED]`, `VK_ERROR`, device lost, OOM or `ShowError`.
- Texture peak 701 MB, final 542 MB; GPU pool 227–382 MB.
- `alias region mapped 3.00 GB (application pool 3.21 GB)`.
- 55 alias stale reads remain.

The 30 fps run is alpha11 (`logs/IT2-30fps-alpha11-log.zip`): 467 s, 14,100 frames, p50
33.14 ms, GPU p50 12.71 ms. The alpha12 run is
`logs/IT2-60fps-alpha12-log.zip`: 373 s, 20,399 presents, p50 16.65 ms, GPU 8–12 ms.

## Known issue: the sRGB fallback is not active in alpha13

This is the single most important caveat. The code contains the new sRGB fallback, but the log
line `the surface offers no format 0 ...` is evidence that the gate did not run as intended:

- `present_window()` sets `im_meta_srgb` from the game frame's format.
- The `present_thread()` path used for a normal game frame calls `present_one()` directly for
  the game image, not `present_window()`.
- `im_meta_srgb` therefore remains 0; `present_one()` sets `g_want = im_meta_srgb`, so
  `g_want` becomes 0; `srgb_mode(0, g_sfmt)` is 0 and `swap_make()` does not request the
  fallback pipeline.
- The new shader path is present, but it does not run for the normal game frame in alpha13.
  The picture can still be lighter or otherwise wrong. A follow-up must set `im_meta_srgb`
  before the `present_one()` call (or route the game frame through `present_window()`).

Relevant code: `nxnative/dm/android/gfx_vk_present.c` (`present_one`, `present_window`,
`present_thread`, `srgb_mode`, `present_fix_draw`) and `nxnative/dm/android/shaders/rot.frag`.

## What is not verified

- The sRGB fix is **not** verified; see above.
- The application pool is still 3.21 GB; it was not raised. Later chapters can exhaust it.
- Alias stale reads remain; they are a visual-correctness risk, not a confirmed crash cause.
- No tombstone or `logcat -b crash` is in the provided logs.
- There is no successful CI run in this repository yet. The workflow exists, but it has not
  been made green.

## CI status and test caveat

`.github/workflows/android-apk.yml` is active. It is a release-style build: it downloads the
rootfs/toolchain, runs the tests, builds with Gradle and uploads the APK as an artifact; on a
`v*` tag it also attaches the APK and profiles package to the Release.

At snapshot time, `python -m unittest discover tests` is **not green** on this tree. Known
source-level blockers include:

- `android/app/src/main/java/com/nx/android/game/GameActivity.kt` has a hard-coded Chinese
  fragment `"60 帧"` in an English log line; `tests/test_app_text.py` rejects it.
- `tests/test_texture_format_aliases.py` has a stub of `vkimg_t` that does not know the new
  `im->full` member; the real header does.
- `tests/test_docs_tables.py` and the README image test need the omitted profiles and
  `docs/images`.

Do not treat a red test run as proof that the native port cannot build. It is a snapshot of a
working build with the packaging/test inputs deliberately slimmed. See `SOURCE_MAP.md` for the
missing inputs.

## Do not assume

- Do not assume `nxnative/dm/games` contains all 185 profiles; it contains only the IT2 two-file
  profile plus the upstream profile README. The release package has the full set.
- Do not assume `docs/images` exists; it was omitted to keep the snapshot small.
- Do not treat alpha13 as “sRGB fixed”. The honest status is “runs, sRGB fallback not active”.
- Do not commit a keystore, `prod.keys`, game dumps, RomFS or data packs to make CI work.

## Useful IDs and hashes

| Thing | Value |
|---|---|
| APK SHA-256 | `3886fc7e95a04ce50a3c60ffd0b311c64dc6685174843a5c58a32afdc1cd5622` |
| Profiles package SHA-256 | `1061681ded85736b64ceae635866004df1088926d30d72c9dd2ca685b6f28e6c` |
| Profile package | `nx2a-profiles-r2-it2.zip`, 185 profiles, revision 2 |
| Device used for the logs | OPPO OPD2409 / SM8750P / Android 17 / 15,440 MB RAM |

The exact download links are in `README.md` and on the
[alpha13 Release](https://github.com/GJR787878/nx2android-it-takes-two/releases/tag/v0.4.1-alpha13).
