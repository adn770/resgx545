+++
id = "Q041"
question = "what does FRAG_FLAGS.BIT2 keep after a render, when the completion leaves the access word and the DPM context slot alone under the mask 0xc but no image changes with the bit?"
unit = "render"
phase = 11
evidence = ["E164", "E158", "E051", "E052", "E053"]
terms = ["FRAG_FLAGS.BIT2", "FRAG_FLAGS.NO_DEALLOCATE", "hw_render_details.access_dev_vaddr"]
+++

When the last render target of a render completes, the firmware clears the word that render details
dword 52 points at (`access_dev_vaddr`) and the RT data's entry in TA3DCtl dwords 20 and 21, unless
the render flags meet the mask 0xc (E164). Dwords 20 and 21 record which RT data owns each of the
two DPM context slots (E158), so with the mask met the scene's DPM state stays assigned to its slot
after the render. The mask covers BIT2 (bit 2) and NO_DEALLOCATE (bit 3); whether one of the two
bits is enough or both are needed is not stated.

On the hardware no image changes with either bit: one job per render (E051), a scene of several
kicks and the render after it (E052), and a third render appending to a closed scene (E053) give the
control's images in both runs whether the closing render carries BIT2, NO_DEALLOCATE or both. The
kernel rewrites the RT data's size words and counters before each job (E052), which may undo what
the bits keep.

What is open: what a later job does with the access word and the slot the bits keep, and what BIT2
adds to NO_DEALLOCATE.

To settle it: with the debug option, dump the word `access_dev_vaddr` points at and TA3DCtl dwords
20 and 21 after renders with the render flags at 0, 0x4, 0x8 and 0xc, two runs each; the dumps say
which bits the test needs. Then render the same scene twice with the kernel's rewrite of the RT data
words switched off between the two jobs, with and without the bits: a kept scene shows the first
job's geometry in the second image.
