+++
id = "Q119"
question = "does one TA command carrying both FIRST_KICK and LAST_KICK act as two commands in the firmware (a kick and a closing kick)?"
unit = "render"
kind = "fw"
phase = 11
evidence = ["E156", "E165"]
terms = ["GEOM_FLAGS.FIRST_KICK", "GEOM_FLAGS.LAST_KICK", "ta3d_ctl.cmd_ta_dev_vaddr"]
+++

Split off in 11.21 from Q065, whose hardware part (what the 3D waits for under render flag bit 0)
stays there. At TA_FINISHED the EDM queues a render only when the kick carries LAST_KICK (E156), and
the render details reach the 3D queue only through that routine (E165). Our tool's scenes always put
the geometry in every kick, so no run has a command with both flags.

Open: whether one command with both kick flags acts as two. It asks what the closed firmware does
with a command, not what the hardware does, so it is parked.

To settle it: a library job whose closing kick holds no geometry, against a single command with both
flags, the render memory compared.
