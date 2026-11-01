+++
id = "Q065"
question = "what does the 3D wait for when render flag bit 0 hangs a kernel-built triangle job (the TA finishes and the 3D takes the render: E361, E435)?"
unit = "render"
kind = "hw"
value = "low"
phase = 11
evidence = ["E050", "E156", "E164", "E165", "E184", "E303", "E304", "E361", "E435"]
terms = ["FRAG_FLAGS.NO_RENDER"]
+++

The TA finish queues a render only for a LAST_KICK command (E156); with NO_RENDER the finish frees
the scene's memory first. On the hardware render flag bit 0 hangs the job (E050). A render without
render flag bit 10 adds nothing to the executed count, and the kernel's count follows (E314).

Narrowed by E361 (one run, held): with render flag bit 0 the TA finishes (the PB descriptor holds
its two pages, both frame numbers read 1) and the 3D takes the render (`hw_render_details_3d`
names it), but the render never completes: the executed count stays 0 against the kernel's pending
1, the RT data state reads 0x20, the context's pending list keeps the render details. So the bit
hangs the render in the 3D, not its cleanup.

What is open: what the 3D waits for with bit 0. Whether one command with both kick flags acts as
two (our tool's scenes always put the geometry in every kick) is the firmware's own behaviour and is
Q119, parked.

To settle it: the same job with the 3D's registers sampled from the kick (regtimeline).

Narrowed in 11.16 (E435, three runs, and five runs at denser sampling): the held job with render
flag bit 0 ends with CR_EVENT_STATUS bit 11 set and 0x0748 at 0x1d in 8 of 8 runs, and the TA
kick's 0x0218 dip shows in some held jobs (2 of 5 at denser sampling) as in the unpoked ones (4 of
5), so the TA's kick runs. What the 3D waits for is not run. Status: narrowed, not answered.
