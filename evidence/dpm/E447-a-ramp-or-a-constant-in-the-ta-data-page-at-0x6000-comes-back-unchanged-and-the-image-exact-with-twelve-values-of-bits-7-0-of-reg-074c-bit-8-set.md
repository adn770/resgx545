+++
id = "E447"
claim = "With the TA data page at 0x6000 of a 4096x4096 render context filled before the job with a ramp (0xa5000000 plus the word's index) or a constant (0x5a5a5a5a), a 64x64 triangle with CR_DPM_REG_074C written through the TA command (word 167) as 0x0ff, as 0x100, 0x101, 0x102, 0x104, 0x108, 0x110, 0x120, 0x140, 0x180, 0x1ff, 0x155 and 0x1aa (bit 8 with bits 7:0 of 0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0xff, 0x55 and 0xaa) and unpoked draws the exact image in all 17 runs, no fault, and the page reads back as written in 1024 of 1024 words in every run, the TA data's other nonzero page (page 67, 71 words) the same in all"
unit = "dpm"
method = "probes/dpm/ta-data-pattern.toml (ta-data-pattern.sh) on the laptop (direct cable), linux fork ef6ba7cd1b9f with the debug option on: debugfs tadata_fill 'PAGE VALUE [ramp]' written before each sgxfive-test tri (64x64, its context for 4096x4096, one render) with --kpoke-render 1:ta:167=V; the tool's --dump-render copy of the TA data (debugfs render_tadata) compared with python3 with what was written; 17 runs, one per case"
tiers = ["HW", "infer"]
date = "2026-11-07"
data = ["dpm-ta-data-pattern"]
terms = ["CR_DPM_REG_074C", "cmd_ta.dpm_reg_074c"]
+++

**What runs.** E203 and E313 found that with bit 8 of `CR_DPM_REG_074C` set a job reaches
0x20006010 to 0x20006013 (page 0x6000 of the TA data) and that on a context for up to 4096x4096,
which covers the page, it renders exactly; E362 found the TA data equal to an unpoked job's. No
poke reaches the TA data, so what the access reads could not be given a value. debugfs tadata_fill
(linux fork commit 38) fills a page of the next render's TA data just before its kick.

**Results.** Fourteen runs with the ramp (no poke, 0x0ff, and twelve values with bit 8 set: bits
7:0 = 0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0xff, 0x55, 0xaa), three with the
constant (no poke, 0x100, 0x1ff). In all 17: job ok, 0 of 4096 pixels differ, the page 0x6000
of the TA data after the job holds the ramp or the constant in 1024 of 1024 words, no other page
of the TA data holds anything but page 67's 71 nonzero words. The tadata_fill line was taken by
the kernel at each kick (the debugfs file reads empty after).

**What it shows.**

- Bit 8 with any of these twelve values of bits 7:0 (not all 256) writes nothing in the page and
  does not change the picture, with either pattern in the page [HW]. The access E203 saw (four
  bytes at +0x10) is a read, or a write of the value already there (E362); a ramp or constant
  there is no longer that value, so it is a read [infer].
- What it reads does not reach the image or the TA data in any of these runs, and the values of
  bits 7:0 select nothing visible in them [HW].

**What it does not show.** Whether the read reaches a register or the DPM's state (no register was
sampled in these runs); other patterns (a page of addresses, of zero); other pages of the TA data
(the question's place at +0x6010 only); a smaller context, whose TA data does not cover the page
(E203: it faults).

**Provenance.** The campaign read the srcversion of the installed module file (modinfo), not of
the loaded module. The run printed E431D4FEB0F36E3C337AD50 for the installed file; that it was
also the loaded module is inferred (the four runs that print it share one boot, 183 to 511 s of
uptime, after the install, with no reload logged). The kit's env.toml was patched after the runs.
The edm/host-events run, E444, was on an earlier boot with a different installed file. This record
uses tadata_fill (fork commit 38).

The linux series was revised after these runs (tip 01cff214d7d2, the one of the control runs of E445
and E446): the debug switches (kregnow's arm, alias_ctx_rw, render_share_pb, tadata_fill) are
disarmed at a firmware load and at a reset, kregnow's arm, read and write and the host-interrupt
restore run under one lock, a render context that shares a PB holds a reference on its donor until
it is freed, and the cleanup commands and the TA data fill are moved into helpers with the same
order and effect. The scripts of these runs reset the GPU before they arm anything, nothing resets
between the arming and its use, and the shared PB's context is closed before its donor, so the
revision does not change the paths the runs used (read against the diff of the two tips and the
scripts) [infer].
