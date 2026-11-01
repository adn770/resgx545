+++
id = "E592"
claim = "The page directory word of a render context's HW context (debugfs render_words ctx:2, newest context) equals the list register the kick wrote in 15 of 15 jobs: CR_BIF_DIR_LIST_BASE1 after the first kick following a reset (3 of 3 jobs) and never CR_BIF_DIR_LIST_BASE15 (the EDM's own directory, 15 of 15 jobs); the k-th process's context (a new VM each) has it in BASEk for k = 1 to 4 (4 of 4, the lists before unchanged); a second context of the same VM, rendered, adds no list (BASE2 stays 0, 2 of 2); and a partial render (1024x768 on 0x28 pages) under alias_skip masks 0, 0xc0 and 0xdc0 has it in BASE1 (6 of 6)"
unit = "bif"
method = "script dirs (15 jobs), on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion 34729EB82083B1D04B0643E (built from the linux fork's p1135 branch, base 3d9b8bdefe94, tip da1eaeaa1247: commits 46 to 48 as they were before the review's fixes, series check 6 of 6 PASS, KUnit 176/176 with the debug option; installed equal to loaded at the start of every script, loaded once at 04:59:38), stock firmware (own_arm off), tool sgxfive-test-1126 (sha256 751f7223c8c731a08d75cfc3920a5d1050488ca3bdc426be45b7c431e600f82e, unchanged), no reboot, no clock-gate register written (no kreg, no kregnow), reset only through debugfs, regtimeline (sha256 079f63590ce87ff2a1ac5499291e52340ff448d9c5e41942a9420264764de803) on 0x0c00-0x0c8c, tri --words --regs 0x0c34-0x0c74; debugfs alias_skip and render_pb_pages set per case and put back"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["bif-client-directories"]
terms = ["CR_BIF_DIR_LIST_BASE1", "CR_BIF_BANK0", "ta3d_ctl"]
+++

**What ran.** Script dirs, 15 jobs on the laptop: `tri` with the tool's `--words DIR` (debugfs
render_words after each render, the context alive) and `--regs 0x0c34-0x0c74` (a snapshot of the bus
interface's directory list registers before the first render and after each), regtimeline on
0x0c00-0x0c8c beside. 3 jobs d76-one (reset, `tri -n 2`), 4 jobs d76-seq (one reset, then four
processes in a row, no reset between), 2 jobs d76-ctx2 (`tri -n 1 --ctx2`: two contexts of one VM,
both rendered, `tri2` 2 of 2), 6 jobs d76-part (reset, `tri --width 1024 --height 768
--keep-overflow` on 0x28 parameter-buffer pages, debugfs alias_skip 0, 0xc0, 0xdc0, two each; the
tool reports the overflowing scene as a failed job, 44191 of 786432 pixels wrong in all 6, as E464,
and the job's partial renders ran). The 15 jobs are labelled `heldout` in the case table, which is
wrong for three of the four hypotheses: a pilot of the first form of the script on the old module
(5AD04F33, three jobs, 04:33 to 04:35, not data) had shown the PD word in list 1 (BASE1) in 3 of 3
jobs and BASE2 empty in its ctx2 job before the real run, so H76-D, H76-P and H76-S were not blind;
H76-L (list k for the k-th process) was not shown by the pilot. The first form of the script read
render_words and the registers from the shell 2.5 s into the run, when the tool's context was gone;
the script was changed to the tool's own `--words` and `--regs` (run_dirs.sh and recompute_p1135.py
changed after the first hashes, hashes-changed.txt; the declared tables did not change).

**Results.** [HW] In all 15 jobs the PD word (`ctx:2`, SGX_RENDER_CTX_PD, one value a job, page
aligned) equals the list register that the kick wrote: BASE1 (0x0c38) in the 3 of 3 of d76-one, in
the 2 of 2 of d76-ctx2 and the 6 of 6 of d76-part, BASE1, BASE2 (0x0c3c), BASE3 (0x0c40), BASE4
(0x0c44) for the first to the fourth process of d76-seq (the lists before stayed as they were);
BASE15 (0x0c70) held 0x33283000, the EDM's own directory, in all 15 jobs and never the PD. The lists
1 to 14 were all 0 before the first render of the jobs that follow a reset. In d76-ctx2 the second
context took no list of its own: BASE2 and the others stayed 0, while the second context's render
ran (`tri2` 2 of 2), which is what makes BASE2 = 0 meaningful. The tool puts both contexts in one
VM, so that is the design of the job and the only evidence that the first context's PD word is the
second's is BASE2 staying 0: render_words was read for the newest context only, and the first
context's PD word is not in the data. CR_BIF_BANK0's high nibble follows k in the d76-seq jobs
(0x1022, 0x2033, 0x404f), a corroboration of the list's index the record does not otherwise use. The
alias_skip masks (a pair of the buffers 6 and 7, the five 6, 7, 8, 10 and 11) did not change the
list or the partial render. Declared before the runs: H76-D (PD in list 1 after a reset, not in 15),
scored as pd-in-list and pd-eq-base15, right in 3 of 3 and 3 of 3, H76-L (list k for the k-th
process) right in 4 of 4, H76-P (the partial render under masks: list 1) right in 6 of 6, H76-S (two
contexts of one VM, lists 1 and 2) wrong in 2 of 2.

**What this adds to E360.** E360 (11.19) compared the PD word of the k-th context's first kick with
BASEk for k = 1 to 14 in two runs (14 and 16 render contexts alive, one VM each): the first claim of
this record, for k = 1 to 4, is E360's again. What it adds is the cases after a reset with BASE1
holding it in 3 of 3 first-kick jobs and BASE1 to BASE4 in a sequence, the partial render and the
masks (6 of 6), and the second context of one VM taking no list.

**Reading.** [infer] The list a render's kick writes is the client's directory by construction: the
value of the HW context's PD word, which the kernel fills with the VM's directory; the measurement
is the equality of that word with the register. A context whose VM's directory is already in a list
takes no other list (the EDM finds it, Q118) [infer]. This corrects the statements of E457 and E573
(and of Q076 and the 3d spec) that no debugfs file shows the client's directory and that list 1 or 2
was not compared with it: render_words has shown it as ctx:2 since 11.17, E360 compared it in 11.19,
and the comparison was possible in those runs; it was not made. debugfs layout's pd_phys is the
EDM's directory (BASE15), as E573 says.

**Not shown.** Which requestor translates through which list at one time (the TA, the 3D and the PB
load were not told apart), what a job does when its list is given to another directory while it runs
(no switch writes the list registers), larger scenes with more than two renders and a DPM reload
under the masks.
