+++
id = "E209"
claim = "In a two-layer background object the coordinate dwords are read vertex by vertex, layer A's (u, v) then layer B's, when the tag's size field is raised from 2 to 4: coordinate set 1 then copies the 8x4 source and set 2 mirrors it, for the format word at 0, 0x202 and 0x404, and set 2 gives one image for eight format words (0 to 0xffff); with the dwords laid out layer by layer the two sets give other images; with the size field left at 2 both sets give one texel; the format word 0xffffffff breaks the copy"
unit = "isp"
method = "the script background-layers.sh of probes/isp/background-layers.toml on the laptop, linux fork with the debug option on: 20 runs of an 8x4 copy (source texel (x, y) = 0xa5 | y << 16 | x << 8 | (x xor y), so a pixel names the coordinates it sampled) whose background object is rewritten by pokes (bg:3 to bg:28) with layer A the identity and layer B the same mirrored in u, laid out vertex-major or layer-major, with bg:16 at a value, xfer:0 xor 0x06000000 (the tag's size field 2 to 4) or left, and the primary PDS program's iteration (pds:prim:4) fetching coordinate set 1 or 2; every pixel read back; one run"
tiers = ["HW"]
date = "2026-11-02"
data = ["isp-background-layers"]
terms = []
+++

**What runs.** The copy of E069 with a two-layer object: 12 coordinate dwords at bg:3 to bg:14, the
dword at bg:15 zero, the format word at bg:16, four zeros, then the three vertices. Layer A's
coordinates at the three vertices are (0, 0), (1, 0), (0, 1); layer B's are (1, 0), (0, 0), (1, 1).
Vertex-major means each vertex's A pair then its B pair; layer-major means A's three pairs,
then B's.
The script's output ends each case with the tool's exit status: 0 when the copy equals the source
and 1 when a pixel differs, which here only says that the image is not the plain copy.

**Results.** Every case completed ("job: ok"). Images by hash:

| arrangement | tag size | format word | set 1 | set 2 |
|---|---|---|---|---|
| vertex-major | raised to 4 | 0, 0x202, 0x404 | the source, 0 of 32 pixels differ | the source mirrored in u (row 0: u = 7 down to 0, v = y), 32 of 32 differ |
| vertex-major | raised to 4 | 0x101, 0x808, 0xff, 0xff00, 0xffff | not run | the same image as the set 2 above |
| vertex-major | raised to 4 | 0xffffffff | not run | every pixel the texel (0, 0): 31 of 32 differ |
| layer-major | raised to 4 | 0, 0x202, 0x404 | row 0 is u = 0, v = x / 2 (pairs of equal pixels), 31 differ | u = 7 on every pixel and v = y, 28 differ |
| vertex-major | left at 2 | 0x404 | one texel (u = 7, v = 3) on every pixel | the same image as set 1 |

Set 2 of the eight vertex-major format words (0, 0x101, 0x202, 0x404, 0x808, 0xff, 0xff00, 0xffff)
is one image (one hash), and the three layer-major runs of a set are one image each.

**What it shows.** With the tag's size field at 4 the object's coordinate dwords are consumed in
vertex-major order: layer A's and layer B's pair for vertex 0, then for vertex 1, and so on; read
layer-major the same words give different images, so the layout is not layer-major. The format word
at bg:16 did not change the image over eight values between 0 and 0xffff (0x101, 0x202, 0x404,
0x808 and the byte and half masks), and 0xffffffff, which sets bits 31:16, makes every pixel sample
the texel (0, 0). With the size field left at 2 the two-layer words are not read as two layers.

**Not shown.** The size field's effect at values other than 2 and 4. The format word's bits 31:16
were only tried together. The layout of the objects that the tile accelerator writes to the
parameter buffer is not read here. One run, each case once.
