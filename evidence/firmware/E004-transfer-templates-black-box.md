+++
id = "E004"
claim = "Captures of 52 fills and 15 copies of the closed stack reproduce the transfer-queue templates of the format's v2 and v3: every piece's bytes sit in libsrv_um where the piece table cuts them, every varying field is a TQ_PATCHES record with its encoding and value, and the tables rebuild all 441 captured ARGB8888 programs byte for byte"
unit = "firmware"
method = "the closed OpenVG stack run under the harness (captures/firmware/transfer.toml: fakedrm, fakewsegl, xfer.c) through fills and copies with varied colours, rectangles, surfaces, formats and heap bases; each transfer followed from its command to the programs the GPU would receive and read with tools/fwcutter/tqcapture.py: a masked byte search of libsrv_um.so for the captured bytes, a diff of every copy of each program, and checks of the CCB, the placements and the ring of the copy's primaries"
tiers = ["CAP"]
date = "2026-10-30"
data = ["firmware-transfer"]
terms = ["CR_PDS_EXEC_BASE", "CR_BIF_3D_REQ_BASE", "CR_USE_CODE_BASE_0",
         "transfer_cmd.event_pixel_pds_code", "transfer_cmd.bif_3d_req_base",
         "transfer_cmd.pds_exec_base", "PORT.DOUTU", "DOUTU0.TEMPS"]
+++

**What ran.** 14 runs of the closed OpenVG stack under the harness, with no GPU, submitted 67
transfers (`SGX_SUBMITTRANSFER`): creating an image fills it, `vgClearImage` fills a
rectangle, `vgCopyImage` copies one. The runs vary the colour (0 to `0xffffffff`), the
rectangle (corners up to x = 2039, y = 1023; sides 1 to 600), the surface (34 to 2048 pixels
wide; ARGB8888, XRGB8888 and RGB565) and, in two runs, the bases of the GENERAL, PIXELSHADER
and PDSPIXEL heaps. 63 of the 67 transfers are ARGB8888; the other 4 are fills of XRGB8888 and
RGB565 surfaces.

**Following a transfer.** The command sits in the client CCB at the kick's shared offset minus
`0xac`. In every run the first command starts at 0 (its shared block at `0xac`), each later one
lies further on in the same CCB and ends inside it, so the CCB does not wrap within a run
(`tqcapture.command_stream`). The words of the command are named as in the glossary where it has
them: `EDMPixelPDSExec` (+0x24, glossary `transfer_cmd.event_pixel_pds_code`) gives the
pixel-event PDS program, `PDSExecBase` (+0x3c, `transfer_cmd.pds_exec_base`) the base the PDS
programs are addressed from, `Bif3DReqBase` (+0x18, `transfer_cmd.bif_3d_req_base`, the GPL DDK's
`EUR_CR_BIF_3D_REQ_BASE`) the base of the background object. The first word, `ISPBgObjTag`
(+0x00), has no glossary term at this point; it is our label for the word whose bits [23:0], in
16-byte units above `Bif3DReqBase`, locate the background object, and whose `TSPDATASIZE` [30:25]
counts its layers (the captures show that and nothing more of it). The background object's PDS
state pointers (dwords 0 and 2: base [23:0] in 16-byte units above `PDSExecBase`, data size
[31:26]) give the secondary and primary PDS programs. The first dword of each PDS program is a
`DOUTU` word (the glossary's `PORT.DOUTU`, a task started on the USE): its word 0 gives the USE
program it starts, and so do the pixel-event program's data dwords 0, 3 and 4. In a `DOUTU` word,
`EXE` [19:4] is the program's offset from the heap base in 8-byte instructions, `CBASE` [3:0] the
offset's bits [22:19] (named after the GPL DDK's `EUR_CR_USE_CODE_BASE_0` to `_15` of
`sgx545defs.h`, glossary `CR_USE_CODE_BASE_0`; the captures show only that it is 0, so that `EXE`
alone gives the offset) and `TRC` [31:24] the temporaries in units of 4 (glossary `DOUTU0.TEMPS`).
All 67 commands chain: no fill has a TSP layer, every copy one, and each step of the request
agrees. A program's extent is its slot (up to the next program in its allocation, or the step
between two placements of it in one allocation) without trailing zero dwords. Every copy of every
program has the size of its `TQ_META` record: `0x10` (`USE_FILL`, `USE_SEC`, `USE_COPY`), `0x38`
(`USE_EOT`), `0x18` (`USE_EOR`, `PDS_PRIM`, `PDS_SEC`), `0xc4` (`PDS_PIXEVENT`), `0x40`
(`PDS_PRIM_1SRC`).

**The template records.** USE programs sit in PIXELSHADER, PDS programs in PDSPIXEL. The PDS
data segments are `0x10` (`PDS_PRIM`, `PDS_SEC`), `0x50` (`PDS_PIXEVENT`, from
`EDMPixelPDSData` = 5) and `0x30` (`PDS_PRIM_1SRC`). The `DOUTU` words carry `TRC` [31:24] = 1
for `USE_EOT` and `USE_EOR` and 0 for `USE_FILL`, `USE_SEC` and `USE_COPY`, which is
`(temps + 3) >> 2` for the recorded temporaries 4, 1 and 0. Where the stack puts them
(`tqcapture.placement_pattern`): the fill shader and `USE_EOT` share one object and the
pixel-event program, `PDS_PRIM` and `PDS_SEC` another, and in both every transfer of a run
gets a new, higher address (rings); `USE_SEC`, `USE_EOR` and `USE_COPY` each sit alone in an
object at one address for the whole run (allocations), and their bytes never vary. The copy's
`PDS_PRIM_1SRC` takes 64-byte slots of an object of its own that holds 16 (`copy_ring`): at each
of the 15 copies the slots after the one used are exactly the cut template (the code dwords
written, the data dwords zero) and the slots up to it differ from it in patched fields only.
Every address is a multiple of 16 (`PDS_PRIM_1SRC`: 64) and no copy crosses a 4 KiB page.

**The pieces.** For each piece of the table, libsrv_um.so was searched for the captured bytes
under it, with the bits that vary or that a patch writes as don't-care. All 21 pieces are found
at their offset. Seven are the only place with those bytes (`USE_FILL` +12, `USE_EOT` +44, +48,
+52, `USE_EOR` +16, +20, `PDS_PRIM_1SRC`). Eight, the other 4-byte pieces of `USE_EOT` and
`USE_EOR` (5 to 57 places each), are placed at the candidate nearest the template's unique
pieces: the table's offset is that candidate. Six are one of several equal copies the search
cannot tell apart: `USE_FILL` +0 (one of 53), `USE_SEC` (2), `PDS_PRIM` and `PDS_SEC` (the same
2 places, `0x227e0` and `0x229a0`), `PDS_PIXEVENT` (`0x23080` and `0x23160`) and `USE_COPY`
(`0x21d60` and `0x223a8`); any of them cuts the same bits. No template byte with a fixed, unpatched,
non-zero bit lies outside a piece.

**The patched fields.** 15 fields vary between copies, each exactly a per-transfer record of
`TQ_PATCHES` at the same offset, with the same encoding and value: the colour (`USE_FILL` +8),
the four PBE words (`USE_EOT` +8 to +32) and the sideband (+48), the `DOUTU` words of the PDS
programs (`PDS_PRIM`, `PDS_SEC`, `PDS_PRIM_1SRC` +0; `PDS_PIXEVENT` +0, +12, +16) and the
copy's texture words T2, T0, T1 (`PDS_PRIM_1SRC` +24, +32, +36). No bit varies outside a field
`TQ_PATCHES` writes. The colour varies in all 32 bits of the immediate, which fills its three
fields e[20:0], e[40:36], e[49:44]; the PBE words vary inside the same fields. In the `DOUTU`
words bits [15:5] vary with the placement and `CBASE` [3:0] is 0 in every copy (every program
lies in the first 512 KiB of its heap). Of the sideband only value bits [1:0] vary (e[23:22]).
Each of the 16 `CONST` records holds in every copy; 11 write values the cut templates do not
hold, so the captures show them: the destination registers `1 << 21`, `2 << 21`, `3 << 21` of
`USE_EOT` +16, +24, +32, `U1` = 4 of `PDS_PRIM` and `PDS_SEC`, `0x02000004` of
`PDS_PRIM_1SRC`, `0x00800000` and `0x00c00000` of the pixel-event program (+4, +20, +48), and
`DOUTI` `0x40012001` and T3 `0xa0800000` of `PDS_PRIM_1SRC`. The other 5 write a 0 the template
already holds (data dword 2 of each PDS program and the copy's `DOUTI` word 1). The registers
are in no run of the library: searched with the immediates as don't-care and the registers
cared (`tqcapture.dest_register_search`), a single load of `USE_EOT` is found in 2 (+8, `r0`), 9
(+16), 2 (+24) and 0 places (+32), but no two consecutive loads of the template, so no run of 16
or more bytes of the library could be cut as the template's loads.

**The parameters.** For the 63 ARGB8888 transfers, the tables, with each program placed where
the capture placed it and the parameters of format §9.6 and §10.4 computed from the request,
rebuild all 441 programs byte for byte, and the 12 `TQ_CMD` words hold in all 67 commands
(`PDSExecBase` follows the moved PDSPIXEL heap). The request gives the colour, the rectangle
(OpenVG's coordinates as they are: the stack stores line 0 first), the surface address (the
image's allocation) and the stride: the stack pads each line to 8 pixels (34 pixels: 160 bytes,
`LINESTRIDE` `0x13`). A copy's T words describe the whole source surface (its base, size and
stride), not the copied rectangle; its PBE words the destination rectangle. XRGB8888 and RGB565
fills keep the colour immediate in ARGB8888 (`0xff5a5a5a` for both); their sideband is `0x200`
and `0x203`, and a 64-pixel RGB565 surface has `LINESTRIDE` `0x1f` (pixel pairs).

**What it does not show.** Which of several equal copies the library itself reads (the six
pieces above); the template bits under patched fields, never seen unpatched, and so the
templates' SHA-256 beyond the bits they share with the captures; the temporaries beyond
`(temps + 3) >> 2` and the PDS attributes; the alignment the allocator requires and its page
rule, which every placement satisfies; `DOUTU`'s `CBASE` field and the sideband above bit 1;
the 5 `CONST` records that write the template's own 0. No GPU ran: what the hardware does with
the programs is not shown here.
