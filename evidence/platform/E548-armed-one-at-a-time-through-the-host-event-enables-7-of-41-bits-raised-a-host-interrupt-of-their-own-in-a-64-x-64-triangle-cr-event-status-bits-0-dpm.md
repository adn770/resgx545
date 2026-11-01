+++
id = "E548"
claim = "Armed one at a time through the host event enables, 7 of 41 bits raised a host interrupt of their own in a 64 x 64 triangle (CR_EVENT_STATUS bits 0 DPM_3D_MEM_FREE, 6 DPM_STATE_CLEAR, 9 DPM_CONTROL_CLEAR, 18 PIXELBE_END_RENDER, 20 OTPM_INV, 26 MADD_CACHE_INVALCOMPLETE and CR_EVENT_STATUS2 bit 1 DPM_3D_FREE_LOAD) and 1 of 41 in a fill (bit 26); with TA_FINISHED and TA_TERMINATE the host saw none; three repeats give the first run's answer in 51 of 54 case-runs (21 of 24 for the 8 cases with an interrupt, 30 of 30 for the 10 without; the three misses are bit 9 and STATUS2 bit 1 of the triangle and bit 26 of the fill), and the 24 unarmed controls raise none; that the armed bit is what raised the interrupt is inferred, the handler having read only TIMER and MASTER_INTERRUPT in all 82 armed jobs [infer]"
unit = "platform"
method = "script tables event-irq-matrix (88 jobs) and three repeats (72 jobs), on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion 7ED723C25D78D7FCB3C08C1 (installed equal to loaded), stock firmware (own_arm off), tool sgxfive-test-1126 (sha256 751f7223c8c731a08d75cfc3920a5d1050488ca3bdc426be45b7c431e600f82e, unchanged), no kernel or module change, no reboot, no clock-gate register written, a 64 x 64 triangle drawing exactly before and after every script: after a debugfs reset one host enable bit written through kregnow (CR_EVENT_HOST_ENABLE 0x0130 = 0x4000 | bit, CR_EVENT_HOST_ENABLE2 0x0110 = bit; the script refuses every other offset), a job (`tri` 64 x 64 or `fill`), one second later kregnow's counters (host_irqs, extra = interrupts with no SW_EVENT, last = the status words the handler read) and both status registers; E444's method over ordinary jobs; the repeats ran tri and fill with CR_EVENT_STATUS bits 0, 6, 9, 12, 13, 18, 20, 26 and CR_EVENT_STATUS2 bit 1 three times with three unarmed controls a kind; H111-fw and H111-rep declared before the runs (plan.md sections 1 and 12); output.txt prints rc 0 for every job and prints the health result of a script only when it failed, so that a 64 x 64 triangle drew exactly before, between and after the scripts rests on the absence of a failure line"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["platform-event-bits"]
terms = ["CR_EVENT_STATUS", "CR_EVENT_STATUS2", "CR_EVENT_HOST_ENABLE", "CR_EVENT_HOST_ENABLE2", "CR_EVENT_HOST_CLEAR"]
+++

**First run.** [HW] 88 jobs: tri 64 and fill, each with 3 unarmed controls, 26 CR_EVENT_STATUS bits
(0 to 13, 15, 16, 18 to 26, 28) and 15 CR_EVENT_STATUS2 bits (0 to 9, 11 to 15) (82 armed). An
unarmed `tri` shows 2 host interrupts (the firmware's SW_EVENTs) and a `fill` 1, with no extra (6 of
6). Armed, an extra interrupt (none with SW_EVENT in the status read) appeared in tri 64 for bits 0,
6, 9, 18, 20, 26 and CR_EVENT_STATUS2 bit 1, and in fill for bit 26 only; the status the handler
read was 0xa0000000 and 0x00000400 in all 82 armed jobs (TIMER with MASTER_INTERRUPT [infer]: the
armed bit was already acknowledged when the handler ran). TA_FINISHED (13) and TA_TERMINATE (12)
raised no extra interrupt in either kind: the host's counters saw none, which does not show that the
bit cannot interrupt, and E547 shows TA_FINISHED in no 64 x 64 timeline, so in that job the event
may simply not occur. Of the 54 cases the plan declared Y or N for (H111-fw), 49 were as declared;
the 5 misses are TA_FINISHED and TA_TERMINATE declared Y for tri 64 and bits 6 and 9 and STATUS2 bit
1 declared N; the other 28 armed cases were declared `?` and are exploration.

**Repeats.** [HW] Three further runs of 18 cases (tri and fill, nine bits each) with the first run's
value declared (analysis/predictions-followup8.tsv): 51 of 54 as first seen. tri 64 bits 0, 6, 18,
20 and 26 raised an extra interrupt in 3 of 3 runs, bit 9 and STATUS2 bit 1 in 2 of 3, bits 12 and
13 in 0 of 3; fill bit 26 in 2 of 3 and every other fill bit in 0 of 3 (fill bit 18, which E547 sees
in 5 of 10 fill jobs, in 0 of 3 again: its pulse coincides with the firmware's own interrupt); the
18 controls of the repeats raise none. A detection is a yes in a run, not a rate of the bit: an
event whose interrupt coincides with another is not counted [infer]. The 51 of 54 is 21 of 24 for
the 8 cases with an interrupt (tri bits 0, 6, 18, 20, 26 and 9, STATUS2 bit 1, fill bit 26) and 30
of 30 for the 10 without; the three misses are positives (bit 9 and STATUS2 bit 1 of the triangle,
bit 26 of the fill).

**The two methods together.** Which event bits assert in which kind of job is hardware [HW]: bits 6,
9, 20 and 26 and STATUS2 bit 1 reach the host as interrupts in a 64 x 64 triangle but were not seen
in E547's timelines of that kind (1.2 microsecond samples, 10 jobs), and an armed bit can raise the
host interrupt line (MASTER_INTERRUPT) in that triangle. How long a pulse is and whether the host
sees an extra interrupt depend on the firmware's acknowledgement and on a race with it [infer]: the
pulses of those bits are shorter than a sample or hidden in the firmware's acknowledge, a yes in a
run needs the pulse to land before the acknowledge, and a no says only that the host saw no extra
interrupt. TA_FINISHED and TA_TERMINATE are seen by the timelines only in the 256-pixel and partial
jobs and the host saw no extra interrupt for them in a 64 x 64 triangle.

**What it does not show.** CR_EVENT_HOST_CLEAR and CR_EVENT_HOST_CLEAR2 are not written by any
script (the debugfs offers kregnow only for the two enables, and a clear cannot be read back); what
a write clears is Q166, which needs a kernel change. The irq matrix kinds other than tri64 and fill
were not run (E547 is the only evidence for the other kinds); the handler read the status words
TIMER and MASTER_INTERRUPT only, so which armed bit raised an interrupt is inferred from the enable
written, not read. The order of bits within a job and the word the firmware reads are the
firmware-task work of p1130 and are not repeated here.
