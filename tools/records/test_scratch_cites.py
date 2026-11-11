# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""scratch_cites.py: a path of the scratch area that the tree cites must be published, as a
session directory of a data repository or under its cited/ directory, so no citation rests on
disposable scratch."""
import pytest

import scratch_cites as sc


@pytest.fixture
def world(tmp_path, monkeypatch):
    root, data, priv, scratch = (tmp_path / n for n in ("resgx545", "data", "priv", "scratch"))
    for d in (root, data, priv, scratch):
        d.mkdir()
    monkeypatch.setattr(sc, "ROOT", root)
    monkeypatch.setattr(sc, "tracked", lambda r: sorted(
        p.relative_to(r).as_posix() for p in r.rglob("*") if p.is_file()))
    monkeypatch.setattr(sc, "repos", lambda: {"data": data, "data-private": priv})
    monkeypatch.setattr(sc, "SCRATCH", scratch)
    return root, data, priv, scratch


def put(base, rel, text="x\n"):
    p = base / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)
    return p


def test_tokens_rooted_in_scratch():
    text = ("see `closing4/p7/reading-r5.md`, closing/s3/, and closing2/geometry. "
            "Not vectors/closing/r3-pixel/ nor tools/closing/session_tests.sh nor closing3/ "
            "alone; ~/src/scratch/resgx545/closing4/rank/faultseq.out and "
            "/Users/x/src/scratch/resgx545/closing3/kernel/layout_f4.out.")
    assert sc.cites_in(text) == ["closing4/p7/reading-r5.md", "closing/s3/", "closing2/geometry",
                                 "closing4/rank/faultseq.out", "closing3/kernel/layout_f4.out"]


def test_a_path_broken_over_lines_is_joined():
    py = "scorers (closing4/pixel/\n    px_rule.py and ta_rule.py)"
    rs = "//! read `closing4/pixel/\n//! qt.out`"
    assert sc.cites_in(py) == ["closing4/pixel/px_rule.py"]
    assert sc.cites_in(rs) == ["closing4/pixel/qt.out"]


def test_cites_are_read_from_tracked_text_files_but_not_mechanics(world):
    root, *_ = world
    put(root, "evidence/edm/E1.md", "closing4/a.out\n")
    put(root, "questions/q/Q1.md", "closing4/b.out\n")
    put(root, "tools/closing/session_tests.sh", "closing3/x/y\n")
    put(root, "datasets/d.toml", 'method = "froze closing4/lead/wt/tools/a.py"\n')
    put(root, "bin/blob.bin", "closing4/c.out\n")
    assert sc.cites() == {"closing4/a.out": ["evidence/edm/E1.md"],
                          "closing4/b.out": ["questions/q/Q1.md"]}


def test_a_session_alias_resolves_to_the_published_session(world):
    root, data, *_ = world
    (data / "render" / "closing-s3").mkdir(parents=True)
    put(data, "render/closing-r3-geo-c/score/score_r3.py")
    put(data, "edm/closing-s1b/README.md")
    assert sc.resolve("closing/s3/") == "data:render/closing-s3/"
    assert sc.resolve("closing3/r3-geo-c/score/score_r3.py") == \
        "data:render/closing-r3-geo-c/score/score_r3.py"
    assert sc.resolve("closing/s1b-v2/README.md") == "data:edm/closing-s1b/README.md"
    assert sc.resolve("closing3/r3-geo-c/nothing.txt") is None


def test_a_published_copy_resolves_in_either_repository(world):
    root, data, priv, _ = world
    put(data, "cited/closing4/rank/faultseq.out")
    put(priv, "cited/closing4/p7/reading-r5.md")
    (data / "cited" / "closing2" / "geometry").mkdir(parents=True)
    assert sc.resolve("closing4/rank/faultseq.out") == "data:cited/closing4/rank/faultseq.out"
    assert sc.resolve("closing4/p7/reading-r5.md") == \
        "data-private:cited/closing4/p7/reading-r5.md"
    assert sc.resolve("closing2/geometry") == "data:cited/closing2/geometry"
    assert sc.resolve("closing4/rank/other.out") is None


def test_check_lists_every_unresolved_cite_with_its_citers(world):
    root, data, *_ = world
    put(root, "evidence/edm/E1.md", "closing4/a.out and closing4/b.out\n")
    put(data, "cited/closing4/a.out")
    assert sc.problems() == ["closing4/b.out: not published (cited by evidence/edm/E1.md)"]


def test_publish_copies_files_and_dirs_and_writes_the_manifest(world):
    root, data, priv, scratch = world
    put(scratch, "closing4/rank/faultseq.out", "f\n")
    put(scratch, "closing2/geometry/a.py", "a\n")
    put(scratch, "closing2/geometry/debug/junk", "j\n")
    put(scratch, "closing2/geometry/__pycache__/a.pyc", "c\n")
    put(scratch, "closing4/p7/reading-r5.md", "r\n")
    sc.publish(["closing4/rank/faultseq.out", "closing2/geometry"], private=False)
    sc.publish(["closing4/p7/reading-r5.md"], private=True)
    assert (data / "cited/closing4/rank/faultseq.out").read_text() == "f\n"
    assert sorted(p.name for p in (data / "cited/closing2/geometry").rglob("*")) == ["a.py"]
    assert (priv / "cited/closing4/p7/reading-r5.md").is_file()
    pub = (root / "datasets" / "cited-scratch.toml").read_text()
    assert 'repo = "data"' in pub and 'paths = ["cited/"]' in pub and "files = 2" in pub
    assert 'repo = "data-private"' in (root / "datasets" / "cited-scratch-private.toml").read_text()


def test_publish_refuses_a_missing_source_and_an_existing_copy(world):
    root, data, priv, scratch = world
    with pytest.raises(SystemExit, match="not in the scratch area"):
        sc.publish(["closing4/none.out"], private=False)
    put(scratch, "closing4/a.out")
    put(data, "cited/closing4/a.out", "old\n")
    with pytest.raises(SystemExit, match="already published"):
        sc.publish(["closing4/a.out"], private=False)


def test_republish_keeps_the_manifest_title_and_updates_the_digest(world):
    root, data, priv, scratch = world
    put(scratch, "closing4/a.out")
    put(scratch, "closing4/b.out")
    sc.publish(["closing4/a.out"], private=False)
    m = root / "datasets" / "cited-scratch.toml"
    m.write_text(m.read_text().replace("title = ", "title = \"kept\"\n#", 1))
    sc.publish(["closing4/b.out"], private=False)
    t = m.read_text()
    assert t.startswith('title = "kept"') and "files = 2" in t


def test_without_any_data_repository_check_passes_with_a_note(world, monkeypatch, capsys):
    root, *_ = world
    put(root, "evidence/edm/E1.md", "closing4/a.out\n")
    monkeypatch.setattr(sc, "repos", lambda: {})
    assert sc.main(["--check"]) == 0
    assert "no data repository" in capsys.readouterr().err
