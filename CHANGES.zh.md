# 本快照的改动

**中文** | [English](CHANGES.md)

这是改动清单，不是 Git 历史。已跟踪文件的精确文本 diff 在
[`patches/it2-alpha13.patch`](patches/it2-alpha13.patch)。补丁相对本地工作树基准
`ba205aa`；移植的上游侧提交见 `AI_CONTEXT.md` / `AI_CONTEXT.zh.md`。

alpha13 补丁共 **13 个已跟踪文件：301 行新增、58 行删除**。两个未跟踪资产目录也在仓库里，但
无法出现在 `git diff` 中，单独列在下面。本 fork 另有 **第 14 个已跟踪改动**：
`nxnative/scripts/build_ipa_from_nsp.py` 的 clean-port 修复；它单独列在下面，刻意不放进
`patches/it2-alpha13.patch`。

## 已跟踪文件改动

| 文件 | 改了什么 | 为什么 |
|---|---|---|
| `android/app/build.gradle.kts` | `versionCode 25 → 32`，`versionName 0.4.1-alpha06 → 0.4.1-alpha13` | 标记已测试的 alpha13 包，并保留覆盖 alpha12 的升级路径。 |
| `android/app/src/main/java/com/nx/android/data/playback/PackEnvStore.kt` | 新增 `ensureRows()` 和共享的 `write()` helper | 把 `DM_FPS_LOCKS` / `DM_AOC_DIR` 等启动行改写成这台手机上便携包内的真实路径。 |
| `android/app/src/main/java/com/nx/android/domain/PortablePack.kt` | `PACK_PATHS` 加入 `/fpslock.tsv` | 让限帧表随包移动，包文件夹换位置后路径仍然有效。 |
| `android/app/src/main/java/com/nx/android/game/GameActivity.kt` | 新增 `GameConfigRepository`、`ensureFullGameEntitlement()`、`ensurePackEnvironment()`、`copyAssetTree()`；注入 `DM_AOC_DIR` 和 60 帧相关行 | 当 Title ID 是 `010092A0172E4000` 时安装 DLC 授权资产；只有玩家选择 60 帧时才启用；把宿主指向包内的 AOC/FPSLocker 路径。 |
| `android/gradle.properties` | Gradle JVM 内存 `4g → 2g`；parallel `true → false` | 构建资源调整，不影响运行时行为。 |
| `nxnative/dm/android/gfx_vk_present.c` | 新增 `fmt8()`、`fmt_is_srgb()`、`srgb_mode()`、`present_view()`、`present_fix_draw()`；present 描述符池扩到 9 个 set；push constant 扩到 28 字节；按条件走 blit 或 shader fallback | 为只提供另一种 8-bit 格式的 surface 准备的 sRGB fallback。**已知门控 bug：** 普通 `present_thread()` 游戏帧路径没有设置 `im_meta_srgb`，导致 `g_want` 变成 0，alpha13 中 fallback 实际没有启用。 |
| `nxnative/dm/android/gfx_vk_tex.c` | `img_drop()` 通过 `vk_defer_free_view()` 释放 `im->full` | 防止 present fallback 创建的整图 view 泄漏。 |
| `nxnative/dm/android/shaders/rot.frag` | 新增 push constant `mode`；`srgb_to_linear()` / `linear_to_srgb()`；mode 0/1/2 | sRGB fallback 的 shader 部分：直接复制、UNORM 源写入 sRGB 目标前解码、sRGB 源写入 UNORM 目标前编码。 |
| `nxnative/dm/tools/nx_extract/Program.cs` | 新增 `--aoc-xci <card.xci> <title id> <out dir>` 和 `AocXci()` | 按 Title ID 从卡带中提取追加内容的 data NCA，而不是取第一个 data NCA。完整版授权资产需要这个。 |
| `porter/datapack.py` | 把所有 `DM_FPS_LOCKS` 行改写成 `<pack>/fpslock.tsv` | 移植器原来写出包那台手机的 `/sdcard/Android/data/<package>/files` 路径；App 内的包在私有目录，旧路径读不到。 |
| `porter/pipeline.py` | UE inline 阶段打印 batch 统计、最多 12 条 hex 样本和样本路径 | 让着色器扫描失败/为空时留下证据，而不是只显示“0 shaders”。 |
| `porter/revision.py` | `PLAYER_API_REVISION 8 → 9` | alpha13 的 present 路径变化后，强制手机重建每个包的 runtime，而不是重新移植整个游戏。 |
| `porter/ue_inline.py` | 新增 LZ4 压缩内联记录识别、逐记录校验计数，以及 `ue_sample.bin` / `ue_sample.md` 转储 | 处理《双人成行》中 LSLG 记录包在 LZ4 block 里的 cooked UE 包；转储用于诊断以后着色器布局变化。 |

## 新增资产（源工作树中未跟踪，本仓库已提交）

| 路径 | 大小 | 用途 |
|---|---|---|
| `android/app/src/main/assets/aoc/010092A0172E4000/1/FullGameEntitlement.uplugin` | 395 B | DLC 授权描述文件 |
| `android/app/src/main/assets/aoc/010092A0172E4000/1/Content/Paks/Switch/FullGameEntitlementNuts-Switch.pak` | 5,182 B | DLC 授权 pak |
| `android/app/src/main/assets/fpslock/010092A0172E4000.tsv` | 609 B | 从上游 `C4067E8CB3258656` 配置生成的 FPSLocker 表；玩家选择 60 帧时使用 |

## 已有档案文件

`nxnative/dm/games/010092A0172E4000/game.tsv` 和 `android.tsv` 是为本移植新建的。该档案
有意只包含这两个文件；另外 184 个档案的着色器表不在本快照中（见 `SOURCE_MAP.md` /
`SOURCE_MAP.zh.md`）。

## alpha13 快照之后的改动（本 fork）

- `.github/workflows/android-apk.yml` 是能出包的工作流，不是占位文件：`workflow_dispatch`
  构建 APK 和 profiles artifact；`v*` tag 把它们挂到 Release。工作流不跑单元测试。
- 四个上游档案脚本 `game.py`、`profile_guess.py`、`settings.py`、`settings.tsv` 已补回
  `nxnative/dm/games/`；没有它们，APK 里的档案工具不完整。
- `nxnative/scripts/build_ipa_from_nsp.py`（提交 `70f4e38`）修复 clean 移植《双人成行》：
  只有 `game.tsv` 和 `android.tsv` 的档案，直接采用 shader split 生成的
  `shader_map.tsv`、`shader_facts.tsv`、`shader_pairs.tsv`，不再读取不存在的档案表。
  这是相对 alpha13 补丁的第 14 个改动文件，未放进 `patches/it2-alpha13.patch`。

## 本快照已知测试阻塞

- `GameActivity.kt` 的英文日志行里有中文片段 `"60 帧"`，这是 `test_app_text` 的失败项；
  属于 UI/日志文本问题，不是原生移植失败。
- `tests/test_texture_format_aliases.py` 使用旧版 `vkimg_t` stub，没有 `full`；真实头文件
  `nxnative/dm/android/gfx_vk.h` 里有。
- `docs/images` 和完整 profile 树被省略；在恢复它们或给 CI 提供输入前，
  `test_docs_tables` 和 `test_every_readme_image_exists` 会失败。

## 未改动

- `app_pool` 仍是 `0xCD500000`（3.21 GB）。alpha13 日志已映射到 3.00 GB；本快照没有尝试
  扩容。
- 55 条 alias stale read 没有处理。
- 不含任何游戏数据、密钥、RomFS 或存档。
