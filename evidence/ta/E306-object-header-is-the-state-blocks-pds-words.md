+++
id = "E306"
claim = "The TA object's three header words are the state block's words 3, 4 and 5 (the pixel PDS secondary pointer, size word and primary pointer) copied as given: each of six values set in one of them appears unchanged in the object's matching dword, and no other dword of the parameter buffer or the TA data changes; the secondary pointer set to 0x08000004 faults the render yet its object holds the word, and the primary pointer set to 0x08000000 changes no pixel; one run"
unit = "ta"
method = "probes/ta/object-words.toml on the laptop, linux fork with the debug option on: its probe ta-object-words-pds runs the probe's triangle with a green pixel shader and the state block's word 4 at 0x00030001 (the job's), 0x00030002, 0x00020001, 0x00010001 and 0x00000001, word 3 at 0x08000004 and word 5 at 0x08000000, the render memory dumped after each; compared with pbdump.py --diff and read with ta_words.py object"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["ta-object-words"]
terms = ["PB_OBJ.PDS_WORDS", "PDS_SIZE.BITS17_16"]
+++

**What runs.** The triangle's state block words 3-5 hold the pixel program's words (userspace
libsgxfive render.c: secondary pointer 0x04000004, size word 0x00030001, primary pointer
0x04000000). Each case changes one of them.

**Results.**

| state block | object dwords 0-2 | other dwords differing from the control | image |
|---|---|---|---|
| word 4 = 0x00030001 (control) | 04000004 00030001 04000000 | | 1062 triangle pixels |
| word 4 = 0x00030002 | 04000004 00030002 04000000 | none | the control's |
| word 4 = 0x00020001 | 04000004 00020001 04000000 | none | the control's |
| word 4 = 0x00010001 | 04000004 00010001 04000000 | none | the control's |
| word 4 = 0x00000001 | 04000004 00000001 04000000 | none | the control's |
| word 3 = 0x08000004 | 08000004 00030001 04000000 | four parameter slot dwords (below) | the render faults |
| word 5 = 0x08000000 | 04000004 00030001 08000000 | none | the control's |

The faulting case differs from the control in four more dwords of the parameter slot: three in
its page table area (0x423004-0x42300c), which the kernel rebuilds when it recovers the job, and
one at 0x424088 (0x0421ffff for 0x04210001). Its saved TA data holds no written page.

**What it shows.** `PB_OBJ.PDS_WORDS` is the state block's three pixel-program words, copied by the
TA without change; the TA does not read them for its own work (the rest of the object and the
regions are the same). That the 3D runs them for the object's pixels is a reading [infer]: the
primary pointer moved to 0x08000000 (word 5) gave the control's image, and only the secondary
pointer's change faulted, so these data do not show the 3D using the primary pointer.
