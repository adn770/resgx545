# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""health.sh, deploy-tool.sh and run-table.sh in dry-run mode (SGX_DRY_RUN=1 prints the
commands instead of running them): hosts and paths come from the environment or local.env,
nothing about a machine is in the scripts, and no laptop is contacted."""
import os
import pathlib
import subprocess

import pytest

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SCRIPTS = {n: HERE / n for n in ("health.sh", "deploy-tool.sh", "run-table.sh")}


def clean_env(**extra):
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(("SGX_", "RESGX545_", "R2_"))}
    env["SGX_LOCAL_ENV"] = os.devnull
    env.update(extra)
    return env


def run(script, *args, **extra):
    return subprocess.run(["bash", str(SCRIPTS[script]), *args],
                          env=clean_env(SGX_DRY_RUN="1", **extra), capture_output=True,
                          text=True, timeout=30)


def test_scripts_are_valid_bash_and_executable():
    for p in SCRIPTS.values():
        assert os.access(p, os.X_OK), p
        subprocess.run(["bash", "-n", str(p)], check=True)


@pytest.mark.parametrize("script,args", [("health.sh", ()), ("deploy-tool.sh", ()),
                                         ("run-table.sh", ())])
def test_usage_without_arguments(script, args):
    r = run(script, *args)
    assert r.returncode == 2 and "usage" in r.stderr


# --- health.sh ---------------------------------------------------------------------------

def test_health_runs_the_named_tool_on_the_target():
    r = run("health.sh", "sgxfive-test-1138", SGX_TARGET_HOST="me@laptop",
            SGX_TARGET_SSH_OPTS="-o HostKeyAlias=box")
    assert r.returncode == 0, r.stderr
    assert "ssh -o BatchMode=yes -o ConnectTimeout=10 -o HostKeyAlias=box me@laptop" in r.stdout
    assert "~/sgxfive-test-1138 fill" in r.stdout and "~/sgxfive-test-1138 tri" in r.stdout
    for word in ("hold_recovery", "kpoke", "dmesg"):
        assert word in r.stdout


def test_health_defaults_to_the_example_host():
    assert "sgx-target" in run("health.sh", "sgxfive-test").stdout


# --- deploy-tool.sh ----------------------------------------------------------------------

def test_deploy_builds_on_the_target_and_names_the_tool():
    r = run("deploy-tool.sh", "1138", SGX_TARGET_HOST="me@laptop",
            SGX_TARGET_SSH_OPTS="-o HostKeyAlias=box")
    assert r.returncode == 0, r.stderr
    out = r.stdout
    assert "tar cf -" in out and "userspace/libsgxfive" in out and "include/uapi" in out
    assert "tools/gen_tri_progs.py" in out
    assert "-o HostKeyAlias=box me@laptop" in out
    assert "make -j2 build/sgxfive-test" in out
    assert "~/sgxfive-test-1138" in out
    assert out.count("sha256sum") >= 3          # the source here, the source and binary there


def test_deploy_rejects_a_name_with_a_slash():
    assert run("deploy-tool.sh", "a/b").returncode == 2


# --- run-table.sh ------------------------------------------------------------------------

def test_run_table_needs_the_kernel_commit():
    r = run("run-table.sh", "1138", "usse/branch")
    assert r.returncode != 0 and "RESGX545_KERNEL_COMMIT" in r.stderr


def test_run_table_runs_the_campaign_per_table(tmp_path):
    r = run("run-table.sh", "1138", "usse/branch", "isp/arith", RESGX545_KERNEL_COMMIT="abc123",
            SGX_TARGET_HOST="me@laptop", SGX_TARGET_SSH_OPTS="-o HostKeyAlias=box",
            RESGX545_DATA="/data", RUN_LOG_DIR=str(tmp_path))
    assert r.returncode == 0, r.stderr
    out = r.stdout
    assert out.count("tools/campaign/campaign.py") == 2
    assert "SGX_SWEEP_TOOL=./sgxfive-test-1138" in out
    assert "SGX_PROBE_TOOL=./sgxfive-test-1138" in out
    assert "RESGX545_KERNEL_COMMIT=abc123" in out
    assert "SGX_TARGET_HOST=me@laptop" in out
    assert "--target laptop" in out and "--repo data --data /data" in out
    assert "--datasets" in out
    assert "probes/usse/branch.toml" in out and "probes/isp/arith.toml" in out


def test_run_table_keeps_one_log_per_table(tmp_path):
    r = run("run-table.sh", "1138", "usse/branch", RESGX545_KERNEL_COMMIT="abc",
            RUN_LOG_DIR=str(tmp_path))
    assert r.returncode == 0
    assert "1138/usse-branch.log" in r.stdout


# --- the settings ------------------------------------------------------------------------

def test_the_example_names_the_run_settings_with_placeholders_only():
    text = (HERE / "local.env.example").read_text()
    for var in ("RESGX545_DATA", "RESGX545_DATA_PRIVATE", "RESGX545_UKERNEL", "R2_PREFIX",
                "RESGX545_CDV_LIBS", "RESGX545_GUARD_DIR"):
        assert var in text, var
    assert "/Users/" not in text and "/home/" not in text
