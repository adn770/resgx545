+++
id = "E514"
claim = "An unfenced stad is seen by a load of another instance that ran earlier and in part by one that ran later, [infer] as a rule of timing (raster and tile order, not a fence): in the pairs with the x and y neighbours in the same 2x2 quad (n ^ 1 and n ^ 64; the diagonal n ^ 65 was not run) every one of 2048 loads returned the partner's value in each of four cases (with and without an idf and its wait), with the instances of other quads (n ^ 2: the next quad in x, n ^ 128: two rows on, n ^ 32: 32 columns on) 1088, 1088 and 1024 of 2048 (all 1024 of the loads whose partner has the lower number, and 64, 64 and 0 of those whose partner has the higher), after 64 and 192 nop 1816 and 2008 of 2048 for n ^ 2 (1024 lower, 792 and 984 higher) and 1024 for n ^ 32 after 192 nop (no higher), and for the partners n ^ 1023, which lie in the other column of 32 (the left half is partner of the right half), 1024 of 2048 in the three cases (no idf, an idf and its wait, 192 nop): exactly the pixels with x from 32 to 63"
unit = "usse"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1126 (sha256 751f7223c8c731a08d75cfc3920a5d1050488ca3bdc426be45b7c431e600f82e): probes/usse/store-own2.toml probe usse-store-own2-cross (11 cases) and probes/usse/store-own3.toml probe usse-store-own3-cross (6 cases), one run each, and the first run usse-store-own-cross (5 cases, SETTLED the \"visible\" hypothesis on same-quad partners only); the verdicts of the second and third are NONE (the hypotheses were visible, not visible and, in store-own3, lower-numbered only, none a mix), so the readbacks were counted from the raw pixel rows by scripts outside the kit; in store-own2 cases 8 to 10 (n ^ 2047) are a table error of mine: the mask 0x1FFC flips bit 12 of the scratch's absolute address, which is set in the base, so the partner lay below the stored region (0 of 2048 in the three cases, kept) and the case was redone as n ^ 1023 in store-own3 (mask 0xFFC); every pixel read, as in E512"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["usse-store-own2", "usse-store-own3", "usse-store-own"]
terms = []
+++

**What runs.** Each instance stores V1(n) to its own dword and then loads the dword of a partner: n
^ 1 and n ^ 64 (its x and y neighbours in the quad; n ^ 65 was not run), n ^ 2 and n ^ 128 (next
quads), n ^ 32 (32 columns on), n ^ 1023, with `wdf drc0` after the load and no idf, an idf and its
wait before the load, or 64 or 192 `nop` between the stad and the load; controls without the stad
read the old value.

**Results.** Counts of the 2048 pixels (partner's V1 / the dword's old value): n ^ 1 and n ^ 64 with
and without the idf: 2048 / 0 in four cases (control without the stad: 0 / 2048). n ^ 2: 1088 / 960;
n ^ 128: 1088 / 960; n ^ 32: 1024 / 1024; in each the pixels with a lower-numbered partner are 1024
of 1024 seen and those with a higher-numbered partner 64, 64 and 0 seen. After 64 and 192 `nop`: n ^
2: 1816 and 2008 (1024 and 1024 lower; 792 and 984 of the higher); n ^ 32 after 192: 1024 (no
higher); n ^ 1023: 1024 in the three cases, the pixels n with x = n mod 64 of 32 to 63.

**What it shows.** [HW] A store of another instance is read by a later load without a fence when
that instance has already run its stad: the x and y neighbours in its quad (n ^ 1 and n ^ 64: 2048
of 2048, 4 cases; n ^ 65 was not run), those of lower-numbered instances in other quads (1024 of
1024 in each of the three masks), and the higher-numbered ones in a measure that grows with the
delay (64 at no delay, 792 after 64 `nop` and 984 after 192 for n ^ 2; 0 for n ^ 32 even after 192
`nop`; an idf before the load did not change the count at n ^ 1023; it was not run at the other
masks). [infer] The instances run roughly in raster order within the 32-wide halves (tiles) of the
64 x 32 target, left half before the right half, so the right half reads all that the left half
stored and the left half reads none of the right (n ^ 1023: 1024 of 1024 for x >= 32, 0 of 1024 for
x < 32), and a quad runs together; the instance number rule is not measured by a timer. All of this
was measured in client pixel tasks (fills), not in firmware tasks.

**What it does not show.** Another instance's load with the other instance's idf, the host reading
during the job, a texture fetch of a stored dword, other target sizes, and whether the order is the
same in a render with more tiles (Q143).
