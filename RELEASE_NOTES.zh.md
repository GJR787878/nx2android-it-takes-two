# It Takes Two Android 移植版 — alpha13（已验证构建）

这个 Release 是当前已验证的《双人成行》移植构建，附 30 帧/60 帧日志、源码快照和档案包。

## 已验证构建

- **APK：** `nx2android-v0.4.1-alpha13-it2-srgb.apk`
- **versionCode / versionName：** `32` / `0.4.1-alpha13`
- **SHA-256：** `3886fc7e95a04ce50a3c60ffd0b311c64dc6685174843a5c58a32afdc1cd5622`
- **包名：** `com.gjr.nx2androidx`（与 alpha12 同一签名，可覆盖安装）
- **不含游戏数据 / 密钥。**

## 测试日志

- `IT2-30fps-alpha11-log.zip`：467 秒、14,100 帧；帧 p50 33.14 ms，GPU p50 12.71 ms。
- `IT2-60fps-alpha12-log.zip`：373 秒、20,399 次 present；帧 p50 16.65 ms，GPU 8–12 ms。
- `IT2-60fps-alpha13-srgb-log.zip`：417 秒、约 21,200 帧；帧 p50 16.6–16.7 ms，GPU p50
  10.2–11.1 ms；无 `[RED]`、`VK_ERROR`、device lost 或 OOM。应用池达到
  `3.00 GB / 3.21 GB`。

## 档案包

`nx2a-profiles-r2-it2.zip` — 185 个档案（原 184 个 + `010092A0172E4000`），revision 2，
SHA-256 `1061681ded85736b64ceae635866004df1088926d30d72c9dd2ca685b6f28e6c`。在 App 的
Profiles 环境中导入；它只是元数据，不会扩大 3.21 GB 的 `app_pool`。

## 本构建携带的已知问题

alpha13 的 sRGB present shader **没有确认生效**。日志行
`the surface offers no format 0 ...` 说明 `g_want == 0`；`present_thread` 调用
`present_one()` 前没有设置 `im_meta_srgb`，所以新路径回退到旧 blit。后续构建需要在使
shader 前从图像格式设置 `im_meta_srgb`，或改走 `present_window()`。移植本身可以运行；本
Release 不声称 sRGB 正确。

所有改动的源码在仓库树里；原始上游 README 保存在 `docs/README-upstream.md` 和
`docs/README-upstream.zh.md`。
