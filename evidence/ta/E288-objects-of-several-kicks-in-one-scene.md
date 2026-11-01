+++
id = "E288"
claim = "In a scene over two and three TA kicks each kick writes its own object (kick 1's at 0x1000, kick 2's on a new page at 0x3000, kick 3's appended to kick 1's at 0x105c), a region's stream holds one primitive and object word pair per object in kick order, and the object word's low bits are the dword address of the object's ISP words (0x406, 0xc06, 0x41d); bits 31:26 of the object word are 1, 3 and 9 for objects of one, two and five triangles, twice the primitives less one; the scenes ran twice, the one-kick probes once"
unit = "ta"
method = "probes/render/kick-objects.toml on the laptop, linux fork with the debug option on: its script kick-objects.sh runs sgxfive-test tri with one, two and three TA kicks in one scene (geometry jobs, the later triangles moved 12 pixels), twice, and prints the parameter buffer and TA data the kernel's debugfs dumps after the closing render (gzip in base64, written back by isp_words.py unpack); its probes dump one kick holding one object of two and of five triangles, and two objects; read with pbdump.py"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["render-kick-objects"]
terms = ["CSTREAM.OBJ_ISP_ADDR", "CSTREAM.OBJ_PRIMS", "CSTREAM.PRIM_TILES", "control stream"]
+++

**What runs.** The script's three scenes: one kick (`tri -n 1`); kick 1 geometry only and kick 2
closing with its triangle 12 pixels right and down (`-n 2 --geometry 1 --move 2:12,12`); kicks 1
and 2 geometry and kick 3 closing, moved (12, 12) and (24, 0). Each scene's parameter buffer and
TA data are dumped after the closing render, both runs. The probes `render-kick-objects-tris2`,
`-tris5` and `-obj2` draw two and five triangle copies in one object, and two objects in one kick
(`--obj2`), each dumped, once.

**Results.** The images are those of the notebook's scenes: 1062, 1730 (625 of them outside the
closing render's own triangle) and 2026 (1074 outside) triangle pixels. Both runs dumped the same
bytes for each scene.

- One kick: one object of 23 dwords at slot offset 0x1000, its ISP words at 0x1018; every stream
  holds one pair, the object word `0x04000406`.
- Two kicks: kick 1's object as before and kick 2's on a new page, 0x3000; the regions both
  triangles meet hold `4490ffff 04000406` then kick 2's pair (`44980701 04000c06`, or `4490ffff
  04000c06`), and the last region only kick 2's.
- Three kicks: kick 3's object follows kick 1's, the 46-dword block from 0x1000 holding both, its
  ISP words at 0x1074, object word low bits 0x41d; the regions hold up to three pairs, in kick
  order.
- One kick, one object of two triangles: object word bits 31:26 = 3, its ISP words at 0x1024
  (0x409); five triangles: 9 (0x412), with the 0x8a and 0x8c primitive forms; two objects in one
  kick: the second appended at 0x105c (0x41d) as kick 3's, its third PDS word 0x04000070 where
  the first has 0x04000000.

**What it shows.** Every TA kick, and every object of a kick, writes an object of its own; a
later kick takes a new parameter page when the first is in use by the scene so far, and a third
fills the room after the first object. A region's stream lists the objects that touch it in the
order they were written, a primitive word and an object word each. The object word's low bits are
the dword address of the object's ISP words in the parameter slot, and bits 31:26 = 2 x
primitives - 1 for one, two and five triangles [infer: three values]. This reproduces the
notebook's several-objects record.
