# 源码地图与有意省略的内容

**中文** | [English](SOURCE_MAP.md)

本仓库是**发布快照**，不是完整上游 checkout。源码对《双人成行》的改动是完整的，但一些大
目录和上游 Git 历史被有意省略。说某个路径“缺失”或认为测试应该通过之前，先读这里。

## 根目录地图

| 路径 | 内容 |
|---|---|
| `android/` | 手机 App：Kotlin、Compose UI、Gradle、游戏库和播放链路 |
| `android/app/src/main/assets/aoc/010092A0172E4000/` | 完整版解锁用的两个 DLC 授权文件 |
| `android/app/src/main/assets/fpslock/010092A0172E4000.tsv` | 从 FPSLocker 生成的 30/60 帧表 |
| `porter/` | 移植流水线（Python）：解包、着色器拆分、数据包组装、revision |
| `nxnative/dm/` | 原生宿主：Vulkan 后端、Android 服务、输入、overlay、纹理/present 代码 |
| `nxnative/dm/games/010092A0172E4000/` | 本移植的 `game.tsv` + `android.tsv` 档案 |
| `nxnative/dm/games/{game.py,profile_guess.py,settings.py,settings.tsv}` | App 会打包的上游档案脚本；第一版瘦身快照漏了，现已补回 |
| `nxnative/dm/games/README.md` | 上游的档案格式文档 |
| `packaging/android-apk/` | `build_apk.sh`、资产暂存、NDK/LLVM 下载、APK 组装 |
| `docs/` | 移植/架构/开发文档；原始上游 README 保存在 `docs/README-upstream.md` 和 `docs/README-upstream.zh.md` |
| `logs/` | 2026-11-24 成功 clean port 的文本日志（`it2-alpha13-r2-20261124-080056/`）；完整 ZIP 是 Release 资产 |
| `.github/workflows/` | CI 定义，包括 `android-apk.yml` 和 `tests.yml` |
| `patches/` | 本快照的精确已跟踪文件 diff |

## 有意不放进 Git 的内容

### 1. 其他游戏档案（大表集合）

这里的 `nxnative/dm/games` 有：

- `010092A0172E4000/game.tsv`
- `010092A0172E4000/android.tsv`
- 四个上游脚本（`game.py`、`profile_guess.py`、`settings.py`、`settings.tsv`）
- 上游 `README.md`

它没有其他 184 个档案文件夹。

上游档案是约 **572 MB** 的着色器表。提交它们会让这个快照变成档案仓库的第二份拷贝，并让
仓库不必要地变大。

完整档案集 — 185 个档案（184 个上游 +《双人成行》）— 是独立 Release 资产：

- `nx2a-profiles-r2-it2.zip`
- `https://github.com/GJR787878/nx2android-it-takes-two/releases/download/v0.4.1-alpha13/nx2a-profiles-r2-it2.zip`
- revision 2；SHA-256 `1061681ded85736b64ceae635866004df1088926d30d72c9dd2ca685b6f28e6c`

要在本地构建/测试时恢复档案树：

```bash
unzip -q nx2a-profiles-r2-it2.zip -d nxnative/dm/games
```

zip 根目录就是各个档案文件夹，所以解压到这里是正确的。不要解压到
`android/app/src/main/assets`；App 不内嵌档案。

### 2. `docs/images`

约 18 MB 的截图和 logo，已从快照中省略。这会导致：

- `README.md` 的 `docs/images/logo-badge.svg` 链接在本仓库里可能打不开；
- 在图片恢复前，`tests/test_docs_tables.py::test_every_readme_image_exists` 会失败。

它们在上游仓库的 `docs/images/` 树里，不是编译 APK 的必需项。

### 3. 上游 Git 历史

本仓库是新的快照，没有 `zFitness/nx2androidX` 历史。要与上游对比：

```bash
git remote add upstream https://github.com/GJR787878/nx2androidX.git
git fetch upstream it2-diag
```

相关上游侧提交：

- `e850f3ad95af44c8e63d681ebb8805efebee8597` — sRGB present 路径和 revision 代码
- `6bd4a9f4641f5cf726836481e300c1523f444cbb` — `PLAYER_API_REVISION` 9

精确工作树 diff 在 `patches/it2-alpha13.patch`。未跟踪的 AOC/FPSLocker 资产不在补丁里；
路径和大小见 `CHANGES.md` / `CHANGES.zh.md`。

### 4. 构建产物与私有输入

不放进 Git，也不应该添加：

- `packaging/android-apk/.cache/` — 下载的 rootfs、NDK、LLVM、wheel、NuGet 包；
- `android/app/build/`、`.gradle/`、`build/`、`dist/`；
- 任何 `prod.keys`、`title.keys`、XCI/NSP/NCA/RomFS、存档、数据包或 keystore；
- 含私有路径或超出所提供压缩包范围用户数据的设备日志。

构建本身从公开的 `NixPort/nixport-rootfs@payload-latest` Release 下载 rootfs，并从
Google/Microsoft 下载工具链；构建 APK 不需要游戏密钥。

## 构建与 CI 路径

标准 APK 构建命令：

```bash
bash packaging/android-apk/build_apk.sh release
```

GitHub 工作流是 `.github/workflows/android-apk.yml`：

- `workflow_dispatch` 构建当前分支，并把 `nx2android-android-apk` 作为 artifact 上传；
- `v*` tag 构建同样的 APK，并在 Release 存在时把 APK 和 profiles zip 挂上去；
- 需要用 `NX2A_KEYSTORE_B64`（以及匹配的密码/别名 secrets）才能用项目密钥签名。没有时，
  Gradle 使用 runner 的临时 debug key。

API/dispatch 构建已成功：运行 `45294935869` 在 7 分 25 秒内产出 APK。该运行包含 `70f4e38`
的 clean-port 修复：只有 `game.tsv` 和 `android.tsv` 的档案，直接采用 shader split 生成的
三张表，不再读取不存在的档案表。**测试套件**在本快照上仍不是全绿；已知源码级阻塞项在
`CHANGES.md` / `CHANGES.zh.md`，缺失的测试输入（profiles、docs images）见上。构建工作流不跑
测试，所以 APK 绿不等于测试绿。

## 给 AI 工具的阅读规则

- `android/` + `porter/` + `nxnative/` + `packaging/` 是代码；`docs/` 是文档。
- `nxnative/dm/games` 有四个档案脚本、README 和 IT2 档案文件夹；其他档案文件夹有意不在
  Git 中。
- 档案包是 App 的输入，不是 APK 内嵌内容。
- sRGB fallback 在代码里，但 alpha13 中没有生效；见 `AI_CONTEXT.md` / `AI_CONTEXT.zh.md`。
- 测试红或 `docs/images/logo-badge.svg` 缺失，不代表原生移植不存在；只代表快照被瘦身了。
