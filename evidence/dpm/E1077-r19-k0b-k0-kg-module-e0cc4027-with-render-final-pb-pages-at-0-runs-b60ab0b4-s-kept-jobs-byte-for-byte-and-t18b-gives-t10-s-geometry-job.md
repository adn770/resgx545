+++
id = "E1077"
claim = "r19-k0b stages k0 and kg on module E0CC40275493F8AEAD8180B (fork 456404fcffe5, debugfs render_final_pb_pages at its default 0): every control passed and H-SAME held 20 of 20 (k0) and 15 of 15 (kg): the module runs B60AB0B4's kept jobs as they were (3072x2048 probe at P 0x2b6: 1 partial render, 0x0624 0x294, twice; at P 0xe2: 4 and 0xc0; 2048x2048 a0-cal-2048 at P 0x162: tadata dump byte-identical, param dump identical once each stream's repeated terminate words are masked, 1 partial render, page steps 0x51, 0x9d, 0xe8, 0x132; zb-c-ctl's 64x32 depth store byte-identical on t10 and t18b, 2048 drawn), and t18b gives t10's geometry job (tri 1024x768 -n 2 --geometry 1 at P 0x28, two replicates each: the kick overflows with 0x0624 0x6, the final overflows too, final dumps equal, pb:10-13 0x38, 0x6, 0x6, 0); E625's raise held 12 of 12 (TA3DCtl dwords 35, 37, 38 = 0x4, 0x10006, 0x20 after the kick). The first build, r19-k0, stopped at its a0 control on 4 dwords past a stream's end (0x12de30 to 0x12de3c of the param dump: 0xc0000000 kept, 0 then), which the lead took as a stale tail, not the module"
unit = "dpm"
method = "r19-k0b (render/closing-r19-k0b), stages k0 and kg of round 19's S1 (cited/closing19/DECISIONS-R19.md, R19-1 a: S1 gates the round; cited/closing19/plan/rank-round19.md section 2a, its stage k0 split in two so that each stage's rows keep the same files), built on the session kit (resgx545 main 50606dc, data 95df71e98) and frozen before the run (FROZEN.sha256 b0977a4e8fc32bca1d9996feb35a3e9a2675ba27ca28178f9e250ee27a8dcdf1), dataset render-closing-r19-k0b; attempt out/20261114-224248 (scores score-k0.txt, score-kg.txt, the lead's log out/r19-k0b-run.lead.log), 2026-11-14 22:42 to 22:45, run by the lead with the kit's driver over the travel cable, on the laptop (host cedar, kernel 7.3.0-resgx545, module srcversion E0CC40275493F8AEAD8180B, fork 456404fcffe5, installed and loaded alike, stock firmware), tools ~/sgxfive-test-t10 (sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, resgx545 a581c06) and ~/sgxfive-test-t18b (58e7985504d0d3311155d94627da8b8473335d9a843f5610e44731864315b21e, ec50498, recipe lead/build_tool18b.sh with its built line), both under ~/regtimeline (079f63590ce87ff2a1ac5499291e52340ff448d9c5e41942a9420264764de803) over r13-dpm's registers and 0x0620, 0x0668 except the zb-c-ctl rows, the debugfs knob render_pb_pages written per row and restored to 0x422, a reset and the kit's health check around each job; every row replayed on the library mock built from its tool's source before the freeze, and the builder's scene check (the mock patched to dump each render job's VM, debug/scenecheck of the build, not published) gave rgn4 (4623753), t10 and t18b the same a0-cal-2048 job (sha256 61dad21f...) and t10 and t18b the same geometry jobs. k0 (6 jobs): k0-pr1-1/2 and k0-pr4 = r13-dpm pr2-c1/pr2-c4's argv on t10, k0-a0 = r10-dpm a0-cal-2048's (rgn4's) on t10 with --dump-render, k0-z-t10/t18b = r13-zls zb-c-ctl's; kg (4 jobs): tri --width 1024 --height 768 -n 2 --geometry 1 --keep-going --keep-overflow --dump-render --dump-each --words --regs 0x0600-0x0750 at P 0x28, t10 and t18b twice. No stop, fault or hang; the frozen scorer re-run on the kept files is byte-identical (fold/score-k0.txt, fold/score-kg.txt). The lead's decision before it: r19-k0 (render/closing-r19-k0, the same rows with k0-a0's param control the plain sha256, attempt out/20261114-223342) stopped at k0-a0 (rc 24, no fault) after k0-pr1-1 and k0-z-t10 had passed; the lead kept E0CC4027 and had this session built with the param control masked (README.md: a dword 0xc0000000 directly after another is compared as 0, the sha256 of the masked dwords as %08x lines, ed097a08... for r10-dpm's dump and r19-k0's alike)"
tiers = ["HW", "infer"]
date = "2026-11-14"
data = ["render-closing-r19-k0b:out/20261114-224248/k0/", "render-closing-r19-k0b:out/20261114-224248/kg/", "render-closing-r19-k0b:fold/", "render-closing-r19-k0:out/20261114-223342/k0/", "render-closing-r19-k0:fold/"]
terms = ["Dynamic Parameter Management (DPM)", "Parameter Buffer (PB)"]
+++
**What ran.** The round 18 module adds debugfs `render_final_pb_pages` (default 0), a longer free
list for a final render and a TA command that can carry thresholds; at 0 its commits promise every
PB and command as before. Stage k0 reran six jobs whose B60AB0B4 runs are kept (r13-dpm pr2-c1 and
pr2-c4, r10-dpm a0-cal-2048, r13-zls zb-c-ctl, the last on t10 and t18b); stage kg ran the
geometry form at P 0x28, which has no kept twin, on t10 and t18b twice each.

**Frozen verdict (as printed).** `out/20261114-224248/score-k0.txt`: five CONTROL lines PASS
(k0-pr1-1, k0-z-t10, k0-a0, k0-pr1-2, k0-z-t18b); "SUMMARY: k0: H-SAME: H-SAME holds (20 of 20
rows decided)". `score-kg.txt`: "CONTROL k0-geo-t10-1: ovf1 1 (frozen 1), knob 6 (frozen 0x6):
PASS" and the same for k0-geo-t18b-1; "SUMMARY: kg: H-SAME: H-SAME holds (15 of 15 rows
decided)", "SUMMARY: kg: H-E625: H-E625 holds (12 of 12 rows decided)".

**Results [HW].** k0: 1 partial render and 0x0624 0x294 at P 0x2b6 (both), 4 and 0xc0 at 0xe2,
as r13-dpm; a0-cal-2048: 1 partial render, 0x0624 0x140, page steps S2 to S5 0x51, 0x9d, 0xe8,
0x132 as r9-ldpm and r10-dpm, its tadata dump byte-identical and its param dump's masked sha256
ed097a08... equal; its plain sha256 2643d77d... is r19-k0's (below), not r10-dpm's;
zb-c-ctl's depth store sha256 92f04c7c... on t10 and t18b, 2048 drawn and 2048 store dwords
changed. kg: on t10 and t18b alike the geometry kick overflows with 0x0624 0x6 and 1 partial
render, the closing render overflows too (2 partial renders in the job, 0x0624 0x6, 0x26, 0x6,
0x26, 0x6 in the timeline), the final dumps are equal across tools and replicates, pb:10-13 read
0x38, 0x6, 0x6, 0 after the kick and TA3DCtl dwords 35, 37, 38 0x4, 0x10006, 0x20. r19-k0's
stopped a0 (render/closing-r19-k0, fold/NOTES.md): 4 dwords at 0x12de30 to 0x12de3c, page 301,
read 0 where both kept runs have 0xc0000000, the tail of a run of terminate words after a
stream's last entry (7 there, 3 then); nothing else differed.

**What it shows.** With the knob at 0 the module changes none of these jobs: the ZLS store, the
DPM's partial renders and thresholds, the TA data and, but for the 4 words, the parameter buffer
are B60AB0B4's; the round's other sessions may run on it. t18b builds t10's geometry job, so its
rows compare with t10's. E625's raise reading (dword 35 thr0 - 2, 37 1 << 16 | thr0, 38 0x20)
holds on this module and tool. The 4 words are words the job need not write [infer]: the dump is
the whole buffer, not cleared between jobs, and in both kept runs a0 came first in its stage while
in r19-k0 and r19-k0b it ran third, after the same two jobs, and gave the same dump both times;
the fork's knob-0 path builds the same descriptor and command
(2a650d74..456404fcffe5).

**What it does not show.** That the 4 words are stale: no run cleared the buffer first, and the
same dump twice on this module fits a stale tail left by the same jobs before as well as a
module-made one. The mask
hides any change confined to repeated terminate words. The geometry form has no B60AB0B4 twin,
so kg compares tools on this module only.
