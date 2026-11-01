+++
id = "E027"
claim = "Bit 5 of the flags word of the kernel-built transfer command (word 42, byte offset 0xa8) makes a fill or a copy complete without writing anything, the target keeping its sentinel; the other 31 bits, singly, change nothing in either job; every transfer word userspace may set leaves the flags alone"
unit = "transfer"
method = "kernel-poke sweeps of probes/transfer/kernel-words.toml (fill-kernel, copy-kernel) and the userspace-word sweeps of probes/transfer/command-words.toml (xfer-fill, xfer-copy), on the laptop, linux fork with the debug option on; 64x32 fill and copy, 205 and 1429 cases a table"
tiers = ["HW"]
date = "2026-11-01"
data = ["transfer-kernel-words", "transfer-command-words"]
terms = ["transfer_cmd", "transfer_cmd.flags"]
+++

**What runs.** The kernel fork builds the firmware command of a transfer itself, and its
debugfs can flip bits of that command after userspace has submitted the job (`tq:N` words).
Each case runs sgxfive-test's 64x32 fill or copy once, with one flip armed on word 42, which
is the flags word of the command (E016). The target holds a sentinel (0xdeadbeef) before the
job, and the tool compares every pixel and every dword outside the rectangle afterwards. Each
bit of the word is flipped on its own, and the word is also set to 0xffffffff. The same table
flips words 16, 42 and 98 to 101 of the command (205 cases a table, one baseline).

**Results.** In both jobs the baseline job writes its pixels (fill hash 0xb60c6095080bd325,
copy hash 0x9b1c0be484ac0d25) and word 42 gives two cases that differ from it: the flip of
bit 5 (0x20) and the value 0xffffffff.

- Both cases report `job: ok`, the same outcome as the baseline's, and the target hash is
  0xfc8ce806207f8325 in all four, the hash of the untouched sentinel: 2048 of 2048 pixels
  differ from the expected image, the first one reads 0xdeadbeef, and no dword outside the
  rectangle changes.
- The other 31 single-bit flips of word 42 leave the image identical to the baseline's, fill
  and copy alike.
- The kernel poke applied in all 34 cases of the word.

The 6.1 transfer-command sweeps (xfer-fill and xfer-copy, 1429 cases each, every bit of every word
userspace submits) leave the target at its sentinel only in cases whose job is rejected, faults or
hangs (222 of the fill's, 230 of the copy's), and in none does the job report ok. No userspace
word reaches this flag: the flags word is one the kernel writes itself, and only the kernel poke
changes it. Words 16 and 98 to 100, poked in the same table, leave the image unchanged; word 101
hangs for three of its flips (bits 1, 2 and 0xffffffff, both jobs).

**Not shown.** That the job also signals its sync and status word: the tool waits for the job
and finds it complete, but these runs do not read the status word (E018 does, for the dummy
transfer the kernel builds with this flag). What the other bits of the word mean in other
contexts: each is inert in these two jobs.
