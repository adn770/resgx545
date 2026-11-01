+++
id = "Q050"
question = "what do the visibility group's instructions do, and how do smp's mipmaps and LOD values, the border address modes, the compressed and YUV formats and firh's rounding biases and coefficient loads behave?"
unit = "usse"
phase = 11
evidence = ["E083", "E091", "E123", "E147"]
terms = []
+++

The probes ran a case for each of 16 groups of forms that had no hardware readback (E091), pinned
atst8 as an alpha test of src0's top byte against src2's under the function in src2 bits 15:13
(E083), and fitted bilin, firv and firh models to every video-filter case they were fitted to
(E123). Run through the simulator, the vectors show no mismatch, but it stops on 19,243 USSE
vectors rather than guess: 16,521 of them firh vectors whose coefficients come from the job, and
1,126 more firh centred below byte 0 (E147).

What is open (usse_isa.md §8, item 1): the rest of the visibility group, which no program of ours
has run; smp with mipmaps and LOD values; the border address modes; the compressed and YUV texture
formats; fdpc's clip-plane result outside the TA state our kernel sets; and firh below #-4, its
rounding biases and how its coefficient sets are loaded.

To settle it: a probe table per group on the laptop with the campaign runner: the visibility group's
forms each with a known test value and the visibility counters read back; smp over level-tagged mip
chains and border colours (with Q009's texture words); firh with the job's CR_USE_COEFFS words set
to known taps, so its vectors carry their coefficients.
