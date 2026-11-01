+++
id = "Q015"
question = "why does VDM state word 1 with bits 11:9 = 7 hang the triangle sweep but render in the probe job that sets the same word?"
unit = "vdm"
phase = 6
evidence = ["E060"]
terms = ["VDM_STATE1.BITS11_9"]
+++

The triangle job's state word `vdm:1` is 0x0a022405 (bits 11:9 = 2, E060). The sweep case
`vdm:1^=0xa00` sets it to 0x0a022e05, bits 11:9 = 7. It hangs the job (`job hung, context
lost (Connection timed out)`, 4096 pixels at the sentinel, hash 0xe4364b426cdce325), in the
first run and in the follow-up run (E060).

The probe job `vdm-state1-vdm-state-11-9-7` sets the identical word, `vdm = { 1 = 0xa022e05 }`,
replaces the pixel program by `mov.skipinv.end o0, o0` and reads every pixel back. It does not hang:
it completes and draws a triangle. The pixels it shows are the o0 leftovers of an unwritten
register: 0xff203040 in 3827 pixels and 0xff00ff00 in 269 in the first run, 3911 and 185 in the
follow-up run. So the hang depends on the job, not on the word alone, and the pixel counts vary from
run to run. The other values of bits 11:9 that have a probe agree between sweep and probe (0 removes
the triangle in both; 1 and 6 render).

What differs between the two jobs: the pixel program (the sweep keeps the triangle's own shader,
the probe replaces it), the pixel readback (`--pixels`), and the render dump (`dump_render`).
Which of these makes bits 11:9 = 7 hang is not tested.

To settle it: run the sweep case with the probe's pixel program only, then with the probe's
readback only, then with the render dump only (three jobs, three runs each), and the probe with
the triangle's shader; the combination that hangs names the dependence. The 0xff00ff00
leftover also appears in Q018.
