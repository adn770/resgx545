+++
id = "E350"
claim = "Of the 46 USSE forms still open (no passing simulator vector, or no semantics in the simulator), the closed GLES compilers and the closed driver's fixed programs use 14 across the 425 distinct USSE programs of 595 captured runs: phas (form 8) in every program, emitpix1 in 223 and emitpix2 in 224 end-of-tile programs, the four vertex emits (emitmtest, emitmtevtx, emitvcbst, emitvcbvtx) in every vertex program, wdf in 93 programs, wop in 8, ptoff in one program every run holds, smlsi in 24 programs of the shader, input and GLES1 runs, atst8 and pcoeff only where a fragment is discarded or alpha-tested (atst8 also under the GLES1 alpha test), and the dual-issue form 64 only under GLES1 lighting; the other 32 open forms (among them smoa, smr, smbo, imo, setfc, moest, setm, depthf, ldr, str, idf, nop, emitpds, ba and the second phas forms) appear in no captured program"
unit = "usse"
method = "the 13 3D capture tables of 11.11 (604 runs, 595 with programs; the 9 runs the closed stack refused hold none), unpacked with harness/ukernel-extract/cap3d.py and scanned with opscan3d.py: every USSE program state3d.py reaches (the programs each kick's PDS programs start with doutu, and the end-of-tile task), deduplicated by content, each instruction's form by tools/usse-dis --which, open forms from doc/isa/sim-coverage.json and the simulator's list of forms without semantics; names and counts only"
tiers = ["CAP"]
date = "2026-11-03"
data = [
    "render-state-variations", "render-register-gaps", "render-draws-frames-pb",
    "isp-registers", "isp-line-width", "ta-target-sizes", "texture-textures",
    "texture-samplers", "texture-formats", "texture-streams", "usse-shaders", "usse-inputs",
    "usse-gles1-programs",
]
terms = ["Universal Scalable Shader Engine (USSE)"]
+++

**What runs.** `opscan3d.py` over the unpacked runs of all 13 tables. A form counts as open
when no vector of the simulator's coverage passes on it (36 forms) or when the simulator gives it
no semantics (10 more, by name): 46 forms. A program is counted once however many runs hold it.

**Results.** 425 distinct USSE programs; 14 of the 46 open forms occur.

| form | name | programs | uses | runs | where |
|---|---|---|---|---|---|
| 8 | phas | 425 | 515 | 595 | every program |
| 10 | emitpix1 | 223 | 223 | 595 | end-of-tile programs |
| 11 | emitpix2 | 224 | 224 | 595 | end-of-tile programs |
| 150 | emitmtest | 8 | 8 | 595 | vertex programs |
| 151 | emitmtevtx | 41 | 41 | 595 | vertex programs |
| 152 | emitvcbst | 8 | 8 | 595 | vertex programs |
| 153 | emitvcbvtx | 41 | 41 | 595 | vertex programs |
| 7 | wdf | 93 | 94 | 595 | all tables |
| 143 | wop | 8 | 8 | 595 | all tables |
| 155 | ptoff | 1 | 1 | 595 | one program every run holds |
| 136 | smlsi | 24 | 49 | 134 | shaders, inputs, GLES1, discard with depth |
| 156 | atst8 | 3 | 3 | 5 | the three discard runs, GLES1 `alpha_less` and `alpha_greater` |
| 154 | pcoeff | 2 | 2 | 3 | `fs_discard`, `fs_discard_alpha`, `discard_depth` (the discard runs) |
| 64 | dual | 2 | 3 | 3 | GLES1 `light`, `light_tex`, `light_vcolor` |

The 223 and 224 end-of-tile programs are one shape with the PBE words of each target size and
format; the counts differ by one program, which the scan does not name. `smlsi` is absent from the
base triangle's programs and present in every program set of the shader corpus and the GLES1 runs
listed in the scan. Unused: forms 9, 159 and 160 (`phas`), 12 (`ba`), 14 and 15 (`bexception`),
38, 39, 147 and 148 (`str`), 145 and 146 (`ldr`), 66 (`dual`), 121 and 123 (`smp` with `drc`), 128
(`nop`), 129-136 apart from 136 (`smoa`, `smr`, `smlsi` form 131, `smbo`, the MOE forms 129-135),
137 (`imo`), 138 (`setfc`), 139 (`moest`), 140 (`idf`), 141 (`wdf` form 141), 142 (`setm`), 144
(`lock`), 149 (`emitpds`), 157 (`depthf`).

**What it shows.**

- The forms a hardware run must settle first for the closed compiler's programs to run in the
  simulator are `phas`, the emits, `wdf`, `wop`, `ptoff` and `smlsi`: every captured program
  uses at least one of them [CAP].
- `atst8` and `pcoeff` belong to fragment discard and the alpha test only, so a discard shader
  is the case that would exercise them [CAP]; the GLES1 lighting programs are the only users of a
  dual-issue form.
- The MOE group but `smlsi`, `setfc`, `moest`, `setm`, `depthf`, the loads and stores and `idf`
  are not used by the closed compilers for any feature these lists exercise.
