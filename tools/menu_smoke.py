#!/usr/bin/env python3
"""Verify the mod's actual game-menu row in an isolated virtual display."""
import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version_dir", type=Path)
    args = parser.parse_args()
    version = args.version_dir.resolve()
    resources = next((version / ".local/horizon-client").glob("*/worldgen/world_presets.json")).parent.parent
    with tempfile.TemporaryDirectory(prefix="tectonic-menu-") as temporary:
        work = Path(temporary)
        socket = work / "control.sock"
        env = os.environ.copy()
        for key in ("WAYLAND_DISPLAY", "HORIZON_CONTROL"):
            env.pop(key, None)
        for key in ("HORIZON_HOME", "HORIZON_LAUNCHER_HOME", "XDG_DATA_HOME", "XDG_CONFIG_HOME", "XDG_RUNTIME_DIR"):
            folder = work / key.lower()
            folder.mkdir(mode=0o700)
            env[key] = str(folder)
        env.update(HORIZON_NO_AUDIO="1", HORIZON_NO_DISCORD="1", HORIZON_TELEMETRY_URL="off", WINIT_UNIX_BACKEND="x11")
        lavapipe = Path("/usr/share/vulkan/icd.d/lvp_icd.json")
        if lavapipe.exists():
            env["VK_ICD_FILENAMES"] = str(lavapipe)
        game = subprocess.Popen(["xvfb-run", "-a", "-s", "-screen 0 1280x720x24", version / "horizon-client",
            "--resources", resources, "--game-dir", work, "--control-socket", socket], cwd=work, env=env,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        try:
            deadline = time.monotonic() + 90
            while not socket.exists():
                if game.poll() is not None:
                    raise RuntimeError(f"isolated game exited: {game.returncode}")
                if time.monotonic() > deadline:
                    raise RuntimeError("isolated game did not open its control socket")
                time.sleep(0.25)

            def control(*words):
                reply = subprocess.run([version / "horizon-ctl", "--socket", socket, *words],
                    cwd=work, env=env, check=True, capture_output=True, text=True, timeout=30)
                return json.loads(reply.stdout.strip().splitlines()[-1])

            control("options", "mods")
            tree = control("ui")
            labels = [w.get("label", "") for w in tree.get("widgets", [])]
            found = [label for label in labels if "Tectonic-Horizon" in label]
            assert found, f"native mod row missing from actual UI: {labels}"
            out = ROOT / "target"
            out.mkdir(exist_ok=True)
            (out / "menu-ui.json").write_text(json.dumps(tree, indent=2) + "\n")
            control("screenshot", str(out / "menu.png"))
            print(json.dumps({"menu_entry": found, "screenshot": str(out / "menu.png")}, indent=2))
        finally:
            if game.poll() is None:
                os.killpg(game.pid, signal.SIGTERM)
                game.wait(timeout=15)


if __name__ == "__main__":
    main()
