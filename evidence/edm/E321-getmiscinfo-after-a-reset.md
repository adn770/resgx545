+++
id = "E321"
claim = "After each of three debugfs resets (about 0.27 s each from the shell) the EDM answers GETMISCINFO within 169 to 175 µs, on the first and the second query alike, and 168 µs after a render; while a faulted or hung job is held the query is not answered and the kernel's 500 ms wait ends it, about 0.65 s from the shell; one run"
unit = "edm"
method = "probes/edm/miscinfo-reset.toml on the laptop, linux fork 66dc1fda6ae8 with the debug option on: its script miscinfo-reset.sh writes debugfs reset three times, each timed from the shell, then reads debugfs miscinfo twice, keeping the kernel's answered-after time; then the triangle and one more query; the held cases from render-hold-fault, render-hold-hang and render-ta3d-ro"
tiers = ["HW", "DDK"]
date = "2026-11-03"
data = ["edm-miscinfo-reset", "render-hold-fault", "render-hold-hang", "render-ta3d-ro"]
terms = ["misc_info", "misc_info_features"]
+++

**Results.**

| | reset | first query | second query |
|---|---|---|---|
| 1 | 271 ms | 172 µs | 172 µs |
| 2 | 273 ms | 172 µs | 175 µs |
| 3 | 274 ms | 169 µs | 169 µs |

After the triangle the query is answered in 168 µs. The shell's own read of the file takes 134
to 148 ms (sudo and the file's output), against which the kernel's times are small. This
table keeps only the answered-after line of each answer; the answers render-hold-fault and
render-hold-hang keep in part report core revision 0x0001000d and core id 0x01150000, both
matching the registers. In the held cases (E317, E318, E319) the query fails with -ETIMEDOUT
after 649 to 667 ms of the shell's time; the kernel's own wait is 500 ms [DDK: linux fork,
sgxfive_debug.c].

**What it shows.**

- A boot leaves the EDM answering GETMISCINFO in under 0.2 ms, whether or not it is the first
  query since the boot [HW]: asking at every boot costs that, against a reset of about 0.27 s.
- A firmware that has stopped serving commands does not answer, and the kernel's wait bounds the
  query [HW]: a query at boot fails cleanly if the firmware does not come up.
