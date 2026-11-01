+++
id = "E604"
claim = "In a firmware (EDM) task of ours (stage f15, p1137_strjob, slots=0x1 entry=0, the landed verifier unchanged), `str` then `ldr` of the two allow-list registers 0x0814 and 0x0a78 read back the stored value in 3 of 3 jobs, each time both right after the `str` and again at the end of a 30000-iteration spin (about 2 ms): 12 of 12 reads equal the stored value (0x0814 stored 0x1d5de, 0x1b85d and 0x1a355 with bit 16 always set, 0x0a78 stored 0x21, 0x24 and 0x27). A client fill (sgxfive-test fill) was started by the host 0.5 ms into the spin and drew exactly (diff 0 of 2048 pixels, 3 of 3); that the fill reached the engine while the task was still spinning was not measured (the host process started 0.5 ms into a 2 ms spin and no job time was kept), so the run shows the read-back across the start of a client job and does not show an overlap"
unit = "edm"
method = "on the laptop (direct cable), linux fork tip 1dd291a61499, module srcversion B21FDA82BD5E5CB5A627E3B (installed and loaded), stock firmware, kernel 7.3.0-resgx545, own_arm off before and after, our firmware task p1137_strjob armed with slots=0x1 entry=0 (probes/p1136/asm/p1137_strjob.s, blob sha256 15ae6f2ac1c8e057f9a0a83bce7f8913c1c45cfdd75f29641427a760d199e22d, 394 bytes, accepted by the verifier), driven by probes/p1136/run_1137.py (through probes/p1136/run_1137_logged.py, one run) with the remote command slowevent of probes/p1136/fwext1137.py (it writes the command, sleeps delay_ms, runs the fill of the sgxfive-test tool as a blocking process, waits for done and reads the page; it writes only own_res dwords) after the frozen predictions (probes/p1136/predictions-1137.toml sha256 17f6cc52...) and the manifest were verified; the three jobs' seeds (draw 1142), values and results are in verdicts-f15.json, the arm and reset records, env.toml and the journalctl -k of the stage (gzipped) in the dataset"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["firmware-tasks-p1137-f15"]
terms = []
+++

**What ran.** One arm, three jobs. Each job passes two stored values (V1 for 0x0814, V2 for 0x0a78,
both inside the register's width) and a spin count of 30000 in the page. The task executes `str
0x0814, V1`, `ldr` of it (read 1), the same for 0x0a78 (read 2), then the 30000-iteration spin
(about 2.1 ms, from E539's 0.7 ms per 10000), then `ldr` of both again (reads 3 and 4), and
stores them to the page. 0.5 ms after the command the host starts a client fill (the 64 x 32 job of
the health script) as a blocking process on the same GPU; the task's slot 0 is the only armed slot.
The task's only register writes are `str` to those two registers (the runner's own debugfs reset
and gate come after the last job). No clock-gate register is anywhere in the material, the
verifier refuses them (probes/p1136/verifier-matrix.txt). The values: V1 has bit 16 forced to 1
(the three are 120286, 112733 and 107349), V2 is 33, 36 and 39.

**Results.** [HW] 3 of 3 jobs: the four reads of each job are V1, V2, V1, V2 (12 of 12), the task
reached `done` inside the 300 ms window each time, the fill drew exactly (0 of 2048 pixels differ)
three times, and the ticks advanced after the final reset and gate (rate 968 Hz, serv_event moving;
the arm's rate was 997 Hz). The journal of the stage holds the one debugfs reset (BIF_FAULT 0x0,
EVENT_STATUS 0x20000000/0x400) the runner does at the end, no fault line, no watchdog line, one
reset in all. The run kept no job time and no time of the fill's submission: whether the fill ran
before, during or after the spin is not in the data.

**Against the predictions.** P37_F15 held (3 of 3 jobs, 4 reads each, the fill exact).

**What it shows.** [HW] A write to 0x0814 or 0x0a78 by the firmware reads back unchanged at the end
of a spin that a client fill was started in (the process was started 0.5 ms into it), and the fill
drew exactly. Three value pairs are a weak test of the registers' bits: of the 6 bits of 0x0a78
bits 3 and 4 were never 1 and bit 5 never 0, and of the 17 bits of 0x0814 bit 16 was never 0 and
bits 2, 4, 6 and 15 never 0 either. That these two registers are plain storage rests on E534's 318
of 318 runs and E026, not on these three jobs. [infer] A backend can treat them as scratch while a
client job is submitted; this run does not show that the job overwrote or did not overwrite them
while it ran.

**What it does not show.** That the fill ran during the spin (the overlap is not measured; a run
would need a spin longer than the process start of the host, or a client process already armed
and waiting), any register whose write has an effect (the str allow list holds only these two, and
widening it is the user's decision: Q198), a value wider than the register's bits, a triangle or
any 3D job during the spin (the fill is a transfer-class pixel job), the register-index forms, and
reads while the EDM is held for longer than 30000 iterations.
