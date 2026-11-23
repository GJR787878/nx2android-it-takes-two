# It Takes Two — Android port (nx2androidX)

It Takes Two (Switch, `010092A0172E4000`, v131072 / 1.0.2) brought up on Android with
[nx2androidX](https://github.com/GJR787878/nx2androidX). This repository holds the verified
alpha13 build, the 30 fps and 60 fps logs, the source snapshot of the changes, and the profile
package.

**No game data is included.** You still need your own legally obtained XCI and `prod.keys`.

## Latest build

| Item | Value |
|---|---|
| APK | `nx2android-v0.4.1-alpha13-it2-srgb.apk` |
| versionCode / versionName | `32` / `0.4.1-alpha13` |
| Size | 248 MB (full package, includes the porter toolchain; no RomFS/game files) |
| SHA-256 | `3886fc7e95a04ce50a3c60ffd0b311c64dc6685174843a5c58a32afdc1cd5622` |
| Install | Over alpha12 (`versionCode 31`), same debug signer |

The APK is in **Releases**, not in the Git tree, because it is over GitHub's 100 MB file limit.
`nx2a-profiles-r2-it2.zip` (90 MB) and the log archives are there too.

## What is in this repository

- `android/`, `porter/`, `nxnative/`, `docs/`, `scripts/` — the nx2androidX source snapshot with
  the It Takes Two changes (sRGB present path, DLC injection, 60 fps environment, profile
  handling, `nx_extract --aoc-xci`, and profile/revision bumps).
- `nxnative/dm/games/010092A0172E4000/` — the new `game.tsv` + `android.tsv` profile.
- `android/app/src/main/assets/aoc/010092A0172E4000/1/` — the two DLC entitlement files used by
  the full-game unlock (5,577 bytes).
- `android/app/src/main/assets/fpslock/010092A0172E4000.tsv` — the FPSLocker-derived frame-limit
  table used by the 60 fps test.
- `logs/` — alpha11 30 fps, alpha12 60 fps, alpha13 60 fps log archives.
- `docs/IT2-完整版解锁说明.md` — the full-game unlock notes.
- `docs/apk-sha256-v13.txt`, `docs/profiles-r2-it2.sha256` — checksums.

The complete source is under the repository root; `nxnative/dm/games` keeps only
`010092A0172E4000` and its README to keep the snapshot small. The upstream profile tables are
not duplicated here. The original upstream README is kept as `docs/README-upstream.md`.

## Logs and measured behaviour

| Log | Build | Run | Key numbers |
|---|---|---|---|
| `IT2-30fps-alpha11-log.zip` | alpha11, 30 fps | 467 s, 14,100 frames | frame p50 33.14 / p95 44.16 / max 65.12 ms; GPU p50 12.71 / p95 13.21 ms; heavy-scene CPU replay 18.39 ms; 2,522 draws |
| `IT2-60fps-alpha12-log.zip` | alpha12, 60 fps | 373 s, 20,399 presents | frame p50 16.65 ms; GPU 8–12 ms; textures 745–762 MB; 45 alias stale reads; no crash |
| `IT2-60fps-alpha13-srgb-log.zip` | alpha13, 60 fps | 417 s, ~21,200 frames | frame p50 16.6–16.7 ms; GPU p50 10.2–11.1 ms; textures peak 701 MB, final 542 MB; GPU pool 227–382 MB; 55 alias stale reads; no `[RED]`, `VK_ERROR`, device lost or OOM |

The alpha13 profile rebuild log is inside the alpha13 archive as `rebuild.log`: 203 host sources,
0 failed, `player_api_revision 9`.

## Known issues (honest status)

1. **sRGB fallback is present but not actually engaged in the alpha13 log.** The log line
   `the surface offers no format 0 ...` shows `g_want == 0`; `present_thread` calls
   `present_one()` directly and bypasses `present_window()`, so `im_meta_srgb` stays 0 and
   `srgb_mode()` returns 0. The new shader path therefore falls back to the old blit. The picture
   can still be lighter/incorrect. The next change is to set `im_meta_srgb` from the image's
   format (or call `present_window()`) before presenting.
2. **Application pool is close to its ceiling.** The log shows
   `alias region mapped 3.00 GB (application pool 3.21 GB)`; later chapters can exhaust the guest
   pool. The profile keeps `app_pool 0xCD500000` (3285 MiB); this repository does not change it.
3. **Alias stale reads remain.** 55 cross-format reuses in alpha13; they are mostly visual
   correctness risks, not a confirmed crash cause.
4. **No crash in the provided logs.** All three runs end normally or on background; there is no
   tombstone or `logcat -b crash` in the archives.

## Profile package

`nx2a-profiles-r2-it2.zip`:

- revision `2`, count `185` (the original 184 profiles + It Takes Two), SHA-256
  `1061681ded85736b64ceae635866004df1088926d30d72c9dd2ca685b6f28e6c`;
- import it in the app's **Profiles** environment; it is metadata only, not a runtime or APK;
- its `app_pool` is still 3.21 GB, so it does **not** solve the memory-pool limit.

## Build

```bash
cd <this-repository>
export ANDROID_HOME=/path/to/android-sdk
export JAVA_HOME=/path/to/jdk-17
bash packaging/android-apk/build_apk.sh release
```

The build needs an Android NDK r27c, the ARM64 LLVM toolchain and the Python wheels used by
`packaging/android-apk/build_toolchain.py`. The alpha13 APK was produced with
`versionCode 32` and the debug signing key.

## Credits and rights

The port is based on [nx2androidX](https://github.com/GJR787878/nx2androidX) and its upstream
work. It Takes Two and its assets are property of Hazelight Studios / Electronic Arts. This
repository distributes no game content, keys, or saves.
