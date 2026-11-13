+++
id = "Q036"
question = "what do the DPM's status words hold (0x0748 bit by bit, CR_DPM_3D_PAGE_COUNTS' high half, and the owner words 0x0700 to 0x0728 a kept owner changes), what do CR_DMS_CTRL bits 2:0 and the signature and settle registers report about the two pipes, and what DPM or page-table-builder state does a base-only builder fault leave that a core reset does not clear?"
unit = "vdm"
kind = "hw"
value = "medium"
phase = 10
evidence = ["E153", "E160", "E184", "E200", "E201", "E256", "E309", "E310", "E312", "E316", "E358", "E362", "E438", "E443", "E446", "E448", "E451", "E453", "E458", "E462", "E463", "E574", "E626", "E630", "E631", "E1019", "E1032"]
terms = ["Dynamic Parameter Management (DPM)", "Parameter Buffer (PB)", "ta3d_ctl", "hw_pb_desc.page_table_base", "CR_DMS_CTRL", "hw_pb_desc.pb_flags", "FRAG_FLAGS.BIT2", "FRAG_FLAGS.NO_DEALLOCATE"]
+++

What the four free-list status registers hold after a 3D is answered (E309): STATUS1 holds the
list's tail page in its high half and its head in the low half, STATUS2 the page before the tail
in its low half; during the TA the head rises as pages are taken (E312).

Narrowed by E358 (timelines through one to three renders on a context at 64x64 to 256x256 and a
1024x768 render with partial renders, two runs): the STATUS2 registers' high halves read 0
throughout; 0x0748 reads 0x1f idle and clears one bit while one step runs (bit 4 while the TA
takes pages, bit 0 at a PB load, bit 1 for about 10 us before each page the 3D frees, bit 3 at the
out-of-memory event; bit 2 never cleared); 0x072c reads 0x10001 from the TA's first page to the
3D's last free; `CR_DPM_3D_PAGE_COUNTS` holds 2 at 64x64, 3 at 128x128, 5 at 256x256, a high half
of 1 at 128x128 and 256x256 (0x10003, 0x10005), its low half the pages a job used (E310) [infer].
TA3DCtl dword 36 reads 0 after the partial renders again.

What is open: whether STATUS2's high half ever holds anything; what 0x0748 bit 2 marks; and how
dword 36 follows the global list's pages against E160's reading of the abort.

To settle it: a timeline of the DPM registers (0x0710, 0x071c, 0x0748, `CR_DPM_3D_PAGE_COUNTS`) at
the finest sampling through a partial render of scenes whose global list holds more than five
pages (more triangles in a bigger parameter buffer than the 0x422 pages that overflow at 1500
vertices), with the runs split by whether 0x0748 bit 2 clears.

Narrowed in 11.16 (E438, 66 jobs, three runs of each case; E443, 12 timelines): the tool's scenes
now hold up to 1500 vertices. After the 42 jobs that completed or overflowed, STATUS2's high halves
(0x0710 and 0x071c) read 0 again, with global lists of up to five pages, and in every sample of the
12 timelines through scenes of 3 to 1500 vertices; TA3DCtl dword 36 reads 2 and 3 after the
4096x4096 jobs of 900 and 1500 vertices in 0x422 pages (global lists of 4 and 5 pages), 1 after the
1024x768 job of 1500 vertices in 0x23 pages and 0 after the other overflows, so it is not always 0
after a partial render; 0x0748 clears bit 2 (the value 0xb) in 4 of the 12 timelines (the three
runs of 300 vertices in 0x100 pages and one of 900 in 0x422) and in none of the other 8. A scene of
300 or more vertices at 4096x4096 in 0x40 or 0x23 pages, or 900 or more in 0x100 pages, hangs where
the one-triangle scene recovers (24 of 24 jobs; Q211). Status: narrowed, not answered; missing:
what makes 0x0748 bit 2 clear, and a scene whose global list holds more than five pages.

Folded in 11.21 from Q067, Q105 and Q106 (retired into this question, and Q106's state page part
into Q045; a fold is not an answer). What the three asked about the closed firmware's and the
kernel's own behaviour (the order of the settle routine's steps, why a context's recovery fails)
is not carried here; their hardware parts are the open points below.

Known from Q067 (E153, E200, E201, E309, E362, E446, E448, E453). The EDM loads a PB descriptor into
the TA or 3D DPM registers, stores the free-list status back and, with flag bit 0, rebuilds the page
table from the block list, one entry per page (E200); the registers read back as these loads leave
them (E201). Before a PB swap on a running pipe the routine at 0x15bc sets `CR_DMS_CTRL` bits 2:0
and polls the other pipe's signature and settle registers (E153). A host lays out a table it builds
itself as one 32-bit entry per page at the base plus four times the page number, previous page in
the high half, next in the low half (E309). With the context page mapped writable for one context
(debugfs alias_ctx_rw, flag bit 0 set) the stores into the table named by the base are four bytes a
page from the base, one dword for each of the 1058 pages of the descriptor, none past them, and the
render is exact, also with flag bit 0 set on the kernel's own table, whose result equals the
kernel's [HW] (E446); a control with the base at the scratch and the flag clear faults the render
and changes 0 to 2 scratch dwords (six runs), so the stores need the flag [HW]; that the page-table
builder makes them is [infer]. With a table the host filled (flag clear) the render completes
exactly (6 of 6) and changes 4 scratch dwords, the ends of the list; with the flag set over the same
table the scratch changes by the same 4 (6 of 6), and over zeros by 1058, so the flag's action
stores them (E453). The table a finished job leaves is not a valid pre-job table (3 of 3 faults).
With flag bit 0 set at the first kick under the kernel's mappings the EDM's write to the render
context's page faults (E362), and E448 kept five timelines of the DPM registers of two contexts on
PBs of their own, not yet read for the settle routine's wait.

Open, from Q067: whether the other pipe is idle once the registers the settle routine polls stop
changing, and whether the builder's result depends on the block list. To settle it: the settle
registers sampled around a PB swap on a running TA with two contexts on PBs of their own,
overlapping (`tri --ctx2 --overlap`), the dump compared with a PB block list that is not the
kernel's.

Known from Q105 (E446, E453, E463). With the page-table base at zeroed scratch pages and flag bit 0
set, the render wrote 1058 scratch dwords in every run and rendered exactly in 3 of 3 runs of E446
and in 2 of 2 runs of E453 that followed a run that had not faulted; it faulted in 5 of 5 runs of
E453 that followed a run that had. After the base alone over zeros (kernel poke pb:4, the flag
clear) faults, exactly the next two jobs fault, whatever they are: the flagged build over zeros (20
of 20), the plain triangle (8 of 8) and the base over the kernel's table (4 of 4); the third
completes (8 of 8). It is the same with a debugfs GPU reset before each job and with none (16
sequences, E463). A fault from an unmapped scene stream leaves nothing (16 of 16 followed by an
exact job), and the flagged build over zeros is exact whenever no base-only fault came before (40 of
40). The BIF faults are status `0x90004`, 44 of 48 at 0x10000051. Three exact renders over a table
the host filled in the kernel's layout came right after a run that faulted, but of another kind than
a base-only fault (an H-table fault; the two runs that poked the flag as well as the base), the
other nine after a run that rendered (E453): after those other kinds no follow-on fault shows [HW].

Open, from Q105: which state of the DPM or the page-table builder (or the bus interface's lists)
the base-only fault leaves for two jobs that a debugfs GPU reset, a core soft reset, does not
clear, and whether a base-only job whose recovery succeeds leaves it. Why the first job after it
recovers and the second does not is the kernel's recovery and is not the target. To settle it: the
base-only job followed by two jobs with the BIF registers (0x0c00 to 0x0cff) and the DPM registers
(0x0600 to 0x0750) read between the jobs, and the context page's table compared before and after.

Known from Q106 (E316, E451, E458, E462). With both contexts alive, a render on a second context
clears the words render flag bit 3 (NO_DEALLOCATE, alone or with bit 2) keeps and is exact (4 of 4
runs); with the first context closed after its render, the same render faults (6 of 6 runs: BIF
fault status `0x90004` at `0x200030c1`, page 0x20003000 through list 1) and the close leaves the
kept words in place (TA3DCtl dwords 20 and 25 both the first context's RT data + 0x18). With bit 2
alone the second render is exact in both cases and dword 20 stays. After a render that
keeps the owner with bit 3 the DPM status registers read 0x0700 and 0x070c = 0x04220003, 0x0710 and
0x071c = 0x421, 0x0724 = 0x00020002 and 0x0728 = 2, where bit 2 alone and no flag leave 0x00020003,
1, 0 and 0 (6 of 6 runs each); the close changes none of the 85 registers 0x0600 to 0x0750 (4 of 4
runs with bit 3) and the second render then faults (9 of 9 runs) with none changing before the
recovery (3 of 3 runs that sampled them all); with the first context open the second render takes
the registers back to 0x00020003, 1, 2 and 0 (5 of 5, E462).

Open, from Q106: what the owner words 0x0700 to 0x0728 hold as owner state, and how a later
render's DPM load uses them. What accesses page 0x20003000 is carried by Q045. To settle it: the
same case with the first context's memory kept and the DPM registers read through the faulting
render.

Narrowed in 11.33 (E574, 36 jobs, three runs of 12 cells of vertices and PB pages at 4096x4096):
the high halves of STATUS2 (0x0710, 0x071c) read 0 in every line again (30 to 1066 lines a job,
readings about 29 us apart; no page count is read here, E438's global lists held up to five
pages), and 0x0748 bit 2
cleared in 5 of the 36 jobs, in one reading each, only at the 0x100-page cells (5 of 15 jobs; 0 of
21 elsewhere), 1 of 3 runs at (300, 0x100) where E443 saw 3 of 3 and 0 of 3 at (900, 0x422) where
it saw 1 of 3. Across the two batches the clearing is not a function of the vertices and pages
alone; 29 of the 36 jobs here ran after a reset, which may be a second variable. A short pulse the
sampling catches by chance [infer] fits it. 450 and 600 vertices in 0x100 pages overflow without a
hang (6 of 6). Status: narrowed, not answered.

Narrowed in 11.38 (E626, E630, E631). TA3DCtl dword 36 is 2 at 900, 1050, 1200 and 1350 vertices
(4 pages in the global list) and 3 at 1500 (5 pages), so the step lies between 1350 and 1500
vertices; "the pages less 2" is a two-point fit that fails at E438's one-page list (dword 36 = 1)
and its one or two pages with 0, so it is not a rule. STATUS2's high halves read 0 in every line
of 65 more timelines (21 of 21 scores). 0x0748 bit 2 clears in a line of 23 of those 65 jobs, 66
lines in all, one reading (about 29 us) each, and in 10 of 16 runs of two cells at 0x100 pages (4
of 8 after a reset, 6 of 8 without); the jobs with many partial renders have the most lines (300
vertices in 0x23 pages, 92 partial renders: 18 lines), but job length is the same variable, and
the jobs the kernel watchdog saw (E630), so a rate that rises with the number of partial renders
is [infer] and not separated from the length. The pool is a FIFO and the walk covers every page
after every render (E626). Open: what the pulse is, the global list above 5 pages, the owner
words' meaning (E631: 0x04000417 does not follow the buffer's size).

Narrowed in round 12 (offline, E1019). STATUS2's high halves are answered: 0 in every kept
closing-pass sample, 285824 timeline lines of 697 jobs (0x0710) and 1594 after-reads (0x071c),
through jobs whose global list reached 6, 7, 11, 13 and 18 pages, the case above five pages that
no earlier record reached; the clause is off the question. 0x0748 bit 2 clears in 195 of 197136
held-out lines; of four frozen rates a rate per partial render ranks first on the held-out jobs at
global counts up to 5 and above, a rate per line, the 0x100-page class and a constant behind it:
[infer] the pulse goes with partial renders, not with the job's length (the confound E626's batch
left), but no rule predicts a line. Open: what bit 2 marks and the other bits of 0x0748,
`CR_DPM_3D_PAGE_COUNTS`' high half, the owner words, and the settle and builder clauses above. A
row that would part bit 2 from the session (E1032 ran it: see below).

Narrowed in round 13 (E1032, 8 jobs on the laptop). One scene (3072x2048, 1500 vertices) at 0, 1, 2
and 4 partial renders, two replicates each: both runs at 0 partial renders read no bit 2 clear
line, and across the six runs with a partial render one clear line in 14 partial renders (a
run of 4 partial renders), 0 at 1 and 2; so bit 2 is not cleared once per partial render, the form
the plan froze (0 of 6 rows held), and a clear is rare (0.07 a partial render here, 0.17 in
E1019's fit). The frozen ranking still put the rate per partial render first (log-loss 2.43
against 4.06 per line and 4.87 constant), which the builder had not expected: it rests on the seven
jobs without a clear, not on the one with. STATUS2's high half read 0 again (8 of 8); 0x0710 peaks
at the buffer's pages less one and 0x0728 at the threshold or the need. Open: what bit 2 marks
(the pulse is shorter than the sampling, or not tied to the render), the other bits of 0x0748,
the owner words, and the settle and builder clauses above.
