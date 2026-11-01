+++
id = "E003"
claim = "The firmware file's PATCHES table (our format) holds 81 expression records for 1.7.862890: 9 ukernel immediates, 24 PDS data words, 8 TA3DCtl words and 40 signature-buffer words"
unit = "firmware"
method = "the firmware cut from the Cedarview package (tools/fwcutter) and its PATCHES table counted by buffer, kind and encoding with tools/fwcutter/fwformat.py; the reference loader reproduces both layout captures from it (E002)"
tiers = ["RE", "CAP"]
date = "2026-10-30"
data = ["firmware-images"]
terms = ["CR_EVENT_OTHER_PDS_EXEC", "CR_EVENT_OTHER_PDS_DATA", "CR_USE_CODE_BASE_0", "CR_USE_CODE_BASE_0.ADDR", "CR_USE_CODE_BASE_0.DM", "ta3d_ctl"]
+++

Each record computes one 32-bit value and says how to store it (format: `doc/specs/fw_format.md`
§4).

The `PATCHES` table of the cut 1.7.862890 firmware has 81 records, by buffer:

- **ukernel, 9 `USSE_LIMM`**, the 9 instructions of E002: insn 428 (byte 0xd60) `PDS_CTL` #11,
  0x1000, the `emitpds` control of PDS #11; 430
  (0xd70) `ADDR_SHR4` PDS #11, its `emitpds` address; 431 (0xd78) `ADDR` TA3DCtl, which the boot
  task reads; 438 (0xdb0) `PDS_CTL` #12, 0x100; 440 (0xdc0) `ADDR_SHR4` PDS #12; 456 (0xe40)
  `ADDR` PDS #13, to `EVENT_OTHER_PDS_EXEC`; 458 (0xe50) `PDS_ROWS` #13, to
  `EVENT_OTHER_PDS_DATA`; 5983 (0xbaf8) `PDS_CTL` #14, 0x100; 5986 (0xbb10) `ADDR_SHR4` PDS #14.
- **PDS data segments, 24 `WORD32`** (2, 4, 2, 7 and 9 in PDS #10 to #14): the code words of
  every USSE entry (addend 0x0800000f, except PDS #11's 0xf), PDS #11's TA3DCtl copy source
  address and copy control word 0x03c0003f, and constants (2, 0x100, 0x200, the PDS #14 request
  masks 0x4000f and 0x120080).
- **TA3DCtl, 8 `WORD32`**: `sa0` TA3DCtl, `sa1` HostCtl, `sa2` CCB control, `sa22` CCB, `sa23`
  `PD_PHYS`, `sa43`-`sa45` the HWPerf, TA signature and 3D signature buffers.
- **Signature buffers, 40 `WORD32` `CONST`** (7 TA, 33 3D): the register count (offset 0), then
  6 (TA) or 32 (3D) register offsets from offset 8. The zero word at offset 4 is not a record.
  `infer`: that these are the register offsets the EDM samples is an inference from their
  values; this record does not trace them in the EDM.

Seven of the eight kinds occur in `PATCHES` (53 `CONST`, 10 `ADDR`, 10 `CODE_WORD`, 3 `PDS_CTL`,
3 `ADDR_SHR4`, 1 `PDS_ROWS`, 1 `PD_PHYS`); `HEAP` and the `CODE_BASE` encoding appear in the
`VALUES` lists.

This shows what srvinit computes, not how the hardware uses the values; the kind and encoding
names are ours.
