+++
id = "E547"
claim = "In ordinary jobs CR_EVENT_STATUS shows PIXELBE_END_RENDER, DPM_3D_MEM_FREE and MADD_CACHE_INVALCOMPLETE in triangle jobs, TA_FINISHED, TPC_FLUSH and the DPM state and control bits only in the 256-pixel and partial jobs, a fill only PIXELBE_END_RENDER and a copy neither, and SW_EVENT with MASTER_INTERRUPT in 41 of 41 jobs in which one appears, and CR_EVENT_STATUS2 shows OTPM_MEM_CLEARED in 5 of 20 depth-store and partial jobs and DPM_TA_FREE_LOAD in 1 of 10 256-pixel jobs; the short pulses of PIXELBE_END_RENDER, DPM_3D_MEM_FREE and TA_FINISHED are 4.2 to 6.0 microseconds at an average sampling interval of 1.06 to 3.68 and 5.7 to 6.1 at 2.36 to 5.58, at most a few samples wide, and what holds them that long is the firmware's acknowledgement [infer]"
unit = "platform"
method = "script table event-timelines (66 jobs), on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion 7ED723C25D78D7FCB3C08C1 (installed equal to loaded), stock firmware (own_arm off), tool sgxfive-test-1126 (sha256 751f7223c8c731a08d75cfc3920a5d1050488ca3bdc426be45b7c431e600f82e, unchanged), no kernel or module change, no reboot, no clock-gate register written, a 64 x 64 triangle drawing exactly before and after every script: regtimeline (E435) through /dev/mem sampling CR_EVENT_STATUS2 (0x0118) and CR_EVENT_STATUS (0x012c) alone (on average 1.06 to 3.68 microseconds a sample in a job) and with five more registers (0x0218, 0x0700, 0x0710, 0x0724, 0x0748; 2.36 to 5.58 microseconds) through `tri` (64 x 64), `fill`, `tri -n 3` (256 x 256), `copy`, `tri --depth --depth-store` and a partial render (`tri` at 1024 x 768, `-n 2 --keep-overflow`, `render_pb_pages` 0x30, put back), five runs of each kind per register set after a reset (10 a kind), and three idle controls a register set; the changes of each bit counted by recompute_events.py (analysis/events-timelines.txt) and analysis/an_event_stats.py; the controls declared before the runs"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["platform-event-bits"]
terms = ["CR_EVENT_STATUS", "CR_EVENT_STATUS2", "CR_EVENT_HOST_ENABLE", "CR_EVENT_HOST_ENABLE2"]
+++

**The idle word.** [HW] In the six idle controls CR_EVENT_STATUS reads 0x20000000 (TIMER) and
CR_EVENT_STATUS2 0x00000400 (DCU_INVAL_COMPLETE) for 305 ms with no change.

**What a job shows.** [HW] Jobs of ten (five runs of each of the two register sets) in which a bit
rose and fell, and the widths of its pulses (the sampling interval a job's average, 1.06 to 5.58
microseconds):

| kind | pulses a job | bits of CR_EVENT_STATUS (jobs of 10; width in microseconds) |
|---|---|---|
| fill | 0 to 2 | PIXELBE_END_RENDER 5 (72 to 113); SW_EVENT and MASTER_INTERRUPT 2 (57 to 84); MADD 1 |
| copy | 0 to 2 | SW_EVENT and MASTER_INTERRUPT 7 (54 to 85); MADD 1 |
| tri 64 x 64 | 2 to 7 | DPM_3D_MEM_FREE 7 (4.3 to 6.1); PIXELBE_END_RENDER 7 (4.3 to 8.7); MADD 5 (53 to 81); SW_EVENT and MASTER 9 (6.6 to 72) |
| tri 256 x 256 (3) | 5 to 21 | DPM_3D_MEM_FREE 10; PIXELBE_END_RENDER 7; MADD 8; SW_EVENT and MASTER 7; TA_FINISHED 5 (4.6 to 106); TPC_FLUSH, DPM_CONTROL_CLEAR and DPM_STATE_CLEAR 1 each |
| depth store | 0 to 7 | SW_EVENT and MASTER 7; MADD 4; PIXELBE_END_RENDER 3; DPM_3D_MEM_FREE 1 |
| partial render | 7 to 19 | DPM_3D_MEM_FREE 10; PIXELBE_END_RENDER 10 (4.2 to 5.8); SW_EVENT and MASTER 9; MADD 8; TA_FINISHED 5; DPM_OUT_OF_MEMORY_MT 3 (5 to 136); TA_TERMINATE 2; TPC_FLUSH 1; DPM_STATE_LOAD 1 |

CR_EVENT_STATUS2: OTPM_MEM_CLEARED in 1 of 10 depth-store jobs (62 microseconds) and 4 of 10 partial
jobs (5.9 to 115), DPM_TA_FREE_LOAD in 1 of 10 256-pixel jobs (72 microseconds), none in the others.
The short pulses of PIXELBE_END_RENDER, DPM_3D_MEM_FREE and TA_FINISHED in the 64 x 64, 256-pixel
and partial jobs are 4.2 to 6.0 microseconds at the sampling of two registers (one of 8.7) and 5.7
to 6.1 at that of seven: at most a few samples wide [HW]; the width follows the sampling interval,
so the bits are held until something acknowledges them and are not timed by the hardware [infer: the
acknowledgement is the firmware's write of CR_EVENT_HOST_CLEAR, and the width is its latency].
Longer pulses [HW]: in a fill PIXELBE_END_RENDER 72 to 113, MADD_CACHE_INVALCOMPLETE 4.5 to 131,
DPM_3D_MEM_FREE and PIXELBE_END_RENDER up to 97 in the 256-pixel jobs, DPM_OUT_OF_MEMORY_MT (bit 1)
5 to 136. A rise between samples is missed (E548 reads those as interrupts). SW_EVENT (14) and
MASTER_INTERRUPT (31) rise and fall together in 41 of 41 jobs in which either appears, 4.3 to 87.5
microseconds [HW]; SW_EVENT is the firmware's own event, so its width is the host's handling of it
[infer]. The order of the first rises differs from job to job (partial render: 26 18 13 0 12, 1 0 18
13 14 31 26, 18 14 31 0 26 and 26 1 0 18 5 13 14 31 in four jobs).

**Not seen.** [HW] ISP_END_TILE, DPM_INITEND, TA_DPM_FAULT, DPM_OUT_OF_MEMORY_ZLS and _GBL,
DPM_TA_MEM_FREE, OTPM_FLUSHED and every status bit not in the table, in the 60 job timelines (the 10
partial jobs end with the scene's overflow, which the tool reports as a failed job by design); TIMER
(29) stays set throughout and is never cleared.

**What it does not show.** The pulses between samples; the order within a job beyond the four
partial jobs listed (E548 and the firmware-task work of p1130); CR_EVENT_HOST_CLEAR (not written;
Q166).
