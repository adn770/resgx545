+++
id = "Q158"
question = "which sa, i and temporaries of a firmware task keep their value across a debugfs reset and across a firmware reload and boot (E536's controls read i0, i1, sa100 and sa127 as the writer of phase 11.29 left them 15 minutes and a reset and a reload earlier, and sa20, sa24, sa64, r20 and r21 not)"
unit = "edm"
kind = "hw"
value = "low"
phase = 11
evidence = ["E536", "E537"]
terms = ["Event Data Master (EDM)", "Universal Scalable Shader Engine (USSE)"]
+++

E536's two controls and E537's first control. Between the writer of 11.29 (E533) and E536's
controls there were a debugfs reset, a stock check and the reload of the arming; i0, i1, sa100 and
sa127 had the 11.29 values, sa20, sa24 and sa64 did not, and r20 and r21 held what client fills
leave. Between E536's third round and E537's control there was a reload: sa100, sa127, i0 and r21
were E536's, sa20 and sa24 read 0, sa63 0, sa64 2 and sa65 0x02000000. If a reset does not clear
the registers the firmware does not load, a backend that relies on "sa starts at zero" is wrong
above the range the boot loads. To settle it: write a marker to sa100, i0, r20 and sa20 from a
writer, reset (debugfs) and read them with the plain reader; with a reload and boot between; and
across a client fill. The question needs the closed task only for the tick, not for itself.
