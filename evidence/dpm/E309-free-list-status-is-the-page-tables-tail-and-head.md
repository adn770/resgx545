+++
id = "E309"
claim = "After a job CR_DPM_TA_ALLOC_FREE_LIST_STATUS1 and CR_DPM_3D_FREE_LIST_STATUS1 hold the free list's tail page in the high half and its head page in the low half, and the two STATUS2 registers the page before the tail in the low half, as the page table in memory chains them: the DPM rewrites the table in place, one 32-bit entry per page at the table base plus four times the page number, appending each freed page at the tail; one run of ten jobs, its registers repeated by E256's register timelines"
unit = "dpm"
method = "probes/dpm/free-list.toml on the laptop, linux fork with the debug option on: its script free-list.sh runs the triangle as sgxfive-test probe --tri (a green pixel shader) at 64x64, 256x256, 1024x768 and 4096x4096 with the whole parameter buffer (0x422 pages), at 1024x768 with 0x40 and 0x30 pages, at 4096x4096 with 0x100 pages, the 64x64 triangle on contexts for up to 1024x768 and 4096x4096, and two renders on one context; after each the registers 0x0600-0x0750 (debugfs regs), the TA/3D control block (debugfs buf09) and the render dump's page table walked from its head; one run, read with dpm_words.py free-list"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["dpm-free-list"]
terms = [
    "CR_DPM_TA_ALLOC_FREE_LIST_STATUS1", "CR_DPM_3D_FREE_LIST_STATUS1",
    "CR_DPM_TA_ALLOC_FREE_LIST_STATUS2", "CR_DPM_3D_FREE_LIST_STATUS2",
    "CR_DPM_TA_ALLOC_FREE_LIST_STATUS1.HEAD", "CR_DPM_TA_ALLOC_FREE_LIST_STATUS1.TAIL",
    "CR_DPM_TA_ALLOC_FREE_LIST_STATUS2.PREV", "CR_DPM_3D_FREE_LIST_STATUS1.HEAD",
    "CR_DPM_3D_FREE_LIST_STATUS1.TAIL", "CR_DPM_3D_FREE_LIST_STATUS2.PREV",
    "hw_pb_desc.page_table_base",
    "hw_pb_desc.current_stack_top", "hw_pb_desc.dpm_ta_alloc", "CR_DPM_3D_FREE_LIST",
    "Parameter Buffer (PB)",
]
+++

**What runs.** Our kernel builds the page table itself: the parameter slot's pages 1 to N (N the
PB's size) chained in order, entry i holding i - 1 in the high half and i + 1 in the low half,
0xffff at both ends, at slot offset 0x423000 (the descriptor's page-table base). The render dump
holds the table; the script walks it from the one entry whose previous page is 0xffff along the
next links, and prints every entry that differs from the kernel's chain.

**Results.** One run. Only the registers are repeated: E256's register timelines, another run,
end with the same 0x0700 and 0x0710 after the 64x64, 256x256, 1024x768 and 4096x4096 triangles,
the 1024x768 one in 0x30 pages and two 64x64 renders. The walks, the changed entries and the state
pages (E310) exist once.

| case | pages used | walk: head, tail, page before tail | 0x0700 / 0x070c | 0x0710 / 0x071c |
|---|---|---|---|---|
| 64x64, 0x422 pages | 2 | 0x3, 0x2, 0x1 | 0x00020003 | 0x00000001 |
| 256x256 | 5 | 0x6, 0x1, 0x5 | 0x00010006 | 0x00000005 |
| 1024x768 | 0x13 | 0x14, 0x1, 0x8 | 0x00010014 | 0x00000008 |
| 4096x4096 | 0x11f | 0x120, 0x1, 0x94 | 0x00010120 | 0x00000094 |
| 1024x768, 0x40 pages | 0x13 | 0x14, 0x1, 0x8 | 0x00010014 | 0x00000008 |
| 1024x768, 0x30 (partial render) | | 0x15, 0x1, 0x12 | 0x00010015 | 0x00000012 |
| 4096x4096, 0x100 (partial render) | | 0xc7, 0x1, 0x16 | 0x000100c7 | 0x00000016 |
| two 64x64 renders | 4 | 0x5, 0x4, 0x3 | 0x00040005 | 0x00000003 |

In every case the walk covers all N pages, every previous link matches the page walked before it,
and the registers agree with the walk: STATUS1 is (tail << 16) | head, STATUS2's low half the page
before the tail, its high half 0. The entries that change are the freed pages' and their
neighbours': after the 64x64 job entries 1, 2, 3 and 0x422 (0x04220002, 0x0001ffff, 0xffff0004,
0x04210001), so the list runs 0x3-0x422, then 1, 2. The pages a job used come back at the tail in
the order the 3D freed them, page 1 last in every job but the four 64x64 ones, where it is freed
first (0x6-0x422, then 2, 4, 3, 5, 1 after the 256x256 job); the second of the two 64x64 renders
takes pages 3 and 4, the head the first left. The 3D's free-list register 0x0604 reads the TA's list
after its TA (0x04220003 at 64x64, tail 0x422 and head 3).

**Reading [infer].** The DPM itself writes the page table, at base + 4 x page: entries at those
places are the ones that change, and the walk is consistent after every job. So a host-built table
must be one 32-bit entry per page indexed by the page number from the base, as our kernel builds it.
The values E184 and E256 saw after jobs (0x0001 and 0x94 after 4096x4096) are the tail page and the
page before it, so E256's reading of them as the head and the tail page [infer] is superseded. While
the TA runs (E256), STATUS2's low half is the page before the initial tail (0x421), which the
descriptor holds shifted into its high half (E200's store).

**Not shown.** The EDM's own page-table builder (PB_FLAGS.INIT_PAGE_TABLE) is not run: our kernel
never sets the flag and no poke reaches the PB descriptor, so the builder's stride stays
unmeasured (Q067). STATUS2's high half is 0 in every sample.
