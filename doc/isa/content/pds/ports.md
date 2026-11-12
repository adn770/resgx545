<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### The output ports

A `movs` (or `movsa`) writes four source words to a **port**; the `dout*` ports issue work to
other units **[RE]**. What each port does with its words, where we know it:

| port | words | known meaning |
|------|-------|---------------|
| `doutu` | U0, U1, U2 | start a USSE task **[HW]** |
| `doutd` | address, control | DMA memory into the USSE attributes **[HW]** |
| `douta` | value, control | write one secondary attribute **[HW]** |
| `douti` | two words | issue iterator work **[HW]** |
| `doutt` | T0-T3 | the state of a texture fetch **[HW]** |
| `tim` | value, (ignored) | load the counter `tim`: bits 24-0, bit 24 the run bit **[HW]** |
| `doutc` | | faults the job, from a fill's secondary or a primary pixel program **[HW]** |
| `douts`, `slc`, `mr`, `ir0` | | no effect seen (E264) **[open]** |

- **`doutu`** **[HW]**. U0 holds the code address: `CBASE` (`USE_CODE_BASE_n`) in bits 3-0 and
  the instruction index above it (`EXE`, bits 19-4 on this build's layout), plus the
  temporaries in fours (`TRC`) in bits 31-24. U1 holds flags: bit 2 `SDSOFT` for the pixel
  and secondary programs, bit 23 `PBENABLE` for the end-of-tile task, bit 22 `ENDOFRENDER`,
  bit 25 `TEXTUREDEPENDENCY` (wait for the texture result); U2 is 0 in all our programs
  (`doc/specs/transfer.md` §4.2, §4.4). A `movs` always names four sources; `doutu`
  uses three. The tile position the pixel-event program puts in the end-of-tile task's U1
  does not place the tile: flipping its lowest `tile_x` or `tile_y` bit changed no pixel of a
  64x64 render (2026-10-24, the triangle probe host) **[HW]**, so the PBE words place it.
  On the fill, read after the fact from the kept sweeps of every value of the x field (bits
  11:3) and the y field (bits 21:12) poked into the program's U1 word, the fields do place it,
  in half-tile units (16 pixels in x, 8 rows in y): each 32 x 16 tile t stores at
  (2t | f) >> 1 or (2t + f) >> 1 per axis and nothing is stored where that lies outside the
  target, which gives the tool's image hash in 1536 of 1536 jobs, XOR in place of OR in 1532
  (E876, post hoc). The lowest bit is half a tile, which is why its flip changed nothing. Held
  out on fills of 128 x 64 and 256 x 32, where OR and addition differ, OR gave every image hash
  (20 of 20 rows, 8 of 8 that separate the two) and addition failed 8 of 8, with nothing stored
  outside the target **[HW]** (E884): the program ORs the poked word into the tile's own field
  and the task stores the tile at the place the field names, field >> 1 in 32 x 16 tiles. E126's
  XOR flips on a 128 x 128 render move whole tiles the same way (19 of 19 pictures, post hoc).
  With both fields poked at once each axis is placed by its own field the same way, independently
  of the other: held out on a 128 x 64 fill, 8 of 8 image hashes, where only the x field acting or
  only the y field gave none **[HW]** (E909).
- **`doutd`** **[CAP/HW]**. The first word is the source address; the second is
  burst size − 1 (bits 3-0), lines − 1 (7-4), the destination attribute (19-8) and
  stride − 1 (29-22) With `movsa` the third source is added to
  the address: our vertex program fetches vertex `index × stride` this way.
- **`douta`** writes its first word to the secondary attribute named by bits 19-8 of the
  second **[HW]**: from a fill's secondary program the words reach `sa0`-`sa15` of its pixel
  tasks, given room for them in the PDS state's secondary attribute size; from the primary
  program nothing reached the USE task. Our pixel-event program uses it before starting the
  end-of-tile task. Secondary attributes keep their values from one job to the next **[HW]**:
  a task reads what an earlier one left in any it was not given.
- **`douti`** and **`doutt`** **[HW]**: our copy's primary program issues one iterator word pair
  (one texture fetch from the first layer, no USE issue) and the four texture state words
  T0-T3, and the texel arrives in `pa0` of the task `doutu` started
  (`doc/specs/transfer.md` §4.4).
  The task waits for its iterations with U1 bit 24 and for its fetches with U1 bit 25, and
  the program's last iteration of each kind ends the wait: `DOUTI0` bit 29 (`LAST_ITER`) and
  bit 30 (`LAST_FETCH`); a wait no word ends, or an end no wait takes, hangs the job. The word
  pair's other fields are in the glossary's `DOUTI0` rows (E047, E048).
