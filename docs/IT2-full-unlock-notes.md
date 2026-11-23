# It Takes Two Android port: full-game unlock notes (alpha11)

**English** | [中文](IT2-完整版解锁说明.md)

## The problem

The game was not missing assets, and the save was not short of a later chapter. The build had
simply not mounted the cartridge's AddOnContent into the port.

- The base title `010092A0172E4000` is a **shared shell**: the full game and the Friend's Pass
  both use it.
- The full game is unlocked by AddOnContent `010092A0172E5001` (v0), whose RomFS is present on
  the cartridge:
  - `FullGameEntitlement.uplugin` (395 bytes)
  - `Content/Paks/Switch/FullGameEntitlementNuts-Switch.pak` (5,182 bytes)
- The Friend's Pass is `010092A0172E5002` (v0).
- The port mounted no AOC, so `nn::aoc::CountAddOnContent` returned 0 and the game ran as the
  trial. The chapter selector could read “阁楼” from the save, but entering it was blocked by
  “保存章节无法于试玩版游玩”.

## What alpha11 does

1. `nx_extract --aoc-xci` reads the 5001 RomFS directly from the XCI's secure partition by title
   ID (no separate DLC NSP required).
2. Both files ship in the APK under `assets/aoc/010092A0172E4000/1/`.
3. On launch of this title, `GameActivity.startGame`:
   - copies the whole directory from the APK assets if
     `<port dir>/aoc/1/FullGameEntitlement.uplugin` does not exist;
   - injects `DM_AOC_DIR=<port dir>/aoc` into the host.
4. The host should then log `aoc: reporting 1 add-on contents {1}` and mount index 1 as a
   read-only RomFS.

No save edit, no UID change, and coexistence with the official app is unaffected (the package
name remains `com.gjr.nx2androidx`).

## Install

Install over alpha11 directly (`versionCode 30`, same signer as alpha10). Do not uninstall; the
saves stay.

## Verify

Open “Continue → 阁楼·交响乐章”. If it still says trial, export the port directory's `log.txt`
and check these two lines first:

```text
aoc: reporting 1 add-on contents {1}
fs mount add-on content ... index 1
```

- `reporting 1` and a successful mount: the entitlement is mounted; what remains is a
  chapter/save condition.
- Still `reporting 0` or a failed mount: send the `log.txt` back. The next build checks whether
  `DM_AOC_DIR` was overwritten by an old line in the port's `env.txt`, or whether the game uses
  another trial check.

## Why 60 fps did not work earlier (alpha12)

The “60 fps” checkbox is a build-time option. The porter wrote the FPSLocker table path as the
build machine's:

`/sdcard/Android/data/com.gjr.nx2androidx/files/fpslock.tsv`

But the app's port lives in the private directory `.../files/ports/ItTakesTwo-data/`; the host
could not open that table, so it did not change the game's `t.MaxFPS` from 30 to 62.

alpha12 does this at launch:

- rewrites `DM_FPS_LOCKS` and `DM_AOC_DIR` to the real paths inside the port;
- installs a copy of `fpslock.tsv` from the APK assets when the port has none (build
  `C4067E8CB3258656`, matching base 1.0.2);
- writes `DM_FPS_TARGET=60` and `DM_PRESENT_INTERVAL=display`.

Install the alpha12 update (`versionCode 31`) over the existing app; no re-port is needed. The
log should contain:

```text
60 fps: installed fpslock.tsv for main build C4067E8CB3258656 -> ...
env: DM_FPS_TARGET=60, DM_FPS_LOCKS=..., DM_PRESENT_INTERVAL=display
main: 2 frame limit write(s) from .../fpslock.tsv (FPSLocker-Warehouse config)
```

If the HUD still shows 30, send `log.txt`; check whether `DM_FPS_LOCKS` was opened and whether
the `build` row matches the game `main` build ID.
