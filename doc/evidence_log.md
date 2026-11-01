<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
# SGX545 evidence log

*Generated from `evidence/` by `tools/records/evidence_log.py`; do not edit.*

Every evidence record, by the day it was made and again by unit: its claim, the unit it belongs to,
its provenance tiers (HW our hardware, CAP captures of the closed stack, RE our reading of the
firmware, DDK the GPL kernel sources, infer an inference) and the datasets or files it rests on. The
record itself, in `evidence/<unit>/`, gives the method and what it does and does not show.

## Chronology

### 2026-10-30

- `E001` srvinit passes the kernel 13 MKIF structure sizes, among them CMDTA 0x2b0, TRANSFERCMD
  0x4c8, HWRENDERDETAILS 0x1ec, HWTRANSFERCONTEXT 0xb4 and HOST_CTL 0x44.
  *firmware; CAP; data: `firmware-layout`.*
- `E002` The EDM reads sa0-sa2 as base pointers into TA3DCtl, HostCtl and the kernel CCB control,
  filled by PDS #11; 9 patched immediates.
  *firmware; CAP, RE; data: `firmware-layout`, `firmware-images`.*
- `E003` The firmware file's PATCHES table (our format) holds 81 expression records for 1.7.862890:
  9 ukernel immediates, 24 PDS data words, 8 TA3DCtl words and 40 signature-buffer words.
  *firmware; RE, CAP; data: `firmware-images`.*
- `E004` Captures of 52 fills and 15 copies of the closed stack reproduce the transfer-queue
  templates of the format's v2 and v3: every piece's bytes sit in libsrv_um where the piece table
  cuts them, every varying field is a TQ_PATCHES record with its encoding and value, and the tables
  rebuild all 441 captured ARGB8888 programs byte for byte.
  *firmware; CAP; data: `firmware-transfer`.*

## By unit

### firmware

Records: E001, E002, E003, E004.
