+++
id = "E456"
claim = "A write to register 0x0740 through kregnow (values 0x1ff, 0x200, 0x400, 0x1000, 0x3fe00, 0x3ffff) reads back 0 right after each of 156 writes (26 before the first kick, 10 between kicks, 120 beside 300 renders) and every one of 64 samples after a job; the 76 renders of 64x64 on one or two contexts are exact"
unit = "dpm"
method = "probes/dpm/task-fields-0740.toml (task-fields-0740.sh) on the laptop (direct cable), debugfs kregnow writes of 0x0740 (linux fork commit 41) before the first kick of sgxfive-test tri (one context, two alternating with --ctx2 and --kreg-render/--kreg-render2 between the kicks, partial renders of 1024x768 on 0x23 pages) and beside 300 renders; the register read back by the kernel after each write (kernel log) and by /dev/mem after each job (tri --regs 0x0700-0x0750), TA3DCtl by debugfs buf09; sgxfive-test 6f8f2bf8, linux fork ea5482bc59a6 with the debug option on, module srcversion 9A7BCDC4FC2A2166A409EEA (loaded and installed equal, both printed by the run); two runs of each case"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["dpm-task-fields-0740"]
terms = ["CR_DPM_TASK_STATE", "CR_DPM_TASK_CONTROL", "CR_DPM_STATE_CONTEXT_ID"]
+++

**What runs.** The TA kick turns two 9-bit fields of register 0x0740 into a DPM store task and a
load task (3d.md section 4.4); it read 0 in every sample of every earlier job (E256, E312). The
linux fork's debugfs `kregnow` (commit 41 adds 0x0740 to its list) writes it, and the kernel logs
the value the register reads right after the write. Parts, two runs of each: one context, 64x64,
two renders, with 0 (control), 0x200, 0x400, 0x1000, 0x3fe00, 0x1ff and 0x3ffff written before the
first kick (14 runs); two contexts alternating (`tri --ctx2`, 12 runs: 0 (control), 0x200, 0x3fe00
and 0x3ffff written before the first kick, and two runs of each of two series of writes between the
kicks with `--kreg-render` and `--kreg-render2`); the partial renders (1024x768 on a PB of 0x23
pages, `-n 1` and `-n 2`, with 0, 0x200 and 0x3fe00 written, 12 runs); and 300 renders with 0x200
written 60 times 50 ms apart beside them (2 runs).

**Results.**

- The kernel logged 156 writes of the register: 130 of 0x200, 12 of 0x3fe00, 4 each of 0x1ff and
  0x3ffff, 2 each of 0x400, 0x1000 and 0 (the last write of one series); after every one the
  register read 0x00000000. The 120 writes of the last part were issued while 300 renders ran, two
  times.
- 0x0740 read 0x00000000 in all 64 samples taken after a job (the 28 renders of the one-context
  part, 24 samples of the two-context part and the 12 partial-render runs); TA3DCtl dwords 20, 21
  and 25 read 0 in all 102 snapshots.
- The 28 renders of the one-context part and the 48 of the two-context part were exact (0 wrong
  inside, outside and at the edges, guard 0), and the 2 x 300 renders of the last part completed.
- The 12 partial-render runs (1024x768, 0x23 pages) each failed their first job with "scene
  overflowed the parameter buffer" (-ENOSPC); the tool dumps nothing from a failed job, so no state
  page was read.

**What it shows.** A host write to 0x0740 does not stay: the register read 0 right after 156 of 156
writes, idle and beside running renders [HW]. It is a status or derived register, or one that
ignores the host, which would make the fields the TA kick takes from it come from the hardware, not
from a value the host sets [infer]; a write only taken while the DPM unit is clocked, or from a
unit other than the bus the host writes through, is not excluded by a write made at these moments.

**What it does not show.** What sets the fields (they read 0 in every sample), whether a load task
reads a partial render's macrotile lists back (no partial render finished through the tool; the 12
runs did not reach a state page, and with the register at 0 no store or load task is issued), and
what the register holds while a TA runs (sampled after jobs only).

**Provenance.** linux fork commit ea5482bc59a6 with the debug option on, module srcversion
9A7BCDC4FC2A2166A409EEA (the loaded module, read from /sys/module, equal to the installed file's
modinfo; both printed by the run), sgxfive-test sha256
6f8f2bf8295d302f50594b02b92989a72a127adc36b0a8cf245cbd14c53da4f5 (built from this phase's overlay
source, named in each env.toml), the laptop over the direct cable.
Revised after these runs: the series was rebuilt on tip 6ee9501832af, which clears armed pokes on
load and reset (commit 40), moves the submission's poke calls into one function,
sgxfive_submit_xfer_pokes() (40), makes alias_skip refuse bits 16-31 with -EINVAL (42) and rewords
comments and commit messages (40 to 42); the module of these runs is the one built from
ea5482bc59a6. The paths this run used did not change [infer]: git diff ea5482bc59a6 6ee9501832af
shows only comment changes in kregnow's write and its register list, and task-fields-0740.sh writes
0x0740 after its reset of each case and arms no kernel poke.
