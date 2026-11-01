+++
id = "E020"
claim = "Copies built from the firmware file's templates render exactly on the laptop: a whole 64x32 surface, a 32x16 rectangle from (5,3) of a 320-byte-stride source to (8,4) of a 288-byte-stride destination, and a 33x16 rectangle across tiles, from a texture-heap source whose dwords all differ, with every other destination dword untouched"
unit = "transfer"
method = "the phase-4 kernel's debugfs on the laptop (probes/transfer/copy.toml): xfer_copy (three rectangles) three times, then twice a fill and a copy"
tiers = ["HW"]
date = "2026-10-31"
data = ["transfer-copy"]
terms = ["transfer_cmd.bif_3d_req_base", "transfer_cmd.event_pixel_pds_code"]
+++

**What runs.** The kernel builds the copy's programs from the file's format-v3 templates
(format §10, E004), placed separately from a fill's, a background object with one texture
layer whose coordinates cover the whole source rectangle (0 to 1), and the command with the
layer count 1 in the tag word; the command's 12 TQ_CMD words match the file's.

**Results.** 15 copies out of 15 are exact: each destination dword inside the rectangle equals
the source texel at the same offset from the source's first texel (the pattern `0xa5yyxxzz`
varies the three low bytes with x and y, so a swizzle, a skew or an off-by-one row would show),
every other dword of the three destination pages keeps the sentinel. Fills alternating with
copies stay exact (8 of 8), so each operation's placement of its own programs is enough. Each
copy raises one SW_EVENT (84 to 142 µs, once 927 µs) with the status, CCB and count as in E019.

This does not show texture coordinates other than 0 and 1: each copy's texture is exactly the
copied rectangle, reached through the source address.
