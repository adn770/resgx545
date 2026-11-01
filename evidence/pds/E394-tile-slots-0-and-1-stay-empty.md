+++
id = "E394"
claim = "E130's grid16 probe (a 128x128 render, each 16x16 tile's end-of-tile task storing a slot) run five times: 57-61 of the 64 slots hold data each run (ir1 2 or 6 in their third dword, E130's rule), slots 0 and 1 are empty in all five, 1 to 5 others differ from run to run (13, 20, 22, 25, 33, 46, 51, 52), and slots 64 and 768 hold only colour words in four of the runs, slot 768 holding data (ir0 0x1407, ir1 2) in the first"
unit = "pds"
method = "probes/pds/tile-slots.toml on the laptop over the cable, linux fork b5a86838ae59 with the debug option on: pds-pixel-event-pixev-grid16 of probes/pds/pixel-event.toml as it ran for E130, five runs"
tiers = ["HW"]
date = "2026-11-03"
data = ["pds-tile-slots"]
terms = []
+++
**Results.** Empty slots per run: 0, 1, 20, 33, 52; 0, 1, 46; 0, 1, 20, 25; 0, 1, 25, 51; 0, 1, 13,
22, 25, 46, 51. A slot with only colour words (0xff203040, 0xff00ff00) and its slot word, such as
slot 52 in run 1, is empty by E130's rule. Slot 64 holds only colour words in all five runs; slot
768 holds data in run 1 and only colour words in the other four.
