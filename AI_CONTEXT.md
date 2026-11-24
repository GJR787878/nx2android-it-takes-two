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
- Baseline build: **alpha13**, `versionCode 32`, `versionName 0.4.1-alpha13`, SHA-256
  `3886fc7e...5622`.
- Latest CI build: **CI r2 clean-port**, same `versionCode 32` / `0.4.1-alpha13`, SHA-256
  `e64654d2...0303`; it adds the shader-table fix for a clean It Takes Two port.
- Signing: alpha13 and CI r2 use the same debug keystore
  (certificate SHA-256 `2224ed75eecc74c5e9ca4adedf94ab2ddb9e3c28b09e049fd09c88244111c3e0`),
  so the CI APK installs over alpha13. The keystore and its password/alias are repository
  secrets; no key is committed.
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
3. `CHANGES.md` — the 13 alpha13 changes, the clean-port fix, and the exact purpose of each.
4. `patches/it2-alpha13.patch` — the textual diff of those 13 alpha13 files against the local base
   (the clean-port fix is a 14th change, described in `CHANGES.md`).
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
- The test suite is still not green. The CI build workflow deliberately does not run it; a
  green APK artifact is not a green test suite.

## CI status and test caveat

This fork's `.github/workflows/android-apk.yml` is a working build, not a placeholder. A
`workflow_dispatch` run builds the payload and the APK and uploads `nx2android-android-apk`;
a `v*` tag attaches the APK and profiles package to the matching Release. Run
`45294935869` succeeded in 7m25s and produced a 259,504,735-byte APK with SHA-256
`e64654d297b9c008e6c741b833af9e329cfc67f88a5c0b0bcc196dc085100303`.

### Clean-port fix

The first CI APK built fine, but a fresh It Takes Two port stopped with `FileNotFoundError` on
`dm/games/010092A0172E4000/shader_map.tsv`: `split_shaders()` read the profile's shader tables
even though the repository profile has only `game.tsv` and `android.tsv`. Commit `70f4e38`
makes a table-less profile copy the split's `shader_map.tsv`, `shader_facts.tsv` and
`shader_pairs.tsv` as its first port's, and disables package reuse until those tables exist.
The shader split succeeds (32,118 shaders: 2,171 compute, 81 geometry, 24,779 pixel, 5,087
vertex). The fix is in the r2 APK (`ci-20261124-alpha13-r2`). A device run then completed all
nine stages with exit code 0 at `2026-11-24 07:53:06` (OPPO OPD2409, Android 17, 60 fps); its
text log is under `logs/it2-alpha13-r2-20261124-080056/`. The tables are written into the
per-port `dm/games` copy and removed by `drop_profile`, so every clean port still splits again.

The workflow does **not** run the tests: `python -m unittest discover tests` is still not green
on this tree. Known source-level blockers include:

- `android/app/src/main/java/com/nx/android/game/GameActivity.kt` has a hard-coded Chinese
  fragment `"60 帧"` in an English log line; `tests/test_app_text.py` rejects it.
- `tests/test_texture_format_aliases.py` has a stub of `vkimg_t` that does not know the new
  `im->full` member; the real header does.
- `tests/test_docs_tables.py` and the README image test need the omitted profiles and
  `docs/images`.

Do not treat a red test run as proof that the APK cannot build: it is a snapshot of a working
build with packaging/test inputs deliberately slimmed. The build workflow was validated
separately. See `SOURCE_MAP.md` for the missing inputs.

## Do not assume

- Do not assume `nxnative/dm/games` contains all 185 profiles; it contains the four upstream
  scripts (`game.py`, `profile_guess.py`, `settings.py`, `settings.tsv`), the README, and the
  IT2 two-file profile. The release package has the full set.
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
