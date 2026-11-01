+++
id = "E516"
claim = "stad.fetchN [rb,+#k] stores at the dwords b + k + 1 to b + k + N for k = 2, 3, 4, 7, 8 and 15 (fetch4), 3 (fetch8) and 2 (fetch16) (8 of 8 cases), [rb,#k++] stores at b + k to b + k + N - 1 and moves rb by N for k = 1 to 4 (4 of 4: fetch4 with k = 2 and 3, fetch8 with k = 2, fetch2 with k = 4; k = 1 from E482), and [rb,++#k] stores at b + k + 1 to b + k + N and moves rb by N for k = 1 and 2 (3 of 3: fetch4 with k = 1 and 2, fetch16 with k = 1), in a client pixel task; the plain rule was predicted (8 of 8), the post and pre rules are fits to their 4 and 3 readbacks, read after the run, whose predictions failed"
unit = "usse"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1126 (sha256 751f7223c8c731a08d75cfc3920a5d1050488ca3bdc426be45b7c431e600f82e): probes/usse/repeat-ptrs.toml probes fetch-offset (8 cases, SETTLED by the shift-always hypothesis), fetch-post (4 cases) and fetch-pre (3 cases), the last two NONE: the table predicted [rb,#k++] to store from b + 1 and move rb by N or by k * N, and [rb,++#k] to leave rb at b + k, none fits (the post and pre rules of the claim are read from those 7 readbacks, so they are fits, not predictions); the data were read out of the scratch dwords as for E482 (the marker 32 dwords past rb's final value), one campaign run"
tiers = ["HW"]
date = "2026-11-08"
data = ["usse-repeat-ptrs"]
terms = []
+++

**Results.** Plain [r40,+#k]: the N registers r2 onward land at b + k + 1 on (b + 3 for k = 2, ...,
b + 16 for k = 15); post [r40,#k++]: from b + k (E482's k = 1 gives b + 1), rb moved by N (marker at
b + N + 32) in the four cases; pre [r40,++#k]: from b + k + 1, rb moved by N (marker at b + N + 32)
in the three. The post-increment's step is the width of the fetch, not k.

**What it shows.** [HW] The offset rule of a fetch store: a plain or pre-incremented fetch starts at
b + k + 1 (the one-dword shift of E482 and E093 for every k run), a post-incremented one at b + k,
and both increments move rb by N. All of this was measured in client pixel tasks (fills), not in
firmware tasks.

**What it does not show.** k above 15, N above 16, the 16-dword copy with k other than 0 (the copy
of E482 used k = 0), the registers of a fetch above r33.
