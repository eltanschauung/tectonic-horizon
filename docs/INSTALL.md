# Build and install

Tectonic-Horizon is an independent native source mod, not a fork or a Java mod.
The README intentionally follows the original project's short README.

The tested game is the `eltanschauung/horizon` fork at the exact commit recorded
in `compatibility.json`. The native bundle is pinned because it patches world
generation internals. It does not claim the stable client hook API.

On the desktop, with Horizon beside this repository:

```sh
python3 tools/desktop.py test
python3 tools/desktop.py stage
python3 tools/validate.py
python3 tools/desktop.py build
python3 tools/package.py
```

The helper uses Horizon's `tools/fork.py` to find its Rust toolchain and cache.
On another installation, put Rust/Cargo on PATH. Staging exports the committed
Horizon revision to `target/original` and applies the bundle to `target/modded`.
It never patches the source checkout. `validate.py` requires your own prepared
Minecraft resources and generates chunks in memory, with isolated config/data
homes. No accounts, saves or worlds are opened by validation.

Install from this repository through the launcher's GitHub mod installer, then
build the instance's native mods. The source-only `.hnmod` is also generated in
`target/tectonic_horizon-0.3.2.hnmod` for distribution.

```sh
horizon-launcher mods add-github https://github.com/eltanschauung/tectonic-horizon \
  --trust-native-code
horizon-launcher native-build --trust-native-code --profile fast
```

For development, the CLI can also build the bundle folder directly:

```sh
horizon-launcher native-build /path/to/tectonic-horizon/mixins/tectonic_horizon \
  --trust-native-code
```

If the instance already has native mods, install/import the bundle first and
build the full installed set, so they remain in the selected executable.

## Find the installed mod

In the launcher, open **Mods** and look in the **Add a native mod from GitHub**
section for `tectonic_horizon`. GitHub installs have their own list rather than
the registry's Installed list. If it was installed from the command line while
the launcher was open, restart the launcher to refresh that list.

In the newly built game, **Options → Mods** lists **Tectonic-Horizon 0.3.2**.
Restart an already running game to use the new executable.

## Configuration

Defaults reproduce the settings of Tectonic 3.0.1. Optional configuration is
`config/tectonic-horizon.json` in the game directory (`--game-dir` for the client,
`--dir` for a dedicated server). `TECTONIC_HORIZON_CONFIG` overrides that path.
Copy [config.example.json](../config.example.json) there and edit it, or specify
only the fields you want; omitted sections/fields keep their defaults.
The Mods-menu Settings page exposes all six configuration sections, with toggles, numeric decrement/increment controls, selectable adjustment steps and section resets. It writes this same JSON file atomically. Invalid or unreadable configurations are shown as an error and are not overwritten.

Configuration is read once per process. Restart the game after editing it.
Malformed configurations fail before terrain generation instead of generating
a world with unexpected settings. There is no Java config-screen dependency.

Only newly generated chunks use the selected terrain configuration. Create a
new world for a continuous Tectonic landscape; existing saved chunks retain
their terrain. Use increased height only when creating a new world. Changing
worldgen settings after exploring a world can create terrain boundaries.

Terralith/CliffTree integration and the Java UI are not shipped: those require
their own Horizon ports. The terrain recipe is from the pinned CC0 v3 revision,
not the unlicensed `rewrite-squared` development branch. Density/noise schemas,
aquifers, surface queries and ore-vein integration are adapted to Horizon 26.3;
this is not a claim of block-for-block identity with Java Minecraft 1.21.

River decoration uses native deterministic, chunk-local placement of glow lichen
and rare hanging lanterns. It samples Tectonic's river eligibility density and
lantern noise, and does not depend on Lithostitched. Its placement order and
random stream differ from Lithostitched's Java feature pipeline.
