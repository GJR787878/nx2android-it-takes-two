# 补丁清单

**中文** | [English](README.md)

`it2-alpha13.patch` 是本快照中 13 个已跟踪文件相对本地工作树基准 `ba205aa` 的文本 diff。
生成方式：

```bash
git -C <nx2androidX 工作树> diff --no-color -- . > patches/it2-alpha13.patch
```

它**不包含**以下未跟踪资产：

- `android/app/src/main/assets/aoc/010092A0172E4000/1/FullGameEntitlement.uplugin`
- `android/app/src/main/assets/aoc/010092A0172E4000/1/Content/Paks/Switch/FullGameEntitlementNuts-Switch.pak`
- `android/app/src/main/assets/fpslock/010092A0172E4000.tsv`

这些资产已直接提交到本仓库；路径和大小见 `CHANGES.md` / `CHANGES.zh.md`。上游侧的移植
提交见 `AI_CONTEXT.md` / `AI_CONTEXT.zh.md`。
