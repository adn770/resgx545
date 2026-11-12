# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""new_record.py: an evidence record drafted from a published closing session's own files."""
import re

import pytest

import datasets
import evidence
import new_record

H = {k: k * 64 for k in "abcdef"}       # toy sha256s
LOG = """attempt 20261112-101010: /x/out/20261112-101010; FROZEN.sha256 {a}; t6 {b}
#### s1 10:10:11
  class ok
## STOP: the 2-th fault-class event of the stage (2 is the limit): stop after j3
SUMMARY: S1: H-ONE held (3 of 3 rows decided); controls pass
the lead decided to go on (decision D7-1 a)
[123.4] gma500: kernel line with a lead word
stage s1 done, health ok
#### s2 10:12:00
SUMMARY: S2: cannot tell
"""


@pytest.fixture()
def session(tmp_path):
    s = tmp_path / "render" / "closing-r9-toy"
    a = s / "out" / "20261112-101010"
    (a / "s1").mkdir(parents=True)
    (a / "s1" / "j1.txt").write_text("x")
    (a / "s2").mkdir()
    (a / "score-s1.txt").write_text("s1 table\n")
    (a / "score-s1.fixed.txt").write_text("s1 fixed table\n")
    b = s / "out" / "20261112-121212"
    (b / "s1").mkdir(parents=True)
    (s / "run-r9.log").write_text(LOG.format(**H))
    (s / "run-r9-s1.log").write_text(
        f"attempt 20261112-121212 (set B): /x; FROZEN-B.sha256 {H['c']}\n#### s1 12:12:13\n"
        "SUMMARY: S1: H-ONE held again\n")
    (s / "FROZEN.sha256").write_text(f"{H['d']}  score/s.py\n{H['e']}  gen/t.tsv\n")
    (s / "FROZEN-B.sha256").write_text(f"{H['d']}  score/s.py\n")
    (s / "PREDICTIONS.sha256").write_text(f"{H['e']}  predictions/p.tsv\n")
    (s / "FROZEN.commits").write_text(
        "# header\n"
        f"{H['f']}  382b7362131de2bddfb73772c84158bd38158401  tools/bringup/health.sh\n"
        f"{H['f']}  untracked  tools/usse-asm/usse-asm\n"
        f"{H['f']}  e5cdaf0a1234  data:render/closing-r2-geo/x.toml\n")
    (s / "freeze1").mkdir()
    (s / "freeze1" / "FROZEN.sha256").write_text(f"{H['a']}  score/s.py\n")
    (s / "freeze1" / "FREEZE.txt").write_text("r9 freeze 1, before any job\nmore\n")
    (s / "FREEZE-B.txt").write_text("r9 set B freeze, after set A ran\n")
    (s / "TOOL.sha256").write_text(f"{H['b']}  /home/u/sgxfive-test-rgn4\n")
    (s / "TOOLSRC.sha256").write_text(f"{H['c']}  4623753:userspace/libsgxfive/tools/t.c\n")
    (s / "run").mkdir()
    (s / "run" / "k.env").write_text(
        "# comment\nTOOL_SHA=" + H["b"] + "\nSRCV_EXPECT=99CD90DA26E3AFF9C450517\n"
        "JOB_TIMEOUT=300\n")
    (s / "README.md").write_text("# r9-toy\n\nBuilt offline against resgx545 main **d9b2969**.\n")
    (s / "postrun").mkdir()
    (s / "postrun" / "data-view.txt").write_text(
        "# The render sessions of resgx545-data main e5cdaf0a (2026-11-12 13:23)\n")
    (s / "POSTRUN-FIX.md").write_text("a fix\n")
    return s


def method_of(text):
    return re.search(r'^method = "(.*)"$', text, re.M).group(1)


def test_the_method_names_the_attempts_that_ran_the_stage(session):
    m = method_of(new_record.draft(session, "E901", ["s1"]))
    assert "out/20261112-101010" in m and "out/20261112-121212" in m
    assert "10:10:11" in m and "12:12:13" in m and "run-r9.log" in m
    m2 = method_of(new_record.draft(session, "E901", ["s2"]))
    assert "out/20261112-101010" in m2 and "out/20261112-121212" not in m2


def test_the_method_names_every_freeze_and_its_digest(session):
    m = method_of(new_record.draft(session, "E901", ["s1"]))
    for name in ("FROZEN.sha256", "FROZEN-B.sha256", "PREDICTIONS.sha256",
                 "freeze1/FROZEN.sha256", "FREEZE-B.txt", "freeze1/FREEZE.txt"):
        assert name in m, name
    assert "(2 files)" in m and "r9 set B freeze, after set A ran" in m
    # the attempt's own freeze, as its log names it
    assert H["a"][:8] in m and H["c"][:8] in m


def test_the_method_names_pins_tools_module_and_commits(session):
    m = method_of(new_record.draft(session, "E901", ["s1"]))
    assert "tools/bringup/health.sh at 382b7362" in m
    assert "tools/usse-asm/usse-asm untracked" in m
    assert "data:render/closing-r2-geo/x.toml at e5cdaf0a" in m
    assert H["b"] in m and "sgxfive-test-rgn4" in m and "4623753:userspace" in m
    assert "SRCV_EXPECT=99CD90DA26E3AFF9C450517" in m and "JOB_TIMEOUT" not in m
    assert "resgx545 main d9b2969" in m and "resgx545-data main e5cdaf0a" in m
    assert "dataset render-closing-r9-toy" in m


def test_stops_decisions_and_scores_are_carried(session):
    text = new_record.draft(session, "E901", ["s1"])
    m = method_of(text)
    assert "STOP: the 2-th fault-class event" in m
    assert "the lead decided to go on (decision D7-1 a)" in m
    assert "kernel line" not in m
    assert "score-s1.txt" in m and "score-s1.fixed.txt" in m and "POSTRUN-FIX.md" in m
    body = text.split("\n+++\n", 1)[1]
    assert "`SUMMARY: S1: H-ONE held (3 of 3 rows decided); controls pass`" in body
    assert "`SUMMARY: S1: H-ONE held again`" in body
    assert "S2: cannot tell" not in body


def test_the_front_matter_lists_the_data_and_the_todos(session):
    text = new_record.draft(session, "E901", ["s1"], unit="ta")
    assert 'id = "E901"' in text and 'unit = "ta"' in text and 'date = "2026-11-12"' in text
    assert '"render-closing-r9-toy:out/20261112-101010/s1/"' in text
    assert '"render-closing-r9-toy:freeze1/"' in text
    assert '"render-closing-r9-toy:postrun/"' in text
    for section in ("claim", "What it shows", "What it does not show"):
        assert re.search(rf"{section}.*{new_record.TODO}", text), section


def test_a_filled_draft_passes_the_form_check(session, tmp_path):
    text = new_record.draft(session, "E901", ["s1"], unit="ta")
    filled = text.replace(new_record.TODO, "filled")
    p = tmp_path / "ev" / "ta" / "E901-filled.md"
    p.parent.mkdir(parents=True)
    p.write_text(filled)
    assert evidence.problems(p, set()) == []
    assert new_record.todos(text) >= 4 and new_record.todos(filled) == 0


def test_an_unknown_stage_is_refused(session, capsys):
    rc = new_record.main(["--session", str(session), "--id", "E901", "--stage", "zz"])
    assert rc == 2 and "zz" in capsys.readouterr().err


def test_the_cli_writes_the_draft(session, tmp_path):
    out = tmp_path / "d.md"
    assert new_record.main(["--session", str(session), "--id", "E901", "--stage", "s1",
                            "--unit", "ta", "--out", str(out)]) == 0
    assert out.read_text().startswith('+++\nid = "E901"\n')


# Published sessions: the drafted method mentions every attempt and freeze that the landed
# records' methods mention (attempt stamps, freeze files and their digests' prefixes).
PUBLISHED = {
    "E884": ("render/closing-r6-misc", ["q289"]),
    "E885": ("render/closing-r6-misc", ["q287"]),
    "E886": ("render/closing-r6-misc", ["q086"]),
    "E887": ("render/closing-r6-render4x", ["s0", "a"]),
    "E888": ("render/closing-r6-render4x", ["t"]),
    "E889": ("render/closing-r6-render4x", ["s0b", "b", "k", "r"]),
}


@pytest.mark.parametrize("rid", sorted(PUBLISHED))
def test_published_sessions_cover_the_landed_methods(rid):
    data = datasets.repos().get("data")
    if data is None:
        pytest.skip("SKIPPED, NOT PASSED: no resgx545-data checkout")
    where, stages = PUBLISHED[rid]
    landed = method_of(next(evidence.DIR.glob(f"*/{rid}-*.md")).read_text())
    drafted = method_of(new_record.draft(data / where, rid, stages))
    wanted = set(re.findall(r"out/\d{8}-\d{6}", landed))
    wanted |= set(re.findall(r"\b(?:FROZEN|PREDICTIONS)[-A-Za-z0-9.]*\.sha256\b", landed))
    wanted |= set(re.findall(r"\bFREEZE[-A-Za-z0-9]*\.txt\b|\bfreeze\d+/", landed))
    wanted |= {h[:8] for h in re.findall(r"\b([0-9a-f]{8})\.\.\.", landed)}
    assert wanted
    missing = sorted(w for w in wanted if w not in drafted)
    assert not missing, missing
