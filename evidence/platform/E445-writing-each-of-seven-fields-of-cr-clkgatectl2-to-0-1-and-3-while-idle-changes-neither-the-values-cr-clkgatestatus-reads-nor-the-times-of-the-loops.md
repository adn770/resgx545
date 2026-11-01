+++
id = "E445"
claim = "With CR_CLKGATECTL2 written through debugfs kregnow, each of seven of its two-bit fields (bits 13:12 and 21:20, the MADD0 and MADD1 fields of the GPL kernel's header, and bits 15:14, 17:16, 19:18, 23:22 and 1:0) at 0, 1 and 3 in turn with the others as the boot leaves them (2), CR_CLKGATESTATUS reads the same five values 0x20, 0x000ccfa0, 0x000fffa4, 0x000fffa7 and 0x000fffff under a floating-point loop, an integer loop, a texture copy and a fill as it does unwritten, the loops take 43.99 to 44.49 ms in all 22 settings written while idle, and the copy and the fill finish with the right pixels; with both MADD fields written at 0, 1 and 3 while a loop ten times as long ran, all six runs hung (job hung, context lost) and the GPU was reset, and the same long loops run with no write at all hung in 6 of 7 runs (floating-point 3 of 3, integer 2 of 3, a plain run 1 of 1; linux fork 01cff214d7d2), so the hang is the long loop's and not the write's"
unit = "platform"
method = "probes/usse/clockgate2.toml (clockgate2.sh) on the laptop (direct cable), linux fork ef6ba7cd1b9f with the debug option on: after a debugfs reset per setting, kregnow 0x0004=V, then four jobs each under regtimeline over CR_CLKGATESTATUS (0x0008) from 50 ms before the job: fills running 1250000 iterations of eight instructions (six fmads, or six integer multiply-adds), a copy and a plain fill; the busy runs write both MADD fields 0.3 s after the tool starts, while 12500000 iterations run (one job each, floating-point or integer); the control (probes/usse/clockgate2-noload-control.toml) runs the same two long loops with no write: three runs of each under regtimeline, and one plain run of the floating-point loop, a debugfs reset and one second before each, kernel 7.3.0-resgx545 at linux fork 01cff214d7d2"
tiers = ["HW", "infer"]
date = "2026-11-07"
data = ["usse-clockgate2", "usse-clockgate2-noload-control"]
terms = ["CR_CLKGATECTL2", "CR_CLKGATESTATUS", "MADD"]
+++

**What runs.** The GPL kernel's register header gives `CR_CLKGATECTL2` two bits per unit and the
boot sets every field to 2 (0x00aaaaaa, E006). debugfs kregnow (linux fork commit 36) writes the
register at any time; the kernel log shows each write and the value it reads back (all 22 settings
read back what was written). Per setting: idle reads of the status, then the four jobs. The values
tried were the unwritten 0x00aaaaaa, the fields at bits 13:12 (MADD0) and 21:20 (MADD1), and those
at bits 15:14, 17:16, 19:18, 23:22 and 1:0, each at 0, 1 and 3. A first run over those fields froze
the laptop until its watchdog reset it, and its output was lost; the fields at bits 3:2 to 11:4
were not run again, and the notes of the second run are written to a file before each write. The
busy runs came last: a loop of 12500000 iterations (about 0.44 s) with both MADD fields written
0.3 s after the tool started, at 0, 1 and 3, one floating-point and one integer run each. The
control came afterwards, on the revised series: the same two long loops with nothing written,
three runs of each under regtimeline (reset and one second before each) and a plain run of the
floating-point loop.

**Results.**

| | jobs | `CR_CLKGATESTATUS` values read | job time |
|---|---|---|---|
| all 22 settings (unwritten, 21 written while idle) | floating-point loop | 0x20, 0x000ccfa0, 0x000fffa7, 0x000fffa4, and 0x000fffff in 3 settings | 44047 to 44488 us |
| | integer loop | the same four and 0x000fffff in 5 settings | 43995 to 44458 us |
| | copy | 0x20, 0x000ccfa0 and, in some settings, 0x000fffa4, 0x000fffa7, 0x000fffff | 651 to 994 us |
| | fill | 0x20, 0x000ccfa0 and, in some settings, 0x000fffa7, 0x000fffff | 639 to 1245 us |
| both MADD fields at 0, 1 and 3 written during a long loop (3 values, both loops, 6 runs) | all six: job hung, context lost | 0x20, 0x000ccfa0, 0x000fffa7, 0x000fffa4 before the hang, 0x000fffff in 3 of the 6 runs (floating-point at 0 and 3, integer at 3), 0 after the hang | no job time; scratch unchanged |

Idle reads were 0x20 in every setting. The values 0x000fffff and 0x000fffa4 come and go between
settings (the unwritten value shows 0x000fffff under the copy and not under the fill); no value
of a field goes with them. The status as the boot leaves it (E365) shows the same set under the
same jobs. In the six busy runs the kernel's log has "job ... hung, recovering" about 0.8 s after
each write, and the 0 the status reads at the end is the GPU after that reset, not a stop of the
loop.

The control, the long loops with no write (kernel at 01cff214d7d2, loaded and installed srcversion
both FC6EB50DEF21E3A6249727F, the same tool): the floating-point loop hung in 3 of 3 runs under
regtimeline and in the plain run ("job hung, context lost", "job N hung, recovering" in the
kernel's log, scratch unchanged), the integer loop hung in 2 of 3 runs and finished in the third
(433976 us); `CR_CLKGATECTL2` read 0x00aaaaaa throughout and the status read 0x000ccfa0 (run 1) or
0x20 after.

**What it shows.** No setting of the fields tried, MADD0 or MADD1 or the others, at 0, 1 or 3,
written while idle, changes what `CR_CLKGATESTATUS` reads or how long a floating-point or integer
loop takes, and every copy and fill finishes exact [HW]. So the status does not tell what the MADD
fields gate, and neither does the speed of arithmetic, for fields written idle [HW]; the two
readings of Q048 (floating-point multiply-add units, or the main cache's arbiter and decompression
unit) are not separated [infer].
- A loop of 12500000 iterations hangs the job with no write at all in 6 of 7 runs, as it did in all
  six runs with a write [HW]. So the hang of the busy runs is not shown to be the write's or the
  written values', and those runs say nothing of what a write during a loop does [HW]. The control
  ran on a revised module (see the provenance), whose changes are not on the job or hang path
  [infer].

**What it does not show.** What a write while a loop runs does: nearly every long loop hung by
itself, so the write-while-busy half stays untested until a loop that finishes (between 1250000
and 12500000 iterations) is written during. Why the long loop hangs, and at what length it starts
to, are not known. Also that a field at 0 or 1 gates anything (the register holds the value; a
gated clock with no visible effect is also possible); the fields at bits 3:2 to 11:4, which were
not run again after the first run; a job that uses the main cache more heavily than a 64x32 fill
or the copy; more than one run of each setting.

**Provenance.** The campaign read the srcversion of the installed module file (modinfo), not of
the loaded module. The run printed E431D4FEB0F36E3C337AD50 for the installed file; that it was
also the loaded module is inferred (the four runs that print it share one boot, 183 to 511 s of
uptime, after the install, with no reload logged, and the kernel log shows kregnow in use). The
kit's env.toml was patched after the runs. The edm/host-events run, E444, was on an earlier
boot with a different installed file.

The linux series was revised after these runs (tip 01cff214d7d2, the one of the control runs of E445
and E446): the debug switches (kregnow's arm, alias_ctx_rw, render_share_pb, tadata_fill) are
disarmed at a firmware load and at a reset, kregnow's arm, read and write and the host-interrupt
restore run under one lock, a render context that shares a PB holds a reference on its donor until
it is freed, and the cleanup commands and the TA data fill are moved into helpers with the same
order and effect. The scripts of these runs reset the GPU before they arm anything, nothing resets
between the arming and its use, and the shared PB's context is closed before its donor, so the
revision does not change the paths the runs used (read against the diff of the two tips and the
scripts) [infer].
