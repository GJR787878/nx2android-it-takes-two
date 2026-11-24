# It Takes Two — Android 移植版（nx2androidX）

**中文** | [English](README.md)

《双人成行》（Switch，`010092A0172E4000`，v131072 / 1.0.2）通过
[nx2androidX](https://github.com/GJR787878/nx2androidX) 移植到 Android。本仓库保存已验证的
alpha13 构建、30 帧与 60 帧日志、改动源码快照和游戏档案包。

**不含任何游戏数据。** 你仍需要自己合法取得的 XCI 和 `prod.keys`。

## 给 AI 审阅者 / Agent

这是发布快照，不是完整的上游 Git 历史。判断代码或测试状态前，先读：

- [`AI_CONTEXT.md`](AI_CONTEXT.md) — 项目定位、基准 commit、已验证事实与已知问题。
- [`CHANGES.md`](CHANGES.md) — 13 个改动文件与两个新增资产目录。
- [`SOURCE_MAP.md`](SOURCE_MAP.md) — 为什么少了 184 个上游 profile 和 `docs/images`。
- [`patches/it2-alpha13.patch`](patches/it2-alpha13.patch) — 精确的已跟踪文件 diff。

中文版本见 [`AI_CONTEXT.zh.md`](AI_CONTEXT.zh.md)、[`CHANGES.zh.md`](CHANGES.zh.md)、
[`SOURCE_MAP.zh.md`](SOURCE_MAP.zh.md)。

## 最新构建

| 项目 | 值 |
|---|---|
| APK | `nx2android-v0.4.1-alpha13-it2-srgb.apk` |
| versionCode / versionName | `32` / `0.4.1-alpha13` |
| 大小 | 248 MB（完整包，内含移植工具链；不含 RomFS/游戏文件） |
| SHA-256 | `3886fc7e95a04ce50a3c60ffd0b311c64dc6685174843a5c58a32afdc1cd5622` |
| 安装 | 覆盖 alpha12（`versionCode 31`），同一 debug 签名 |

APK 放在 **Releases**，不在 Git 树里，因为它超过 GitHub 单文件 100 MB 限制。
`nx2a-profiles-r2-it2.zip`（90 MB）和日志压缩包也在 Release 里。

## 仓库内容

- `android/`、`porter/`、`nxnative/`、`packaging/` — nx2androidX 源码快照，含《双人成行》
  改动（sRGB present 路径、DLC 注入、60 帧环境、档案处理、`nx_extract --aoc-xci`、版本号/
  revision 调整）。
- `nxnative/dm/games/010092A0172E4000/` — 新增的 `game.tsv` + `android.tsv` 档案。
- `android/app/src/main/assets/aoc/010092A0172E4000/1/` — 完整版解锁用的两个 DLC 授权文件
  （5,577 字节）。
- `android/app/src/main/assets/fpslock/010092A0172E4000.tsv` — 从 FPSLocker 表生成的限帧表，
  60 帧测试使用。
- `logs/` — alpha11 30 帧、alpha12 60 帧、alpha13 60 帧日志压缩包。
- `docs/IT2-完整版解锁说明.md`、`docs/IT2-full-unlock-notes.md` — 完整版解锁说明（中文 / 英文）。
- `docs/apk-sha256-v13.txt`、`docs/profiles-r2-it2.sha256` — 校验值。
- `AI_CONTEXT.md`、`CHANGES.md`、`SOURCE_MAP.md`、`patches/` — 给 AI/源码阅读的上下文。

完整源码在仓库根目录；`nxnative/dm/games` 只保留 `010092A0172E4000` 和上游 profile 的
README，以控制快照体积。上游其他游戏的 profile 表没有重复放入。原始上游 README 保存在
`docs/README-upstream.md` / `docs/README-upstream.zh.md`。

## 下载

所有大文件都在 [alpha13 Release](https://github.com/GJR787878/nx2android-it-takes-two/releases/tag/v0.4.1-alpha13)：

- [alpha13 APK](https://github.com/GJR787878/nx2android-it-takes-two/releases/download/v0.4.1-alpha13/nx2android-v0.4.1-alpha13-it2-srgb.apk)
- [profiles r2](https://github.com/GJR787878/nx2android-it-takes-two/releases/download/v0.4.1-alpha13/nx2a-profiles-r2-it2.zip)
- [30 帧日志](https://github.com/GJR787878/nx2android-it-takes-two/releases/download/v0.4.1-alpha13/IT2-30fps-alpha11-log.zip)
- [60 帧 alpha12 日志](https://github.com/GJR787878/nx2android-it-takes-two/releases/download/v0.4.1-alpha13/IT2-60fps-alpha12-log.zip)
- [60 帧 alpha13 日志](https://github.com/GJR787878/nx2android-it-takes-two/releases/download/v0.4.1-alpha13/IT2-60fps-alpha13-srgb-log.zip)

本 fork 的 GitHub Actions 构建产物在 [CI r2 Release](https://github.com/GJR787878/nx2android-it-takes-two2/releases/tag/ci-20261124-alpha13-r2)：

- [CI 构建 APK](https://github.com/GJR787878/nx2android-it-takes-two2/releases/download/ci-20261124-alpha13-r2/nx2android-v0.4.1-alpha13-it2-ci-r2.apk)，与 alpha13 同一签名密钥
- [CI profiles 包](https://github.com/GJR787878/nx2android-it-takes-two2/releases/download/ci-20261124-alpha13-r2/nx2a-profiles-ci-r2.zip)，仅《双人成行》
- [对比报告](https://github.com/GJR787878/nx2android-it-takes-two2/releases/download/ci-20261124-alpha13-r2/CI_BUILD_REPORT.md)

## 日志与实测表现

| 日志 | 构建 | 运行 | 关键数据 |
|---|---|---|---|
| `IT2-30fps-alpha11-log.zip` | alpha11，30 帧 | 467 秒，14,100 帧 | 帧 p50 33.14 / p95 44.16 / 最大 65.12 ms；GPU p50 12.71 / p95 13.21 ms；重场景 CPU replay 18.39 ms；2,522 次 draw |
| `IT2-60fps-alpha12-log.zip` | alpha12，60 帧 | 373 秒，20,399 次 present | 帧 p50 16.65 ms；GPU 8–12 ms；纹理 745–762 MB；45 条 alias stale read；无崩溃 |
| `IT2-60fps-alpha13-srgb-log.zip` | alpha13，60 帧 | 417 秒，约 21,200 帧 | 帧 p50 16.6–16.7 ms；GPU p50 10.2–11.1 ms；纹理峰值 701 MB、末段 542 MB；GPU 池 227–382 MB；55 条 alias stale read；无 `[RED]`、`VK_ERROR`、device lost 或 OOM |

alpha13 的运行库重建日志在压缩包内的 `rebuild.log`：203 个宿主源文件，0 个失败，
`player_api_revision 9`。

## 已知问题（真实状态）

1. **sRGB fallback 代码在，但 alpha13 日志里没有真正启用。** 日志行
   `the surface offers no format 0 ...` 说明 `g_want == 0`；`present_thread` 直接调用
   `present_one()`，绕过了 `present_window()`，所以 `im_meta_srgb` 保持 0，`srgb_mode()`
   返回 0，新 shader 路径回退到旧 blit。画面仍可能偏亮/不正确。下一步需要在 present 前
   从图像格式设置 `im_meta_srgb`，或让游戏帧走 `present_window()`。
2. **应用池接近上限。** 日志显示
   `alias region mapped 3.00 GB (application pool 3.21 GB)`；后续章节可能耗尽 guest 池。
   档案仍是 `app_pool 0xCD500000`（3285 MiB），本仓库没有改动。
3. **alias stale read 仍然存在。** alpha13 有 55 次跨格式复用；主要是画面正确性风险，
   不是已确认的崩溃原因。
4. **提供的日志里没有崩溃。** 三次运行都正常结束或切后台；压缩包中没有 tombstone 或
   `logcat -b crash`。

## 档案包

`nx2a-profiles-r2-it2.zip`：

- revision `2`，数量 `185`（原 184 个档案 +《双人成行》），SHA-256
  `1061681ded85736b64ceae635866004df1088926d30d72c9dd2ca685b6f28e6c`；
- 在 App 的 **Profiles** 环境中导入；它只是元数据，不是 runtime 或 APK；
- 它的 `app_pool` 仍是 3.21 GB，因此 **不能** 解决应用池上限问题。

## 构建

```bash
cd <本仓库>
export ANDROID_HOME=/path/to/android-sdk
export JAVA_HOME=/path/to/jdk-17
bash packaging/android-apk/build_apk.sh release
```

构建需要 Android NDK r27c、ARM64 LLVM 工具链，以及
`packaging/android-apk/build_toolchain.py` 使用的 Python wheel。alpha13 APK 用
`versionCode 32` 和 debug 签名密钥构建。

## CI 构建

本 fork 用 GitHub Actions 出 APK。打开 **Actions → Android app → Run workflow**；
`workflow_dispatch` 运行会产 `nx2android-android-apk`（APK）和 `nx2a-game-profiles`。
运行 [`45283177475`](https://github.com/GJR787878/nx2android-it-takes-two2/actions/runs/45283177475)
在 5 分 17 秒内成功，产物 259,504,747 字节，SHA-256 为
`9b8111b56281dfbcaa5408d59d9ebc28cf812490b81742d4d4cb3f68b319de95`。

它和 alpha13 使用同一张 debug 证书，因此可以覆盖安装 alpha13。keystore 存放在仓库
Secrets（`NX2A_KEYSTORE_B64` 及密码/别名/密钥密码），不提交进 Git。工作流只出 APK，
不跑单元测试；测试在本快照上仍不是全绿。

### clean-port 修复

第一版 CI APK 能正常构建，但全新移植《双人成行》时在 `split_shaders()` 读取
`dm/games/010092A0172E4000/shader_map.tsv` 处报 `FileNotFoundError`。仓库档案只有
`game.tsv` 和 `android.tsv`；旧端口能跑，是因为旧端口工作目录里已有上一次 split 生成的表。
提交 `70f4e38` 让缺表档案直接把本次 split 的三张表当作首次移植的表，不再读不存在的文件。
shader split 本身成功：32,118 个 shader（compute 2,171、geometry 81、pixel 24,779、
vertex 5,087）。修复已进入上面的 r2 APK。

第一次带修复的真机构建日志在
[`logs/it2-alpha13-r2-20261124-080056/`](logs/it2-alpha13-r2-20261124-080056/README.md)：
端口退出码 0，结束时间 `2026-11-24 07:53:06`，九个阶段全部完成，产物
`ItTakesTwo-data`。完整 15 文件 ZIP 挂在 `ci-20261124-alpha13-r2` Release。

## 致谢与权利

移植基于 [nx2androidX](https://github.com/GJR787878/nx2androidX) 及其上游工作。
《双人成行》及其资产归 Hazelight Studios / Electronic Arts 所有。本仓库不分发任何游戏内容、
密钥或存档。
