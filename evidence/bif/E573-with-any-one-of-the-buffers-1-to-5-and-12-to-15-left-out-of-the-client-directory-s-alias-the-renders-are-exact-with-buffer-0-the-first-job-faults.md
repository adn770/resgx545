+++
id = "E573"
claim = "With the read-only alias of the EDM's buffer left out of the client directory one buffer at a time, the renders are exact for each of the buffers 1, 2, 3, 4, 5, 12, 13 and 14 (2 of 2 runs each, 2 renders a run), for the mask bit 15, which names no buffer of the debugfs layout (ids 0 to 14), and for the pairs 6+7, 8+10, 10+11 and the five 6, 7, 8, 10, 11 together (2 of 2 each); with buffer 0 (0x30000000) left out the first job faults (2 of 2: BIF fault status 0x91000 at 0x3000b022) and the context is lost; the directory the faulting kick used is list 2 (BASE2 equals the page directory of the fault line, BASE1 holds the health triangle's), and the debugfs layout's pd_phys, 0x28b0c000, equals CR_BIF_DIR_LIST_BASE15 (the EDM's own directory) and differs from BASE1 in 30 of 30 runs"
unit = "bif"
method = "script bif-alias, on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion 5AD04F33F6BCDA7B880E238 (installed equal to loaded at the start of every script, never reloaded), stock firmware (own_arm off), tool sgxfive-test-1126 (sha256 751f7223c8c731a08d75cfc3920a5d1050488ca3bdc426be45b7c431e600f82e, unchanged), no kernel or module change, no reboot, no clock-gate register written: debugfs alias_skip written to the mask after a reset and a drawing health triangle, then tri -n 2 --keep-going --wait-ms 6000 under regtimeline (0 s, lead 0.3 s, registers 0x0c00-0x0c8c), the debugfs layout read 2.5 s into the run, the mask put back to 0 and the GPU reset after each case; 15 cases twice, the risky ones (buffers 0 to 5) after the others"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["bif-alias-skip"]
terms = ["CR_BIF_DIR_LIST_BASE1", "CR_BIF_BANK0", "ta3d_ctl"]
+++

**What ran.** 30 case runs (15 cases x 2): the control (mask 0), the mask bits 12, 13, 14 and 15,
the pairs 6+7 (0xc0), 8+10 (0x500), 10+11 (0xc00), the five 6, 7, 8, 10, 11 (0xdc0), and buffers 0,
1, 2, 3, 4, 5, the last six in a script of their own, one case at a time with a reset and a health
triangle between. The kernel's alias made at the VM's first render context leaves a buffer out
when its bit is set (E457). The debugfs layout of every case lists 15 buffers, ids 0 to 14: the
bit 15 names none of them, so its two runs are controls of the mask rather than a buffer left out
(whether the kernel's table has a sixteenth entry is not read here); 14 buffers were tested.

**Results.** [HW] 28 of 30 case runs: `tri: 2 renders ok`; the regtimeline shows the first kick of
the VM write its page directory into list 2 (BASE2, 0x0c3c) in each, while list 1 (BASE1, 0x0c38)
holds a directory from the first sample on, the health triangle's before it (E360). Buffer 0 (the
first of the heap 0x30000000: the EDM's code heap in the layout): `tri: FAILED after 0 renders`,
`job faulted, context lost`, the bus interface's fault status 0x91000 at 0x3000b022 (inside buffer
0) in the 2 of 2 runs. The faulting kick wrote list 2 like the 28 exact runs: BASE1 holds the
health triangle's directory from the first sample (0x685d000 and 0x13d8d000), BASE2 gets 0x685c000
(0x2b4fe000) by the sample that shows the fault (one sample earlier in the first run, the same one
in the second), and kernel.log prints that same
directory in the fault line (the driver reads it from the register: the register agreeing with
itself, as in E457). H76-A (declared: the buffers 0 to 5 each fault, 12 to 15 not) was right in 20
of 30 case runs (the 18 safe ones and the 2 of buffer 0) and wrong in the 10 of buffers 1 to 5; the
null (every single buffer exact) is right in 28 of 30. The declared H76-N rows of the risky cases
were written by a generator error as a copy of H76-A's and are not used. CR_BIF_BANK0 (0x0c78)
took the values 0x101f, 0x1022, 0x102f, 0x2022 and 0x202f over the renders (INDEX_TA and INDEX_EDM
2 at 0x1022 and 0x2022), and 0, 0xf, 0x101f and 0x1022 in the faulted runs before the fault, not
only 1 (E457): the low byte differs with the sampling instant [infer].

**The directory.** [HW] The debugfs layout's pd_phys read 0x28b0c000 in every run and that is the
value of CR_BIF_DIR_LIST_BASE15 (0x0c70), the EDM's own directory (E360). BASE1 differs from
it in 30 of 30 runs: H76-D (declared: BASE1 equals the layout's pd_phys at the render's end,
taking pd_phys for the client's directory) is refuted, 0 of 30, because its premise was wrong,
pd_phys is the EDM's directory; it was not unscored. The client's directory is the list the kick
writes. Correction (11.34): this paragraph said that no existing debugfs file shows the client's
directory, so that "list 2 holds the client's directory" was not compared with the client's own.
That was wrong: debugfs render_words has shown the client's directory as `ctx:2` since 11.17 and
E360 compared it with BASEk in 11.19; the comparison was possible in these runs and was not made
(E592 makes it after a reset, with BASE1). The measurements above are unchanged.

**Not shown.** Which buffers beyond 0 and 9 the TA, the 3D and the PB load use together (a pair of
the buffers 1 to 5 was not run); the larger scenes and the partial render under a mask; what
buffer 0's page 0xb000 holds. The dmesg lines the script printed after each case were not scoped
to the case (the run's journal in kernel.log is: 2 BIF fault lines).
