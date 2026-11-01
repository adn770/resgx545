# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""isa/gen.py: the committed tables are current, and a broken description is
refused with a message naming the file and the form."""
import pathlib
import subprocess
import sys

import tomllib

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import gen  # noqa: E402

GOOD = """
code = ["K_DST"]
[const]
U = "b(48) | b(29)"
[layout]
DST = "27:21 33:32 51"
[field]
F_DST = "DST(K_DST)"
[kind.PRED]
enum = ["", "p0 ", false, "p1 "]
[kind.SPARSE]
enum = { 3 = "x", 5 = "y" }
[kind.SEQ]
seq = [["", ".a"], ["", ".b", false, ".c"]]
[[form]]
pat = "{0}mov {1}, #{2}"
mask = "CLSM | m(58, 56)"
val = "cls(31) | b(58)"
fields = ["PRED 43:41", "dst=F_DST", "SEQ 55 54:53"]
dflt = "U"
op = "limm"
"""


def isa_from(tmp_path, text, order="order = 10\n"):
    """GOOD-style text split the way the repository keeps it: the definitions in
    kinds/a.toml, the forms in forms/a.toml, each form with its decode order."""
    defs, sep, forms = text.partition("[[form]]")
    for sub, body in (("kinds", defs), ("forms", sep + "\n" + order + forms if sep else "")):
        (tmp_path / "t" / sub).mkdir(parents=True, exist_ok=True)
        (tmp_path / "t" / sub / "a.toml").write_text(body)
    return gen.load("t", base=tmp_path, parts=["a"])


def test_committed_tables_are_current():
    r = subprocess.run([sys.executable, str(gen.HERE / "gen.py"), "--check"],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_a_description_loads(tmp_path):
    isa = isa_from(tmp_path, GOOD)
    (f,) = isa.forms
    assert f.mask == 0xFF00000000000000 and f.val == 0xFC00000000000000
    assert f.dflt == 1 << 48 | 1 << 29
    assert [(x.kind, x.chunks) for x in f.fields] == [
        ("PRED", [(41, 3)]), ("K_DST", [(21, 7), (32, 2), (51, 1)]), ("SEQ", [(55, 1), (53, 2)])]
    assert gen.names_of(isa.kinds["SPARSE"], "enum") == [None, None, None, "x", None, "y"]
    assert f.op == "limm" and [x.role for x in f.fields] == ["", "dst", ""]


def test_roles_and_ops_reach_rust_only(tmp_path):
    isa = isa_from(tmp_path, GOOD)
    c, rs = gen.gen_c(isa), gen.gen_rust(isa)
    assert 'op: "limm"' in rs and 'r: "dst"' in rs and 'r: ""' in rs
    assert "limm" not in c and "dst" not in c.replace("K_DST", "")


def test_outputs_name_every_kind(tmp_path):
    isa = isa_from(tmp_path, GOOD)
    c, rs = gen.gen_c(isa), gen.gen_rust(isa)
    # the enum is padded to the width of its widest field, 2^3
    assert 'PRED_T[8] = { "", "p0 ", NULL, "p1 ", NULL, NULL, NULL, NULL };' in c
    assert "{ &PRED, { { 41, 3 } } }" in c and "0xFF00000000000000ull" in c
    assert 'Enum(&[Some(""), Some("p0 "), None, Some("p1 ")])' in rs
    assert "Seq(&[(1, &[Some(\"\"), Some(\".a\")]), (2," in rs


@pytest.mark.parametrize("change, msg", [
    (("\"PRED 43:41\"", "\"NOPE 43:41\""), "unknown kind NOPE"),
    (("cls(31) | b(58)", "cls(31) | b(2)"), "val has bits outside mask"),
    (("\"SEQ 55 54:53\"", "\"SEQ 55 53:54\""), "bad bit range"),
    (("\"dst=F_DST\",", "\"dst=DSTX(K_DST)\","), "unknown layout DSTX"),
    (("{0}mov {1}, #{2}", "{0}mov {1}, #{3}"), "{3} has no field"),
    (("[kind.SPARSE]", "[kind.PRED2]\nenum = []\n[kind.U]"), "U defined twice"),
    (("\"dst=F_DST\"", "\"dst=F_DST\", \"dst=K_DST 9:0\""), "role dst twice"),
    (("op = \"limm\"", "op = \"no op\""), "bad op"),
])
def test_broken_descriptions_are_refused(tmp_path, change, msg):
    with pytest.raises(gen.DescError, match=msg.replace("{", r"\{").replace("}", r"\}")) as e:
        isa_from(tmp_path, GOOD.replace(*change))
    assert "a.toml" in str(e.value)


def test_seq_names_must_cover_their_width(tmp_path):
    isa = isa_from(tmp_path, GOOD.replace('["", ".b", false, ".c"]', '["", ".b", ".c"]'))
    with pytest.raises(gen.DescError, match="not a power of two"):
        gen.gen_c(isa)


FORM = """[[form]]
order = {o}
pat = "{p}"
mask = "CLSM"
val = "cls({c})"
"""


def test_forms_decode_in_their_order_whatever_file_holds_them(tmp_path):
    isa_from(tmp_path, GOOD)
    forms = tmp_path / "t" / "forms"
    (forms / "b.toml").write_text(FORM.format(o=5, p="first", c=1) + FORM.format(o=30, p="last", c=2))
    (forms / "c.toml").write_text(FORM.format(o=20, p="middle", c=3))
    isa = gen.load("t", base=tmp_path, parts=["a"])
    assert [f.pat for f in isa.forms] == ["first", "{0}mov {1}, #{2}", "middle", "last"]


def test_a_form_needs_an_order(tmp_path):
    with pytest.raises(gen.DescError, match="no order"):
        isa_from(tmp_path, GOOD, order="")


def test_two_forms_cannot_share_an_order(tmp_path):
    isa_from(tmp_path, GOOD)
    (tmp_path / "t" / "forms" / "b.toml").write_text(FORM.format(o=10, p="x", c=1))
    with pytest.raises(gen.DescError, match="order 10 twice"):
        gen.load("t", base=tmp_path, parts=["a"])


@pytest.mark.parametrize("name", ["usse", "pds"])
def test_the_descriptions_are_kinds_and_form_groups(name):
    """isa/<isa>/kinds/<family>.toml define; isa/<isa>/forms/<group>.toml hold forms only;
    nothing beside them."""
    d = gen.HERE / name
    assert not list(d.glob("*.toml"))
    assert sorted(p.stem for p in (d / "kinds").glob("*.toml")) == sorted(gen.ISAS[name]["parts"])
    for p in (d / "kinds").glob("*.toml"):
        assert "form" not in tomllib.loads(p.read_text()), p
    groups = list((d / "forms").glob("*.toml"))
    assert len(groups) > 5
    for p in groups:
        t = tomllib.loads(p.read_text())
        assert list(t) == ["form"] and all("order" in f for f in t["form"]), p
