+++
id = "E298"
claim = "firh reads line position p (0 to 11) at centre p; at centres -4 to -1 rep reads byte 0, msc byte -p and mdc byte -1-p; at 12 to 18 rep reads byte 11, msc byte 22-p and mdc byte 23-p; from 19 to 27 every mode reads 0. With a load, sets 6 and 7 give 0 at 0x0a9c = 0, and are not 0 at 1 and 2: bank 1's two sets and bank 2's set 6 give values no loaded group gives"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/usse/filter-edges.toml, fills whose pixel program runs firh r10, r1, r2, r3, u8, rep|msc|mdc, fcs0, #s, #0 with the filter block loaded at 0x0a9c = 3 and group 0 an identity filter (the tap at the centre 1, shift 0, bias 0) on a ramp line (bytes 0x10 to 0xc0), for every centre -4 to 27 (written #-16 to #-5 above 15); and fcs6 and fcs7 at 0x0a9c = 0, 1 and 2 with groups 0 to 2 loaded as identity filters times 1, 2 and 3; 102 cases, one run"
tiers = ["HW"]
date = "2026-11-02"
data = ["usse-filter-edges"]
terms = ["CR_USE_COEFFS_MODE.MODE"]
+++

**What runs.** With one tap of 1 at the centre and nothing else, firh's result is the line byte
at its centre, so the ramp (byte n holds 0x10 (n + 1)) names the position read.

**Results.** Positions read, by centre (byte n, or 0):

| centre | -4 | -3 | -2 | -1 | 0-11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19-27 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| rep | 0 | 0 | 0 | 0 | itself | 11 | 11 | 11 | 11 | 11 | 11 | 11 | reads 0 |
| msc | 4 | 3 | 2 | 1 | itself | 10 | 9 | 8 | 7 | 6 | 5 | 4 | reads 0 |
| mdc | 3 | 2 | 1 | 0 | itself | 11 | 10 | 9 | 8 | 7 | 6 | 5 | reads 0 |

The centre field's values written #-16 to #-5 are centres 16 to 27, as E292's 1,126 vectors
below #-4 need. The folds at 12 to 18 are the mirror images of those below 0 (msc mirrors about
the end byte, mdc repeats it first); 19 is where every mode stops reading the line.

Sets 6 and 7 on the ramp, centred at byte 4 (0x50), with the three groups loaded: 0 and 0 at
0x0a9c = 0; 0x5c and 0x5c at 1; 0x38 and 0x50 at 2. The loaded groups give 0x50, 0xa0 and 0xf0
here. 0x5c (bank 1, both sets) and 0x38 (bank 2, set 6) are none of them, so those three are sets
of their own. Bank 2's set 7 reads 0x50, which group 0 gives, and so does any filter of unit
gain that reads the centre byte: this case does not tell it from either. One case per set does
not give the taps.

**Not shown.** Centres past 27 do not exist (the field is 5 bits); sets 6 and 7's taps under
banks 1 and 2. One run.
