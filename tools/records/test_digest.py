# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""digest.py: doc/state_digest.md, the project's state on one page, from the tracked tree."""
import pathlib

import pytest

import digest


def flat(text):
    """The text with its line breaks and runs of spaces as single spaces (entries wrap)."""
    return " ".join(text.split())


def rec(root, unit, rid, date, claim, kind="E"):
    d = root / ("evidence" if kind == "E" else "questions") / unit
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{rid}-x.md").write_text(
        f'+++\nid = "{rid}"\nclaim = "{claim}"\nunit = "{unit}"\nmethod = "m"\n'
        f'tiers = ["HW"]\ndate = "{date}"\ndata = []\nterms = []\n+++\n\nProse.\n')


def question(root, unit, qid, kind, value, ev, text="what is it?"):
    d = root / "questions" / unit
    d.mkdir(parents=True, exist_ok=True)
    v = f'value = "{value}"\n' if value else ""
    (d / f"{qid}-x.md").write_text(
        f'+++\nid = "{qid}"\nquestion = "{text}"\nunit = "{unit}"\nkind = "{kind}"\n{v}'
        f'phase = 11\nevidence = {ev!r}\nterms = []\n+++\n\nProse.\n'.replace("'", '"'))


@pytest.fixture()
def tree(tmp_path):
    r = tmp_path
    rec(r, "dpm", "E010", "2026-11-01", "an old claim")
    rec(r, "dpm", "E011", "2026-11-10", "a claim of the tenth")
    rec(r, "ta", "E012", "2026-11-12", "the newest claim")
    question(r, "dpm", "Q001", "hw", "low", ["E003", "E010", "E002"])
    question(r, "ta", "Q002", "hw", "high", ["E001", "E011", "E012", "E004"], "which way?")
    question(r, "edm", "Q003", "fw", None, [])
    (r / "datasets").mkdir()
    (r / "datasets/render-closing-r9-toy.toml").write_text(
        'title = "laptop session R9-toy"\nrepo = "data"\npaths = ["render/closing-r9-toy/"]\n'
        'method = "on the laptop, module srcversion 99CD90DA26E3AFF9C450517 (fork branch '
        'resgx545 at a2788bd8), tool ~/sgxfive-test-rgn4 and ~/scratch/r9/bin/sgxfive-test"\n'
        'date = "2026-11-12"\nfiles = 1\nsize = 1\nsha256 = "0"\nrecipe = "run/m.sh"\n')
    (r / "datasets/vectors-other.toml").write_text(
        'title = "t"\nrepo = "data"\npaths = ["vectors/x/"]\nmethod = "m"\n'
        'date = "2026-11-12"\nfiles = 1\nsize = 1\nsha256 = "0"\nrecipe = "r"\n')
    (r / "tools/closing").mkdir(parents=True)
    (r / "tools/forkpin.py").write_text('PIN = "664fd0d00765"        # the pin\n')
    (r / "tools/closing/scorekit.py").write_text("x = 1\n")
    (r / "tools/closing/sessioncheck.py").write_text("y = 2\n")
    (r / "HACKING.md").write_text(
        "# H\n\n## Known tool weaknesses\n\n- `session_tests.sh` rebuilds every run.\n"
        "- the guard is slow.\n\n## Markdown\n\nWrap.\n")
    (r / "crates").mkdir()
    (r / "crates/SIM_UNMODELLED.toml").write_text(
        '[[unmodelled]]\nid = "a"\n\n[[unmodelled]]\nid = "b"\n\n[[unmodelled]]\nid = "c"\n')
    return r


def test_open_questions_with_unit_value_and_last_three_records(tree):
    text = flat(digest.render(tree))
    hw = text.index("## Open questions")
    q2 = text.index("Q002", hw)
    assert q2 < text.index("Q001", hw)                    # high before low
    assert "`Q002` ta, high: which way? (E004, E011, E012)" in text
    assert "`Q001` dpm, low: what is it? (E002, E003, E010)" in text
    assert "`Q003` edm, fw (parked)" in text
    assert "3 open: 2 hw, 1 parked" in text


def test_records_of_the_last_days_with_claims(tree):
    text = flat(digest.render(tree, days=3))
    sec = text[text.index("## Recent records"):text.index("## Closing sessions")]
    assert "`E012` ta, 2026-11-12: the newest claim" in sec
    assert "`E011` dpm, 2026-11-10: a claim of the tenth" in sec
    assert "E010" not in sec
    assert "2026-11-10 to 2026-11-12" in sec


def test_published_sessions_with_module_and_tools(tree):
    sec = flat(digest.render(tree))
    sec = sec[sec.index("## Closing sessions"):]
    assert "render/closing-r9-toy" in sec and "2026-11-12" in sec
    assert "99CD90DA26E3AFF9C450517" in sec and "~/sgxfive-test-rgn4" in sec
    assert "~/scratch/r9/bin/sgxfive-test" in sec and "resgx545 at a2788bd8" in sec
    assert "vectors/x" not in sec


def test_versions_weaknesses_and_sim_baseline(tree):
    text = flat(digest.render(tree))
    assert "fork pin (`tools/forkpin.py`): 664fd0d00765" in text
    assert "scorekit.py" in text and "sessioncheck.py" in text
    assert "`session_tests.sh` rebuilds every run." in text and "the guard is slow." in text
    assert "Wrap." not in text
    assert "3 entries in `crates/SIM_UNMODELLED.toml`" in text


def test_absent_sources_are_said_so(tree):
    (tree / "crates/SIM_UNMODELLED.toml").unlink()
    (tree / "HACKING.md").write_text("# H\n")
    text = flat(digest.render(tree))
    assert "no `crates/SIM_UNMODELLED.toml`" in text
    assert "no known-weaknesses section in HACKING.md" in text


def test_lines_fit_and_check_mode(tree):
    text = digest.render(tree)
    assert all(len(line) <= 100 for line in text.splitlines())
    doc = tree / "doc/state_digest.md"
    assert digest.main(["--check"], root=tree) == 1
    assert digest.main([], root=tree) == 0 and doc.read_text() == text
    assert digest.main(["--check"], root=tree) == 0
    rec(tree, "ta", "E013", "2026-11-13", "a new one")
    assert digest.main(["--check"], root=tree) == 1


def test_the_tracked_digest_is_current():
    root = pathlib.Path(digest.__file__).resolve().parents[2]
    assert (root / "doc/state_digest.md").read_text() == digest.render(root)
