+++
id = "Q038"
question = "when a scene overflows its parameter buffer, are the missing pixels geometry the partial render discards or pixels a later background object paints over, and why does the amount drawn not follow the buffer size?"
unit = "dpm"
phase = 10
evidence = ["E202", "E204", "E160"]
terms = ["Parameter Buffer (PB)", "Dynamic Parameter Management (DPM)"]
+++

A triangle larger than its parameter buffer reports an overflow with the context kept and draws
only part of the image, the same image in both repeats of every size (E202). The EDM's partial
render runs in these jobs, once at 1024x768 and 1 to 10 times at 4096x4096 (E204), by the path
that aborts a macrotile, renders what was tiled and restarts the TA (E160).

Two things do not fit a plain "less buffer, less image". At 1024x768 the lost pixels fall as the
buffer shrinks, 154574 at 0x30 pages, 44191 at 0x28 and 2225 at 0x24, and at 0x23 the job still
reports an overflow and runs a partial render, yet the image is pixel-exact. At 4096x4096 the
amount drawn is not monotone in the buffer size: 0x100 and 0x80 draw more than 0x62, and 0x28 and
0x24 more than 0x30. Two readings fit the partial images: an aborted macrotile's geometry is
discarded, or each partial render paints the whole background object over what earlier renders
stored, since the scene has no colour reload [infer]. Neither is favoured by the data.

To settle it: run the 1024x768 sizes 0x23 to 0x30 and the 4096x4096 sizes with the background
object given a colour different from the target's sentinel and from the first render's clear, so
that a pixel painted over by a later partial render is told from one never drawn; then with a
colour reload of the target between partial renders. Print the missing pixels by macrotile, and
save the parameter buffer at each partial render to see which macrotiles' objects were dropped.
