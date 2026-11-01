+++
id = "E265"
claim = "The word E046's EMIT2 table varied is the pixel-event program's data dword 8, the end-of-render mask (0x100) of asm/transfer/pds_pixevent.s, and not an emit word: XOR 0x100 (0x81 in that table's terms) sets it to 0 and the fill, the copy and the triangle then write no pixel, as at 0 and 0x2; at 0x4 the last 32x16 tile is left unwritten (512 pixels) in all three jobs; 0x8000, 0x8100, 0x200, 0x4000 and 0x8 leave every image as built; both repeats of each case agree"
unit = "pbe"
method = "the sweeps pbe-emit-words-pixev-fill, -copy and -tri of probes/pbe/emit-words.toml on the laptop, linux fork with the debug option on: the 64x32 fill and copy and the 64x64 triangle with pds:pixev:8 at ten values, each case run twice"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["pbe-emit-words", "pbe-emit-words-followup"]
terms = ["EMIT2.BITS15_8", "PIXEL_EVENT.END_OF_TILE", "PIXEL_EVENT.LAST_TILE"]
+++

**What runs.** E046 swept `pixev:8` of the fill, the word it took for the end-of-tile emit's
EMIT2, over every value of bits 15:8, and found that 0x81 alone wrote no pixel. In the jobs our
tools build, `pixev:8` is data dword 8 of the pixel-event program (asm/transfer/pds_pixevent.s,
`ds0[4]`), which holds 0x00000100. The program runs the end-of-tile task when `ir1` bit 1 is
set, unless `~ir1 & ds0[4]` is zero, when it runs the end-of-render task instead; the PBE words
themselves are immediates of the end-of-tile USE program (E266, E267). Each case here sets or
flips that dword and compares the target with the unpoked job's; each runs twice, and the
follow-up table (`pbe-emit-words-followup`) runs each once more.

**Results**, pixels that differ from the baseline (2048 for the fill and the copy, 4096 for the
triangle), the same in every run:

| dword 8 | value | fill | copy | triangle |
|---|---|---|---|---|
| `^=0x100` (E046's 0x81) | 0 | 2048, all sentinel | 2048 | 4096 |
| `=0` | 0 | 2048 | 2048 | 4096 |
| `=0x2` | 0x2 | 2048 | 2048 | 4096 |
| `=0x4` | 0x4 | 512, from (32, 16) | 512 | 512, from (32, 48) |
| `^=0x8100` (E046's 0x01) | 0x8000 | 0 | 0 | 0 |
| `^=0x300` (0x83) | 0x200 | 0 | 0 | 0 |
| `^=0x4100` (0xc1) | 0x4000 | 0 | 0 | 0 |
| `^=0x8000` | 0x8100 | 0 | 0 | 0 |
| `=0x8`, `=0x200` | | 0 | 0 | 0 |

Every job completed (`job: ok`). The pixels left unwritten hold the sentinel 0xdeadbeef.

**What it shows.** The value of the dword decides whether the end-of-tile task runs: 0 and 0x2
(`ir1` bit 1 is set on every end-of-tile event) make `~ir1 & dword` zero on every tile, so no
tile is emitted; 0x4 makes it zero where `ir1` bit 2 is set, the last tiles, so the bottom-right
32x16 pixels stay unwritten, as `PIXEL_EVENT.LAST_TILE` has it. Every other value tried keeps a
bit `ir1` never has, and the image is the baseline. E046's single value 0x81 is this dword at 0,
so it says nothing about EMIT2. That the end-of-render task runs in place of the end-of-tile task
follows from the program's text **[infer]**; the data show only the missing pixels.
