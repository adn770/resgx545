+++
id = "Q242"
question = "how is the 16-bit stored depth format laid out at a pitch G other than 33 and at an edge, what do the 24-bit and 16-bit formats store for a depth outside 0.25 to 0.4166 other than 1.0 (where round(z * 0xffffff) and floor(z * 2^24) differ), which pixel's value does a dword shared by two overlapping tiles hold, and why did the E411 jobs with G past 3 fault?"
unit = "zls"
kind = "hw"
value = "low"
phase = 12
evidence = ["E466", "E490", "E663"]
terms = ["CR_ISP_ZLSCTL"]
+++

The pipeline simulator (E663) stores the 24-bit format as round(z * 0xffffff) and the 16-bit one as
that shifted right by 8, two rows to a dword at 256 dwords a slot, and refuses everything the dumps
did not cover: a 16-bit store at a pitch other than G = 33 (the layout was derived at G = 33 only,
E490), any integer format over a depth other than 0.25 to 0.4166 and 1.0, a store whose tiles
overlap (a pitch under the tiles of a row: E465 counted the dwords written there and recorded
no values), and, in E411's 16-page scratch arrangement, a pitch G above 3 (bits 5 to 11 of the
control set: the jobs faulted, read as the pitch running out of the buffer, [infer]).

The depth of the format runs lies in 0.25 to 0.4166 (the f0 dumps hold 0.250081 to 0.416585; the
clear value 1.0 is stored by E411's two rows). Four rules were tried on the 786432 dwords of the
24-bit run: floor and ceil of z * 0xffffff differ, round(z * 0xffffff) and floor(z * 2^24)
clamped to 24 bits both give 0 differences. They agree over the range above and differ for most
depths from 0.5 up, so the dumps do not choose between them there.

What would settle it: the format runs of E466 repeated with the depth ramp over 0 to 1, at two or
three other pitches, with the 16-bit format at G of 0, 1 and 511, a target with edge tiles, and
tiles that overlap with a per-tile marker; a scratch run with a buffer longer than the pitch needs;
the dumps kept.

Status: open.
