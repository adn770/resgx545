+++
id = "E435"
claim = "With render flag bit 0 and debugfs hold_recovery set, the job holds in its hang with CR_EVENT_STATUS (0x012c) gaining bit 11 and 0x0748 ending at 0x1d in 3 of 3 runs; with five registers sampled instead of 118 (five runs) 0x0218 dips in 2 of 5 held jobs and in 4 of 5 unpoked ones, so the TA kick is not absent from the held job"
unit = "render"
method = "probes/render/flag-bit0-timeline.toml (flag-bit0-timeline.sh) on the laptop (direct cable), linux fork f1fad0ed9d0e with the debug option on: sgxfive-test tri at 64x64 with --kpoke-render 1:ta:7^=0x1 and hold_recovery set, 2.5 s wait, under regtimeline for 3 s from 50 ms before the job over 118 registers (0x0118, 0x012c, 0x0200-0x0240, 0x0400-0x04fc, 0x0630, 0x0640-0x0660, 0x0700-0x0760), the unpoked job beside it, three runs each, a reset after each held job"
tiers = ["HW"]
date = "2026-11-07"
data = ["render-flag-bit0-timeline", "render-flag-bit0-dense"]
terms = ["CR_TE_PSG"]
+++

**Results.** In the second and third unpoked jobs the sampled registers 0x0218 (the dip at the
kick), 0x0228, 0x022c, 0x0700, 0x0710 and 0x0724 change; the first shows no change (a missed
sample, or a window that began after the kick). The three held jobs ('Timer expired', the wait ran
out) change 0x012c from 0x20000000 to 0x20000800 and 0x0748 from 0x1f to 0x1d; 0x0710 changes in
all three (0x1, 0x421, 0x1 in the first), 0x0228, 0x022c and 0x0700 in the second, 0x0700 in the
third, and 0x0218 and 0x0724 in none. After the reset the triangle draws as before (3 of 3).

**Denser sampling** (render-flag-bit0-dense, five registers 0x0218, 0x0724, 0x0710, 0x0748, 0x012c,
about 570 kHz in the unpoked jobs and 116 kHz in the held ones, five runs each): 0x012c and 0x0748
change in 5 of 5 held jobs and 0x0710 in all 10 jobs; 0x0218 changes in held jobs 1 and 2 (2 of 5)
and in unpoked jobs 1 to 4 (4 of 5); 0x0724 changes in none of the 10. The dip lasts 110 to 192 us
in the six jobs that show it (141 us in the first unpoked job, 153 and 184 us in the held ones),
many times the held jobs' 8.6 us sampling interval, and unpoked job 5, at about 570 kHz, shows no
change of 0x0218 at all: a dip can be absent from a densely sampled job. So the first run's reading
that the TA side does not run is withdrawn.

**What it shows.** The held job ends with the event register's bit 11 set and 0x0748's bit 1
clear, the bit E358 read as the 3D freeing pages; 0x0724 never changes in the held jobs, and 0x0218
dips in 2 of 5 of them as in 4 of 5 unpoked ones, so the kick runs in at least some held jobs. Why
the other held jobs show no dip, sampling or a kick that does not run, is not shown.

**What it does not show.** What the 3D waits for. Q065 stays open.
