+++
id = "E088"
claim = ".quadlead on an instruction runs it for the top-left instance of each 2x2 quad only (512 quads: the 512 top-left pixels stored the incremented value and the other 1536 stored the unchanged one); lock #0 or #3 around a shared counter serialises quads, not instances (the counter ends at 0xd0000200, 512 updates for 2048 pixels, each value in exactly the four pixels of one quad); setm #0, #1, #2, #4, #8 and #15 change nothing of that"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/usse/quad-lock.toml, probes counter and quadlead-setm, a 64x32 fill (2048 instances) whose pixel program loads a scratch counter, adds 1 with iadd32 (with or without .quadlead), stores it back and writes the value it stored as its pixel, with and without lock/release; two runs (the second is the follow-up run)"
tiers = ["HW"]
date = "2026-11-01"
data = ["usse-quad-lock", "usse-quad-lock-followup"]
terms = []
+++

**What runs.** `ldad` of a scratch dword (0xd0000000 at start), `iadd32` of 1 to it, `stad`
back, with the pixel the value stored; around it `lock #0` / `release #0`, `lock #3` /
`release #3` or nothing, `.quadlead` on the add in two cases, and `setm #n` before the lock.

**Results.**

- No lock: the counter ends at 0xd000002c (44 values over the 2048 pixels; 481 of the 512
  quads show one value in all four pixels); the follow-up run ends at 0xd000002b.
- `lock #0` or `lock #3`: the counter ends at 0xd0000200; 512 distinct values appear, each in
  exactly four pixels, and all four pixels of each quad hold the same value. So the lock
  serialises the quads: a quad's four instances load the same value together.
- `lock #0` without `release`: the job hangs and the context is lost.
- `.quadlead` on the add under the lock: 512 pixels hold 0xd0000001 and 1536 hold
  0xd0000000, and the 512 are the top-left pixels of the quads (x and y even): the other three
  instances of every quad keep their old value, and their stores overwrite the incremented one.
- `.quadlead` without a lock: 13 distinct values, a counter of 0xd0000009, the top-left
  pixels at 0xd0000001 in 48 of 512 quads. The follow-up run gives another mix (counter
  0xd000000e).
- `setm #0`, `#1`, `#2`, `#4`, `#8` and `#15` before the lock: each gives the control's result,
  counter 0xd0000200 and 512 values of four pixels, every quad uniform.
  The locked cases repeat in the follow-up run (counter 0xd0000200, every quad uniform).

**Not shown.** The final counter of the `.quadlead` case under the lock is not in the readback (the
pixels are). The unlocked cases differ from run to run; the locked ones repeat as stated. The
mnemonic of the modifier in the table is `.quadlead`.