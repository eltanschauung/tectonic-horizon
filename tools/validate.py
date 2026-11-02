#!/usr/bin/env python3
"""Compile the real patched world generator, then exercise it without writing worlds."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import desktop

ROOT = desktop.ROOT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--horizon", type=Path, default=ROOT.parent / "horizon")
    args = parser.parse_args()
    horizon = args.horizon.resolve()
    env, cargo = desktop.environment(horizon)
    candidates = list((horizon / ".local/horizon-client").glob("*/worldgen/world_presets.json"))
    if not candidates:
        candidates = list((Path.home()/".local/share/horizon-launcher/fork-versions").glob("*/.local/horizon-client/*/worldgen/world_presets.json"))
    if not candidates:
        raise SystemExit("Prepared resources are required for actual worldgen validation")
    env["HORIZON_RESOURCES"] = str(candidates[0].parent.parent)
    probe = ROOT / "target/probe"
    probe.mkdir(parents=True, exist_ok=True)
    stage = ROOT / "target/modded"
    manifest = ('[package]\nname="tectonic-worldgen-probe"\nversion="0.1.0"\nedition="2024"\n'
                '[dependencies]\nserde_json="=1.0.151"\n'
                f'horizon-world={{path={json.dumps(str(stage / "crates/horizon-world"))}}}\n'
                f'horizon-core={{path={json.dumps(str(stage / "crates/horizon-core"))}}}\n'
                '[[bin]]\nname="tectonic-worldgen-probe"\npath="probe.rs"\n')
    (probe / "Cargo.toml").write_text(manifest)
    shutil.copy2(ROOT / "tools/probe.rs", probe / "probe.rs")
    command = [cargo, "run", "--manifest-path", probe / "Cargo.toml", "--target-dir", Path(env["CARGO_TARGET_DIR"]), "--profile", "dev", "-j", "2"]
    config = ROOT / "target/test-home/config.json"
    config.parent.mkdir(parents=True, exist_ok=True)
    results = {}
    try:
        for name, content in [("default", {}), ("tall", {"global_terrain":{"increased_height":True},"islands":{"enabled":False}}),
                              ("disabled", {"general":{"mod_enabled":False}})]:
            config.write_text(json.dumps(content) + "\n")
            env.pop("TECTONIC_TEST_TALL", None)
            env.pop("TECTONIC_TEST_DISABLED", None)
            if name == "tall": env["TECTONIC_TEST_TALL"] = "1"
            if name == "disabled": env["TECTONIC_TEST_DISABLED"] = "1"
            run = desktop.run(command, env=env, stdout=subprocess.PIPE, text=True)
            results[name] = json.loads(run.stdout.splitlines()[-1])
            print(name, results[name], flush=True)
        assert results["default"]["terrain"] != results["disabled"]["terrain"], "mod must change actual terrain"
        assert results["default"]["other_dimensions"] == results["disabled"]["other_dimensions"] == results["tall"]["other_dimensions"], "Nether/End terrain must remain identical"
        (ROOT/"target/validation.json").write_text(json.dumps(results, indent=2) + "\n")
    finally:
        config.write_text("{}\n")


if __name__ == "__main__":
    main()
