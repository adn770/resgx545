# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""guard.py on synthetic trees: a fake confidential tree, a fake public tree and planted
tokens built in tmp, so no real data is needed and none appears here."""
import hashlib
import pathlib
import subprocess

import pytest

import guard

SECRET = "zorptokalpha"          # only in the fake confidential tree
SHARED = "sharedtokenbeta"       # in the fake confidential and the fake public tree
OLD = "ancientnamegamma"
PATTERN = r"forbiddenwordd\w*"


def write(path: pathlib.Path, text: str | bytes) -> pathlib.Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text if isinstance(text, bytes) else text.encode())
    return path


def digest(word: str) -> str:
    return hashlib.sha256(word.encode()).hexdigest()


@pytest.fixture
def world(tmp_path):
    """Fake trees, a guard directory and the Rules loaded from them."""
    conf = tmp_path / "conf"
    write(conf / "a.c", f"int {SECRET}; int {SHARED}; int commonname;")
    pub = tmp_path / "pub"
    write(pub / "x" / "b.c", f"int {SHARED}; int commonname;")
    gdir = tmp_path / "guard"
    write(gdir / "allowed.txt", "# reviewed\nallowedword otherallowed\n")
    write(gdir / "patterns.txt", f"# private\nd1\t{PATTERN}\nfork\toraclelike\n")
    write(gdir / "oldnames.toml", f'[rename]\n{OLD} = "newname"\n')
    write(gdir / "glossary-reviewed.txt", "# reviewed glossary tokens\n")
    write(gdir / "refs.local.toml",
          f'confidential = "{conf}"\npublic_root = "{tmp_path}"\npublic = ["pub"]\n'
          'rogue = []\nlibs = []\n')
    return tmp_path


def rules(world, terms=()):
    return guard.load_rules(world / "guard", terms=terms)


def repo(path: pathlib.Path) -> pathlib.Path:
    path.mkdir(parents=True, exist_ok=True)
    git(path, "init", "-q")
    git(path, "config", "user.name", "t")
    git(path, "config", "user.email", "t@example.com")
    return path


def git(path, *args):
    return subprocess.run(["git", "-C", str(path), *args], capture_output=True, text=True,
                          check=True).stdout


def commit(path, files: dict, message="topic: change"):
    for name, text in files.items():
        write(path / name, text)
    git(path, "add", "-A")
    git(path, "commit", "-q", "-m", message)


# --- the data ----------------------------------------------------------------------------

def test_forbidden_is_confidential_minus_public(world):
    r = rules(world)
    assert SECRET.encode() in r.forbidden
    assert SHARED.encode() not in r.forbidden
    assert b"commonname" not in r.forbidden


def test_another_casing_of_a_public_token_is_not_forbidden(world):
    write(world / "conf" / "case.c", "#define CASEWORDDELTA 1\nint Mixedcaseword;\n")
    write(world / "pub" / "x" / "case.c", "int casewordDelta; int MIXEDCASEWORD;\n")
    r = rules(world)
    assert b"CASEWORDDELTA" not in r.forbidden
    assert b"Mixedcaseword" not in r.forbidden
    assert SECRET.encode() in r.forbidden and SECRET.upper().encode() not in r.forbidden


def test_one_letter_and_digits_is_not_forbidden(world):
    write(world / "conf" / "num.c", "int n1100; int x0101; int _1234; int nn1100; int n11a0;\n")
    r = rules(world)
    assert {b"n1100", b"x0101", b"_1234"}.isdisjoint(r.forbidden)
    assert {b"nn1100", b"n11a0"} <= r.forbidden


def test_allowed_words_read_from_the_list(world):
    r = rules(world)
    assert {"allowedword", "otherallowed"} <= r.allowed


def test_missing_guard_dir_raises(tmp_path):
    with pytest.raises(guard.GuardMissing):
        guard.load_rules(tmp_path / "nowhere")


def test_missing_confidential_tree_raises(world):
    write(world / "guard" / "refs.local.toml",
          f'confidential = "{world}/absent"\npublic_root = "{world}"\npublic = []\n')
    with pytest.raises(guard.GuardMissing):
        guard.load_rules(world / "guard")


def test_missing_refs_file_raises(world):
    (world / "guard" / "refs.local.toml").unlink()
    with pytest.raises(guard.GuardMissing):
        guard.load_rules(world / "guard")


# --- scanning ----------------------------------------------------------------------------

def test_planted_token_is_found(world):
    found = guard.scan_blob("f.md", f"we use {SECRET} here\n".encode(), rules(world))
    assert [f.category for f in found] == ["token"]


def test_allowed_token_passes(world):
    r = rules(world)
    r.allowed.add(SECRET)
    assert guard.scan_blob("f.md", f"we use {SECRET}\n".encode(), r) == []


def test_shared_token_passes(world):
    assert guard.scan_blob("f.md", f"{SHARED} commonname".encode(), rules(world)) == []


def test_token_inside_a_longer_name_is_not_a_hit(world):
    assert guard.scan_blob("f.md", f"x{SECRET}y {SECRET}1".encode(), rules(world)) == []


def test_pattern_and_oldname_found_in_text(world):
    text = f"line one\nforbiddenwordd here\nand {OLD}\n".encode()
    cats = {(f.category, f.line) for f in guard.scan_blob("f.md", text, rules(world))}
    assert cats == {("pattern-d1", 2), ("oldname", 3)}


def test_fork_pattern_only_in_fork_scope(world):
    r = rules(world)
    assert guard.scan_blob("f.md", b"an oraclelike thing", r) == []
    found = guard.scan_blob("f.md", b"an oraclelike thing", r, fork=True)
    assert [f.category for f in found] == ["pattern-fork"]


def test_binary_blob_skips_text_rules_but_not_tokens(world):
    data = b"\0\0 forbiddenwordd " + SECRET.encode() + b" \0"
    assert [f.category for f in guard.scan_blob("f.bin", data, rules(world))] == ["token"]


def test_message_scan(world):
    found = guard.scan_message(f"topic: x\n\n{OLD} and forbiddenwordd", rules(world))
    assert {f.category for f in found} == {"oldname", "pattern-d1"}


def test_output_never_carries_the_matched_text(world):
    f = guard.scan_blob("f.md", f"{SECRET} forbiddenwordd {OLD}".encode(), rules(world))
    shown = "\n".join(x.render() for x in f)
    for word in (SECRET, "forbiddenwordd", OLD):
        assert word not in shown
    assert digest(SECRET)[:8] in shown
    assert SECRET in "\n".join(x.render(show=True) for x in f)


# --- the glossary hole -------------------------------------------------------------------

ROW = {"term": SECRET, "name": f"PRE_{SECRET}.FIELD"}


def test_glossary_term_does_not_launder_an_unreviewed_token(world):
    """A new glossary term whose spelling is confidential-only must not allow the token."""
    r = rules(world, terms=guard.glossary_tokens([ROW]))
    assert SECRET not in r.allowed
    found = guard.scan_blob("glossary/x.toml", f'term = "{SECRET}"'.encode(), r)
    assert [f.category for f in found] == ["token"]


def test_reviewed_glossary_token_is_allowed(world):
    write(world / "guard" / "glossary-reviewed.txt", f"{digest(SECRET)}\n")
    r = rules(world, terms=guard.glossary_tokens([ROW]))
    assert guard.scan_blob("glossary/x.toml", f'term = "{SECRET}"'.encode(), r) == []


def test_reviewed_hash_allows_a_token_that_is_no_term(world):
    write(world / "guard" / "glossary-reviewed.txt", f"{digest(SECRET)}\n")
    assert guard.scan_blob("f.md", SECRET.encode(), rules(world, terms=())) == []


def test_glossary_token_that_is_public_needs_no_review(world):
    r = rules(world, terms=guard.glossary_tokens([{"term": SHARED, "name": SHARED}]))
    assert guard.scan_blob("g.toml", SHARED.encode(), r) == []


def test_unreviewed_glossary_tokens_are_listed(world):
    r = rules(world, terms=guard.glossary_tokens([ROW]))
    assert digest(SECRET) in r.unreviewed
    write(world / "guard" / "glossary-reviewed.txt", f"{digest(SECRET)}\n")
    assert rules(world, terms=guard.glossary_tokens([ROW])).unreviewed == set()


def test_glossary_tokens_split_name_parts():
    toks = guard.glossary_tokens([{"term": "ONE_term", "name": "AAAA.BBBB.cc"}])
    assert {"ONE_term", "AAAA", "BBBB", "cc"} <= toks


# --- the git modes -----------------------------------------------------------------------

def test_tree_mode_reads_tracked_files_only(world):
    r = repo(world / "r")
    commit(r, {"ok.md": "fine\n"})
    commit(r, {"bad.md": f"{SECRET}\n"})
    write(r / "untracked.md", SECRET)                  # never added: not scanned
    assert [(f.where, f.category) for f in guard.scan_tree(r, rules(world))] == [
        ("bad.md", "token")]


def test_staged_mode_reads_index_blobs(world):
    r = repo(world / "r")
    commit(r, {"a.md": "fine\n"})
    write(r / "a.md", f"{SECRET}\n")
    git(r, "add", "a.md")
    write(r / "a.md", "fine again\n")                  # the working tree is clean, the index is not
    assert [f.category for f in guard.scan_staged(r, rules(world))] == ["token"]


def test_staged_mode_nothing_staged(world):
    r = repo(world / "r")
    commit(r, {"a.md": "fine\n"})
    assert guard.scan_staged(r, rules(world)) == []


def test_history_finds_a_token_deleted_later(world):
    r = repo(world / "r")
    commit(r, {"a.md": f"{SECRET}\n"}, "topic: first")
    commit(r, {"a.md": "clean\n"}, "topic: second")
    found = guard.scan_history(r, rules(world))
    assert [f.category for f in found] == ["token"]
    assert found[0].commit and len(found[0].commit) >= 7


def test_history_scans_messages(world):
    r = repo(world / "r")
    commit(r, {"a.md": "clean\n"}, f"topic: {OLD} appears")
    found = guard.scan_history(r, rules(world))
    assert [f.category for f in found] == ["oldname"]
    assert found[0].where == "message"


def test_history_range_excludes_the_base(world):
    r = repo(world / "r")
    commit(r, {"a.md": f"{SECRET}\n"}, "topic: base")
    git(r, "tag", "base")
    commit(r, {"b.md": "clean\n"}, "topic: new")
    assert guard.scan_history(r, rules(world), base="base") == []
    assert guard.scan_history(r, rules(world)) != []


def test_history_ref_limits_the_scan_to_one_branch(world):
    r = repo(world / "r")
    commit(r, {"a.md": "clean\n"})
    git(r, "checkout", "-q", "-b", "other")
    commit(r, {"b.md": f"{SECRET}\n"})
    git(r, "checkout", "-q", "-")
    assert guard.scan_history(r, rules(world)) != []
    assert guard.scan_history(r, rules(world), ref="HEAD") == []
    assert guard.scan_history(r, rules(world), ref="other") != []


def test_history_clean(world):
    r = repo(world / "r")
    commit(r, {"a.md": "clean\n"})
    assert guard.scan_history(r, rules(world)) == []


# --- the command line: fail, do not skip -------------------------------------------------

def test_cli_absent_data_fails_when_required(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("RESGX545_GUARD_DIR", str(tmp_path / "nowhere"))
    monkeypatch.setenv("RESGX545_REQUIRE_GUARD", "1")
    assert guard.main(["--tree", str(repo(tmp_path / "r"))]) == 2
    assert "ABSENT" in capsys.readouterr().err


def test_cli_absent_data_is_reported_loudly_when_not_required(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("RESGX545_GUARD_DIR", str(tmp_path / "nowhere"))
    monkeypatch.delenv("RESGX545_REQUIRE_GUARD", raising=False)
    assert guard.main(["--tree", str(repo(tmp_path / "r"))]) == 0
    assert "NOT CHECKED" in capsys.readouterr().err


def test_cli_finding_exits_one(world, monkeypatch, capsys):
    monkeypatch.setenv("RESGX545_GUARD_DIR", str(world / "guard"))
    r = repo(world / "r")
    commit(r, {"bad.md": SECRET})
    assert guard.main(["--tree", str(r), "--no-glossary"]) == 1
    out = capsys.readouterr()
    assert SECRET not in out.out + out.err


def test_cli_clean_exits_zero(world, monkeypatch):
    monkeypatch.setenv("RESGX545_GUARD_DIR", str(world / "guard"))
    r = repo(world / "r")
    commit(r, {"ok.md": "fine"})
    assert guard.main(["--tree", str(r), "--no-glossary"]) == 0


def test_cli_message_mode(world, monkeypatch, tmp_path):
    monkeypatch.setenv("RESGX545_GUARD_DIR", str(world / "guard"))
    msg = write(tmp_path / "msg", f"topic: x\n\n{OLD}\n")
    assert guard.main(["--message", str(msg), "--no-glossary"]) == 1
    msg = write(tmp_path / "msg", "topic: x\n")
    assert guard.main(["--message", str(msg), "--no-glossary"]) == 0


# --- the real thing ----------------------------------------------------------------------

def test_real_guard_data_present_when_required(monkeypatch):
    """With RESGX545_REQUIRE_GUARD=1 a missing private directory is a failure, not a skip."""
    try:
        guard.load_rules(guard.guard_dir(), terms=())
    except guard.GuardMissing as e:
        if guard.required():
            pytest.fail(f"guard data absent: {e}")
        pytest.skip(f"guard data absent: {e}")


def test_this_tool_does_not_match_the_private_patterns():
    """The guard's own text (code, tests, example config) matches none of the everywhere
    patterns (scope d1) and holds no confidential-only token."""
    try:
        r = guard.load_rules(guard.guard_dir())
    except guard.GuardMissing as e:
        if guard.required():
            pytest.fail(f"guard data absent: {e}")
        pytest.skip(f"guard data absent: {e}")
    here = pathlib.Path(__file__).parent
    bad = []
    for name in ("guard.py", "test_guard.py", "refs.local.toml.example"):
        bad += [(name, f.category) for f in guard.scan_blob(name, (here / name).read_bytes(), r)]
    assert bad == []


def test_real_tree_is_clean():
    """The tracked tree of this repository passes the guard (needs the private data)."""
    try:
        r = guard.load_rules(guard.guard_dir())
    except guard.GuardMissing as e:
        if guard.required():
            pytest.fail(f"guard data absent: {e}")
        pytest.skip(f"guard data absent: {e}")
    found = guard.scan_tree(guard.ROOT, r)
    assert found == [], [f.render() for f in found[:40]]
