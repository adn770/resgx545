+++
id = "E1117"
claim = "r30-pde stages s0, f1 and f45 (Q109, module 7CE8E38E, every control passed): a client page directory entry whose size field (bits 3:1) names 16 KiB, 64 KiB, 256 KiB, 1 MiB or 4 MiB (codes 1 to 5), over a dense table of large-page entries, is walked as an ordinary 4 KiB table: entry va / 4 KiB, its address plus va % 4 KiB, the size field ignored; every copy read and every fill wrote the region pages the 4 KiB reading names (H-4K 9 of 9 in f1, 6 of 6 dense rows in f45, fit and held out), none faulted or hung, and the frozen H-DENSE (entry va / S, masked to S) was refuted on all 15 rows, as were H-SECTION and H-FAULT"
unit = "bif"
method = "r30-pde (render/closing-r30-pde), stages s0, f1, f45 of the question-closing pass (round 30, the round 29 kernel plan's N1 session (decision N-4 a): the full flagged session approved by the user 2026-11-16, at most 20 planned faults), dataset render-closing-r30-pde; attempt out/20261116-131809 (scores score-f1.txt, score-f45.txt, score-s0.txt); on the laptop (host cedar over the travel cable, kernel 7.3.0-resgx545, module srcversion 7CE8E38EDB97FC5EA4F6C90 (linux fork r30-kernel 8bc0877e8603: debugfs vm_pde_addr, vm_pde_size, vm_pde_layout and vm_large; installed and loaded alike, booted once with the user's OK; its KUnit suites passed in the fork's series check on the laptop, 222 of 222 with the debug option), stock firmware, tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7, built on the laptop by lead/build_tool30_laptop.sh), health ~/sgxfive-test-t10; every job a debugfs reset, the row's dbg: knobs written and read back (vm_pde_addr 0x60000000, vm_pde_size, vm_pde_layout), `sgxfive-test-t30 copy --src-addr A --height H --large-copy W` or `fill --dst-addr A --height H --large-copy W` (64 pixels wide, stride 256), the knobs restored; the rows tables/STAGE.txt from gen/make.py, the frozen predictions predictions/STAGE.tsv from gen/pde.py, a port of the fork's sgx_mmu_large.c held to its KUnit values); freezes: FROZEN.sha256 9050a555c5997e08fa476c53e34ac06ac71929a50b5d03cca77aa202778d3830 (47 files), PREDICTIONS.sha256 d8ee143980226f0b0e0092b6946349c79611bf0b5cb41abd1993cb740fdc1d97 (5 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at 42c4de78, resgx545:tools/closing/kit/lib_kit.sh at 42c4de78, resgx545:tools/closing/kit/run_stage.sh at 42c4de78, resgx545:tools/closing/kit/kitscore.py at 42c4de78, resgx545:tools/closing/kit/fake/sudo at 42c4de78, resgx545:tools/closing/kit/fake/timeout at 42c4de78, resgx545:tools/closing/kit/fake/df at 42c4de78, resgx545:tools/closing/kit/fake/modinfo at 42c4de78, resgx545:tools/closing/kit/fake/sha256sum at 42c4de78, resgx545:tools/closing/kit/fake/tool.sh at 42c4de78, resgx545:tools/closing/kit/fake/tool.py at 42c4de78, resgx545:tools/closing/kit/fake/ssh.py at 42c4de78, resgx545:tools/closing/scorekit.py at 42c4de78, resgx545:tools/closing/sessioncheck.py at 42c4de78, resgx545:userspace/libsgxfive/tools/sgxfive-test.c at 42c4de78, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built, 42c4de7855d6f310321cc03fa0780b698a735e4d at built; tools: TOOLSRC.sha256: 253fd15bcb6a0a6381d20aacbb635af1c99d764388f394f9a24dc61266b6418d 42c4de7855d6f310321cc03fa0780b698a735e4d:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=7CE8E38EDB97FC5EA4F6C90; pinned commits named by the session: resgx545 main 42c4de7855d6; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW", "infer"]
date = "2026-11-16"
data = ["render-closing-r30-pde:out/20261116-131809/s0/", "render-closing-r30-pde:out/20261116-131809/f1/", "render-closing-r30-pde:out/20261116-131809/f45/", "render-closing-r30-pde:fold/"]
terms = ["CR_BIF_DIR_LIST_BASE0"]
+++
**What ran.** 36 jobs in five stages on one attempt (out/20261116-131809, rc 0, no fault, hang
or stop; README, pre-run). The fork maps a VM_MAP of exactly 4 MiB at vm_pde_addr through a PDE of
size code vm_pde_size over a naturally aligned region of contiguous pages it owns: page 0 the
table, every other 4 KiB tagged `0xa0000000 | slab << 24 | page << 12 | dword`; vm_large reads the
PDE, table and tags back after the job. t30's copy prints, per 4 KiB of its source, the tag it
read (`tags:` lines); vm_large names the pages a fill changed. This record holds s0 (s0-warm: code
5 mapped, its copy reading only the page before the slot, so the 4 MiB region is had right after
the boot; eight controls: the knobs off, exact, vm_large `none`; vm_pde_size 0, the tags of the 4
KiB reading `1:0,2:0,3:0,7:0` and the fill changing the trap page only), f1 (codes 1-3, dense:
copy a over large page 0's end into page 1, fit; copy b over page 1's end into page 2 and the fill
over page 0's end, held out) and f45's dense rows (code 4 as f1; code 5: copy a [4M - 16K, 4M -
8K) fit, copy b [4M - 8K, 4M) and the fill [4M - 16K, 4M) held out).

**Frozen verdict (as printed).** s0: `8 of 8 references passed; s0-warm held`. f1: `H-4K: the
size field is ignored: 4 KiB entries, entry va / 4 KiB (9 of 9 rows decided)`; `H-DENSE ... is
not supported: 0 held, 9 FAILED`; H-SECTION and H-FAULT likewise 0 held, 9 FAILED. f45: `H-4K
... (8 of 8 rows decided)`, H-DENSE 0 held, 6 FAILED, H-SECTION 0 held, 8 FAILED, H-FAULT 0 held,
8 FAILED. Reproduced byte for byte at the fold (fold/reproduce.out). The frozen rule `score.py
q109 out/20261116-131809` prints `Q109 CLAUSE 1 code N: as 4 KiB` for codes 1 to 5.

**Results [HW].** Codes 1-4 dense: both copies read the trap slab's first page (`3:0`) in every 4
KiB, the fill changed it alone; the large-page reading (H-DENSE) predicted the last pages of block
0 and the first of block 1. Code 5: both copies read region page 1023 (the trap entry of 4 KiB
entries 1020 to 1023), the fill changed page 1023 only; H-DENSE predicted pages 1020 to 1023.
Every row completed (`job: ok`), the table page stayed intact, no copy changed the region, and
BIF_INT_STAT read 0x80000 and BIF_FAULT 0 after every job, the idle values the kit's reset
prints. Every vm_large `pde` line is the region's address | code << 1 | VALID with the row's code
(fold/posthoc.txt).

**What it shows.** On the SGX545 BIF the size field of a client directory entry does not change
the walk: the entry names a 4 KiB table whatever bits 3:1 hold, so the large-page sizes of the
CE headers' PDE format are not taken by this core [infer: it holds for client directories through
the transfer's texture reads and pixel writes, the paths these rows used].

**What it does not show.** vm_large prints the directory word the driver computed and stored
(one 32-bit write into the uncached directory page), not a read-back; that the BIF fetched that
word rests on the table it walked being the one the word names, in a region of its own for codes
1 to 3 (fold/FOLD-NOTES.md) [infer]. Codes 4 and 5 used the pooled region 0x2f800000 also used by
other codes; there only the per-job reset and BIF invalidate exclude a cached word [infer]. The
EDM's own directory, render requestors (TA, ISP, PBE) and the kernel directory were not tried.
