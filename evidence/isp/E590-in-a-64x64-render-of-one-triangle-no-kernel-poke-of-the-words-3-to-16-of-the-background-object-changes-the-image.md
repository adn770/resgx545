+++
id = "E590"
claim = "In a 64x64 render of one triangle on a coloured background (ISP_BGOBJVALS 0x300), a kernel poke of any one of the words 3 to 16 of the render's background object (17 dwords, at 0x463000 of debugfs render_param's dump: six zero words, then the vertex words) leaves the image the control's in 140 of 140 jobs (ten values a word: bits 0, 3, 7, 8, 15, 16, 24 and 31 flipped, 0, 0xffffffff; 131 of the 140 change the word, 9 set a zero word to 0) and the poked value reads back in the object after the job in 140 of 140; setting the words 3 to 16 together to 0xffffffff, to 0 and to 0xa5000000 + N leaves it the control's in 6 of 6; a poke of one of the words 0 to 2 is not in the object after the job (the EDM's value) in 18 of 18 and changes nothing in 18 of 18; all 169 jobs completed, none faulted or hung"
unit = "isp"
method = "script bg-words (161 jobs) and bg-words-f1 (8 jobs), on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion 34729EB82083B1D04B0643E (built from the linux fork's p1135 branch, base 3d9b8bdefe94, tip da1eaeaa1247: commits 46 to 48 as they were before the review's fixes, series check 6 of 6 PASS, KUnit 176/176 with the debug option; installed equal to loaded at the start of every script, loaded once at 04:59:38), stock firmware (own_arm off), tool sgxfive-test-1126 (sha256 751f7223c8c731a08d75cfc3920a5d1050488ca3bdc426be45b7c431e600f82e, unchanged), no reboot, no clock-gate register written (no kreg, no kregnow), reset only through debugfs: one `tri --pixels --dump-render DIR` job a case with `--kpoke-render 1:bg:N^=V` (or `=V`), the poke cleared and the GPU reset only after a failed job; the recompute (analysis/recompute/recompute_p1135.py) reads only the kept raw dumps"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["isp-bg-object-pokes"]
terms = ["CR_ISP_BGOBJVALS", "hw_render_details.pds_bgnd", "hw_rt_data.bgobj_dev_vaddr"]
+++

**What ran.** Script bg-words, 161 jobs (kernel commit 46, debugfs kpoke space `bg`, applied at the
render's kick after the kernel has written the object): 3 controls (no poke), words 0 to 2 at six
values each (bits 0, 8, 16, 31 flipped, 0, 0xffffffff: 18 jobs), words 3 to 16 at the ten values
(140 jobs, of which 9 set a word that is already 0 to 0, words 3 to 8, 11, 13 and 16, and 131 change
a word), one `tri --pixels --dump-render` job each (64x64, the plain triangle on the coloured
background, ISP_BGOBJVALS 0x300, every pixel printed, the parameter dump kept). Follow-up
bg-words-f1, 8 jobs declared after the first run: the 14 words 3 to 16 poked together (all
0xffffffff, all 0, word N = 0xa5000000 + N, two jobs each) and two controls. The object of the
control reads (dwords 0 to 16) 0x04000004, 0x00030000, 0x04000002, 0 (x6), 0x00100000, 0x1000, 0,
0x10400010, 0, 0x00104000, 0x1000, 0: the three PDS words, six zero words, then eight words that the
kernel's layout and the explore script (analysis/bg_geometry.py) read as three corners of a
rectangle, (0, 0), (64, 0) and (0, 64), in 24-bit fixed point with 8 fraction bits and an offset of
4096 [infer]. Pilot, not data: two jobs on the old module (5AD04F33, which has no `bg` space) at
04:34 to 04:43, a control and a poke of word 0 that the old module refused (rc 1), to see the tool's
output.

**Results.** [HW] All 169 jobs completed (`tri: 1 renders ok`, diff 0 of 4096 pixels, the tool's own
target hash 0x99385a04ee01c585 in all 161 jobs of the first run and in the 8 of the follow-up; the
recompute's pixel hash is one value for all 169): no flip, 0 or 0xffffffff of any word 3 to 16
changes a pixel (140 of 140, 131 of them changing the word), nor the 14 words together (6 of 6). In
140 of 140 jobs the post-job dump holds the poked value at its word (14 of 14 words a job in the 6
of the follow-up); in the 18 of 18 jobs that poked words 0 to 2 it holds the control's word, not the
poked one (the EDM wrote it again at the kick, E162), and the image is the control's. Declared
before the run: H66-E (words 0 to 2 lost, image = control) right in 18 of 18 and 18 of 18; H66-N
(words 3 to 8 not read, image = control) right in 54 of 54 scored jobs (6 more set a zero word to 0,
scored as controls); H66-V (vertex bits that move an edge by a pixel or more change the image) wrong
in 34 of 34 scored jobs (its predictions assumed that the vertex words move the rectangle), the 43
jobs it gave `?` (the explore set) all gave the control's image too; H66-Z (follow-up: the whole
object at once changes nothing) right in 6 of 6. Where the vertices read as the layout above says,
the poked values would uncover pixels in 23 of the 80 vertex-word jobs (for example word 12 or word
14 set to 0: a degenerate rectangle, 0 of 4096 covered; word 11 bit 31 flipped: 1024 covered): in
none did a pixel stay uncovered (all 4096 covered).

**Reading.** [infer] In this scene, the one-triangle 64x64 render with a layerless object and
ISP_BGOBJVALS 0x300, the image is the same whatever the words 3 to 16 hold, so the data does not
show the ISP reading any of them: the whole render box gets the background whatever the vertices
say. That is a statement about this scene and about these values, ten a word (131 effective pokes),
not a reading of the object as a whole. The words 0 to 2 can be shown neither read nor not read by
these jobs: the EDM rewrites all three after the poke (18 of 18), so a poked value never reaches the
ISP; whether the ISP reads the words 1 and 2 is open, and word 0 is the one the background pixel
program starts from only by E410's run (the render details' dword 69, through which the first word
reached the image, 11 of 32 bit flips changing it). That path is live in this job, which is the only
control the record has for "a change of the object can change this image": there is no positive
control for words 3 to 16, because every word that the ISP is shown to read (0) is rewritten before
the kick takes it, so a poke that did change an image could not be shown for the same memory. The
poke reaches the object (it reads back after the job through the same pointer, mapping and barrier
as the kernel's own words, [HW]), which is not proof that the ISP's fetch saw it. The coordinate
reading of E209 stays the coordinate words of a transfer copy's texture layers, not shown for a
render's rectangle [infer].

**Not shown.** What the three PDS words mean beyond E410's finding for word 0, and whether the ISP
reads words 1 and 2; the object with texture layers (the 23-dword form of a copy), Q190; a render
with ISP_BGOBJVALS other than 0x300, another size than 64x64, or more than one triangle. The pokes
were made at 64x64 and one scene only.  A bg poke is lost when a render is replayed after a
recovery, which rebuilds the object unpoked (the kpoke header says so).
