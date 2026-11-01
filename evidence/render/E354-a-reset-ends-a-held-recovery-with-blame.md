+++
id = "E354"
claim = "With recovery held, a debugfs reset written while the hold is set recovers the held job with blame: a render faulting on its unmapped stream page fails once with -EIO and a pixel task hung on a fetch it never issued once with -ETIMEDOUT, after one reset each and with no second fault, hang or cleanup failure; while held the driver logs two lines (the detector's recovering line and the hold's warning) and nothing more until the reset, over 11.2 s and 3.1 s; one run"
unit = "render"
method = "probes/render/held-reset.toml on the laptop, linux fork b5a86838ae59 (commits 30 and 31) with the debug option on: its script held-reset.sh marks the kernel log at each case, sets debugfs hold_recovery and runs sgxfive-test tri --fault (30 s wait, in the background) and, as probe --tri, vdm/state1's job hung in its pixel task; it reads the driver's lines and the state (status, GETMISCINFO through debugfs miscinfo) while held, writes debugfs reset with the hold still set, then clears it; the tool's lines and a fill and the triangle after each; the table's kernel log read with render_words.py log"
tiers = ["HW", "DDK"]
date = "2026-11-03"
data = ["render-held-reset"]
terms = ["CR_EVENT_STATUS2", "CR_BIF_FAULT", "misc_info"]
+++

**What runs.** The kernel keeps the held job and the detector that found it; a reset asked for
while the recovery is held becomes that recovery, failing the held job with the detector's error
and running the other contexts' jobs again; the detectors log their "recovering" line only while
no recovery is held [DDK: linux fork, commit 31, sgxfive_recovery_hold].

**Results** (render_words.py log over the table's kernel log):

| case | driver lines while held | held for | after the reset | the job |
|---|---|---|---|---|
| fault | BIF fault 0x90008 ... recovering; recovery held | 11.21 s, 0 lines between | stopped, reset, boot, EDM up: once | -EIO ("job faulted, context lost") |
| hang | job hung, recovering; recovery held | 3.11 s, 0 lines between | once | -ETIMEDOUT ("job hung, context lost") |

- While held, GETMISCINFO times out (the kernel's 500 ms wait, about 0.65 s from the shell) and
  `CR_EVENT_STATUS2` reads 0x480 (fault) and 0x440 (hang), as in E317 and E318.
- After the reset GETMISCINFO is answered in 170 to 181 µs, `CR_EVENT_STATUS2` reads 0x400, and a
  fill and the triangle run exactly. No further line follows: the held job is not run again.

**What it shows.**

- A reset written while a recovery is held costs one recovery and blames the held job: render_uapi
  §13's follow-up is settled for the fault and the timeout detector [HW: one run each].
- The detectors report a held hang once: two lines, then none until the reset [HW].
