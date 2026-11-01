#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Decode the TA/3D kick the closed Cedarview GLES2 stack submits (harness "3D capture").

fakedrm.c dumps each SGX_DOKICK's IN buffer (kickNN_in.bin) and a snapshot of every
device object at that moment (kickNN/objects.txt + objNNN_<dva>.bin). This module decodes
the VDM control stream and walks the pointers from the kick, with the structure layouts of
kick3d.py, to give every object it reaches a role.

- The VDM control stream words: block type in bits 31:30 (link, state, index list,
  terminate). A state block is two words: the PDS program address >> 4 in bits 27:0
  with last-task (29) and complex (28) flags, then (when not complex) the PDS data
  size in 16-byte units
  (31:26), SD (25), fence (18), MTE emit (17), USE pipe (15:13), partial (12),
  partitions (11:9), secondary (8) and the USE attribute size in 16-byte units (7:0).
  An index list header holds the primitive type (29:26), presence bits for its third
  and fourth words (22, 23) and the index count (21:0); its second word is the index
  base address. The block ends with the two words of its vertex task
  (decode_vertex_pds).

    usage: kickwalk.py <kickNN_in.bin> <kickNN/>      # decode one captured kick
"""
from __future__ import annotations

import pathlib
import re
import struct
import sys

from kick3d import FLAG_WORDS, decode, flag_names, offset, size


# --- VDM control stream ----------------------------------------------------------------

VDM_TYPES = ("LINK", "STATE", "INDEXLIST", "TERMINATE")
VDM_PRIMS = {0: "triangles", 1: "lines", 2: "points", 3: "strip", 4: "fan",
             5: "edge triangles", 6: "line strip", 8: "complex triangles", 9: "complex lines",
             10: "complex points", 11: "complex strip", 12: "complex fan",
             14: "complex line strip"}
STATE_W1_FLAGS = ((29, "last task"), (28, "complex"))
STATE_W2_FLAGS = ((25, "SD"), (24, "debug"), (18, "fence"), (17, "MTE emit"), (12, "partial"),
                  (8, "secondary"))


def decode_vertex_pds(w1: int, w2: int) -> dict:
    """The vertex task words that close an index list block [CAP]: the partition size
    (31:28) and the PDS program address >> 4 (27:0); then the output vertex size in
    4-dword units (31:24: 1 for a position, 2 with a varying or a point size), bits 23:22
    (3 in every capture), the USE attribute size in 16-byte rows (14:7: one row per
    vertex attribute) and the PDS data size in 16-byte rows (6:0)."""
    return {"pds_base": (w1 & 0x0FFFFFFF) << 4, "partitions": w1 >> 28, "word2": w2,
            "vertex_dwords": 4 * (w2 >> 24), "advance": (w2 >> 22) & 3,
            "use_attr_bytes": 16 * ((w2 >> 7) & 0xFF), "data_bytes": 16 * (w2 & 0x7F)}


def decode_vdm(words: list[int], limit: int = 4096) -> list[dict]:
    """Walk a VDM control stream from its first word to the first terminate block."""
    out, i = [], 0
    while i < len(words) and len(out) < limit:
        w = words[i]
        kind = VDM_TYPES[w >> 30]
        b = {"offset": i, "type": kind, "word": w}
        if kind in ("STATE", "TERMINATE") and (w & 0x0FFFFFFF) and i + 1 < len(words):
            w2 = words[i + 1]
            flags = [n for bit, n in STATE_W1_FLAGS if w >> bit & 1]
            b.update(pds_base=(w & 0x0FFFFFFF) << 4, word2=w2, words=2, flags=flags)
            if "complex" in flags:        # complex geometry: word 2 has another layout
                b.update(data_bytes=None, use_attr_bytes=None, use_pipe=None, partitions=None)
            else:
                b.update(data_bytes=(w2 >> 26) * 16, use_attr_bytes=(w2 & 0xFF) * 16,
                         use_pipe=(w2 >> 13) & 7, partitions=(w2 >> 9) & 7)
                flags += [n for bit, n in STATE_W2_FLAGS if w2 >> bit & 1]
        elif kind == "INDEXLIST":
            n = 2 + (w >> 22 & 1) + (w >> 23 & 1)
            b.update(primitive=VDM_PRIMS.get(w >> 26 & 0xF, f"type{w >> 26 & 0xF}"),
                     count=w & 0x3FFFFF, words=n + 2,
                     index_base=words[i + 1] if i + 1 < len(words) else None,
                     extra=words[i + 2:i + n])
            if i + n + 1 < len(words):
                b["vertex"] = decode_vertex_pds(words[i + n], words[i + n + 1])
        elif kind == "LINK":
            b.update(words=1, target=(w & 0x3FFFFFFF) << 2)
        else:
            b.update(words=1)
        out.append(b)
        if kind == "TERMINATE":
            break
        if kind == "LINK":       # a link continues elsewhere; the walker does not follow it
            break
        i += b["words"]
    return out


# --- walking the object graph -------------------------------------------------------------

class Snapshot:
    """A capture snapshot directory: objects.txt + objNNN_<dva>.bin."""

    LINE = re.compile(r"\s*(\d+) heap=(\d+)\s+(\S+)\s+dva=([0-9a-f]+) size=(0x[0-9a-f]+) "
                      r"mapped=(0x[0-9a-f]+) attribs=([0-9a-f]+) kind=(\d+)")

    def __init__(self, path):
        self.path = pathlib.Path(path)
        self.objs = []
        for line in (self.path / "objects.txt").read_text().splitlines():
            m = self.LINE.match(line)
            if m:
                k, heap, hname, dva, sz, mapped, attribs, kind = m.groups()
                self.objs.append({"index": int(k), "heap": int(heap), "heap_name": hname,
                                  "dva": int(dva, 16), "size": int(sz, 16),
                                  "mapped": int(mapped, 16), "attribs": int(attribs, 16),
                                  "kind": int(kind),
                                  "file": self.path / f"obj{int(k):03d}_{dva}.bin"})
        self._cache = {}

    def find(self, dva: int):
        for o in self.objs:
            if o["dva"] <= dva < o["dva"] + o["mapped"]:
                return o
        return None

    def by_handle(self, handle: int) -> int:
        k = handle - 0x4D410000
        for o in self.objs:
            if o["index"] == k:
                return o["dva"]
        raise KeyError(hex(handle))

    def data(self, o) -> bytes:
        """An object's bytes; a missing file reads as zeros (copies of a capture may drop
        the all-zero parameter buffer pages)."""
        if o["index"] not in self._cache:
            f = o["file"]
            self._cache[o["index"]] = f.read_bytes() if f.exists() else bytes(o["mapped"])
        return self._cache[o["index"]]

    def read(self, dva: int, n: int) -> bytes:
        o = self.find(dva)
        if o is None or dva + n > o["dva"] + o["mapped"]:
            raise KeyError(hex(dva))
        off = dva - o["dva"]
        return self.data(o)[off:off + n]


# Pointer fields of each structure that the walker follows or records: field -> (role,
# structure to decode there or None). Only fields kick3d.py names (a record gives them).
POINTERS = {
    "cmd_ta": {
        "hw_pb_desc_dev_vaddr": ("parameter buffer descriptor", "hw_pb_desc"),
        "hw_render_details_dev_vaddr": ("render details", "hw_render_details"),
        "dst_sync_list_dev_vaddr": ("destination sync list", "SGXMKIF_HWDEVICE_SYNC_LIST"),
        "hw_rt_data_dev_vaddr": ("render target data (this kick)", "hw_rt_data"),
        "ta_registers.vdm_ctrl_stream_base": ("VDM control stream", "VDM"),
        "ta_registers.te_psgregion_addr": ("TE region headers (PSG)", None),
        "ta_registers.te_tpc_addr": ("TE tail pointer cache", None),
        "ta_registers.bif_ta_req_base": ("TA requestor base (parameter heap)", None),
    },
    "hw_render_context": {
        "ccb_base_dev_vaddr": ("TA client CCB", None),
        "ccb_ctl_dev_vaddr": ("TA client CCB control", None),
        "hw_pb_desc_dev_vaddr": ("parameter buffer descriptor", "hw_pb_desc"),
    },
    "hw_pb_desc": {
        "page_table_base": ("DPM page table (parameter buffer pages)", None),
        "first_block_dev_vaddr": ("parameter buffer block", "pb_block"),
    },
    "hw_render_details": {
        "registers_3d.bif_3d_req_base": ("3D requestor base (parameter heap)", None),
        "registers_3d.isp_region_header_base": ("ISP region headers", None),
        "registers_3d.event_pixel_pds_code": ("end-of-render PDS program (pixel event)", "PDS"),
        "access_dev_vaddr": ("render details access word", None),
        "rt_patch_list_dev_vaddr": ("render target patch list", None),
        "pds_bgnd_list_dev_vaddr": ("background object PDS word list", None),
    },
    "hw_rt_data": {
        "bgobj_dev_vaddr": ("background object", None),
        "dpm_state_dev_vaddr": ("DPM context state", None),
        "dpm_control_dev_vaddr": ("DPM context control", None),
        "otpm_dev_vaddr": ("OTPM", None),
        "rt_status_dev_vaddr": ("render target status word", None),
    },
}


def _pds_data_dwords_3d(d: dict) -> int:
    # The pixel event PDS data size counts rows of four dwords (the data segment comes first).
    return 4 * d["registers_3d.event_pixel_pds_data"]


def walk(kick_in: bytes, ccb_dva: int, mem) -> list[dict]:
    """Roles of everything reachable from one kick. mem.read(dva, n) -> bytes."""
    roles: dict[int, dict] = {}

    def add(dva, role, struct_name=None, **extra):
        if not dva:
            return None
        if dva in roles:
            roles[dva].setdefault("aliases", []).append(role)
            return None
        roles[dva] = {"dva": dva, "role": role, "struct": struct_name, **extra}
        return roles[dva]

    def visit(dva, role, struct_name):
        r = add(dva, role, struct_name)
        if r is None or struct_name is None or struct_name in ("VDM", "PDS"):
            return r
        try:
            d = decode(struct_name, mem.read(dva, size(struct_name)))
        except (KeyError, ValueError):
            return r
        r["fields"] = d
        follow(struct_name, d)
        return r

    def follow(struct_name, d):
        for field, (role, target) in POINTERS.get(struct_name, {}).items():
            dva = d.get(field)
            if target == "VDM":
                vdm_stream(dva)
            elif target == "PDS":
                add(dva & ~0xF, role, "PDS", pds_data_dwords=_pds_data_dwords_3d(d))
            else:
                visit(dva, role, target)

    def vdm_stream(dva):
        r = add(dva, "VDM control stream", "VDM")
        if r is None:
            return
        words = []
        try:
            raw = mem.read(dva, 4)
            n = 4
            while n <= 0x1000:              # read as far as the object allows
                try:
                    raw = mem.read(dva, n * 2)
                    n *= 2
                except KeyError:
                    break
            words = list(struct.unpack(f"<{len(raw) // 4}I", raw))
        except KeyError:
            return
        r["blocks"] = blocks = decode_vdm(words)
        for b in blocks:
            if "pds_base" in b:
                n = b["data_bytes"] // 4 if b["data_bytes"] is not None else None
                add(b["pds_base"], f"PDS state program (VDM word {b['offset']})", "PDS",
                    pds_data_dwords=n)
            if b["type"] == "INDEXLIST" and b.get("index_base"):
                add(b["index_base"], f"index buffer (VDM word {b['offset']})", None)
            if b.get("vertex"):
                v = b["vertex"]
                add(v["pds_base"], f"PDS vertex program (VDM word {b['offset']})", "PDS",
                    pds_data_dwords=v["data_bytes"] // 4)

    k = decode("PVRSRV_BRIDGE_IN_DOKICK", kick_in)
    cmd_dva = ccb_dva + k["sCCBKick.ui32CCBOffset"] - offset("cmd_ta", "shared")
    cmd = add(cmd_dva, "TA command (cmd_ta)", "cmd_ta")
    try:
        d = decode("cmd_ta", mem.read(cmd_dva, size("cmd_ta")))
        cmd["fields"] = d
    except (KeyError, ValueError):
        d = None
    visit(k["sCCBKick.sCommand.ui32Data"][1], "HW render context", "hw_render_context")
    if d:
        follow("cmd_ta", d)
    for kind in ("TA", "3D"):
        n = k[f"sCCBKick.ui32Num{kind}StatusVals"]
        for i, (addr, value, _h) in enumerate(k[f"sCCBKick.as{kind}StatusUpdate"][:n]):
            add(addr, f"{kind} status word [{i}] (EDM writes {value:#x})", None)
    return list(roles.values())


# --- report ------------------------------------------------------------------------------

def report(kick_in: bytes, snap: Snapshot) -> str:
    k = decode("PVRSRV_BRIDGE_IN_DOKICK", kick_in)
    out = ["SGX_CCB_KICK:"]
    for f, v in k.items():
        if f.startswith("sCCBKick.as") and f.endswith("StatusUpdate"):
            n = k[f.replace("as", "ui32Num", 1).replace("Update", "Vals")]
            v = [f"*{a:#010x}={b:#x}" for a, b, _ in v[:n]]
        elif f == "sCCBKick.ahSrcKernelSyncInfo":
            v = v[:k["sCCBKick.ui32NumSrcSyncs"]]
        out.append(f"  {f:44s} {_fmt(v)}")
    ccb = snap.by_handle(k["sCCBKick.hCCBKernelMemInfo"])
    for r in sorted(walk(kick_in, ccb, snap), key=lambda r: r["dva"]):
        o = snap.find(r["dva"])
        where = (f"obj {o['index']} {o['heap_name']}+{r['dva'] - o['dva']:#x}" if o
                 else "not in any object")
        also = f"  (also: {'; '.join(r['aliases'])})" if r.get("aliases") else ""
        out.append(f"\n{r['dva']:#010x} {r['role']} [{where}]{also}")
        flag_words = FLAG_WORDS.get(r.get("struct"), {})
        for f, v in r.get("fields", {}).items():
            if f in flag_words and isinstance(v, int):
                v = f"{v:#x} {flag_names(flag_words[f], v)}"
            if isinstance(v, list):
                while v and not (v[-1] if isinstance(v[-1], int) else any(v[-1])):
                    v = v[:-1]                  # drop unused trailing entries
            if _interesting(f, v):
                out.append(f"    {f:44s} {_fmt(v)}")
        for b in r.get("blocks", []):
            out.append("    " + _fmt_block(b))
    return "\n".join(out)


def _interesting(field, v) -> bool:
    if isinstance(v, list):
        return any(x if isinstance(x, int) else any(x) for x in v)
    return bool(v) if not isinstance(v, str) else True


def _fmt(v) -> str:
    if isinstance(v, int):
        return f"{v:#x}"
    if isinstance(v, list):
        return "[" + ", ".join(_fmt(x) for x in v) + "]"
    return str(v)


def _fmt_block(b: dict) -> str:
    s = f"[{b['offset']:3d}] {b['type']:9s} {b['word']:#010x}"
    if "pds_base" in b and b["data_bytes"] is None:
        s += f" pds={b['pds_base']:#010x} word2={b['word2']:#010x} {' '.join(b['flags'])}"
    elif "pds_base" in b:
        s += (f" pds={b['pds_base']:#010x} data={b['data_bytes']}B "
              f"attr={b['use_attr_bytes']}B pipe={b['use_pipe']} {' '.join(b['flags'])}")
    if b["type"] == "INDEXLIST":
        s += (f" {b['primitive']} count={b['count']} base={b['index_base']:#010x} "
              f"extra={_fmt(b['extra'])}")
        if b.get("vertex"):
            v = b["vertex"]
            s += (f" vertex: pds={v['pds_base']:#010x} partitions={v['partitions']} "
                  f"data={v['data_bytes']}B attr={v['use_attr_bytes']}B "
                  f"out={v['vertex_dwords']} dwords")
    return s


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__.strip().splitlines()[-1].strip(), file=sys.stderr)
        return 2
    print(report(pathlib.Path(argv[0]).read_bytes(), Snapshot(argv[1])))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
