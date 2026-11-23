#!/usr/bin/env python3
# The shaders a version 11 Unreal pak keeps inline in its cooked packages (It Takes Two): the pak's index names no shader code archive, but
# the LSLG records a legacy inline pak holds are inside the .uexp/.uasset/.umap entries, Oodle-compressed as whole packages. The survey
# (ue_diag.py) proved it on the device with the game's own decoder: 1,581 records in Engine/GlobalShaderCache-GLSL_SWITCH.bin and 6 to 8 in
# each material package, LSLG visible right after the pak layer (no second compression).
#
# This module reads that shape for the split: every candidate package is decoded with the game's own Oodle, a batch at a time (the porter
# asks the host for one job per batch, so a phone never holds more than a batch's worth), each record is validated the way the split's own
# reader validates it, deduplicated by its bytes (one shader repeated across materials is one shader), spooled to disk rather than kept in
# memory, and written back as the decoded shader code archives shader_split.py already reads (<version dir>/ue_shaders/*.ushaderbytecode).
#
# The archive is uepak.archive's version 2: tables and a code area, one LSLG record per shader, its frequency taken from the record's stage
# tag (ue_shaders() checks the two against each other).
import hashlib, os, re, struct, zlib
from pathlib import Path

CTL_MAGIC = bytes.fromhex('34127698')
GFX_MAGIC, CS_MAGIC = bytes.fromhex('78563412'), bytes.fromhex('79563412')
UE_TAG = {'SV': 'vs', 'SH': 'hs', 'SD': 'ds', 'SG': 'gs', 'SP': 'ps', 'SC': 'cs'}
FREQ = {'vs': 0, 'hs': 1, 'ds': 2, 'ps': 3, 'gs': 4, 'cs': 5}
CANDIDATE_EXT = ('.uexp', '.uasset', '.umap')
ZLIB_HEAD = re.compile(rb'\x78[\x01\x5e\x9c\xda]')
ARCHIVE_VERSION = 2


def ctl_len(ctl):
    """The control section's own length (control +0x20), or 0x880 when the field is outside its usual range (shader_split.py ctl_len)"""
    n = struct.unpack_from('<I', ctl, 0x20)[0]
    return n if 0x760 <= n < 0x880 else 0x880


def why_bad(st, ctl, code):
    """Why a record cannot be a shader (shader_split.py check), or None"""
    if len(ctl) < 0x24 or ctl[:4] != CTL_MAGIC or len(ctl) < ctl_len(ctl): return 'bad control section'
    if st == 'cs' and code[:4] in (CS_MAGIC, GFX_MAGIC) and code[:4] != CS_MAGIC or st != 'cs' and code[:4] != GFX_MAGIC:
        return 'code area header magic does not match the stage'
    if struct.unpack_from('<I', ctl, 0x704)[0] != len(code): return 'control +0x704 does not match the code area length'
    return None


def _pak(path, uepak, cache):
    pk = cache.get(path)
    if pk is None: pk = cache[path] = uepak.Pak(path)
    return pk


def candidates(romfs, uepak, include_bulk=0, limit=0):
    """[(pak path, entry name)] whose Oodle-compressed bytes may hold LSLG records: .uexp, .uasset, .umap, the engine's global shader
    cache, and any .ubulk under include_bulk bytes (bulk data holds no shader map; a game that keeps one there would be named by a probe)"""
    out, cache = [], {}
    for p in uepak.unreal_paks(str(romfs), legacy=False):
        try: pk = _pak(p, uepak, cache)
        except (OSError, ValueError, TypeError): continue
        for name in sorted(pk.files):
            low = name.lower()
            e = pk.entry(name)
            bulk = low.endswith('.ubulk') and include_bulk and e['raw'] <= include_bulk
            if not (low.endswith(CANDIDATE_EXT) or 'globalshadercache' in low or bulk): continue
            if e['method'] != 'Oodle' or e['encrypted']: continue   # stored packages carry no record (the survey read 74,913: none); zlib ones are configs
            out.append((p, name))
            if limit and len(out) >= limit: return out
    return out


def plan(picks, uepak, max_bytes=192 << 20):
    """[(pak path, [(name, entry)])] whose decoded bytes fit max_bytes (an entry larger than that is a batch of its own)"""
    out, cur, cur_pak, total, cache = [], [], None, 0, {}
    for p, name in picks:
        e = _pak(p, uepak, cache).entry(name)
        if cur and (p != cur_pak or total + e['raw'] > max_bytes):
            out.append((cur_pak, cur)); cur, total = [], 0
        cur_pak = p; cur.append((name, e)); total += e['raw']
    if cur: out.append((cur_pak, cur))
    return out


def job(pak_path, entries, uepak):
    """The DMOJ job of every Oodle block of one batch (hle_oodle.c: u32 count, then per record u32 stored length, u32 raw length, the
    bytes) → (job bytes, [(name, [raw length per block])])"""
    pk = uepak.Pak(pak_path); recs, meta = [], []
    for name, e in entries:
        blocks, left = [], e['raw']
        for s, n in e['blocks']:
            k = min(left, e['block_size']) if e['block_size'] else left
            recs.append((pk.read_at(e['off'] + s, n, e['encrypted']), k)); blocks.append(k); left -= k
        meta.append((name, blocks))
    data = bytearray(b'DMOJ' + struct.pack('<I', len(recs)))
    for comp, raw in recs: data += struct.pack('<II', len(comp), raw) + comp
    return bytes(data), meta


def answer(data, count):
    """DMOR → [bytes] in job order (a record the decoder left out is empty)"""
    if data[:4] != b'DMOR' or struct.unpack_from('<I', data, 4)[0] != count:
        raise ValueError("the game's Oodle decoder answered for other records than it was given")
    out, at = [], 8
    for _ in range(count):
        n = struct.unpack_from('<I', data, at)[0]; at += 4
        out.append(data[at:at + n] if n not in (0, 0xffffffff) else b'')
        if n not in (0, 0xffffffff): at += n
    return out


def scan(data, label, uepak, stats=None, dump=None):
    """The shader records a decoded package holds. The cooked package keeps each record inline as an LSLG record (the magic, the stage tag,
    a header, a length, the code area, a length, the control section). A record's extent is read from the control section: its own length
    field (magic − 4) and the code length the control holds at +0x704 put the code area's start, which the length field before it must
    repeat. The 4.18 shape (an i32 length in front of the magic) is read too, and a package with no raw record is tried for the zlib streams
    that inflate to one. → [(raw record, stage, shader key)]. stats counts what was seen and why it was refused; dump writes the bytes
    around the first records of a run (a list [budget, directory]) so a run that finds nothing leaves evidence."""
    import bisect
    out, seen = [], set()
    if stats is not None:
        for k in ('lslg', 'ctl', 'paired', 'bad_tag', 'bad_control', 'bad_code', 'bad_length', 'ctl_len_bad', 'code_off_bad', 'code_len_bad', 'lz4'):
            stats.setdefault(k, 0)

    if dump and dump[0] > 0 and 'globalshadercache' in label.lower() and len(stats.get('sample', [])) == 0:
        import pathlib   # the engine's global cache: one package with a record for every shader the game has, the best sample of the layout
        d = pathlib.Path(dump[1]); d.mkdir(parents=True, exist_ok=True)
        i = data.find(b'LSLG')
        if i >= 0:
            a = max(0, i - 32); chunk = data[a:a + 24576]
            (d / 'ue_sample.bin').write_bytes(chunk)
            cols = [m.start() for m in re.finditer(b'LSLG', data)][:40]
            ctls = [m.start() for m in re.finditer(CTL_MAGIC, data)][:40]
            lines = [f'package: {label}', f'slice {a:#x}..{a + len(chunk):#x} ({len(chunk)} bytes), first LSLG at {i:#x}',
                     'LSLG: ' + ', '.join(f'{x:#x}' for x in cols), 'CTL:  ' + ', '.join(f'{x:#x}' for x in ctls), '',
                     'hex (16 bytes a line, offset from the slice):']
            for o in range(0, len(chunk), 16):
                lines.append(f'{a + o:08x}  ' + ' '.join(f'{x:02x}' for x in chunk[o:o + 16]))
            (d / 'ue_sample.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
            stats.setdefault('sample', []).append(label)
            dump[0] -= 1

    def lz4_at(q):
        """The record whose LZ4 block starts a few bytes before the LSLG at q: Unreal keeps each shader as an i32 stored length, an LZ4 block
        (whose first literal run is the record itself, so the token and its literal length sit right before LSLG), an i32 raw length and a u8
        frequency (FShaderMapResourceCode). → (record, frequency) or None. A block that decodes to its raw length as an LSLG record is real."""
        import lz4.block
        for k in range(4):
            t = q - 1 - k
            if t < 8: return None
            tok = data[t]
            if tok >> 4 < 15 and k: continue
            if tok >> 4 == 15 and k:
                if any(x != 0xff for x in data[t + 1:q - 1]) or data[q - 1] == 0xff: continue
            if tok >> 4 < 15 and k == 0 and tok >> 4 < 4: continue
            n = int.from_bytes(data[t - 4:t], 'little')
            if not 8 <= n <= len(data) - t: continue
            raw = int.from_bytes(data[t + n:t + n + 4], 'little')
            if not 0x100 <= raw <= (1 << 27) or t + n + 5 > len(data): continue
            try: d = lz4.block.decompress(data[t:t + n], uncompressed_size=raw)
            except Exception: continue
            if len(d) == raw and d[:4] == b'LSLG': return d, data[t + n + 4]
        return None

    def take(record, at):
        rec = uepak.lslg(record)
        if not rec:
            if stats is not None: stats['bad_length'] += 1
            return
        tag, ctl, code = rec
        st = UE_TAG.get(tag)
        if not st:
            if stats is not None: stats['bad_tag'] += 1
            return
        why = why_bad(st, ctl, code)
        if why:
            if stats is not None: stats['bad_control' if why == 'bad control section' else 'bad_code'] += 1
            return
        seen.add(at); out.append((record, st, hashlib.sha1(ctl[:ctl_len(ctl)] + code).digest()))

    ctl_at = [m.start() for m in re.finditer(CTL_MAGIC, data)]
    if stats is not None: stats['ctl'] += len(ctl_at)
    if stats is not None and ctl_at and data.find(b'LSLG') >= 0 and len(stats.get('hex', [])) < 12:
        i0 = data.find(b'LSLG'); k0 = next((k for k in ctl_at if k > i0), None)
        if k0 is not None:
            u = lambda at: int.from_bytes(data[at:at + 4], 'little')
            stats.setdefault('hex', []).append(f'HEX {label} LSLG@{i0:#x}: {data[i0:i0 + 112].hex()}')
            stats['hex'].append(f'HEX {label} CTL@{k0:#x} pre16={data[k0 - 16:k0].hex()} at20={u(k0 + 0x20):#x} at704={u(k0 + 0x704):#x} head96={data[k0:k0 + 96].hex()}')
    for m in re.finditer(b'LSLG', data):
        i = m.start()
        if stats is not None: stats['lslg'] += 1
        if i in seen: continue
        got = lz4_at(i)
        if got:
            if stats is not None: stats['lz4'] += 1
            take(got[0], i)
            if i in seen: continue
        take(data[i:i + 0x1000] if i + 0x1000 <= len(data) else data[i:], i)   # a stored record: no length in front of it
    if not out:
        for m in ZLIB_HEAD.finditer(data):
            i = m.start(); n = int.from_bytes(data[i - 4:i], 'little') if i >= 4 else 0
            if not 2 <= n <= len(data) - i: continue
            z = zlib.decompressobj()
            try: s = z.decompress(data[i:i + n])
            except zlib.error: continue
            if z.eof and not z.unused_data and s[:4] == b'LSLG': take(s, i)
    return out


class Spool:
    """The unique records on disk (a phone's memory does not hold a game's shaders): add(record, stage) → True when it is new; the spool
    keeps (offset, length, frequency) for the archives"""
    def __init__(self, path):
        self.path = Path(path); self.path.parent.mkdir(parents=True, exist_ok=True)
        self.f = self.path.open('wb'); self.keys = set(); self.entries = []; self.bytes = 0
    def add(self, record, st, key):
        if key in self.keys: return False
        self.keys.add(key)
        self.f.write(record); self.entries.append((self.bytes, len(record), FREQ[st]))
        self.bytes += len(record)
        return True
    def close(self):
        self.f.close(); return self


def write_archives(spool, outdir, per=20000, max_bytes=256 << 20):
    """The spool as the shader code archives shader_split.py reads (uepak.archive version 2, code area = the records in order) → [paths]"""
    outdir = Path(outdir); outdir.mkdir(parents=True, exist_ok=True)
    for old in outdir.glob('*.ushaderbytecode'): old.unlink()
    paths, batch = [], []
    def flush():
        if not batch: return
        path = outdir / f'Inline-{len(paths) + 1:04d}.ushaderbytecode'
        with path.open('wb') as f, spool.path.open('rb') as src:
            f.write(struct.pack('<II', ARCHIVE_VERSION, 0))     # version; no map hashes
            f.write(struct.pack('<I', 0))                        # no shader hashes
            f.write(struct.pack('<I', 0))                        # no maps
            f.write(struct.pack('<I', len(batch)))
            off = 0
            for o, n, fr in batch:
                f.write(struct.pack('<QIIB', off, n, n, fr)); off += n
            f.write(struct.pack('<I', 0))                        # no preload ranges
            f.write(struct.pack('<I', 0))                        # no indices
            for o, n, _ in batch:
                src.seek(o); f.write(src.read(n))
        paths.append(path); batch.clear()
    for entry in spool.entries:
        if len(batch) >= per or sum(n for _, n, _ in batch) + entry[1] > max_bytes: flush()
        batch.append(entry)
    flush()
    return paths


def digest(romfs, picks, uepak):
    """What the archives were made from (the pak's size and mtime, the candidate count): a run that already decoded them reuses them"""
    h = hashlib.sha256()
    for p in uepak.unreal_paks(str(romfs), legacy=False):
        s = os.stat(p); h.update(f'{p}|{s.st_size}|{s.st_mtime_ns}'.encode())
    h.update(f'|{len(picks)}'.encode())
    return h.hexdigest()
