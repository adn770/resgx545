# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""fwsim's inputs and output rule, without the firmware: the seeds (every row cites a record),
the kept snapshots' parser and reset values, and the output path rule (T1)."""
import pathlib
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fwsim  # noqa: E402
import kept  # noqa: E402


def test_the_landed_seeds_load_and_each_cites_a_record():
    d = fwsim.load_seeds()
    assert {r["name"]: r["value"] for r in d["seed"]} == {"CORE_ID": 0x01150000, "CORE_REVISION": 0x0001000D}
    assert [(r["reg"], r["kind"], r["value"]) for r in d["rule"]] == [
        (0x0B14, "count_ticks", 0x00010003), (0x012C, "idle_until_event", 0x20000000)]
    assert d["carry"]["pclink"] == 0x98 and d["events"]["tick_tim"] == 0x01061A70


@pytest.mark.parametrize("cite", ["", "the laptop", "E12", "E12345", "XE007", "Q290"])
def test_a_seed_row_without_an_e_number_is_refused_at_load(tmp_path, cite):
    text = fwsim.SEEDS.read_text().replace('cite = "E007"', f'cite = "{cite}"', 1)
    p = tmp_path / "seeds.toml"
    p.write_text(text)
    with pytest.raises(fwsim.Refused, match="cites no record"):
        fwsim.load_seeds(p)


def test_a_rule_the_simulator_has_not_landed_is_refused(tmp_path):
    p = tmp_path / "seeds.toml"
    p.write_text(fwsim.SEEDS.read_text().replace('kind = "count_ticks"', 'kind = "count_all"'))
    with pytest.raises(fwsim.Refused, match="no landed rule"):
        fwsim.load_seeds(p)


def test_the_idle_event_status_rule_is_refused_on_another_register(tmp_path):
    p = tmp_path / "seeds.toml"
    p.write_text(fwsim.SEEDS.read_text().replace("reg = 0x012c", "reg = 0x0118"))
    with pytest.raises(fwsim.Refused, match="no landed rule"):
        fwsim.load_seeds(p)


def test_the_snapshot_parser_resolves_repeats_and_drops_skipped_registers():
    text = ("#### before load\nreg 0x0000 0x00000001\nreg 0x0114 skip\nreg 0x0b14 0x00010000\n"
            "#### booted\nhostctl 0x30 0x000000b3\nreg 0x0000 =\nreg 0x0b14 0x000100b6\n"
            "#### read 1 123.4\nreg 0x0000 0x00000009\n")
    snaps = kept.snapshots(text)
    assert [t for t, _ in snaps] == ["before load", "booted"]
    assert snaps[0][1]["reg"] == {0x0: 1, 0xB14: 0x10000}
    assert snaps[1][1]["reg"] == {0x0: 1, 0xB14: 0x100B6} and snaps[1][1]["hostctl"] == {0x30: 0xB3}


@pytest.mark.skipif(kept.data_dir() is None, reason="no resgx545-data")
def test_the_reset_values_leave_out_every_register_a_kept_snapshot_shows_moving():
    """E009's four moving values and the registers the boot or the host moves are not resets."""
    r = kept.stable_resets(kept.data_dir())
    for off in (0x0144, 0x0ACC, 0x0B14, 0x012C, 0x0118, 0x0A68, 0x0A6C):
        assert off not in r, hex(off)
    assert r[0x001C] == 0x01150000 and r[0x0020] == 0x0001000D
    assert len(r) > 150


def test_outputs_go_only_under_the_private_fwsim_directory(tmp_path):
    private = tmp_path / "p"
    (private / "firmware" / "fwsim").mkdir(parents=True)
    (private / "render").mkdir()
    ok = fwsim.checked_out(private / "firmware" / "fwsim" / "m1-idle", private)
    assert ok == (private / "firmware" / "fwsim" / "m1-idle").resolve()
    (private / "firmware" / "fwsim" / "out").symlink_to(private / "render")
    for bad in (private / "render" / "x", private / "firmware" / "x", private / "firmware" / "fwsim",
                private / "firmware" / "fwsim" / ".." / "x", tmp_path / "x",
                private / "firmware" / "fwsim" / "out" / "x"):
        with pytest.raises(fwsim.Refused):
            fwsim.checked_out(bad, private)
