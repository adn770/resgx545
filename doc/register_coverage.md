<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
# SGX545 register coverage

*Generated from `glossary/` and `evidence/` by `tools/records/register_coverage.py`; do not edit.*

Every register the glossary places at an offset, with the bits a record measured as implemented (the
bits that took a write), the field rows that name its bits, and the bits no field covers. Where no
record measured the register, all 32 bits are assumed; a register with no field rows carries its
meaning at register level (an address, a count) or has fields still to name. Records are the
evidence records its rows, its fields' rows and its measured width cite.

## Summary

| unit | registers | with fields | measured width | uncovered bits | on a measured width |
|---|---|---|---|---|---|
| (no unit) | 11 | 1 | 11 | 0 | 0 |
| BIF | 11 | 11 | 0 | 154 | 0 |
| CACHE | 1 | 0 | 0 | 0 | 0 |
| CLKGATE | 3 | 3 | 0 | 35 | 0 |
| CORE | 2 | 2 | 0 | 0 | 0 |
| DMS | 1 | 0 | 0 | 0 | 0 |
| DPM | 37 | 2 | 18 | 0 | 0 |
| EVENT | 16 | 9 | 0 | 102 | 0 |
| HWPERF | 11 | 1 | 10 | 9 | 9 |
| ISP | 34 | 4 | 29 | 31 | 31 |
| MTE | 6 | 0 | 5 | 0 | 0 |
| PDS | 9 | 5 | 2 | 115 | 2 |
| PPP | 2 | 0 | 1 | 0 | 0 |
| SETTLE | 2 | 0 | 0 | 0 | 0 |
| SOFT | 1 | 1 | 0 | 26 | 0 |
| TA | 4 | 0 | 4 | 0 | 0 |
| TE | 13 | 0 | 10 | 0 | 0 |
| TIMER | 1 | 1 | 0 | 0 | 0 |
| TPU | 14 | 2 | 14 | 2 | 2 |
| TSP | 1 | 0 | 0 | 0 | 0 |
| USE | 32 | 6 | 12 | 65 | 0 |
| VDM | 2 | 0 | 1 | 0 | 0 |
| total | 214 | 48 | 117 | 539 | 44 |

## (no unit)

- `0x0148` `CR_REG_0148`: width 1 bits (0, E252); no field rows. Records: E056, E252.
- `0x0324` `CR_REG_0324`: width 28 bits (31:4, E054, E247); no field rows. Records: E030, E054,
  E056, E071, E072, E159, E182, E183, E247.
- `0x0364` `CR_REG_0364`: width 32 bits (31:0, E054, E247); no field rows. Records: E030, E054,
  E056, E071, E072, E159, E182, E183, E247.
- `0x0368` `CR_REG_0368`: width 15 bits (14:0, E054, E247); no field rows. Records: E030, E054,
  E056, E071, E072, E159, E182, E183, E247.
- `0x0370` `CR_REG_0370`: width 32 bits (31:0, E054, E247); no field rows. Records: E030, E054,
  E056, E071, E072, E159, E182, E183, E247.
- `0x0374` `CR_REG_0374`: width 32 bits (31:0, E054, E247); no field rows. Records: E030, E054,
  E056, E071, E072, E159, E182, E183, E247.
- `0x0400` `CR_REG_0400`: width 13 bits (25, 11:0, E251); 2 fields: INVERT_BYTE3 [25], BITS11_0
  [11:0]; uncovered - (0 bits). Records: E028, E029, E251.
- `0x0800` `CR_REG_0800`: width 22 bits (23:8, 5:0, E067); no field rows. Records: E006, E066, E067,
  E068, E073, E136, E225.
- `0x0810` `CR_REG_0810`: width 1 bits (0, E026); no field rows. Records: E006, E026.
- `0x0814` `CR_REG_0814`: width 17 bits (16:0, E026); no field rows. Records: E006, E026.
- `0x0818` `CR_REG_0818`: width 11 bits (10:0, E026); no field rows. Records: E006, E026.

## BIF

- `0x0c00` `CR_BIF_CTRL`: width 32 bits assumed; 13 fields: MMU_BYPASS_HOST [15], MMU_BYPASS_USE
  [14], MMU_BYPASS_ISP [13], MMU_BYPASS_TSPP [12], MMU_BYPASS_PBE [11], MMU_BYPASS_TE [10],
  MMU_BYPASS_VDM [9], MMU_BYPASS_CACHE [8], CLEAR_FAULT [4], INVAL_DC [3], FLUSH [2], PAUSE [1],
  NO_REORDER [0]; uncovered 31:16, 7:5 (19 bits).
- `0x0c04` `CR_BIF_INT_STAT`: width 32 bits assumed; 3 fields: FLUSH_COMPLETE [19], FAULT_TYPE
  [18:16], FAULT_REQ [15:0]; uncovered 31:20 (12 bits).
- `0x0c08` `CR_BIF_FAULT`: width 32 bits assumed; 3 fields: ADDR [31:12], SB [8:4], CID [3:0];
  uncovered 11:9 (3 bits).
- `0x0c38` `CR_BIF_DIR_LIST_BASE1`: width 32 bits assumed; 1 field: ADDR [31:8]; uncovered 7:0 (8
  bits).
- `0x0c70` `CR_BIF_DIR_LIST_BASE15`: width 32 bits assumed; 1 field: ADDR [31:8]; uncovered 7:0 (8
  bits).
- `0x0c74` `CR_BIF_BANK_SET`: width 32 bits assumed; 6 fields: SELECT_DPM_LSS [9], SELECT_EDM [8],
  SELECT_TA [7:6], SELECT_HOST [4], SELECT_3D [3:2], SELECT_2D [0]; uncovered 31:10, 5, 1 (24 bits).
- `0x0c78` `CR_BIF_BANK0`: width 32 bits assumed; 5 fields: INDEX_2D [19:16], INDEX_3D [15:12],
  INDEX_HOST [11:8], INDEX_TA [7:4], INDEX_EDM [3:0]; uncovered 31:20 (12 bits).
- `0x0c84` `CR_BIF_DIR_LIST_BASE0`: width 32 bits assumed; 1 field: ADDR [31:8]; uncovered 7:0 (8
  bits).
- `0x0c90` `CR_BIF_TA_REQ_BASE`: width 32 bits assumed; 1 field: ADDR [31:20]; uncovered 19:0 (20
  bits).
- `0x0cac` `CR_BIF_3D_REQ_BASE`: width 32 bits assumed; 1 field: ADDR [31:20]; uncovered 19:0 (20
  bits).
- `0x0cb0` `CR_BIF_ZLS_REQ_BASE`: width 32 bits assumed; 1 field: ADDR [31:20]; uncovered 19:0 (20
  bits).

## CACHE

- `0x0804` `CR_CACHE_CTRL`: width 32 bits assumed; no field rows.

## CLKGATE

- `0x0000` `CR_CLKGATECTL`: width 32 bits assumed; 9 fields: AUTO_MAN_REG [24], PDS0_CLKG [15:14],
  VDM_CLKG [13:12], DPM_CLKG [11:10], MTE_CLKG [9:8], TE_CLKG [7:6], TSP_CLKG [5:4], ISP2_CLKG
  [3:2], ISP_CLKG [1:0]; uncovered 31:25, 23:16 (15 bits).
- `0x0004` `CR_CLKGATECTL2`: width 32 bits assumed; 12 fields: PDS1_CLKG [23:22], MADD1_CLKG
  [21:20], TEX1_CLKG [19:18], ITR1_CLKG [17:16], USE1_CLKG [15:14], MADD0_CLKG [13:12], TEX0_CLKG
  [11:10], ITR0_CLKG [9:8], USE0_CLKG [7:6], UCACHEL2_CLKG [5:4], CACHEL2_CLKG [3:2], PBE_CLKG
  [1:0]; uncovered 31:24 (8 bits).
- `0x0008` `CR_CLKGATESTATUS`: width 32 bits assumed; 20 fields: PDS1_CLKS [19], MADD1_CLKS [18],
  TEX1_CLKS [17], ITR1_CLKS [16], USE1_CLKS [15], MADD0_CLKS [14], TEX0_CLKS [13], ITR0_CLKS [12],
  USE0_CLKS [11], UCACHEL2_CLKS [10], CACHEL2_CLKS [9], PBE_CLKS [8], PDS0_CLKS [7], VDM_CLKS [6],
  DPM_CLKS [5], MTE_CLKS [4], TE_CLKS [3], TSP_CLKS [2], ISP2_CLKS [1], ISP_CLKS [0]; uncovered
  31:20 (12 bits).

## CORE

- `0x001c` `CR_CORE_ID`: width 32 bits assumed; 2 fields: ID [31:16], CONFIG [15:0]; uncovered - (0
  bits).
- `0x0020` `CR_CORE_REVISION`: width 32 bits assumed; 4 fields: DESIGNER [31:24], MAJOR [23:16],
  MINOR [15:8], MAINTENANCE [7:0]; uncovered - (0 bits).

## DMS

- `0x0a74` `CR_DMS_CTRL`: width 32 bits assumed; no field rows.

## DPM

- `0x0600` `CR_DPM_3D_PAGE_TABLE_BASE`: width 28 bits (31:4, E253); no field rows. Records: E253.
- `0x0604` `CR_DPM_3D_FREE_LIST`: width 32 bits (31:0, E253); no field rows. Records: E253.
- `0x0618` `CR_DPM_TA_ALLOC_PAGE_TABLE_BASE`: width 28 bits (31:4, E253); no field rows. Records:
  E253.
- `0x061c` `CR_DPM_TA_ALLOC_FREE_LIST`: width 32 bits (31:0, E253); no field rows. Records: E253.
- `0x0620` `CR_DPM_TA_PAGE_THRESHOLD`: width 16 bits (15:0, E253); no field rows. Records: E253.
- `0x0624` `CR_DPM_ZLS_PAGE_THRESHOLD`: width 16 bits (15:0, E253); no field rows. Records: E253.
- `0x0628` `CR_DPM_TA_GLOBAL_LIST`: width 17 bits (16:0, E253); no field rows. Records: E253.
- `0x062c` `CR_DPM_STATE_BASE0`: width 28 bits (31:4, E253); no field rows. Records: E158, E253.
- `0x0630` `CR_DPM_STATE_CONTEXT_ID`: width 3 bits (2:0, E253); no field rows. Records: E253.
- `0x0634` `CR_DPM_CONTROL_BASE`: width 28 bits (31:4, E253); no field rows. Records: E158, E253.
- `0x0638` `CR_DPM_TA_PAGE_COUNTS`: width 32 bits (31:0, E253); 2 fields: GLOBAL [31:16], LOCAL
  [15:0]; uncovered - (0 bits). Records: E200, E253.
- `0x063c` `CR_DPM_3D_DEALLOCATE`: width 32 bits assumed; no field rows.
- `0x0648` `CR_DPM_TA_ALLOC`: width 32 bits assumed; no field rows.
- `0x064c` `CR_DPM_3D`: width 32 bits assumed; no field rows.
- `0x0658` `CR_DPM_PARTIAL_RENDER`: width 32 bits assumed; no field rows. Records: E163, E199, E204,
  E205.
- `0x065c` `CR_DPM_SPM_SWITCH`: width 1 bits (0, E253); no field rows. Records: E199, E253.
- `0x0660` `CR_DPM_3D_PAGE_COUNTS`: width 32 bits (31:0, E253); 2 fields: GLOBAL [31:16], LOCAL
  [15:0]; uncovered - (0 bits). Records: E200, E253.
- `0x0664` `CR_DPM_CONTEXT_PB_BASE`: width 3 bits (2:0, E253); no field rows. Records: E253.
- `0x0668` `CR_DPM_PDS_THRESHOLD`: width 16 bits (15:0, E253); no field rows. Records: E200, E253.
- `0x0674` `CR_DPM_STATE_BASE1`: width 28 bits (31:4, E253); no field rows. Records: E158, E253.
- `0x0680` `CR_DPM_TASK_3D_FREE`: width 32 bits assumed; no field rows.
- `0x0684` `CR_DPM_TASK_TA_FREE`: width 32 bits assumed; no field rows.
- `0x0694` `CR_DPM_TASK_STATE`: width 32 bits assumed; no field rows.
- `0x0698` `CR_DPM_TASK_CONTROL`: width 32 bits assumed; no field rows.
- `0x069c` `CR_DPM_OUTOFMEM`: width 32 bits assumed; no field rows.
- `0x06a0` `CR_DPM_FREE_CONTEXT`: width 32 bits assumed; no field rows.
- `0x0700` `CR_DPM_TA_ALLOC_FREE_LIST_STATUS1`: width 32 bits assumed; no field rows.
- `0x070c` `CR_DPM_3D_FREE_LIST_STATUS1`: width 32 bits assumed; no field rows.
- `0x0710` `CR_DPM_TA_ALLOC_FREE_LIST_STATUS2`: width 32 bits assumed; no field rows.
- `0x071c` `CR_DPM_3D_FREE_LIST_STATUS2`: width 32 bits assumed; no field rows.
- `0x0720` `CR_DPM_ABORT_STATUS_MTILE`: width 32 bits assumed; no field rows.
- `0x0724` `CR_DPM_PAGE_STATUS`: width 32 bits assumed; no field rows.
- `0x0728` `CR_DPM_PAGE`: width 32 bits assumed; no field rows.
- `0x072c` `CR_DPM_GLOBAL_PAGE_STATUS`: width 32 bits assumed; no field rows.
- `0x0734` `CR_DPM_REQUESTING`: width 32 bits assumed; no field rows.
- `0x073c` `CR_DPM_3D_RT_INDEX`: width 9 bits (8:0, E253); no field rows. Records: E163, E253.
- `0x074c` `CR_DPM_REG_074C`: width 9 bits (8:0, E253); no field rows. Records: E030, E056, E071,
  E072, E159, E203, E206, E253.

## EVENT

- `0x0110` `CR_EVENT_HOST_ENABLE2`: width 32 bits assumed; 15 fields: MTE_STATE_FLUSHED [15],
  VDM_CONTEXT_LOAD [14], VDM_TASK_KICKED [13], OTPM_MEM_CLEARED [12], OTPM_FLUSHED_INV [11],
  DCU_INVAL_COMPLETE [10], GSG_FLUSHED [9], GSG_LOADED [8], TRIG_TA [7], TRIG_3D [6], TRIG_DL [5],
  DPM_DHOST_FREE_LOAD [3], DPM_HOST_FREE_LOAD [2], DPM_3D_FREE_LOAD [1], DPM_TA_FREE_LOAD [0];
  uncovered 31:16, 4 (17 bits).
- `0x0114` `CR_EVENT_HOST_CLEAR2`: width 32 bits assumed; 15 fields: MTE_STATE_FLUSHED [15],
  VDM_CONTEXT_LOAD [14], VDM_TASK_KICKED [13], OTPM_MEM_CLEARED [12], OTPM_FLUSHED_INV [11],
  DCU_INVAL_COMPLETE [10], GSG_FLUSHED [9], GSG_LOADED [8], TRIG_TA [7], TRIG_3D [6], TRIG_DL [5],
  DPM_DHOST_FREE_LOAD [3], DPM_HOST_FREE_LOAD [2], DPM_3D_FREE_LOAD [1], DPM_TA_FREE_LOAD [0];
  uncovered 31:16, 4 (17 bits).
- `0x0118` `CR_EVENT_STATUS2`: width 32 bits assumed; 15 fields: MTE_STATE_FLUSHED [15],
  VDM_CONTEXT_LOAD [14], VDM_TASK_KICKED [13], OTPM_MEM_CLEARED [12], OTPM_FLUSHED_INV [11],
  DCU_INVAL_COMPLETE [10], GSG_FLUSHED [9], GSG_LOADED [8], TRIG_TA [7], TRIG_3D [6], TRIG_DL [5],
  DPM_DHOST_FREE_LOAD [3], DPM_HOST_FREE_LOAD [2], DPM_3D_FREE_LOAD [1], DPM_TA_FREE_LOAD [0];
  uncovered 31:16, 4 (17 bits).
- `0x012c` `CR_EVENT_STATUS`: width 32 bits assumed; 29 fields: MASTER_INTERRUPT [31], TIMER [29],
  TA_DPM_FAULT [28], MADD_CACHE_INVAL_COMPLETE [26], DPM_OUT_OF_MEMORY_ZLS [25], DPM_TA_MEM_FREE
  [24], ISP_END_TILE [23], DPM_INIT_END [22], ISP2_ZLS_CSW_FINISHED [21], OTPM_INV [20],
  OTPM_FLUSHED [19], PIXELBE_END_RENDER [18], ISP_VISIBILITY_FAIL [16], BREAKPOINT [15], SW_EVENT
  [14], TA_FINISHED [13], TA_TERMINATE [12], TPC_CLEAR [11], TPC_FLUSH [10], DPM_CONTROL_CLEAR [9],
  DPM_CONTROL_LOAD [8], DPM_CONTROL_STORE [7], DPM_STATE_CLEAR [6], DPM_STATE_LOAD [5],
  DPM_STATE_STORE [4], DPM_REACHED_MEM_THRESH [3], DPM_OUT_OF_MEMORY_GBL [2], DPM_OUT_OF_MEMORY_MT
  [1], DPM_3D_MEM_FREE [0]; uncovered 30, 27, 17 (3 bits).
- `0x0130` `CR_EVENT_HOST_ENABLE`: width 32 bits assumed; 29 fields: MASTER_INTERRUPT [31], TIMER
  [29], TA_DPM_FAULT [28], MADD_CACHE_INVAL_COMPLETE [26], DPM_OUT_OF_MEMORY_ZLS [25],
  DPM_TA_MEM_FREE [24], ISP_END_TILE [23], DPM_INIT_END [22], ISP2_ZLS_CSW_FINISHED [21], OTPM_INV
  [20], OTPM_FLUSHED [19], PIXELBE_END_RENDER [18], ISP_VISIBILITY_FAIL [16], BREAKPOINT [15],
  SW_EVENT [14], TA_FINISHED [13], TA_TERMINATE [12], TPC_CLEAR [11], TPC_FLUSH [10],
  DPM_CONTROL_CLEAR [9], DPM_CONTROL_LOAD [8], DPM_CONTROL_STORE [7], DPM_STATE_CLEAR [6],
  DPM_STATE_LOAD [5], DPM_STATE_STORE [4], DPM_REACHED_MEM_THRESH [3], DPM_OUT_OF_MEMORY_GBL [2],
  DPM_OUT_OF_MEMORY_MT [1], DPM_3D_MEM_FREE [0]; uncovered 30, 27, 17 (3 bits).
- `0x0134` `CR_EVENT_HOST_CLEAR`: width 32 bits assumed; 29 fields: MASTER_INTERRUPT [31], TIMER
  [29], TA_DPM_FAULT [28], MADD_CACHE_INVAL_COMPLETE [26], DPM_OUT_OF_MEMORY_ZLS [25],
  DPM_TA_MEM_FREE [24], ISP_END_TILE [23], DPM_INIT_END [22], ISP2_ZLS_CSW_FINISHED [21], OTPM_INV
  [20], OTPM_FLUSHED [19], PIXELBE_END_RENDER [18], ISP_VISIBILITY_FAIL [16], BREAKPOINT [15],
  SW_EVENT [14], TA_FINISHED [13], TA_TERMINATE [12], TPC_CLEAR [11], TPC_FLUSH [10],
  DPM_CONTROL_CLEAR [9], DPM_CONTROL_LOAD [8], DPM_CONTROL_STORE [7], DPM_STATE_CLEAR [6],
  DPM_STATE_LOAD [5], DPM_STATE_STORE [4], DPM_REACHED_MEM_THRESH [3], DPM_OUT_OF_MEMORY_GBL [2],
  DPM_OUT_OF_MEMORY_MT [1], DPM_3D_MEM_FREE [0]; uncovered 30, 27, 17 (3 bits).
- `0x0a58` `CR_EVENT_PDS_ENABLE`: width 32 bits assumed; no field rows.
- `0x0a5c` `CR_EVENT_PIXEL_PDS_CODE`: width 32 bits assumed; no field rows.
- `0x0a60` `CR_EVENT_PIXEL_PDS_DATA`: width 32 bits assumed; no field rows.
- `0x0a64` `CR_EVENT_PIXEL_PDS_INFO`: width 32 bits assumed; no field rows. Records: E129.
- `0x0a68` `CR_EVENT_OTHER_PDS_EXEC`: width 32 bits assumed; no field rows. Records: E002.
- `0x0a6c` `CR_EVENT_OTHER_PDS_DATA`: width 32 bits assumed; no field rows. Records: E002.
- `0x0a70` `CR_EVENT_OTHER_PDS_INFO`: width 32 bits assumed; no field rows.
- `0x0ac4` `CR_EVENT_KICKER`: width 32 bits assumed; 1 field: ADDRESS [31:4]; uncovered 3:0 (4
  bits).
- `0x0ac8` `CR_EVENT_KICK`: width 32 bits assumed; 1 field: NOW [0]; uncovered 31:1 (31 bits).
- `0x0acc` `CR_EVENT_TIMER`: width 32 bits assumed; 2 fields: ENABLE [24], VALUE [23:0]; uncovered
  31:25 (7 bits).

## HWPERF

- `0x0040` `CR_HWPERF_CTRL`: width 13 bits (12:0, E246); 1 field: GROUP [12:9]; uncovered 8:0 (9
  bits). Records: E149, E150, E246.
- `0x0044` `CR_HWPERF_COUNTER0`: width 0 bits (-, E246); no field rows. Records: E149, E150, E246.
- `0x0048` `CR_HWPERF_COUNTER1`: width 0 bits (-, E246); no field rows. Records: E149, E150, E246.
- `0x004c` `CR_HWPERF_COUNTER2`: width 0 bits (-, E246); no field rows. Records: E149, E150, E246.
- `0x0050` `CR_HWPERF_COUNTER3`: width 0 bits (-, E246); no field rows. Records: E149, E150, E246.
- `0x0054` `CR_HWPERF_COUNTER4`: width 0 bits (-, E246); no field rows. Records: E149, E150, E246.
- `0x0058` `CR_HWPERF_COUNTER5`: width 0 bits (-, E246); no field rows. Records: E149, E150, E246.
- `0x005c` `CR_HWPERF_COUNTER6`: width 0 bits (-, E246); no field rows. Records: E149, E150, E246.
- `0x0060` `CR_HWPERF_COUNTER7`: width 0 bits (-, E246); no field rows. Records: E149, E150, E246.
- `0x0064` `CR_HWPERF_COUNTER8`: width 0 bits (-, E246); no field rows. Records: E149, E150, E246.
- `0x0e80` `CR_HWPERF_PULSE`: width 32 bits assumed; no field rows. Records: E150, E152.

## ISP

- `0x0404` `CR_ISP_RENDER`: width 5 bits (5:3, 1:0, E249); no field rows. Records: E015, E163, E249.
- `0x0408` `CR_ISP_REGION_HEADER_BASE`: width 30 bits (31:2, E249); no field rows. Records: E163,
  E249.
- `0x0414` `CR_ISP_CTL`: width 12 bits (24, 19:16, 8, 5:0, E249); 1 field: VALID_ID [5:0]; uncovered
  24, 19:16, 8 (6 bits). Records: E231, E232, E233, E249.
- `0x0418` `CR_ISP_LINE_SAMPLE_POS`: width 1 bits (0, E067, E249); no field rows. Records: E066,
  E067, E068, E072, E073, E249.
- `0x041c` `CR_ISP_POLY_OFFSET_UNITS`: width 24 bits (23:0, E249); no field rows. Records: E071,
  E249.
- `0x0420` `CR_ISP_POLY_OFFSET_FACTOR`: width 32 bits (31:0, E249); no field rows. Records: E071,
  E249.
- `0x0424` `CR_ISP_POLY_OFFSET_CLAMP`: width 32 bits (31:0, E249); no field rows. Records: E071,
  E249.
- `0x0428` `CR_ISP_START_RENDER`: width 32 bits assumed; no field rows.
- `0x042c` `CR_ISP_MSAA`: width 3 bits (31, 1:0, E249); 2 fields: ENABLE [31], MODE [1:0]; uncovered
  - (0 bits). Records: E066, E074, E210, E211, E215, E219, E220, E249.
- `0x0480` `CR_ISP_ZLSCTL`: width 27 bits (26:0, E250); no field rows. Records: E057, E058, E163,
  E250.
- `0x0484` `CR_ISP_ZLOAD_BASE`: width 27 bits (30:4, E250); no field rows. Records: E058, E250.
- `0x0488` `CR_ISP_ZSTORE_BASE`: width 27 bits (30:4, E250); no field rows. Records: E058, E250.
- `0x048c` `CR_ISP_STENCIL_LOAD_BASE`: width 28 bits (31:4, E250); no field rows. Records: E058,
  E250.
- `0x0490` `CR_ISP_STENCIL_STORE_BASE`: width 28 bits (31:4, E250); no field rows. Records: E058,
  E250.
- `0x0494` `CR_ISP_VISIBILITY_CTRL`: width 0 bits (-, E249); no field rows. Records: E070, E163,
  E249.
- `0x0498` `CR_ISP_VISIBILITY_COUNT0`: width 0 bits (-, E249); no field rows. Records: E070, E164,
  E217, E249.
- `0x049c` `CR_ISP_VISIBILITY_COUNT1`: width 0 bits (-, E249); no field rows. Records: E070, E164,
  E249.
- `0x04a0` `CR_ISP_VISIBILITY_COUNT2`: width 0 bits (-, E249); no field rows. Records: E070, E164,
  E249.
- `0x04a4` `CR_ISP_VISIBILITY_COUNT3`: width 0 bits (-, E249); no field rows. Records: E070, E164,
  E249.
- `0x04a8` `CR_ISP_VISIBILITY_COUNT4`: width 0 bits (-, E249); no field rows. Records: E070, E164,
  E249.
- `0x04ac` `CR_ISP_VISIBILITY_COUNT5`: width 0 bits (-, E249); no field rows. Records: E070, E164,
  E249.
- `0x04b0` `CR_ISP_VISIBILITY_COUNT6`: width 0 bits (-, E249); no field rows. Records: E070, E164,
  E249.
- `0x04b4` `CR_ISP_VISIBILITY_COUNT7`: width 0 bits (-, E249); no field rows. Records: E065, E070,
  E164, E249.
- `0x04b8` `CR_ISP_BGOBJDEPTH`: width 32 bits (31:0, E249); no field rows. Records: E066, E249.
- `0x04bc` `CR_ISP_BGOBJVALS`: width 10 bits (9:0, E249); 2 fields: BGTAG_ENABLE [9], STENCIL [7:0];
  uncovered 8 (1 bits). Records: E015, E163, E216, E249.
- `0x04c8` `CR_ISP_MULTISAMPLECTL`: width 32 bits (31:0, E249); 2 fields: SAMPLE0_Y [7:4], SAMPLE0_X
  [3:0]; uncovered 31:8 (24 bits). Records: E064, E214, E215, E249.
- `0x04d4` `CR_ISP_SIGNATURE0`: width 32 bits assumed; no field rows.
- `0x04d8` `CR_ISP_SIGNATURE1`: width 32 bits assumed; no field rows.
- `0x04dc` `CR_ISP_REG_04DC`: width 3 bits (2:0, E067, E249); no field rows. Records: E066, E067,
  E068, E073, E163, E213, E222, E249.
- `0x04e8` `CR_ISP_REG_04E8`: width 2 bits (8, 0, E067, E249); no field rows. Records: E066, E067,
  E068, E073, E249.
- `0x050c` `CR_ISP_PARTIAL_REGION_BASE`: width 30 bits (31:2, E249); no field rows. Records: E160,
  E249.
- `0x0518` `CR_ISP_SIGNATURE2`: width 32 bits assumed; no field rows.
- `0x051c` `CR_ISP_SIGNATURE3`: width 32 bits assumed; no field rows.
- `0x0520` `CR_ISP_SAMPLE_POS`: width 32 bits (31:0, E067, E249); no field rows. Records: E056,
  E066, E067, E068, E073, E214, E215, E224, E249.

## MTE

- `0x0230` `CR_MTE_MULTISAMPLECTL`: width 32 bits (31:0, E248); no field rows. Records: E248.
- `0x0234` `CR_MTE_OTPM_BASE`: width 28 bits (31:4, E248); no field rows. Records: E158, E248.
- `0x023c` `CR_MTE_CTRL`: width 15 bits (14:0, E248); no field rows. Records: E248.
- `0x0240` `CR_MTE_RHW_MIN`: width 32 bits (31:0, E248); no field rows. Records: E063, E193, E194,
  E197, E248.
- `0x0244` `CR_MTE_RHW_CLAMP`: width 32 bits (31:0, E248); no field rows. Records: E063, E193, E194,
  E197, E248.
- `0x024c` `CR_MTE_OTPM_OP`: width 32 bits assumed; no field rows.

## PDS

- `0x0138` `CR_PDS_CACHE_STATUS`: width 32 bits assumed; no field rows.
- `0x013c` `CR_PDS_CACHE_HOST_ENABLE`: width 32 bits assumed; no field rows.
- `0x0140` `CR_PDS_CACHE_HOST_CLEAR`: width 32 bits assumed; no field rows.
- `0x0a78` `CR_PDS_REG_0A78`: width 6 bits (5:0, E026); no field rows. Records: E006, E026, E045,
  E141.
- `0x0ab8` `CR_PDS_EXEC_BASE`: width 32 bits assumed; 1 field: ADDR [31:20]; uncovered 19:0 (20
  bits).
- `0x0abc` `CR_PDS_REG_0ABC`: width 6 bits (5:0, E026); 1 field: BITS4_1 [4:1]; uncovered 5, 0 (2
  bits). Records: E006, E026, E045, E134, E140.
- `0x0ad0` `CR_PDS_INV0`: width 32 bits assumed; 1 field: DSC [0]; uncovered 31:1 (31 bits).
- `0x0ad4` `CR_PDS_INV1`: width 32 bits assumed; 1 field: DSC [0]; uncovered 31:1 (31 bits).
- `0x0ae0` `CR_PDS_INV_CSC`: width 32 bits assumed; 1 field: KICK [0]; uncovered 31:1 (31 bits).

## PPP

- `0x0248` `CR_PPP_SCREEN`: width 26 bits (28:16, 12:0, E247); no field rows. Records: E175, E247.
- `0x026c` `CR_PPP_SIGNATURE`: width 32 bits assumed; no field rows.

## SETTLE

- `0x0308` `CR_SETTLE_POLL0`: width 32 bits assumed; no field rows. Records: E153.
- `0x030c` `CR_SETTLE_POLL1`: width 32 bits assumed; no field rows. Records: E153.

## SOFT

- `0x0080` `CR_SOFT_RESET`: width 32 bits assumed; 6 fields: TSP_RESET [5], ISP_RESET [4], USE_RESET
  [3], TA_RESET [2], DPM_RESET [1], BIF_RESET [0]; uncovered 31:6 (26 bits).

## TA

- `0x02b0` `CR_TA_REG_02B0`: width 8 bits (31:24, E054, E247); no field rows. Records: E030, E054,
  E056, E071, E072, E159, E182, E183, E247.
- `0x02b4` `CR_TA_REG_02B4`: width 8 bits (7:0, E054, E247); no field rows. Records: E030, E054,
  E056, E071, E072, E159, E182, E183, E247.
- `0x02d0` `CR_TA_REG_02D0`: width 30 bits (31:2, E054, E247); no field rows. Records: E030, E054,
  E056, E071, E072, E159, E182, E183, E247.
- `0x02d4` `CR_TA_REG_02D4`: width 26 bits (25:0, E054, E247); no field rows. Records: E030, E054,
  E056, E071, E072, E159, E182, E183, E247.

## TE

- `0x0204` `CR_TE_AA`: width 3 bits (31:29, E247); no field rows. Records: E159, E247.
- `0x0208` `CR_TE_MTILE1`: width 25 bits (31, 29:22, 19:12, 7:0, E247); no field rows. Records:
  E247.
- `0x020c` `CR_TE_MTILE2`: width 27 bits (30:22, 20:12, 8:0, E247); no field rows. Records: E247.
- `0x0210` `CR_TE_SCREEN`: width 17 bits (20:12, 7:0, E247); no field rows. Records: E055, E247.
- `0x0214` `CR_TE_MACROTILE_STRIDE`: width 18 bits (17:0, E247); no field rows. Records: E159, E175,
  E247.
- `0x0218` `CR_TE_PSG`: width 16 bits (26:18, 6:0, E247); no field rows. Records: E158, E247.
- `0x021c` `CR_TE_PSGREGION_ADDR`: width 26 bits (31:6, E247); no field rows. Records: E247.
- `0x0220` `CR_TE_TPC_ADDR`: width 26 bits (31:6, E247); no field rows. Records: E159, E247.
- `0x0224` `CR_TE_TPCCONTROL`: width 32 bits assumed; no field rows.
- `0x0274` `CR_TE_CONTEXT_STATE`: width 0 bits (-, E247); no field rows. Records: E158, E247.
- `0x0284` `CR_TE_DIAG2`: width 32 bits assumed; no field rows.
- `0x0290` `CR_TE_DIAG5`: width 32 bits assumed; no field rows.
- `0x02a8` `CR_TE_REG_02A8`: width 8 bits (19:12, E054, E247); no field rows. Records: E030, E054,
  E056, E071, E072, E159, E182, E183, E247.

## TIMER

- `0x0144` `CR_TIMER`: width 32 bits assumed; 1 field: VALUE [31:0]; uncovered - (0 bits).

## TPU

- `0x0820` `CR_TPU_YUV_CSC0_0`: width 20 bits (25:16, 9:0, E254); no field rows. Records: E037,
  E254.
- `0x0824` `CR_TPU_YUV_CSC0_1`: width 20 bits (25:16, 9:0, E254); no field rows. Records: E037,
  E254.
- `0x0828` `CR_TPU_YUV_CSC0_2`: width 20 bits (25:16, 9:0, E254); no field rows. Records: E037,
  E254.
- `0x082c` `CR_TPU_YUV_CSC0_3`: width 20 bits (25:16, 9:0, E254); no field rows. Records: E037,
  E254.
- `0x0830` `CR_TPU_YUV_CSC0_4`: width 10 bits (9:0, E254); no field rows. Records: E037, E254.
- `0x0834` `CR_TPU_YUV_CSC1_0`: width 20 bits (25:16, 9:0, E254); no field rows. Records: E038,
  E040, E254.
- `0x0838` `CR_TPU_YUV_CSC1_1`: width 20 bits (25:16, 9:0, E254); no field rows. Records: E038,
  E040, E254.
- `0x083c` `CR_TPU_YUV_CSC1_2`: width 20 bits (25:16, 9:0, E254); no field rows. Records: E038,
  E040, E254.
- `0x0840` `CR_TPU_YUV_CSC1_3`: width 20 bits (25:16, 9:0, E254); no field rows. Records: E038,
  E040, E254.
- `0x0844` `CR_TPU_YUV_CSC1_4`: width 10 bits (9:0, E254); no field rows. Records: E038, E040, E254.
- `0x0848` `CR_TPU_YUV_CSC_INPUT`: width 4 bits (3:0, E254); 2 fields: UV_SIGNED [2], Y_NO_OFFSET
  [0]; uncovered 3, 1 (2 bits). Records: E038, E040, E254.
- `0x0860` `CR_TPU_LUMA_KEY_RG`: width 20 bits (25:16, 9:0, E254); no field rows. Records: E038,
  E039, E254.
- `0x0864` `CR_TPU_LUMA_KEY_B_OFFSET`: width 18 bits (23:16, 9:0, E254); no field rows. Records:
  E038, E039, E254.
- `0x0868` `CR_TPU_LUMA_KEY_ALPHA`: width 32 bits (31:0, E254); 4 fields: ABOVE [31:24], BELOW
  [23:16], THRESHOLD [15:8], LOW [7:0]; uncovered - (0 bits). Records: E038, E039, E254.

## TSP

- `0x043c` `CR_TSP_PARAMETER_CACHE`: width 32 bits assumed; no field rows.

## USE

- `0x0a00` `CR_USE_CTRL`: width 32 bits assumed; no field rows.
- `0x0a04` `CR_USE_REG_0A04`: width 28 bits (31:4, E054, E255); no field rows. Records: E030, E054,
  E056, E071, E072, E159, E182, E183, E255.
- `0x0a08` `CR_USE_CACHE`: width 32 bits assumed; no field rows.
- `0x0a0c` `CR_USE_CODE_BASE_0`: width 32 bits assumed; 2 fields: DM [26:25], ADDR [24:0]; uncovered
  31:27 (5 bits).
- `0x0a34` `CR_USE_CODE_BASE_10`: width 32 bits assumed; no field rows.
- `0x0a48` `CR_USE_CODE_BASE_15`: width 32 bits assumed; no field rows.
- `0x0a7c` `CR_USE_G0`: width 32 bits assumed; no field rows.
- `0x0a80` `CR_USE_G1`: width 32 bits assumed; no field rows.
- `0x0a84` `CR_USE_COEFFS0_A`: width 32 bits (31:0, E255); no field rows. Records: E078, E255.
- `0x0a88` `CR_USE_COEFFS0_B`: width 32 bits (31:0, E255); no field rows. Records: E078, E255.
- `0x0a8c` `CR_USE_COEFFS0_BIAS`: width 20 bits (19:0, E255); no field rows. Records: E078, E255.
- `0x0a90` `CR_USE_COEFFS1_A`: width 32 bits (31:0, E255); no field rows. Records: E078, E255.
- `0x0a94` `CR_USE_COEFFS1_B`: width 32 bits (31:0, E255); no field rows. Records: E078, E255.
- `0x0a98` `CR_USE_COEFFS1_BIAS`: width 20 bits (19:0, E255); no field rows. Records: E078, E255.
- `0x0a9c` `CR_USE_COEFFS_MODE`: width 2 bits (1:0, E255); 1 field: MODE [1:0]; uncovered - (0
  bits). Records: E078, E079, E255.
- `0x0aa0` `CR_USE_REG_0AA0`: width 32 bits (31:0, E054, E255); no field rows. Records: E030, E054,
  E056, E071, E072, E159, E182, E183, E255.
- `0x0aa4` `CR_USE0_DM_SLOT`: width 32 bits assumed; no field rows.
- `0x0aa8` `CR_USE1_DM_SLOT`: width 32 bits assumed; no field rows.
- `0x0aac` `CR_USE_TMPREG`: width 32 bits assumed; no field rows.
- `0x0b0c` `CR_USE0_SERV_PIXEL`: width 32 bits assumed; no field rows.
- `0x0b10` `CR_USE0_SERV_VERTEX`: width 32 bits assumed; no field rows.
- `0x0b14` `CR_USE0_SERV_EVENT`: width 32 bits assumed; no field rows.
- `0x0b18` `CR_USE1_SERV_PIXEL`: width 32 bits assumed; no field rows.
- `0x0b1c` `CR_USE1_SERV_VERTEX`: width 32 bits assumed; no field rows.
- `0x0b20` `CR_USE1_SERV_EVENT`: width 32 bits assumed; no field rows.
- `0x0b24` `CR_USE_COEFFS2_A`: width 16 bits (31:24, 7:0, E255); no field rows. Records: E078, E255.
- `0x0b28` `CR_USE_COEFFS2_B`: width 8 bits (15:8, E255); no field rows. Records: E078, E255.
- `0x0b2c` `CR_USE_COEFFS2_BIAS`: width 20 bits (19:0, E255); no field rows. Records: E078, E255.
- `0x0b88` `CR_USE2_SERV_PIXEL`: width 32 bits assumed; 2 fields: EMPTY [16], TASK_COUNT [15:0];
  uncovered 31:17 (15 bits). Records: E076.
- `0x0b8c` `CR_USE2_SERV_VERTEX`: width 32 bits assumed; 2 fields: EMPTY [16], TASK_COUNT [15:0];
  uncovered 31:17 (15 bits). Records: E076.
- `0x0b94` `CR_USE3_SERV_PIXEL`: width 32 bits assumed; 2 fields: EMPTY [16], TASK_COUNT [15:0];
  uncovered 31:17 (15 bits). Records: E076.
- `0x0b98` `CR_USE3_SERV_VERTEX`: width 32 bits assumed; 2 fields: EMPTY [16], TASK_COUNT [15:0];
  uncovered 31:17 (15 bits). Records: E076.

## VDM

- `0x0200` `CR_VDM_START`: width 32 bits assumed; no field rows.
- `0x0238` `CR_VDM_CTRL_STREAM_BASE`: width 30 bits (31:2, E247); no field rows. Records: E184,
  E247.
