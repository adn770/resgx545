+++
id = "E752"
claim = "During a hold of the EDM of 90 tick periods by a task of ours (2262433 to 2262438 CR_TIMER units, 90.7 ms, ending mid-period), a GETMISCINFO kick issued 3.4 to 3.6 ms after the command (the hold's state read busy before it, 3 of 3) was queued and logged once after the hold's exit (pa0 0, pa1 bits 23:0 0x100, count byte 2, 3 and 4), in 3 of 3 jobs scored QUEUED by the frozen classifier, the debugfs read answered after 86.98, 87.99 and 88.03 ms, with the control (the same hold with no kick) reproducing e4l's shape class (PARTIAL, 2 of 2, E751) so that the stage gate opened; the kick took the fifth, third and third place of the entries drained after the exit (window 2), its pa2 age 12744 units (latched when the drain began, with the pending tick of E751's fourth entry, age 12604) in the first job and 19522 and 21884 units (latched on arrival, ahead of one pending tick of age 12612 and 12600) in the other two; and a 64x64 triangle (tool `tri`, hold_recovery Y for that job only, read back and put back) started in the same kind of hold completed rc 0 in 75230, 73184 and 74788 us against 5673 and 6038 us for the two no-hold controls, with the same 9 event entries (0:8, 1:9, 3:4, 3:22 and five more 0:8 as without a hold) all logged after the hold's exit, the first 552 to 567 units after it, scored QUEUED (the job's events at the exit) in 3 of 3"
unit = "edm"
method = "S2b stages e5c (ctl90 x2: n = 1508279, window 2, no trigger; kick90 x3: the same hold, window 2, GETMISCINFO through the debugfs 3 ms after the command, the hold's state read once before it, the job void unless it read busy) and e5t (tri-nohold x2: tool tri, window 1, no hold; tri90 x3: the same tool command 3 ms after the command of the hold, window 1, hold_recovery Y written, read back, marked in the kernel log and put back to N after each job), paths relative to edm/closing-s2b/ of the dataset, runs 1794266868-31804 and 1794266876-31885, on the laptop (direct cable), 2026-11-10 00:27, kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B, stock firmware, tool ~/sgxfive-test-s1 (sha256 d776afbc...714e); ring_hold as E751, one arm per stage; the e5c gate (control against e4l's shape class, kicks valid) was open before e5t ran; the frozen outcomes were QUEUED and LOST for both, no favourite (predictions/e5c.tsv, e5t.tsv); the tool's own render time against the no-hold control is the proof that the triangle overlapped the hold; scored by the frozen score/score_s2.py e5c and e5t; the kick's pa2 age and place in the drain were read after the run"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["edm-closing-s2b:out/e5c/", "edm-closing-s2b:out/e5t/"]
terms = ["Event Data Master (EDM)", "CR_EVENT_KICK", "CR_EVENT_TIMER", "CR_EVENT_STATUS"]
+++
**What ran.** E750 sent kicks into a hold and the stage's control had nothing to compare; here
the hold ends mid-period (E751), so the control has a told shape, and window 2 logs the drain, so
the place of the kick among the ticks is visible. The triangle stage had never run.

**Frozen verdicts.** e5c: `control reproduced {'reference': ['PARTIAL'], 'control': ['PARTIAL',
'PARTIAL'], 'mismatch': []}; kick ['QUEUED', 'QUEUED', 'QUEUED']`, gate open. e5t: `control tri
times [5673, 6038]; held triangle ["QUEUED (the job's events at the exit)", "QUEUED (the job's
events at the exit)", "QUEUED (the job's events at the exit)"]` (out/score-e5c.txt,
out/score-e5t.txt). The stage did not stop: every job class ok, rc 0, no bad kernel-log line, the
health and the tick fine after each, hold_recovery put back to N.

**Results [HW].** Controls: ctl90 and ctl90-r2 held 90 ticks and drained four tick entries (three
0x01061a74, one of age 12606 and 12603) then the grid, as E751. kick90, -r2 and -r3 (window 2,
entries after the exit, units from the exit, pa1 / pa2 low bits):

| job | drain after the exit |
|---|---|
| kick90 | ticks +107, +245, +394 (0x01061a74), tick +552 (age 12604), kick +708 (age 12744) |
| kick90-r2 | ticks +103, +252 (0x01061a74), kick +402 (age 19522), tick +681 (age 12612) |
| kick90-r3 | ticks +103, +240 (0x01061a74), kick +380 (age 21884), tick +648 (age 12600) |

then the ticks at +12500 and on the grid. The kick was at +3.61, +3.42 and +3.38 ms after the
window opened. Each ring held 16 entries and 58 or 59 drops. For the triangle: the first logged
entry was a (0, 8) entry at +552, +552 and +567 after the exit, then 1:9 at +2338 to +2361, 3:4 at
+3969 to +3987 and 3:22 at +4115 to +4133, and two more (0, 8) entries at +190 k and +195 k,
+135 k and +140 k, +182 k and +187 k units after the exit; the no-hold triangles logged the same 9
entries. The count byte went up by one after each (0, 8) entry as in E747.

**Post hoc [infer; read after the run, not held out].** A host kick that arrives while a task of
ours holds the EDM is delivered once after the task ends and not lost; the host's read waits out
the hold. Together with E751: a kick that arrived with the tick queue full (kick90: three ticks
had arrived) was drained after the pending tick, both with a drain-time pa2; one that arrived with
two ticks queued took the third queue place with an arrival-time pa2 and the pending tick came
after it. So the pending place is not specific to ticks, and the queue holds up to three events
latched on arrival [one run per arrival state, not replicated]. A client job's events (the
kernel's command buffer kick, the TA and end-of-render events of E747) are queued as well: all 9
arrived after the exit, in the order of E747, and the render took 73 to 75 ms against 6 ms
because the job's events wait for the task, so the triangle overlapped the hold. That no job event
was lost is the count of 9 against the control's 9; a lost duplicate bit would not show here.

**Not shown.** Two kicks or a kick and a job in one hold (merged or not), whether a task that holds
the EDM through a TA or end-of-render event of its own queues the same way, holds of another
length or in another slot, and what a hold longer than the kernel's job timeout (500 ms) does.
