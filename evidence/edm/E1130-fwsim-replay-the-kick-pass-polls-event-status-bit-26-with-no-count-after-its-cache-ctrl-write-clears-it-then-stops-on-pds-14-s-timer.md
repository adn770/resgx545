+++
id = "E1130"
claim = "fwsim (stock microkernel in sgx-sim, kept render job render/closing-r9-k1 c-off kicked as our kernel built it) with the kept order of CR_EVENT_STATUS replayed after the kick's CR_CACHE_CTRL write (0x20000000, 0x24000000, 0x20000000; E1115, E1120, E1123): the kick pass reads CR_EVENT_STATUS again and again with its task state the same at every read while the word is 0x20000000 (a wait with no count, so how long the hardware holds the word changes nothing) [RE]; given 0x24000000 it writes 0x04000000 (bit 26) to CR_EVENT_HOST_CLEAR and emits PDS #14 with request mask 0x00020000 [RE, infer: on the replayed word]; PDS #14 reads the counter tim, which no run input gives for a program a task emits, and the run stops there (R1, R3); no register read is refused"
unit = "edm"
method = "fwsim, offline (closing29 fwsim package P4, kept-reading replay; resgx545 branch fw-p4): tools/fwsim/fwsim.py kick --replay on the stock firmware sgx545_ukernel.fw (sha256 da4507d56e90fb03cdb150a9b24436844a271748ecac36d6ed361ce8513c8524), boot, arm (two GETMISCINFO), three ticks, the render job of render/closing-r9-k1 c-off placed by tools/fwsim/kick.py and kicked with cache control 0xb; the hardware model of crates/sgx-sim/src/hw.rs with seeds.toml's rules and replay.toml's one row, which moves to the next kept word only at a proven spin (the task's whole state equal on two arrivals at the read, nothing written in between) and stops a run whose task acts on a word no spin proved; the run directory (run.toml, facts.txt, output.txt, trace.jsonl.gz) kept in resgx545-data-private firmware/fwsim/m2-kick-replay-r9-c-off on its branch fw-p4, a trace of indices and values only; the same run without --replay stops on the first CR_EVENT_STATUS read (strict rule, E1115); facts only, no code"
tiers = ["RE", "infer"]
date = "2026-11-16"
data = ["tools/fwsim/replay.toml", "crates/pysgx/tests/test_fwsim_m2.py"]
terms = ["CR_EVENT_STATUS", "CR_EVENT_STATUS.MADD_CACHE_INVAL_COMPLETE", "CR_CACHE_CTRL", "CR_EVENT_HOST_CLEAR", "CR_EVENT_TIMER"]
+++

**What ran.** The M2 render kick of the fwsim track (plan-fwsim.md M2; the kick of E1115's method)
with replay on: once the kick pass writes CR_CACHE_CTRL 0x1000ffff after the served kick,
CR_EVENT_STATUS reads the words the kept rows show it taking after that change, in their order:
0x20000000 (the change comes before every CR_EVENT_STATUS event, E1123 14 of 14, E1120 19 of 19),
0x24000000 (the word whenever bit 26 is set, E1115 19 episodes; once 0xa4004000, E1120), 0x20000000
(bit 26 falls before the render end, E1115 8 of 8). No time enters: sgx-sim has no clock inside a
pass, so the replay answers the current word and moves to the next only where the task's state
(every register, predicate, link and pending load) is the same on two arrivals at the read with
no register write, store or emit between them.

**Results [RE].** Counts and values from facts.txt. The kick pass is one slot 0 entry (pa0 0, pa1
0x02000100, E746); it reads CR_BIF_CTRL (0x0c00, reset 0), writes it 0x8 then 0, reads
CR_CACHE_CTRL (0x0000ffff, E1122) and writes 0x1000ffff (as E1115's strict run). It then reads
CR_EVENT_STATUS three times: twice 0x20000000 with the same state at each read (the spin the
replay needs; no count, no other read and no write between), then 0x24000000. After it the pass
writes CR_EVENT_HOST_CLEAR (0x0134) 0x04000000 and emits PDS #14 (the request program of E146)
with ir0 0x00020000, in E146's second group (0x00120080). PDS #14 passes the counter tim on (E146:
to a destination word for its task), and tim is not known for a program a task emits: the run stops there. Register
reads: replay 3, reset 1, E1122's rule 1; none refused. Register writes in the kick pass: 4.

**What it shows.** After its data-cache invalidation request the kick pass waits on bit 26
(MADD_CACHE_INVAL_COMPLETE) of CR_EVENT_STATUS with nothing that counts, so it does not go on
without it [RE]: the firmware's side of E1123's open H-WAIT, the kick pass goes on past its CR_CACHE_CTRL
write only after a read that shows bit 26. Its write of bit 26 to CR_EVENT_HOST_CLEAR follows the
read that sees the bit [infer: on the replayed word]; that the bit's fall is that write's doing is
not shown (no kept row orders the fall against a firmware write), but it would fit bit 26's
episodes being wider when more registers are sampled (E1120: 5.0 to 7.2 us with four, 11.9 and
15.7 us with 27) [infer]. With bit 26 and 0xa4004000's other bits (E1120, once) the pass may act
otherwise; the replay gives 0x24000000, the word of 19 of 20 kept episodes.

**What it does not show.** When bit 26 rises or falls against the firmware's reads (the replay
needs neither for this pass: the wait has no count); what the pass does with the counter tim
PDS #14 passes on (the run stops before it); the TA kick and anything after it (K1 to K8 of the
plan are not reached); anything on the hardware: every fact past the 0x24000000 read rests on the
replayed order (R4).
