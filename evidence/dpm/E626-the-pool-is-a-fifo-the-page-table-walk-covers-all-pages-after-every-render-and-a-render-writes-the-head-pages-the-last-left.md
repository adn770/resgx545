+++
id = "E626"
claim = "In 26 jobs (8 whole-buffer jobs at 6 sizes from 64x64 to 1024x768 and 2 repeats of them, 3 renders each; 12 jobs at 1024x768 in 0x23 to 0x38 pages, 10 sizes of the buffer and 2 repeats, 2 renders each; 6 jobs at 4096x4096, 1 render each) the page table at 0x423000 of the slot (0x422000 in the dump, which starts at slot offset 0x1000) walks to all P pages after every render (26 of 26 jobs, every dump), the pages that changed between two consecutive dumps are, as a set, the first pages of the list the previous walk left (H-head, 28 of 28 predictions, fit 8, held out 14, controls 6; the order within a render is not visible in the dumps; one control statement missed), the first render on a fresh table takes pages 1 to 2, 1 to 3, 1 to 5, 1 to 5, 1 to 8 and 1 to 0x13 at 64x64, 128x128, 192x128, 256x256, 512x384 and 1024x768 (H-first predicted three rows, 64x64, 256x256 and the 64x64 repeat, 3 of 3; the other three sizes are observed, not predicted), and the list heads that a partial render stores appear in the walk in ascending macrotile order at its tail (H-free-O, 8 of 8 overflowing 1024x768 jobs, 0x23 to 0x34 pages); the same job after a reset and without one writes the same pages and holds the same lists (2 of 2)"
unit = "dpm"
method = "tri --keep-overflow --dump-each --words with the render memory dumped after each render, on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B, stock firmware, tool sgxfive-test-1135 (sha256 7732b945...): -n 3 on the 8 whole-buffer jobs, -n 2 at 1024x768 in 0x23 to 0x38 pages, -n 1 at 4096x4096 in 0x23, 0x40, 0x60, 0x80, 0xc0 and 0x100 pages; the page table walked from the one entry whose previous page is 0xffff, and the pages whose content changed between dumps compared, by the dataset's analysis/an_pool.py"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["dpm-partial-model-batch"]
terms = ["Dynamic Parameter Management (DPM)", "Parameter Buffer (PB)", "hw_pb_desc.page_table_base"]
+++

**What ran.** Table `free` (26 jobs). The 8 whole-buffer jobs ran `tri -n 3` (3 renders, dumps
after each): 64x64, 256x256 (fit: E309), 128x128, 192x128, 512x384, 1024x768, and the 64x64 and
1024x768 repeats. The 12 jobs at 1024x768 ran `tri -n 2` (2 renders) in 0x23, 0x24, 0x26, 0x28,
0x2a, 0x2c, 0x30, 0x34, 0x36 and 0x38 pages, the 0x30 job repeated without a reset and the 0x38
job after one. The 6 jobs at 4096x4096 ran `tri -n 1` (one render, one dump) in 0x23, 0x40, 0x60,
0x80, 0xc0 and 0x100 pages. Same laptop, kernel, module, firmware and tool as E625, the render
memory dumped after each render (`--dump-each`). The decoders (`analysis/an_pool.py`, the
recompute's corrected copy) read the page table at dump offset 0x422000: the frozen recompute read
0x423000 (and page p at p * 4096), a mistake against `free-list.sh` of E309 (its `PT = 0x423000 -
0x1000`) that made H-walk, H-head, H-first and H-free-O "no data" or a miss in the frozen output;
the corrected copy scores them (disclosed with its own hash in the dataset's method).

**Results [HW].** H-walk: every dump of the 26 jobs walks from the one entry whose previous page
is 0xffff along the next links to all P pages (1058 at 0x422, P at the others). H-first (three
declared rows, 3 of 3): the first render takes pages 1 to 2 (64x64) and 1 to 5 (256x256, as E309);
observed in the other whole-buffer jobs: 1 to 3, 1 to 5, 1 to 8, 1 to 0x13 (128x128, 192x128,
512x384, 1024x768). H-head: the pages whose content changed between two consecutive dumps are the
first pages of the previous walk, as a set: 64x64 changes pages 1, 2 then 3, 4 then 5, 6 (the
heads 3, 5, 7), 1024x768 0x13 pages each render (heads 0x14, 0x27, 0x3a); in the overflowing
1024x768 jobs, which have two renders, the second render's changed pages are the head prefix
again. The order inside one render is not visible, since a dump is taken after it. The control
statement "the pages differ" of the repeat without a reset missed: the repeat at 0x30 held the
same lists on the same pages as after a reset (the kernel builds the table before each job, E453).
H-free-O: in the 8 overflowing 1024x768 jobs the heads of the state page's macrotile lists appear
in the walk in ascending macrotile order, at its tail (fit 4 of 4, held out 4 of 4; the 0x36 job
completes). The 4096x4096 jobs have one render and one dump, so the head-prefix test cannot be
made there: only the walk covering all P pages is scored at that size.

**Reading [infer].** The pool is a FIFO: a render takes the head of the walk the previous one left
and the freed pages are appended at the tail, so a model needs the free order, which for a partial
render is the macrotile order of the lists (list head to tail) and for a whole-buffer job the
orders of E309. The page order inside one job and the final render's free order of an overflowing
job are not shown.

**Not shown.** Which object or region takes which page; the order the final render frees its pages
in; the order of the pages inside one render; the pool after more than one partial render (the
lists of E310 and E625 are the only view).
