+++
id = "Q295"
question = "why does the tick stop after slot 3's end-of-render pass when our task skips the closed handler and ends the pass with the phase end (E836: at least 10 ticks were served after the pass, then the tick stopped with E537's signature within about 20 ms, 1 job; E823: the same pass ended without the phase end stopped it at once), and what of the closed end-of-render handler does a later pass need"
unit = "edm"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E823", "E835", "E836", "E837"]
terms = ["Event Data Master (EDM)", "CR_EVENT_STATUS"]
+++
Split on 2026-11-11 from the question on the end of a pass (answered by E836), when round 4's
session r4-events answered it: a tick pass and a kick pass of ours are finished for the EDM when
they execute `phas #0, #0, pixel, end, parallel` before `nop.end` (E817, E830, E835), and the slot 3
end-of-render pass ended that way was finished too (E836: 10 ticks on the grid after it, where
E823's pass without the phase end was followed by nothing), but the tick stopped later, inside the
50 ms status watch, with E537's busy signature, the fill held, `CR_EVENT_STATUS` bit 18 set as a
level (E837), and a host clear of bit 18 did not restart it (P3 not answered). What is left is
what the skipped closed handler does that the EDM needs later.

Candidates [infer]: the handler's acknowledgement of bit 18 (a host clear came after the stop, so
one before it is untested), the render's state that a later closed pass waits for (a pass that
polls and never ends reads the same signature, E811), or a later event of the held render. The
stop's time is an estimate (HostCtl dword 12 froze about 20 passes later than in E823's job; the
ring was full after 10 ticks).

To settle it: B1P with a larger ring or a ring that keeps the last entries (when and in which pass
the tick stops), replicated; a host write of bit 18 to `CR_EVENT_HOST_CLEAR` right after the slot 3
entry, before the stop; and the skipped pass followed by a tail call to the closed slot 3 handler
on the next one, one stop at most a stage. Value medium: a firmware of our own must end the slot 3
pass itself.
