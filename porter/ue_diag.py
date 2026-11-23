#!/usr/bin/env python3
# Unreal Engine games whose shaders sit in no shader code archive (It Takes Two): what the paks hold, and what the game's own
# Oodle decoder makes of a sample of them. The port classifies a game by where its shaders live (profile_guess.shader_sources):
# the shapes it knows are a version 11 pak's .ushaderbytecode archives, an IoStore shader library, a legacy pak's inline
# zlib/LZ5 records and shaders a game compiles at run time (GLSLC). A version 11 pak that holds neither an archive nor an
# IoStore library keeps its shaders inline in the cooked packages, Oodle-compressed (UE 4.25's bCompressShaderCode), and the
# split reads no such shape yet. This module says what those files are before anything is written:
#
#   - the paks: version, whether the index is encrypted, the compression methods, file count, extension census, encrypted
#     entries, largest files, and every shader-looking name (ShaderArchive, GlobalShaderCache, .ushaderbytecode);
#   - the packages a pak stores uncompressed: how many, and how many hold a shader record (LSLG, or the NVN control / code
#     magics) - a game can keep part of its shaders inline and readable;
#   - a sample of the Oodle-compressed packages, decoded with the game's own Oodle (on the phone app the porter IS the device;
#     a desktop port pushes the job to one), each counted for the same magics, so the record format is known from data;
#   - one conclusion line, which the port's log carries, and the markdown report it points at.
import os, re, struct
from pathlib import Path

ARCHIVE_EXT = '.ushaderbytecode'
LSLG = b'LSLG'
CTL_MAGIC = bytes.fromhex('34127698')   # a shader's control section
GFX_MAGIC = bytes.fromhex('78563412')   # a graphics code area's SPH header
CS_MAGIC = bytes.fromhex('79563412')    # a compute code area's header
SHADER_NAME = re.compile(r'(shaderarchive|globalshadercache|ushaderbytecode|shadercode)', re.I)
PACKAGE_EXT = ('.uasset', '.uexp', '.umap', '.ubulk')
MAGICS = (('LSLG', LSLG), ('control', CTL_MAGIC), ('graphics', GFX_MAGIC), ('compute', CS_MAGIC))


def _paks(romfs):
    return sorted(os.path.join(dp, f) for dp, _, fs in os.walk(romfs) for f in fs if f.endswith('.pak'))


def _ext(name):
    return os.path.splitext(name)[1].lower() or '(none)'


def _count(data):
    """The shader magics a package holds, and where the first of each sits"""
    hits = {tag: data.count(magic) for tag, magic in MAGICS}
    first = {tag: 0 for tag, _ in MAGICS}
    for tag, magic in MAGICS:
        at = data.find(magic)
        if at >= 0: first[tag] = at
    return hits, first


def _top(sizes, limit=8):
    """The eight largest of (bytes, name, method), kept without holding every entry"""
    out = []
    for size, name, meth in sizes:
        out.append((size, name, meth)); out.sort(reverse=True); del out[limit:]
    return out


def survey(romfs, uepak, scan_limit=400):
    """Every pak under the RomFS (footer and index only: no decoding, no keys), and every stored package read for the magic
    scan (scan_limit bounds that read on a phone; the tally says how many of how many)"""
    romfs = str(romfs)
    out = dict(romfs=romfs, paks=[], bytes=0, entries=0, archives=0, cache=[], stored=dict(total=0, scanned=0, hits={}, examples=[]),
               errors=[], tocs=sorted(os.path.relpath(os.path.join(dp, f), romfs) for dp, _, fs in os.walk(romfs) for f in fs
                                      if f.endswith(('.utoc', '.ucas'))))
    for p in _paks(romfs):
        row = dict(path=os.path.relpath(p, romfs), bytes=os.path.getsize(p), version=None, index_encrypted=None, methods=[], entries=0,
                   methods_census={}, ext_census={}, encrypted=0, archives=[], biggest=[], error='')
        try:
            with open(p, 'rb') as f: row['version'] = uepak.pak_version(f)
            with open(p, 'rb') as f: enc, _ioff, _isz, methods, _ver = uepak.footer(f)
            row['index_encrypted'], row['methods'] = bool(enc), [m for m in methods if m]
            try: pk = uepak.Pak(p)   # an encrypted index needs the key Unreal embeds in main: uepak.job finds it, this survey does not
            except (ValueError, TypeError, struct.error) as e:
                row['error'] = f'the index does not read without the key from main ({e})'
                out['paks'].append(row); out['bytes'] += row['bytes']; continue
            row['entries'] = len(pk.files)
            sizes = []
            for name in pk.files:
                e = pk.entry(name)
                row['ext_census'][_ext(name)] = row['ext_census'].get(_ext(name), 0) + 1
                row['methods_census'][e['method'] or 'stored'] = row['methods_census'].get(e['method'] or 'stored', 0) + 1
                row['encrypted'] += bool(e['encrypted'])
                if name.endswith(ARCHIVE_EXT): row['archives'].append(name)
                if SHADER_NAME.search(name): out['cache'].append((row['path'], name, e['raw'], e['method'] or 'stored'))
                sizes.append((e['raw'], name, e['method'] or 'stored'))
            row['biggest'] = _top(sizes)
            out['entries'] += row['entries']; out['archives'] += len(row['archives'])
            for name in sorted(pk.files):
                e = pk.entry(name)
                if e['method'] or e['encrypted'] or not name.endswith(PACKAGE_EXT): continue
                out['stored']['total'] += 1
                if out['stored']['scanned'] >= scan_limit: continue
                try: b = pk.read(name)
                except (ValueError, OSError): continue
                out['stored']['scanned'] += 1
                cnt, _ = _count(b); hits = [t for t, n in cnt.items() if n]
                for h in hits: out['stored']['hits'][h] = out['stored']['hits'].get(h, 0) + 1
                if hits and len(out['stored']['examples']) < 5: out['stored']['examples'].append((row['path'], name, hits, len(b)))
        except (OSError, ValueError, struct.error) as e:
            row['error'] = str(e); out['errors'].append(f'{row["path"]}: {e}')
        out['paks'].append(row); out['bytes'] += row['bytes']
    return out


def _priority(name):
    """Which package the Oodle sample reads first: the engine's global shader cache, then materials, effects, maps, the rest"""
    n = name.lower()
    if 'globalshadercache' in n: return 0
    if '/materials/' in n or '/m_' in n: return 1
    if '/effects/' in n: return 2
    if n.endswith('.umap'): return 4
    return 3


def samples(romfs, uepak, limit=6, max_bytes=48 << 20, min_bytes=16 << 10):
    """[(pak path, entry name)] to decode: Oodle-compressed packages, the global shader cache first, at most max_bytes stored"""
    out, total = [], 0
    for p in _paks(romfs):
        try: pk = uepak.Pak(p)
        except (ValueError, TypeError, struct.error): continue
        cand = []
        for name in pk.files:
            if not name.endswith(PACKAGE_EXT) and 'globalshadercache' not in name.lower(): continue
            e = pk.entry(name)
            if e['method'] != 'Oodle' or e['encrypted'] or not min_bytes <= e['size'] <= max_bytes: continue
            cand.append((_priority(name), e['raw'], name, e))
        for _, _, name, e in sorted(cand):
            if len(out) >= limit: break
            if total + e['size'] > max_bytes: continue
            out.append((p, name)); total += e['size']
        if len(out) >= limit: break
    return out


def _job(romfs, uepak, picks):
    """The DMOJ job of every Oodle block of the picked entries (hle_oodle.c: u32 count, then per record u32 stored length,
    u32 raw length, the bytes) → (job bytes, [(pak, name, [(block, raw length)])])"""
    recs, meta = [], []
    for p, name in picks:
        pk = uepak.Pak(p); e = pk.entry(name)
        blocks, left = [], e['raw']
        for s, n in e['blocks']:
            k = min(left, e['block_size']) if e['block_size'] else left
            recs.append((pk.read_at(e['off'] + s, n, e['encrypted']), k)); blocks.append((len(blocks), k)); left -= k
        meta.append((p, name, blocks))
    job = bytearray(b'DMOJ' + struct.pack('<I', len(recs)))
    for comp, raw in recs: job += struct.pack('<II', len(comp), raw) + comp
    return bytes(job), meta


def _answer(data, count):
    """DMOR → [bytes] in job order (0 failed, 0xffffffff left out): the decoder's records"""
    if data[:4] != b'DMOR' or struct.unpack_from('<I', data, 4)[0] != count: raise ValueError('the Oodle decoder answered for other records than it was given')
    out, at = [], 8
    for _ in range(count):
        n = struct.unpack_from('<I', data, at)[0]; at += 4
        out.append(data[at:at + n] if n not in (0, 0xffffffff) else b'')
        if n not in (0, 0xffffffff): at += n
    return out


def probe(romfs, uepak, decode, limit=6, max_bytes=48 << 20):
    """Decode a sample of the Oodle-compressed packages with the game's own decoder (decode(job bytes) → the DMOR answer) and
    count the shader records in each. → dict(picks, records, verdict)"""
    picks = samples(romfs, uepak, limit=limit, max_bytes=max_bytes)
    if not picks: return dict(picks=[], records=[], verdict='no Oodle-compressed package to sample')
    job, meta = _job(romfs, uepak, picks)
    answer = _answer(decode(job), sum(len(b) for _, _, b in meta))
    records, at = [], 0
    for pak, name, blocks in meta:
        data, failed = [], 0
        for _i, raw in blocks:
            chunk = answer[at]; at += 1
            if len(chunk) != raw: failed += 1
            data.append(chunk)
        b = b''.join(data); cnt, first = _count(b)
        records.append(dict(pak=os.path.relpath(pak, str(romfs)), name=name, size=len(b), failed=failed, magic=cnt, first=first))
    if any(r['magic']['LSLG'] for r in records):
        verdict = 'the records are LSLG, the wrapper a legacy inline pak uses too: a modern pak reader can take them'
    elif any(r['magic']['graphics'] or r['magic']['compute'] or r['magic']['control'] for r in records):
        verdict = 'NVN code areas are there without the LSLG wrapper: the records are the engine\'s own serialization'
    else:
        verdict = 'no shader magic in the decoded sample: the cooked format is neither LSLG nor plain NVN code (the report carries the names and offsets)'
    return dict(picks=[(os.path.relpath(p, str(romfs)), n) for p, n in picks], records=records, verdict=verdict)


def summary(s, p=None):
    """The port log's lines: the numbers that decide what happens next"""
    lines = [f'UE inline survey: {len(s["paks"])} pak(s), {s["entries"]:,} entries, {s["bytes"] / 2**30:.2f} GB']
    for row in s['paks']:
        if row['error']: lines.append(f'  {row["path"]}: {row["error"]}'); continue
        lines.append(f'  {row["path"]}: pak version {row["version"]}, index {"encrypted" if row["index_encrypted"] else "plain"}, '
                     f'{row["entries"]:,} entries, methods {row["methods_census"]}')
    lines.append(f'shader code archives: {s["archives"]}; IoStore containers: {len(s["tocs"])}; shader-looking names: {len(s["cache"])}')
    for _path, name, size, meth in s['cache'][:8]: lines.append(f'  {name} ({size / 2**20:.1f} MB, {meth})')
    st = s['stored']
    lines.append(f'stored packages: {st["scanned"]:,} of {st["total"]:,} read; magic hits {st["hits"] or "none"}')
    if p and p['records']:
        lines.append(f'Oodle sample: {len(p["records"])} package(s) decoded')
        for r in p['records']: lines.append(f'  {r["name"]}: {r["size"]:,} bytes, {r["magic"]}')
        lines.append('verdict: ' + p['verdict'])
    return lines


def report(s, p=None):
    """The markdown report the port writes: everything above, so a reader can plan a reader for the shape without opening the
    game again"""
    L = ['# UE inline shader survey', '', f'- RomFS: `{s["romfs"]}`', f'- paks: {len(s["paks"])}', f'- entries: {s["entries"]:,}',
         f'- bytes: {s["bytes"]:,} ({s["bytes"] / 2**30:.2f} GB)', '']
    for row in s['paks']:
        L += [f'## `{row["path"]}`', '']
        if row['error']: L += [f'- **{row["error"]}**', '']; continue
        L += [f'- size: {row["bytes"]:,} bytes', f'- version: {row["version"]}', f'- index encrypted: {row["index_encrypted"]}',
              f'- methods: {row["methods"]}', f'- entries: {row["entries"]:,}', f'- encrypted entries: {row["encrypted"]:,}',
              f'- method census: {row["methods_census"]}', f'- shader code archives: {len(row["archives"])}', '',
              '### extensions', '', '| ext | files |', '|---|---|']
        for ext, n in sorted(row['ext_census'].items(), key=lambda kv: -kv[1])[:20]: L.append(f'| `{ext}` | {n:,} |')
        L += ['', '### largest files', '', '| bytes | method | name |', '|---|---|---|']
        for size, name, meth in row.get('biggest', []): L.append(f'| {size:,} | {meth} | `{name}` |')
        L.append('')
    L += ['## shader-looking names', '', '| bytes | method | name |', '|---|---|---|']
    for _path, name, size, meth in s['cache'][:40]: L.append(f'| {size:,} | {meth} | `{name}` |')
    L += ['', '## stored packages (uncompressed, readable here)', '',
          f'- read: {s["stored"]["scanned"]:,} of {s["stored"]["total"]:,}', f'- magic hits: {s["stored"]["hits"] or "none"}']
    for _pak, name, hits, size in s['stored']['examples']: L.append(f'  - `{name}` ({size:,} bytes): {hits}')
    L += ['', "## Oodle sample (decoded with the game's own decoder)", '']
    if not p or not p['picks']: L.append('_not run: no decoder was available_')
    else:
        L += ['| bytes | failed blocks | LSLG | control | graphics | compute | name |', '|---|---|---|---|---|---|---|']
        for r in p['records']:
            m = r['magic']
            L.append(f'| {r["size"]:,} | {r["failed"]} | {m["LSLG"]} | {m["control"]} | {m["graphics"]} | {m["compute"]} | `{r["name"]}` |')
        L += ['', f'**verdict**: {p["verdict"]}', '']
        for r in p['records']: L += [f'- `{r["name"]}`: first offsets {r["first"]}']
    L += ['', '## conclusion', '', (p['verdict'] if p and p['picks'] else 'no sample was decoded: the static part above still tells where the shaders are not'), '']
    return '\n'.join(L)


def main(argv):
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from porter.upstream import uepak
    romfs = argv[1] if len(argv) > 1 else '.'
    s = survey(romfs, uepak)
    Path(argv[2] if len(argv) > 2 else 'ue_inline_report.md').write_text(report(s, None), encoding='utf-8')
    print('\n'.join(summary(s, None)))


if __name__ == '__main__':
    main(__import__('sys').argv)
