+++
id = "E515"
claim = "stad.repeatN and ldad.repeatN move the pointer registers r40 to r55 (r56 to r71 for a load) by the form's increment when they are used and leave the unused ones, for N = 5 to 16: iteration i uses r(b + i) in 10 of 10 plain stad.repeatN [r40,+#0] cases (N = 5, 6, 7 and 9 to 15), and with all sixteen pointers read through a marker, the post-increment form [r40,#K++] moved r(40 + i) by K dwords for i < N and no other pointer in 15 of 15 cases (K = 1: N = 5 to 16; K = 2: N = 8, 12, 16), the pre-increment form [r40,++#K] likewise in 4 of 4 (N = 8, 12, 16 with K = 1; N = 8 with K = 2), and ldad.repeatN r10, [r56,#K++] and [r56,+#0] iteration i loads from r(56 + i) into r(10 + i) in 11 of 11 plain cases (N = 5 to 7, 9 to 16, the destinations not reached holding their markers) and moved r(56 + i) for i < N in 10 of 10 post-increment cases (K = 1: N = 5 to 9, 12, 15, 16; K = 2: N = 8, 12), in a client pixel task"
unit = "usse"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1126 (sha256 751f7223c8c731a08d75cfc3920a5d1050488ca3bdc426be45b7c431e600f82e): probes/usse/repeat-ptrs.toml probes stad-plain (10 cases), stad-post (15), stad-pre (4), ldad-plain (11), ldad-post (10), one campaign run, each SETTLED by the table's hypothesis (the exact set of changed scratch dwords), with the template of E483 and a marker 0xB1B1B1B1 stored 32 dwords past every one of the sixteen pointers of the store (r40 to r55) or load (r56 to r71) set, whatever N, so that the end of every pointer is read from where its marker lands; the hypotheses (written before the run): used pointers move and unused stay; only r40 to r43 move; all sixteen move"
tiers = ["HW"]
date = "2026-11-08"
data = ["usse-repeat-ptrs"]
terms = []
+++

**What runs.** `stad.repeatN [r40,+#0|#K++|++#K], r2` for N = 5 to 7 and 9 to 15 (plain), 5 to 16
(post-increment, K = 1) and 8, 12, 16 (K = 2), 8, 12, 16 (pre, K = 1) and 8 (K = 2); `ldad.repeatN
r10, [r56,+#0], drc0; wdf drc0` for N = 5 to 7 and 9 to 16 and `[r56,#K++]` for N = 5, 6, 7, 8, 9,
12, 15, 16 (K = 1) and 8, 12 (K = 2); r2 to r33 hold 0xA5000002 + n, the sixteen store and sixteen
load pointers 0x100 bytes apart.

**Results.** The set of changed scratch dwords equals the prediction in 50 of 50 cases: for a store
the data r(2 + i) at the dword r(40 + i) holds (post and pre: plus K), and the sixteen markers at 32
dwords past r(40 + i) (post: plus K for i < N; the pointers N to 15 at their start value); for a
load the sixteen destination registers r10 to r25 (the loaded dword 0xD0000400 + 64 i for i < N, the
marker 0xAA55000A + j beyond) and the sixteen markers likewise.

**What it shows.** [HW] On a repeat of five to sixteen the pointer register indexed by iteration is
the one the form increments, for every one of the pointers r40 to r55 (r56 to r71): the pointers
beyond r43 move as r40 to r43 do, and the pointers a repeat does not reach stay (the follow-up of
E483, whose markers covered four pointers). The data address is read for every iteration. All of
this was measured in client pixel tasks (fills), not in firmware tasks.

**What it does not show.** N = 2 to 4 again, N above 16, a pre-increment ldad.repeat, a smlsi before
a repeat of five or more, the pointer value after a faulted job.
