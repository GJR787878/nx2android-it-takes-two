# Changes in this snapshot

**English** | [中文](CHANGES.zh.md)

This is a change inventory, not a Git history. The exact textual diff for the tracked files is
in [`patches/it2-alpha13.patch`](patches/it2-alpha13.patch). The patch is taken against the local
working-tree base `ba205aa`; the port's upstream-side commits are listed in `AI_CONTEXT.md`.

The diff contains **13 modified tracked files: 301 insertions and 58 deletions**. Two untracked
asset trees are included in the repository but cannot appear in a `git diff`; they are listed
separately below.

## Modified tracked files

| File | Change | Why |
|---|---|---|
| `android/app/build.gradle.kts` | `versionCode 25 → 32`, `versionName 0.4.1-alpha06 → 0.4.1-alpha13` | Marks the tested alpha13 package and preserves the install-over-alpha12 path. |
| `android/app/src/main/java/com/nx/android/data/playback/PackEnvStore.kt` | Adds `ensureRows()` and a shared `write()` helper | Rewrites the launch rows for `DM_FPS_LOCKS` / `DM_AOC_DIR` to the actual paths inside the portable pack on this phone. |
| `android/app/src/main/java/com/nx/android/domain/PortablePack.kt` | Adds `/fpslock.tsv` to `PACK_PATHS` | Makes the frame-limit table travel with the pack and follow the pack folder when it is moved. |
| `android/app/src/main/java/com/nx/android/game/GameActivity.kt` | Adds `GameConfigRepository`; `ensureFullGameEntitlement()`; `ensurePackEnvironment()`; `copyAssetTree()`; injects `DM_AOC_DIR` and the 60 fps rows | Installs the DLC entitlement asset when the title is `010092A0172E4000`, enables 60 fps only when the player chose it, and points the host at the pack-local AOC/FPSLocker paths. |
| `android/gradle.properties` | Gradle JVM memory `4g → 2g`; parallel `true → false` | Build-resource tuning; no runtime behaviour. |
| `nxnative/dm/android/gfx_vk_present.c` | Adds `fmt8()`, `fmt_is_srgb()`, `srgb_mode()`, `present_view()`, `present_fix_draw()`; expands the present descriptor pool to 9 sets; uses 28-byte push constants; routes the blit or shader fallback | The intended sRGB fallback for a surface that offers only the other 8-bit format. **Known gate bug:** the normal `present_thread()` game-frame path does not set `im_meta_srgb`, so `g_want` becomes 0 and the fallback is not active in alpha13. |
| `nxnative/dm/android/gfx_vk_tex.c` | `img_drop()` releases `im->full` through `vk_defer_free_view()` | Prevents leaking the whole-image view created by the present fallback. |
| `nxnative/dm/android/shaders/rot.frag` | Adds push-constant `mode`; `srgb_to_linear()` / `linear_to_srgb()`; modes 0/1/2 | Shader half of the sRGB fallback: copy, decode UNORM→sRGB target, or encode sRGB→UNORM target. |
| `nxnative/dm/tools/nx_extract/Program.cs` | Adds `--aoc-xci <card.xci> <title id> <out dir>` and `AocXci()` | Extracts the add-on-content data NCA from a cartridge by title ID, instead of taking the first data NCA. Needed for the full-game entitlement asset. |
| `porter/datapack.py` | Rewrites any `DM_FPS_LOCKS` row to `<pack>/fpslock.tsv` | The porter wrote the build phone's `/sdcard/Android/data/<package>/files` path; an in-app pack lives in the app's private folder, so the old path is unreadable. |
| `porter/pipeline.py` | UE inline stage prints batch stats, up to 12 hex samples, and a sample path | Makes a failed/empty shader scan leave evidence instead of an opaque “0 shaders” result. |
| `porter/revision.py` | `PLAYER_API_REVISION 8 → 9` | Forces the phone to rebuild each pack's runtime after the alpha13 present-path change, instead of re-porting the whole game. |
| `porter/ue_inline.py` | Adds LZ4-compressed inline-record detection, per-record validation counters, and `ue_sample.bin` / `ue_sample.md` dumps | Handles It Takes Two's cooked UE packages where the LSLG record is inside an LZ4 block; the dumps help diagnose future shader-layout changes. |

## Added assets (untracked in the source working tree, committed here)

| Path | Size | Role |
|---|---|---|
| `android/app/src/main/assets/aoc/010092A0172E4000/1/FullGameEntitlement.uplugin` | 395 B | DLC entitlement descriptor |
| `android/app/src/main/assets/aoc/010092A0172E4000/1/Content/Paks/Switch/FullGameEntitlementNuts-Switch.pak` | 5,182 B | DLC entitlement pak |
| `android/app/src/main/assets/fpslock/010092A0172E4000.tsv` | 609 B | FPSLocker table derived from the upstream `C4067E8CB3258656` config; used when the player selects 60 fps |

## Already-present profile files

`nxnative/dm/games/010092A0172E4000/game.tsv` and `android.tsv` were created for this port. The
profile deliberately contains only those two files; the other 184 profiles' shader tables are
not in this snapshot (see `SOURCE_MAP.md`).

## Known test blockers in this snapshot

- `GameActivity.kt` contains a Chinese fragment `"60 帧"` in an English log line; this is the
  `test_app_text` failure. It is a UI/log-text issue, not a native port failure.
- `tests/test_texture_format_aliases.py` uses an old stub of `vkimg_t` without `full`; the real
  header (`nxnative/dm/android/gfx_vk.h`) has it.
- `docs/images` and the full profile tree were omitted; `test_docs_tables` and
  `test_every_readme_image_exists` fail until they are restored or the CI inputs are supplied.

## Not changed

- `app_pool` remains `0xCD500000` (3.21 GB). The alpha13 log reaches 3.00 GB mapped; this
  snapshot does not attempt to raise the pool.
- The 55 alias stale reads are not addressed here.
- No game data, keys, RomFS or saves are included.
