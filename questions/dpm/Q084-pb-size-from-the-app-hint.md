+++
id = "Q084"
question = "how does the closed driver turn its PBSize app hint into the parameter buffer's page count and thresholds, given 1 MiB and 8 MiB both give 98 pages and 768 KiB fails?"
unit = "dpm"
phase = 11
evidence = ["E327"]
terms = ["hw_pb_desc.ta_threshold", "hw_pb_desc.zls_threshold", "hw_pb_desc.global_threshold", "hw_pb_desc.pds_threshold", "pb_block.page_count"]
+++

At the default size the closed GLES2 stack's parameter buffer is 0x422 pages with thresholds TA
0x432, ZLS 0x400, global 0x400 and PDS 0x300; with PBSize=1048576 and with PBSize=8388608 it is
0x62 pages with thresholds 0x72, 0x40, 0x40 and 0; PBSize=786432 and every smaller value fail
eglInitialize with EGL_BAD_ALLOC, and MaxParamBufferSize changes nothing (E327, one capture each).
The TA threshold is the page count plus 16 at both sizes; the other three fit no rule two sizes
can pin, and 1 MiB and 8 MiB giving the same 98 pages fits neither a page count from PBSize nor a
clamp to the default.

What is open: the mapping from PBSize to pages (a clamp, a unit other than bytes, a parse of the
value), the threshold rule, and why the default is larger than an 8 MiB request gives.

To settle it: capture PBSize over a ladder (1, 1.5, 2, 3, 4, 4.2, 5 and 16 MiB, and values just
above 786432) with one draw each, and read the descriptor's page count and thresholds; repeat a
few with MaxParamBufferSize set at and above the PBSize, to see whether one bounds the other.
