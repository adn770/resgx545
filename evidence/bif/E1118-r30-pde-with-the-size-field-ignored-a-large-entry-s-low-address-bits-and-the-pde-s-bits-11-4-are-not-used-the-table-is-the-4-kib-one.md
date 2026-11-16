+++
id = "E1118"
claim = "r30-pde stages f2 and f45 (Q109, the table's layout and address bits, every s0 control passed): over codes 1 to 4 a table laid out with each entry 4 KiB past its block (misalign) and a table at + 0x400 named by the PDE's bits 11:4 with a rotated decoy at + 0 (ptoff) are both read as plain 4 KiB entries from the PDE's page: H-4K held on 8 of 8 rows (f2 6 of 6, f45 2 of 2, held out), H-4K-PTOFF refuted on c4-o, where the 4 KiB index crosses into the real table at entry 256 (`3:0,3:0,1:0,2:0`, H-4K's), and H-MASK-S, H-MASK4K, H-PTOFF-IGN, H-PTOFF-USE and H-SECTION refuted on every row"
unit = "bif"
method = "r30-pde (render/closing-r30-pde), stages f2, f45 of the question-closing pass (round 30, the round 29 kernel plan's N1 session (decision N-4 a): the full flagged session approved by the user 2026-11-16, at most 20 planned faults), dataset render-closing-r30-pde; attempt out/20261116-131809 (scores score-f2.txt, score-f45.txt); on the laptop (host cedar over the travel cable, kernel 7.3.0-resgx545, module srcversion 7CE8E38EDB97FC5EA4F6C90 (linux fork r30-kernel 8bc0877e8603: debugfs vm_pde_addr, vm_pde_size, vm_pde_layout and vm_large; installed and loaded alike, booted once with the user's OK; its KUnit suites passed in the fork's series check on the laptop, 222 of 222 with the debug option), stock firmware, tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7, built on the laptop by lead/build_tool30_laptop.sh), health ~/sgxfive-test-t10; every job a debugfs reset, the row's dbg: knobs written and read back (vm_pde_addr 0x60000000, vm_pde_size, vm_pde_layout), `sgxfive-test-t30 copy --src-addr A --height H --large-copy W` or `fill --dst-addr A --height H --large-copy W` (64 pixels wide, stride 256), the knobs restored; the rows tables/STAGE.txt from gen/make.py, the frozen predictions predictions/STAGE.tsv from gen/pde.py, a port of the fork's sgx_mmu_large.c held to its KUnit values); freezes: FROZEN.sha256 9050a555c5997e08fa476c53e34ac06ac71929a50b5d03cca77aa202778d3830 (47 files), PREDICTIONS.sha256 d8ee143980226f0b0e0092b6946349c79611bf0b5cb41abd1993cb740fdc1d97 (5 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at 42c4de78, resgx545:tools/closing/kit/lib_kit.sh at 42c4de78, resgx545:tools/closing/kit/run_stage.sh at 42c4de78, resgx545:tools/closing/kit/kitscore.py at 42c4de78, resgx545:tools/closing/kit/fake/sudo at 42c4de78, resgx545:tools/closing/kit/fake/timeout at 42c4de78, resgx545:tools/closing/kit/fake/df at 42c4de78, resgx545:tools/closing/kit/fake/modinfo at 42c4de78, resgx545:tools/closing/kit/fake/sha256sum at 42c4de78, resgx545:tools/closing/kit/fake/tool.sh at 42c4de78, resgx545:tools/closing/kit/fake/tool.py at 42c4de78, resgx545:tools/closing/kit/fake/ssh.py at 42c4de78, resgx545:tools/closing/scorekit.py at 42c4de78, resgx545:tools/closing/sessioncheck.py at 42c4de78, resgx545:userspace/libsgxfive/tools/sgxfive-test.c at 42c4de78, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built, 42c4de7855d6f310321cc03fa0780b698a735e4d at built; tools: TOOLSRC.sha256: 253fd15bcb6a0a6381d20aacbb635af1c99d764388f394f9a24dc61266b6418d 42c4de7855d6f310321cc03fa0780b698a735e4d:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=7CE8E38EDB97FC5EA4F6C90; pinned commits named by the session: resgx545 main 42c4de7855d6; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW", "infer"]
date = "2026-11-16"
data = ["render-closing-r30-pde:out/20261116-131809/f2/", "render-closing-r30-pde:out/20261116-131809/f45/", "render-closing-r30-pde:fold/"]
terms = ["CR_BIF_DIR_LIST_BASE0"]
+++
**What ran.** f2 (codes 1-3) and f45's last two rows (code 4): one copy over large page 0's end
into page 1 with the table laid out misalign (entry k = block k + 4 KiB, two blocks) and one with
ptoff (the dense table at + 0x400, the PDE's bits 11:4 = 0x40, a decoy naming the blocks rotated
by one at + 0), all held out (README, pre-run; same attempt and module as E1117).

**Frozen verdict (as printed).** f2: `H-4K: the size field is ignored: 4 KiB entries, entry va /
4 KiB (6 of 6 rows decided)`; `H-4K-PTOFF ... is not supported: 2 held, 1 FAILED`; H-MASK-S,
H-MASK4K, H-PTOFF-IGN, H-PTOFF-USE 0 held, 3 FAILED each; H-SECTION and H-FAULT 0 held, 6 FAILED.
f45 (with E1117's rows): H-4K 8 of 8; H-4K-PTOFF, H-MASK-S, H-MASK4K, H-PTOFF-IGN, H-PTOFF-USE 0
held, 1 FAILED each. The frozen rule: `Q109 CLAUSE 2: moot: no named code translates (as 4 KiB)`.

**Results [HW].** Misalign, codes 1-4: `3:0` in every 4 KiB (the trap entries from index 2 on).
Ptoff: c1-o `1:0,3:0,3:0,3:0` (decoy entry 2), c2-o and c3-o `3:0` x 4, c4-o `3:0,3:0,1:0,2:0`
(entries 254 to 257: the trap twice, then the real table's blocks 0 and 1). No fault, the table
intact, nothing changed.

**What it shows.** The PDE's bits 11:4 do not offset the table (c4-o: the 4 KiB index reached
the real table only by counting past entry 255 from the page's start); with the size field not
taken, the table's layout and address bits are those of 4 KiB entries, so clause 2 of Q109 has
no large-page layout to measure.

**What it does not show.** H-4K and H-4K-PTOFF agree on c1-o and c2-o; only c4-o tells them
apart, one row. Whether an entry's bits 11:1 carry anything for 4 KiB entries is outside these
rows (the entries were address | VALID).
