#!/usr/bin/env python3
"""Write a reproducible source-only Horizon native-mod archive."""
import hashlib
import json
from pathlib import Path
import tomllib
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    compat = json.loads((ROOT / "compatibility.json").read_text())
    bundle = ROOT / "mixins/tectonic_horizon"
    mixin = tomllib.loads((bundle / "horizon-mixin.toml").read_text())
    if mixin["compatibility"]["horizon_revision"] != compat["horizon_revision"]:
        raise SystemExit("manifest and compatibility revision mismatch")
    manifest = {"schema": 1, "id": mixin["mod"]["id"], "version": mixin["mod"]["version"],
                "game": "26.3", "horizon": compat["horizon_revision"], "mixins": compat["horizon_mixins_revision"]}
    files = {"horizon-native.json": (json.dumps(manifest, indent=2) + "\n").encode()}
    for file in sorted(bundle.iterdir()):
        if file.is_file() and file.suffix in (".rs", ".toml"):
            files[file.relative_to(ROOT).as_posix()] = file.read_bytes()
    output = ROOT / "target" / f'{manifest["id"]}-{manifest["version"]}.hnmod'
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in sorted(files.items()):
            entry = zipfile.ZipInfo(name, (2026, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, content)
    print(json.dumps({"file": str(output), "sha256": hashlib.sha256(output.read_bytes()).hexdigest()}, indent=2))


if __name__ == "__main__":
    main()
