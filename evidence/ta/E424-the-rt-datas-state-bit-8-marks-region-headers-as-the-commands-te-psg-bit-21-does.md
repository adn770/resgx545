+++
id = "E424"
claim = "Flipping bit 8 of the RT data's state word (kernel poke rtds:19, dword 13 of the RT data) before the first kick makes CR_TE_PSG read 0x01600000 after the kick, and the TA data holds the same bytes as with the TA command's te_psg at 0x01600000 (hash equal in 3 of 3 runs at 64x64 and at 1024x768; 8 and 1536 bytes differ from the control): one region header marked each; the images are the controls' in all 48 jobs and CR_DPM_STATE_CONTEXT_ID read 0 throughout"
unit = "ta"
method = "probes/ta/psg-state.toml (psg-state.sh) on the laptop (direct cable), linux fork f1fad0ed9d0e with the debug option on: sgxfive-test tri at 64x64 and 1024x768, one render and two (-n), three runs each of the control, the TA command's te_psg (--kpoke-render 1:ta:147=0x01600000), the state bit (1:rtds:19^=0x100) and both, 48 jobs, under regtimeline over 0x0218 and 0x0630 from 50 ms before the job, with --dump-render, the dumps' hashes and the bytes that differ from the control's dump (cmp)"
tiers = ["HW", "DDK", "infer"]
date = "2026-11-07"
data = ["ta-psg-state"]
terms = ["CR_TE_PSG", "REGION_HDR.FLAGS", "hw_rt_data.state", "CR_DPM_STATE_CONTEXT_ID"]
+++

**Where the poke is.** The kernel's kpoke space rtds is the RT data set of its render context,
0x50 bytes: the set's six dwords, then the RT data from dword 6 (sgx_render.h,
SGX_RENDER_RTDS_SIZE = 0x18 + 0x38) [DDK: linux fork, source reading]. The RT data's state word
(dword 13, 3d.md section 1.4) is therefore rtds:19; render_words shows it as 0x00000010 (bit 4)
before a first kick. No kernel change is needed to set its bit 8: E409 wrote that no switch sets
it, and rtds:19^=0x100 does.

**Results.** Over the 48 jobs (64x64 and 1024x768, one and two renders, three runs of each of four
cases):

- With rtds:19^=0x100 the timeline of CR_TE_PSG (0x0218) in a one-render job goes 0x01400000 or
  0x01600000 (what the job before left), 0x00400000 for the dip at the kick, 0x01600000; with the
  TA command's te_psg at 0x01600000 it goes 0x01400000, 0x01600000 and stays (no dip shows), as
  E409; unpoked it goes 0x01400000, 0x00400000, 0x01400000. In a two-render job the poke, applied
  to the first kick only, gives 0x01600000 after the first dip and 0x01400000 after the second.
  The register keeps the value of the last kick between jobs: a control that follows a poked job
  can start at 0x01600000.
- The TA data (render_tadata) differs from the control's by 8 bytes at 64x64 and by 1536 bytes at
  1024x768 in the one-render jobs, 3 of 3 runs each, for the command's bit, the state's bit and
  both; the three dumps have the same hash in each size. 8 and 1536 are the numbers of 32x16 tiles
  of the two targets, so one byte of each region header [infer]; the parameter memory
  (render_param) is the control's byte for byte. In the two-render jobs the dumps (taken after the
  second render) equal the control's.
- Every image has the control's hash (24 of 24 one-render and 24 of 24 two-render jobs, in each of
  both renders); no job faulted or hung.
- CR_DPM_STATE_CONTEXT_ID (0x0630) is 0 in all 162 timeline lines of the 48 jobs.

**What it shows.** The RT data's state bit 8 sets CR_TE_PSG bit 21 at the kick and marks the
region headers exactly as the command's te_psg bit 21 does, so the firmware's reading of state bit
8 (E158, step 4) and E305's marking are one mechanism. On this scene the marked headers change no
pixel.

**What it does not show.** What the 3D does with a marked header (the scene is one triangle: no
pixel differs), and the 3D's DPM slot: 0x0630 reads 0 at every change of the register in these
jobs too.
