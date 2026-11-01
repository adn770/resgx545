+++
id = "E508"
claim = "On our stack the 64 x 64 render under the closed driver's 4x settings (mode 2, CR_TE_AA 0xe0000000) stores 4096 pixels that hold 1024 distinct source pixels, the 16 x 8 window of each tile written twice in x and in y: the 4096 stored pixels are not a 64 x 64 image of the pixels; the identity maps of E502 cannot show an average, since every sample slot of a pixel holds the same iterated value and an average equals it"
unit = "isp"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1126 (sha256 751f7223c8c731a08d75cfc3920a5d1050488ca3bdc426be45b7c431e600f82e), the 64 x 64 configuration of probes/isp/msaa-ident.toml with mode 2 and CR_TE_AA 0xe0000000 (A and the repeats D, 3 runs), and the other mode and size runs of E502; the counts of distinct source pixels follow from the rule of E503 (read post hoc), which every one of the 786 tiles equals; the analysis script does not print them"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["isp-msaa-ident"]
terms = ["CR_ISP_MSAA", "CR_TE_AA", "CR_TE_MTILE1", "CR_TE_MACROTILE_STRIDE"]
+++

**Counts.** Mode 2, CR_TE_AA 0xe0000000, 64 x 64: 4096 stored pixels, 1024 distinct source pixels
(8 tiles of 16 x 8 pixels from x = 32 tx + 16, y = 16 ty + 8), each stored four times in a 2 x 2
block; the same at 128 x 128 (4096 distinct of 16384, mode 2, 0x20000000 as well), 96 x 80 (1920
distinct of 7680). Mode 1: 2048 distinct of 4096 at 64 x 64; mode 0: 4096 of 4096. Three runs of
the closed driver's configuration (A and two repeats) agree byte for byte.

**What it shows.** [HW] The multisampled stored image is a quarter (mode 2) or a half (mode 1) of
the pixels, in blocks of samples: a resolve into a 64 x 64 image of 4096 pixels, as the closed
driver's pitch of 64 pixels implies (E333, E339), is not what the render produces by itself. The
stored values cannot show whether a resolve averages: every sample slot of a pixel holds the same
iterated value, so an average equals the value (E502). The colour test is E510's: the control
image has 24 aligned 2 x 2 blocks that mix green and background, partially covered pixels where an
averaging stage would give a third colour, and none appears there. [infer] Together with E439 (no
blend path in the end-of-tile task) and E510 (no single sideband bit of our emit resolves) the
resolve, if the hardware does one, is a later pass of the closed driver and a four-window render in
the sense of E503 is the likelier path (Q138).

**What it does not show.** Whether anything resolves; alpha to coverage and sample coverage (not
reachable with this tool).
