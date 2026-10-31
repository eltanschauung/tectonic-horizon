#!/usr/bin/env python3
"""Stage and validate the native mod using a local Horizon checkout's Rust environment."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[1]


def run(command, **kwargs):
    return subprocess.run([str(arg) for arg in command], check=True, **kwargs)


def environment(horizon):
    wrapper = horizon / "tools/fork.py"
    if wrapper.is_file():
        spec = importlib.util.spec_from_file_location("horizon_fork", wrapper)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        env, cargo = module.build_environment()
    else:
        env, cargo = os.environ.copy(), "cargo"
    env.pop("CARGO_TARGET_DIR", None)
    env["TECTONIC_HORIZON_CONFIG"] = str(ROOT / "target/test-home/config.json")
    env["HORIZON_HOME"] = str(ROOT / "target/test-home/horizon")
    env["XDG_DATA_HOME"] = str(ROOT / "target/test-home/data")
    env["XDG_CONFIG_HOME"] = str(ROOT / "target/test-home/config")
    return env, cargo


def stage(horizon, env, cargo):
    compat = json.loads((ROOT / "compatibility.json").read_text())
    original = ROOT / "target/original"
    pin = compat["horizon_revision"]
    if not original.exists():
        original.mkdir(parents=True)
        process = subprocess.Popen(["git", "-C", str(horizon), "archive", pin], stdout=subprocess.PIPE)
        with tarfile.open(fileobj=process.stdout, mode="r|") as archive:
            for member in archive:
                archive.extract(member, original, filter="data")
        process.stdout.close()
        if process.wait():
            raise RuntimeError("Horizon source export failed")
        for file in original.rglob("*"):
            if file.is_symlink():
                content = file.read_bytes()
                file.unlink()
                file.write_bytes(content)
        (original / ".horizon-revision").write_text(pin + "\n")
    for path, expected in compat["source_sha256"].items():
        if hashlib.sha256((original / path).read_bytes()).hexdigest() != expected:
            raise RuntimeError(f"pinned source hash mismatch: {path}")
    mixins = ROOT / "target/mixins-engine"
    if not mixins.exists():
        run(["git", "clone", "https://github.com/horizon-rust/horizon-mixins", mixins])
        run(["git", "-C", mixins, "checkout", "--detach", compat["horizon_mixins_revision"]])
    revision = subprocess.check_output(["git", "-C", str(mixins), "rev-parse", "HEAD"], text=True).strip()
    if revision != compat["horizon_mixins_revision"]:
        raise RuntimeError("mixin engine revision mismatch")
    run([cargo, "build", "--locked", "--manifest-path", mixins / "Cargo.toml", "-p", "horizon-mixins-cli"], env=env)
    cli = mixins / "target/debug/horizon-mixins"
    common = ["--workspace", original, "--mods", ROOT / "mixins"]
    run([cli, "plan", *common, "--out", ROOT / "target/plan.json"], env=env)
    run([cli, "apply", *common, "--out", ROOT / "target/modded"], env=env)
    return ROOT / "target/modded"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["test", "stage", "check", "build"])
    parser.add_argument("--horizon", type=Path, default=ROOT.parent / "horizon")
    parser.add_argument("--jobs", type=int, default=2)
    args = parser.parse_args()
    env, cargo = environment(args.horizon.resolve())
    if args.action == "test":
        run([cargo, "fmt", "--all", "--check"], cwd=ROOT, env=env)
        run([cargo, "clippy", "--all-targets", "--locked", "--", "-D", "warnings"], cwd=ROOT, env=env)
        run([cargo, "test", "--locked"], cwd=ROOT, env=env)
        return
    output = stage(args.horizon.resolve(), env, cargo)
    if args.action == "stage":
        return
    target = ROOT / "target/horizon-cargo"
    command = [cargo, args.action, "--locked", "--manifest-path", output / "Cargo.toml",
               "--target-dir", target, "-j", args.jobs, "-p", "horizon-client", "--bin", "horizon-client"]
    if args.action == "build":
        command.extend(["--profile", "fast"])
    run(command, env=env)
    print(f"Native game: {target}/fast/horizon-client")


if __name__ == "__main__":
    main()
