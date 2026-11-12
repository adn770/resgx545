# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""tools/wrapmd.py reflows over-long Markdown prose and leaves everything else alone."""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import wrapmd  # noqa: E402

W = "word " * 30  # 150 columns


def fix(text, limit=100):
    return wrapmd.wrap_text(text, limit)


def test_paragraph_is_wrapped_to_the_limit():
    out = fix(W.strip() + "\n")
    assert all(len(l) <= 100 for l in out.splitlines())
    assert " ".join(out.split()) == W.strip()


def test_list_item_continuation_is_indented_to_the_text():
    out = fix("  - " + W.strip() + "\n").splitlines()
    assert len(out) > 1 and out[0].startswith("  - ")
    assert all(l.startswith("    ") and not l.startswith("     ") for l in out[1:])
    out = fix("10. " + W.strip() + "\n").splitlines()
    assert all(l.startswith("    ") for l in out[1:])


def test_plain_indent_and_blockquote_are_kept():
    out = fix("  " + W.strip() + "\n").splitlines()
    assert all(l.startswith("  ") for l in out)
    out = fix("> " + W.strip() + "\n").splitlines()
    assert all(l.startswith("> ") for l in out)


def test_untouched_blocks():
    long = "x " * 80
    for text in (
        "```\n" + long + "\n```\n",
        "~~~\n" + long + "\n~~~\n",
        "para\n\n    " + long + "\n",
        "| " + long + "|\n",
        "# " + long + "\n",
        "+++\ntitle = '" + long + "'\n+++\n\n" + "text\n",
        "---\ntitle: " + long + "\n---\n",
        "<div>" + long + "</div>\n",
        "[ref]: http://example.com " + long + "\n",
    ):
        assert fix(text) == text, text


def test_long_word_is_kept_whole():
    text = "see " + "u" * 120 + " end\n"
    out = fix(text)
    assert "u" * 120 in out.splitlines()[0] or "u" * 120 in out.splitlines()[1]
    assert fix(out) == out


def test_break_never_creates_a_list_marker():
    text = "a" * 96 + " - b c\n"
    out = fix(text)
    assert not any(l.lstrip().startswith("- ") for l in out.splitlines()[1:])


def test_idempotent_and_final_newline_kept():
    once = fix("- " + W + "\n\n" + W + "\n")
    assert fix(once) == once and once.endswith("\n")


def test_check_lists_long_lines(tmp_path):
    f = tmp_path / "a.md"
    f.write_text(W + "\n")
    r = subprocess.run([sys.executable, str(ROOT / "tools/wrapmd.py"), "--check", str(f)],
                       capture_output=True, text=True)
    assert r.returncode == 1 and "a.md:1" in r.stdout
    r = subprocess.run([sys.executable, str(ROOT / "tools/wrapmd.py"), "--fix", str(f)])
    assert r.returncode == 0
    r = subprocess.run([sys.executable, str(ROOT / "tools/wrapmd.py"), "--check", str(f)])
    assert r.returncode == 0


def test_checked_repo_markdown_passes_unchanged():
    for name in ("HACKING.md", "tools/README.md", "doc/roadmap.md"):
        t = (ROOT / name).read_text()
        assert wrapmd.wrap_text(t, 100) == t, name
