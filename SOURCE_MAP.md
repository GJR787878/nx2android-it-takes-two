# Source map and deliberate omissions

**English** | [中文](SOURCE_MAP.zh.md)

This repository is a **release snapshot**, not the full upstream checkout. The source is
complete for the It Takes Two changes, but some large trees and the upstream Git history are
deliberately absent. Read this before saying that a path is “missing” or that a test should pass.

## Root map

| Path | What it is |
|---|---|
| `android/` | The phone app: Kotlin, Compose UI, Gradle, the game library and the playback plumbing |
| `android/app/src/main/assets/aoc/010092A0172E4000/` | The two DLC entitlement files used by the full-game unlock |
| `android/app/src/main/assets/fpslock/010092A0172E4000.tsv` | The FPSLocker-derived 30/60 fps table |
| `porter/` | The port pipeline (Python): extraction, shader split, data-pack assembly, revisions |
| `nxnative/dm/` | The native host: Vulkan backend, Android services, input, overlay, texture/present code |
| `nxnative/dm/games/010092A0172E4000/` | This port's `game.tsv` + `android.tsv` profile |
| `nxnative/dm/games/{game.py,profile_guess.py,settings.py,settings.tsv}` | Upstream profile scripts the app ships; they were absent from the first slim snapshot and are restored |
| `nxnative/dm/games/README.md` | Upstream's profile format documentation |
| `packaging/android-apk/` | `build_apk.sh`, asset staging, NDK/LLVM fetching, APK assembly |
| `docs/` | Porting/architecture/development docs; the original upstream README is kept as `docs/README-upstream.md` |
| `logs/` | The three test log archives |
| `.github/workflows/` | The CI definitions, including `android-apk.yml` and `tests.yml` |
| `patches/` | The exact tracked-file diff for this snapshot |

## What is intentionally not in Git

### 1. The other game profiles (the large table set)

`nxnative/dm/games` here has:

- `010092A0172E4000/game.tsv`
- `010092A0172E4000/android.tsv`
- the four upstream scripts (`game.py`, `profile_guess.py`, `settings.py`, `settings.tsv`)
- the upstream `README.md`

It does not have the other 184 profile folders.

The upstream profiles are about **572 MB** of shader tables. Committing them would make this
snapshot a second copy of the profile warehouse and make the repository unnecessarily large.

The full profile set — 185 profiles (184 upstream + It Takes Two) — is the separate release
asset:

- `nx2a-profiles-r2-it2.zip`
- `https://github.com/GJR787878/nx2android-it-takes-two/releases/download/v0.4.1-alpha13/nx2a-profiles-r2-it2.zip`
- revision 2; SHA-256 `1061681ded85736b64ceae635866004df1088926d30d72c9dd2ca685b6f28e6c`

To reconstitute the profile tree for a local build/test:

```bash
unzip -q nx2a-profiles-r2-it2.zip -d nxnative/dm/games
```

The zip's root contains the profile folders, so this is the correct destination. Do not unzip
it into `android/app/src/main/assets`; the app does not carry the profiles.

### 2. `docs/images`

About 18 MB of screenshots and the logo. They were omitted from the snapshot. This is why:

- `README.md`'s `docs/images/logo-badge.svg` link can be broken in this repository;
- `tests/test_docs_tables.py::test_every_readme_image_exists` fails until the images are
  restored.

They are available in the upstream repository's `docs/images/` tree. They are not needed to
compile the APK.

### 3. Upstream Git history

This repository is a new snapshot, so it has no `zFitness/nx2androidX` history. To compare
against upstream:

```bash
git remote add upstream https://github.com/GJR787878/nx2androidX.git
git fetch upstream it2-diag
```

The relevant upstream-side commits are:

- `e850f3ad95af44c8e63d681ebb8805efebee8597` — sRGB present path and revision code
- `6bd4a9f4641f5cf726836481e300c1523f444cbb` — `PLAYER_API_REVISION` 9

The exact working-tree diff is in `patches/it2-alpha13.patch`. The untracked AOC/FPSLocker
assets are not represented in that patch; their paths and sizes are in `CHANGES.md`.

### 4. Build products and private inputs

Not in Git, and should not be added:

- `packaging/android-apk/.cache/` — downloaded rootfs, NDK, LLVM, wheels, NuGet packages;
- `android/app/build/`, `.gradle/`, `build/`, `dist/`;
- any `prod.keys`, `title.keys`, XCI/NSP/NCA/RomFS, saves, data packs or keystores;
- logs from a device that contain private paths or user data beyond the provided archives.

The build itself downloads the rootfs from the public `NixPort/nixport-rootfs@payload-latest`
release and the toolchain from Google/Microsoft; no game key is required for an APK build.

## Build and CI paths

The canonical APK build is:

```bash
bash packaging/android-apk/build_apk.sh release
```

The GitHub workflow is `.github/workflows/android-apk.yml`:

- `workflow_dispatch` builds the branch and uploads `nx2android-android-apk` as an artifact;
- a `v*` tag builds the same APK and, when the Release exists, attaches it and the profiles zip;
- it needs `NX2A_KEYSTORE_B64` (and the matching password/alias secrets) to sign with the
  project key. Without it, Gradle uses the runner's throwaway debug key.

The API/dispatch build succeeds: run `45283177475` produced the APK in 5m17s. Run
`45283177475` includes the clean-port fix in `70f4e38`: a profile with only `game.tsv` and
`android.tsv` takes the shader split's three tables instead of reading missing profile tables.
The **test suite** is still not green in this snapshot; the known source-level blockers are in
`CHANGES.md`, and the missing test inputs (profiles, docs images) are above. The build workflow
does not run the tests, so a green APK is not a green test suite.

## Reading rules for an AI tool

- `android/` + `porter/` + `nxnative/` + `packaging/` are the code; `docs/` is documentation.
- `nxnative/dm/games` has the four profile scripts, the README and the IT2 profile folder;
  other profile folders are intentionally absent from Git.
- The profile package is an input to the app, not something the APK embeds.
- The sRGB fallback is in the code but is not active in alpha13; see `AI_CONTEXT.md`.
- A red test or a missing `docs/images/logo-badge.svg` does not mean the native port is
  absent; it means the snapshot is slim.
