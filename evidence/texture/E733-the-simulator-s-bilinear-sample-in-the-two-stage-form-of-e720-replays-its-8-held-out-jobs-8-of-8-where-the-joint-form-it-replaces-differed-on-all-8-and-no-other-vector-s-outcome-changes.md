+++
id = "E733"
claim = "The simulator's bilinear sample in the two-stage form of E720 (each 8-bit channel lerped in x on both rows and then in y, each stage (a (64 - f) + b f + 32) >> 6, the weights truncated to 1/64 as before) replays the 8 vectors made from E720's held-out jobs 8 of 8 over 2048 pixels, where the joint form it replaces, (sum + 2048) >> 12, differed on all 8; the outcome of every other vector of the data repository is unchanged (31727 match, of which the 8 new ones, 1112 fitted, 1103 stop, 175 skipped, 1950 left out, 48 of 130 hung jobs predicted, none differs)"
unit = "texture"
method = "offline: tools/usse-asm/vectors.py convert on texture/p1141-recomp/raw/p1141-bilin/raw.txt (the 8 jobs of the bilin script of the 11.39 texture batch in the converter's form, made by make_raw.py) into vectors/nokernel/usse/texture-p1141 (8 vectors), then cargo run --release -p sgx-sim --example replay over the data repository (RESGX545_DATA) before and after the change to crates/sgx-sim/src/tex.rs, and cargo test -p sgx-sim in debug and release; one run each of the replay, no run on the hardware"
tiers = ["HW"]
date = "2026-11-09"
data = ["texture-p1141-recomp", "vectors-texture-p1141"]
terms = ["T0.MINFILTER"]
+++
**Results.** The replay lists one line per USSE vector. Before the change the 8 new vectors read
`mismatch` and 31719 other vectors matched; after it all 8 match and nothing else moved (the replay
of the other 32 000 vectors is the same line for line). The two unit tests that failed on the joint
form (one texel of 1 at fx = fy = 32: the joint form gives 0, the stages 1; texels 1, 2, 3, 4 at fx
= 17, fy = 45: 3 against 2) pass, and so does the test that a fraction of 63.9 / 64 weighs as 63.
The 21 landed `smp-bilinear` vectors give the same words under both forms (E720), so they are
neither changed nor a test of the change.

**What it shows.** [HW] The sampler's bilinear result is the two-stage form on the 1/64 grid of
E720's jobs (every fraction 0 to 63, strided and twiddled textures), and the simulator reproduces
those 8 jobs.

**What it does not show.** The weights' precision: E720's fractions are on the 1/64 grid, so they do
not test that the weights truncate to 1/64 (precisions 64, 128 and 256 give identical images on
them); that rests on the landed vectors (finer weights miss 8 and 15 of the 21) and the 11.32 jobs.
The sample is exact only when no stage rounds, as the joint form was when its sum divided by 4096; a
mip-level blend of samples that round on their own still stops. The gradient footprint, the T3
address chain, sRGB, ETC1 and the texture types and the cube of the same batch are not in the model
(E721 to E726).
