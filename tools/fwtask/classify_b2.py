# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Phase 11.30 stage B2 predictions (which part of our state changes what the next task sees),
frozen before the first run of stage B2 (after the results of stage B were read)."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import classify

ROWS = [
    ("B2_armonly", "after cmd 2 (the writer that only arms the reader and tail-calls) the pclink and p1 read at the next "
     "event are the preceding control's, in 3 of 3 rounds",
     "pclink 6 or p1 changed after a writer that wrote nothing: the event with a command (not our values) is what differs",
     "all(a == b for a, b in zip(pcl_next, pcl_ctl)) and all(a == b for a, b in zip(p1_next, p1_ctl))"),
    ("B2_ponly", "after cmd 3 (p0 to p3 only) the pclink read at the next event is 6 and p1 is 0 (ours), in 3 of 3 rounds",
     "the control's pclink or p1: the predicates are not what changes the closed task's path",
     "all(a == 6 for a in pcl_next) and all(a == 0 for a in p1_next)"),
    ("B2_saonly", "after cmd 4 (sa, r, i only, no predicates) the pclink and p1 read at the next event are the control's, 3 of 3",
     "pclink 6: the sa, r or i values change the closed task's path",
     "all(a == b for a, b in zip(pcl_next, pcl_ctl)) and all(a == b for a, b in zip(p1_next, p1_ctl))"),
    ("B2_full", "after cmd 1 (everything, as stage B) pclink is 6 and p1 is 0 again, 3 of 3",
     "the control's values: stage B's reading does not repeat",
     "all(a == 6 for a in pcl_next) and all(a == 0 for a in p1_next)"),
    ("B2_sa63_65", "after cmd 1 and cmd 4 sa63 and sa65 read at the next event are the markers written (6 of 6)",
     "any other value: sa64 is not the only sa that does not stick", "sa_extra == sa_extra_marked"),
    ("B2_sa64", "sa64 reads 2 at the next event after cmd 1 and cmd 4 (our write of sa64 does not stick, 6 of 6)",
     "sa64 reads our marker, or any other value", "all(a == 2 for a in sa64_next)"),
]


def render():
    out = ["# SPDX-License-Identifier: MIT", "# SPDX-FileCopyrightText: 2026 Josep Torra", "#",
           "# Phase 11.30 stage B2 predictions, frozen before its first run. classify.py reads only this file.", ""]
    for rid, decl, fals, expect in ROWS:
        out += ["[[row]]", f'id = "{rid}"', 'stage = "B2"', f'declared = "{decl}"', f'falsifier = "{fals}"',
                f'expect = "{expect}"', ""]
    return "\n".join(out)


if __name__ == "__main__":
    pathlib.Path(sys.argv[1]).write_text(render())
    print(classify.sha256(sys.argv[1]))
