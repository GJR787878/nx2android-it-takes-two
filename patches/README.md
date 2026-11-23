# Patch inventory

**English** | [中文](README.zh.md)

`it2-alpha13.patch` contains the textual diff of the 13 tracked files modified in this snapshot
relative to the local working-tree base `ba205aa`. It was produced with:

```bash
git -C <nx2androidX working tree> diff --no-color -- . > patches/it2-alpha13.patch
```

It does **not** include the untracked asset files:

- `android/app/src/main/assets/aoc/010092A0172E4000/1/FullGameEntitlement.uplugin`
- `android/app/src/main/assets/aoc/010092A0172E4000/1/Content/Paks/Switch/FullGameEntitlementNuts-Switch.pak`
- `android/app/src/main/assets/fpslock/010092A0172E4000.tsv`

Those are committed directly in this repository; their paths and sizes are in `CHANGES.md`.
The upstream-side port commits are listed in `AI_CONTEXT.md`.
