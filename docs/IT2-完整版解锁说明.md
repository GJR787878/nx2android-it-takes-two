# 《双人成行》安卓移植：完整版解锁说明（alpha11）

## 问题在哪

游戏不是“资源不全”，也不是存档没解到后期，而是**构建时没有把卡带里的追加内容（AddOnContent）挂进端口**。

- 本体 `010092A0172E4000` 是**共用壳**：完整版和好友通行证共用它。
- 完整版由追加内容 `010092A0172E5001`（v0）解锁，卡带里实际带有它的 RomFS：
  - `FullGameEntitlement.uplugin`（395 字节）
  - `Content/Paks/Switch/FullGameEntitlementNuts-Switch.pak`（5,182 字节）
- 好友通行证是 `010092A0172E5002`（v0）。
- 端口没有挂任何 aoc，`nn::aoc::CountAddOnContent` 返回 0，所以游戏按试玩版跑；章节选择虽然读到了存档里的“阁楼”，点进去仍被“保存章节无法于试玩版游玩”挡住。

## alpha11 做了什么

1. 用 `nx_extract --aoc-xci` 直接从 XCI 的 secure 分区按标题 ID 取出 5001 的 RomFS（不依赖单独的 DLC NSP）。
2. 把这两个文件随 APK 打进 `assets/aoc/010092A0172E4000/1/`。
3. 启动该作时（`GameActivity.startGame`）：
   - 若 `<端口目录>/aoc/1/FullGameEntitlement.uplugin` 不存在，就从 APK 资产复制整棵目录；
   - 向宿主注入 `DM_AOC_DIR=<端口目录>/aoc`。
4. 宿主随后应报告 `aoc: reporting 1 add-on contents {1}`，并把 index 1 挂成只读 RomFS。

不改存档、不改 UID，也不影响与官方版共存（包名仍是 `com.gjr.nx2androidx`）。

## 安装

直接覆盖安装 alpha11（versionCode 30，签名与 alpha10 相同），不要卸载，存档会保留。

## 验证

进游戏后打开“继续游戏 → 阁楼·交响乐章”。若还提示试玩版，导出端口目录下的 `log.txt`，先看这两行：

```text
aoc: reporting 1 add-on contents {1}
fs mount add-on content ... index 1
```

- 有 `reporting 1`、mount 成功：授权已挂上，剩下的是章节/存档条件。
- 仍是 `reporting 0` 或 mount 失败：把 `log.txt` 发回来，下一版查 `DM_AOC_DIR` 是否被端口 `env.txt` 里的旧行覆盖，或游戏是否走另一条试玩判定。

## 60 帧为什么之前不生效（alpha12）

勾选“60 帧”是构建期选项。移植器当时把 FPSLocker 表路径写成出包机器的：

`/sdcard/Android/data/com.gjr.nx2androidx/files/fpslock.tsv`

但 App 的端口在私有目录 `.../files/ports/ItTakesTwo-data/`，宿主打不开这张表，就不会把游戏的 `t.MaxFPS` 从 30 改成 62。

alpha12 在启动时：

- 把 `DM_FPS_LOCKS`、`DM_AOC_DIR` 改写成端口里的真实路径；
- 端口没有 `fpslock.tsv` 时，从 APK 资产补一份（build `C4067E8CB3258656`，对应本体 1.0.2）；
- 写入 `DM_FPS_TARGET=60` 和 `DM_PRESENT_INTERVAL=display`。

安装 alpha12 更新包（versionCode 31）覆盖即可，不需要重新移植。日志里应出现：

```text
60 fps: installed fpslock.tsv for main build C4067E8CB3258656 -> ...
env: DM_FPS_TARGET=60, DM_FPS_LOCKS=..., DM_PRESENT_INTERVAL=display
main: 2 frame limit write(s) from .../fpslock.tsv (FPSLocker-Warehouse config)
```

若 HUD 仍是 30，发 `log.txt`；重点看 `DM_FPS_LOCKS` 是否被打开、`build` 行是否与游戏 `main` 的 build ID 一致。
