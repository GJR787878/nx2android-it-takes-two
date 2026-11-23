# AI 上下文 — 判断仓库前先读

**中文** | [English](AI_CONTEXT.md)

本仓库是**发布快照**，不是完整开发历史。它保存基于
[nx2androidX](https://github.com/GJR787878/nx2androidX) 的《双人成行》Android 移植版、
已验证的 alpha13 APK、30/60 帧日志、改动源码和游戏档案包。

如果你是读取本仓库的 AI 工具，先读这里，再读 `CHANGES.md`、`SOURCE_MAP.md` 和
`patches/` 下的补丁。不要只根据文件时间推断改动集：这些文件是从工作树复制来的，上游历史
不在本仓库里。

## 关键事实

- 游戏：**It Takes Two**（Switch），Title ID `010092A0172E4000`，build `v131072 / 1.0.2`。
- 宿主：nx2androidX，包名 `com.gjr.nx2androidx`，`arm64-v8a`，`targetSdk 28`。
- 最新构建：**alpha13**，`versionCode 32`，`versionName 0.4.1-alpha13`。
- 签名：alpha13 使用 debug keystore。要让 CI 构建能覆盖安装，需要稳定密钥；GitHub
  runner 的临时 debug key 不是同一把。
- 移植改动的基准：`GJR787878/nx2androidX`，分支 `it2-diag`。
  - sRGB/present 提交：`e850f3ad95af44c8e63d681ebb8805efebee8597`
  - revision 9 提交：`6bd4a9f4641f5cf726836481e300c1523f444cbb`
  - 本快照使用的工作树还有 13 个未提交修改，以及
    `android/app/src/main/assets/` 下的两个未跟踪资产目录。
- 构建命令：`bash packaging/android-apk/build_apk.sh release`。它把 nixport rootfs、
  Android NDK、ARM64 LLVM 和 glslc 下载到 `packaging/android-apk/.cache`；构建 APK
  不需要游戏文件或 `prod.keys`。
- App **不内嵌** 游戏档案。档案是独立包，由 App 在 APK 之外生成或导入。

## 阅读顺序

1. `README.md` / `README.zh.md` — Release 内容与安装方式。
2. `AI_CONTEXT.md` / `AI_CONTEXT.zh.md` — 本文件。
3. `CHANGES.md` / `CHANGES.zh.md` — 13 个改动文件及每个改动的原因。
4. `patches/it2-alpha13.patch` — 这 13 个文件相对本地基准的文本 diff。
5. `SOURCE_MAP.md` / `SOURCE_MAP.zh.md` — 哪些内容故意没有放入，以及如何恢复。
6. `docs/IT2-完整版解锁说明.md` — 完整版授权说明。

## 已验证内容

alpha13 日志是 `logs/IT2-60fps-alpha13-srgb-log.zip` 里的 417 秒运行：

- 约 21,200 次 present，帧 p50 16.6–16.7 ms，GPU p50 10.2–11.1 ms。
- 无 `[RED]`、`VK_ERROR`、device lost、OOM 或 `ShowError`。
- 纹理峰值 701 MB，末段 542 MB；GPU 池 227–382 MB。
- `alias region mapped 3.00 GB (application pool 3.21 GB)`。
- 仍有 55 条 alias stale read。

30 帧运行是 alpha11（`logs/IT2-30fps-alpha11-log.zip`）：467 秒、14,100 帧，p50
33.14 ms，GPU p50 12.71 ms。alpha12 运行是
`logs/IT2-60fps-alpha12-log.zip`：373 秒、20,399 次 present，p50 16.65 ms，GPU 8–12 ms。

## 已知问题：alpha13 的 sRGB fallback 没有生效

这是最重要的注意事项。代码里有新的 sRGB fallback，但日志行
`the surface offers no format 0 ...` 说明门控没有按预期运行：

- `present_window()` 会从游戏帧格式设置 `im_meta_srgb`。
- 普通游戏帧走的 `present_thread()` 路径直接对游戏图像调用 `present_one()`，没有走
  `present_window()`。
- 因此 `im_meta_srgb` 保持 0；`present_one()` 里 `g_want = im_meta_srgb`，于是
  `g_want` 变成 0；`srgb_mode(0, g_sfmt)` 返回 0，`swap_make()` 不会请求 fallback 管线。
- 新 shader 路径虽然存在，但 alpha13 的普通游戏帧不会用到。画面仍可能偏亮或错误。
  后续修复必须在调用 `present_one()` 前设置 `im_meta_srgb`，或让游戏帧走
  `present_window()`。

相关代码：`nxnative/dm/android/gfx_vk_present.c`（`present_one`、`present_window`、
`present_thread`、`srgb_mode`、`present_fix_draw`）和
`nxnative/dm/android/shaders/rot.frag`。

## 未验证内容

- sRGB 修复 **未验证**；见上。
- 应用池仍是 3.21 GB，没有扩容；后续章节可能耗尽。
- alias stale read 仍存在；主要是画面正确性风险，不是已确认的崩溃原因。
- 提供的日志里没有 tombstone 或 `logcat -b crash`。
- 本仓库还没有成功的 CI 运行。工作流存在，但尚未修到全绿。

## CI 状态与测试注意事项

`.github/workflows/android-apk.yml` 已处于 active。它是 release 风格构建：下载
rootfs/工具链、跑测试、用 Gradle 构建并把 APK 作为 artifact 上传；在 `v*` tag 上还会把
APK 和档案包挂到 Release。

快照生成时，`python -m unittest discover tests` 在本树上 **不是全绿**。已知源码级阻塞项：

- `android/app/src/main/java/com/nx/android/game/GameActivity.kt` 的英文日志行里硬编码了
  中文 `"60 帧"`；`tests/test_app_text.py` 会拒绝。
- `tests/test_texture_format_aliases.py` 的 `vkimg_t` stub 不认识新加的 `im->full`；
  真实头文件里有。
- `tests/test_docs_tables.py` 和 README 图片测试需要被省略的 profiles 与 `docs/images`。

不要把测试红当成“原生移植无法构建”的证据。它是一个可运行构建的快照，只是打包/测试输入
被有意瘦身了。缺失输入见 `SOURCE_MAP.md`。

## 不要假设

- 不要假设 `nxnative/dm/games` 包含全部 185 个档案；它只有 IT2 的两文件档案和上游
  profile README。完整集合在 Release 包里。
- 不要假设 `docs/images` 存在；它为了控制快照体积被省略了。
- 不要把 alpha13 当作“sRGB 已修复”。真实状态是“能运行，sRGB fallback 未生效”。
- 不要为了让 CI 跑通而提交 keystore、`prod.keys`、游戏转储、RomFS 或数据包。

## 有用 ID 与哈希

| 内容 | 值 |
|---|---|
| APK SHA-256 | `3886fc7e95a04ce50a3c60ffd0b311c64dc6685174843a5c58a32afdc1cd5622` |
| 档案包 SHA-256 | `1061681ded85736b64ceae635866004df1088926d30d72c9dd2ca685b6f28e6c` |
| 档案包 | `nx2a-profiles-r2-it2.zip`，185 个档案，revision 2 |
| 日志设备 | OPPO OPD2409 / SM8750P / Android 17 / 15,440 MB RAM |

精确下载链接在 `README.md` / `README.zh.md` 和
[alpha13 Release](https://github.com/GJR787878/nx2android-it-takes-two/releases/tag/v0.4.1-alpha13)。
