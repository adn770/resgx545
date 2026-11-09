# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""check_refs.py: a section reference (`doc.md §N`) names a document the tree holds and, when
that document numbers its headings, a section it has."""
import pathlib
import subprocess

import check_refs


def tree(tmp_path, files: dict) -> list[pathlib.Path]:
    out = []
    for name, text in files.items():
        p = tmp_path / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
        out.append(p)
    return out


def test_reference_to_an_existing_section_passes(tmp_path):
    fs = tree(tmp_path, {"doc/a.md": "# 1. One\n\n## 1.2 Sub\n", "doc/b.md": "see a.md §1.2\n"})
    assert check_refs.check(tmp_path, fs) == []


def test_reference_to_an_absent_document_is_a_problem(tmp_path):
    fs = tree(tmp_path, {"doc/b.md": "see nowhere.md §1\n"})
    (problem,) = check_refs.check(tmp_path, fs)
    assert "doc/b.md:1" in problem and "absent document" in problem


def test_reference_to_an_absent_section_is_a_problem(tmp_path):
    fs = tree(tmp_path, {"doc/a.md": "# 1. One\n", "doc/b.md": "see a.md §9\n"})
    (problem,) = check_refs.check(tmp_path, fs)
    assert "doc/b.md:1" in problem and "absent section" in problem


def test_section_lists_and_ranges_are_all_checked(tmp_path):
    fs = tree(tmp_path, {"doc/a.md": "# 1. One\n# 2. Two\n", "doc/b.md": "a.md §1, §2-§3\n"})
    (problem,) = check_refs.check(tmp_path, fs)
    assert "§3" in problem


def test_a_document_without_numbered_headings_accepts_any_section(tmp_path):
    fs = tree(tmp_path, {"doc/a.md": "# Words\n", "doc/b.md": "see a.md §4\n"})
    assert check_refs.check(tmp_path, fs) == []


def test_short_spec_names_resolve(tmp_path):
    fs = tree(tmp_path, {"doc/specs/transfer.md": "# 4. Four\n", "doc/x.md": "transfer §4\n",
                         "doc/y.md": "transfer §5\n"})
    problems = check_refs.check(tmp_path, fs)
    assert len(problems) == 1 and "doc/y.md" in problems[0]


def test_binary_files_are_skipped(tmp_path):
    p = tmp_path / "x.bin"
    p.write_bytes(b"\0\0 nowhere.md " + "§1".encode())
    assert check_refs.check(tmp_path, [p]) == []


def test_the_tracked_tree_passes():
    """This repository's own references hold."""
    root = check_refs.ROOT
    files = check_refs.tracked(root)
    assert check_refs.check(root, files) == []


def test_main_reports_and_exits_nonzero(tmp_path, capsys):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / "b.md").write_text("see nowhere.md §1\n")
    subprocess.run(["git", "-C", str(tmp_path), "add", "b.md"], check=True)
    assert check_refs.main(["--check", str(tmp_path)]) == 1
    assert "b.md:1" in capsys.readouterr().out
