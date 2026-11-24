# IT2 alpha13-r2 clean-port build log

This directory holds the text logs of the first successful It Takes Two port after the clean-port fix
(`70f4e38`): the run that previously stopped at `shader_map.tsv` now completes all nine stages.

## Result

- Port exit code: `0` (see `port.txt`)
- Finished: `2026-11-24 07:53:06`
- Device: OPPO OPD2409, Android 17 (SDK 37), 15,440 MB RAM, `arm64-v8a`
- App: `com.gjr.nx2androidx`, `0.4.1-alpha13` (`versionCode 32`)
- Build: `010092A0172E4000`, `v131072`, XCI `1G+1U+2D`, 60 fps
- Output: `/data/user/0/com.gjr.nx2androidx/files/ports/ItTakesTwo-data`
- Shader split: 32,118 shaders (compute 2,171; geometry 81; pixel 24,779; vertex 5,087)

The important line is:

```text
game profile 010092A0172E4000 has no shader_map.tsv, shader_facts.tsv, shader_pairs.tsv:
taking the split tables as its first port's
```

It is followed by stages 7/9 Vulkan shaders, 8/9 host and 9/9 data pack, then `done`.

## Files

- `builds/` — the full porter build log
- `stage-logs/010092A0172E4000_build/` — each stage's own log
- `device.txt` — phone and app version
- `log.txt` — the port's own environment/AOC/60 fps lines
- `port.txt` — exit code and finish time

The raw shader sample (`ue_sample.bin`, `ue_sample.md`) is not committed here because it contains game
shader bytes. It is kept in the full ZIP attached to the release.

## Full ZIP

`IT2-60fps-alpha13-r2-cleanport-log.zip` — the original 15-file archive; attach it to the release named
`ci-20261124-alpha13-r2`.
