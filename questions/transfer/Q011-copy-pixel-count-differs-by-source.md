+++
id = "Q011"
question = "why does a copy whose background-object tag (transfer word 0) is wrong read one texel, the source's last, for every pixel, and what stores the samples of CR_ISP_MSAA mode 2 in a copy?"
unit = "transfer"
phase = 6
evidence = ["E028", "E272"]
terms = ["transfer_cmd", "transfer_cmd.isp_background_tag", "transfer_cmd.isp_msaa"]
+++

With word 0 at 0 or bit 24 or 30 flipped every pixel is the texel (63, 31), over both sources;
with word 7 bit 1 (CR_ISP_MSAA mode 2) only the first tile is written, with the texel (16 + x / 2,
8 + y / 2) at (x, y) (E272). So the counts of E028 are answered: 2047 and 2040 are the pixels
that are not the last texel's colour, and 2047 and 2044 those of the enlarged tile plus the
unwritten rest.

What is open: why a wrong tag gives the last texel (the coordinates the hardware takes when the
object it names has no layer, or a layer count it does not read) and which part of the tag each
flip breaks; and what downsamples, or would, the samples of mode 2.

To settle it: the tag's offset moved to a second copy of the background object with other texture
coordinates (bits 24:0) and its layer count 0 and 2 to 63 (bits 30:25), the pixels read back; mode
2 on a copy of 128x64 with the sample positions of E210.
