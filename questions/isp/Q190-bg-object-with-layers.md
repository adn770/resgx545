+++
id = "Q190"
question = "does a render's background object with texture layers (the 23-dword form of a transfer copy: the six words after the PDS words, the layer's coordinates, the format word) read its coordinate words vertex by vertex in a render as it does in a transfer's (E209), and which of the words 3 to 8 matter then, given that no word 3 to 16 of the layerless object is shown to (E590)?"
unit = "isp"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E069", "E209", "E590"]
terms = ["CR_ISP_BGOBJVALS", "hw_render_details.pds_bgnd"]
+++

E590: in a 64x64 render of one triangle whose background object has no layer none of the words 3 to
16 is shown to be read (169 jobs; no positive control). A transfer's copy has a one-layer object (23
dwords) whose coordinate words are read and whose format word after them changes nothing over eight
values (E069, E209). Whether a render with the one-layer object (a bgobj tag size field raised and
the layer's words present) reads the same words, and where the object's size field lives in a render
(dword 1 of the object, bits 24:18, Q019).

To settle it: a kernel switch that builds the render's object in the one-layer form (or a poke space
that reaches the words beyond 17 of the parameter slot's object page), and the bg:N pokes of E590 on
it, coordinates first.
