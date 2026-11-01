+++
id = "E619"
claim = "Of the 2464 triangle-host vectors (717 files) of the data repository 2232 carry an image by pixels, 17 by value counts, 117 hung, 19 faulted and 24 wrote no pixel, and only 65 kept a render dump (`--dump-render`) beside them to check a rebuilt scene against, so the plan's \"about 700 dumps\" are dump directories of other tables; the 197 directories named dumps are classified by unit and by what is missing (4 with unit vectors built in 12.0, 96 ready for one, 84 blocked by an open question, 12 usable only as a whole job, 1 already vectors in sgx-sim), and the MTE clipping and depth-range datasets establish a clip volume of z = -w to w, the w clamp word and no x or y clipping rule"
unit = "platform"
method = "offline, no laptop, no new run: tools/usse-asm/pipe_inventory.py reads every *.vec.json of the data repository (a vector with --tri in provenance.options is a triangle-host vector, classified by its readback: failed text, pixels, mixed counts) and every directory named dumps (a table of rules by path), writes doc/specs/pipe-inventory.md; read E063, E194 and E287 and the clipping and depth-range datasets' images (no dumps)"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["vectors-usse", "mte-clipping", "mte-depth-range", "mte-depth-range2"]
terms = []
+++

**Results.** The table of the report: isp 493 triangle-host vectors, mte 218, pbe 206, pds 683, ta
26, texture 213, usse 582, vdm 43 (2464 in all), by unit and outcome. The 197 dump directories by
kind and status are in the report, with the records and questions that each group waits for. The
65 vectors with a render dump are those of `vectors/`; the script tables outside it (ta/tri-region
35, ta/object-format 59, ta/regions, ta/objects) are also rebuildable scenes with a dump to check
against, a caveat on the 65 and not a count of them.

**What the clipping datasets show.** [HW] z is clipped at -w and w (E287); the viewport's z is not
clipped to [0, 1] [infer: E287 calls it inferred from two values a side]; the triangle's size goes
as 1/w and shrinks away below w 1e-5, set by the state block's w clamp word (E194); the two TA
command floats change no clipping scene (E063). [HW] A vertex crossing w = 0 draws and its pixel
counts (1216, 1258, 1273, 1394) are recorded in E063.

**What it does not show.** Any x or y clipping, a guard band, the clipped polygon's vertices; the
arithmetic by which the ISP turns a clipped triangle into pixels (Q205).
