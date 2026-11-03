# Tectonic-Horizon

An unofficial native Rust port of [Tectonic](https://github.com/Apollounknowndev/tectonic) by Apollo (Apollounknowndev), based on Tectonic 3.0.1, revision `0761b561062de01b701d2571401f625c31059a9a`, released under CC0-1.0. Not made or endorsed by Apollo or the Horizon project.

Adds Tectonic's mountain ranges, terrain density recipes, underground rivers and configuration to Horizon 26.3. This is a source-only native mod: the launcher compiles it into a separate game. It runs with the game's account permissions. No Minecraft JARs, classes, assets or prepared resources are included.

![Tectonic landscape in Horizon](docs/screenshots/tectonic-landscape.png)

The screenshot was supplied by the author and captured on 2026-11-01 in our Horizon fork; it illustrates terrain, not a compatibility test of the pinned upstream build. The minimap is a separate mod.

## Install and configure

Install the native mod through Horizon's launcher, then Build. Enable it under Options > Mods before opening a world. Rebuild and restart to use an updated package. On upstream, keep the same mod selection when reopening worlds to avoid terrain seams. Our fork additionally records mod selections per world.

Open **Options > Mods > Tectonic-Horizon > Settings** to edit General, Global terrain, Continents, Islands, Oceans and Biomes. Boolean buttons toggle; numeric (-)/(+) buttons use the selected adjustment step (0.001, 0.01, 0.1, 1, 10 or 100; integer fields use at least 1). Each section has its own reset button. Edits save immediately to the same JSON configuration and preserve values in the other sections. Restart the game before playing with the new settings. The editor does not change a running world generator.

Configuration: `config/tectonic-horizon.json` in the game home, or `TECTONIC_HORIZON_CONFIG`. See [the example](config.example.json) and [installation notes](docs/INSTALL.md). Missing fields use defaults; restart after edits. Changes affect newly generated chunks. Increased-height terrain must be selected before creating a world.

## Compatibility and limits

Version 0.3.3 pins upstream Horizon `8dbbde43501924d16497d251e6e9d08f812eafcd` and Horizon Mixins `e8cd0aa38cffef49cb2e088ef716baa107148c02`; [compatibility.json](compatibility.json) records source hashes. The height adapter includes upstream's ceiling flag; validation notes distinguish upstream checks from fork builds.

The original terrain definitions and config defaults are imported with provenance in [upstream.json](upstream.json) and [third-party notices](THIRD_PARTY_NOTICES.md). This port adapts noise/density schemas and aquifers to Horizon. It does not claim block-for-block Java parity. Native river decoration uses a chunk-local random stream and differs from Lithostitched's Java feature placement. The Java config screen and Terralith/CliffTree overlays are not included. Biome packs require their own Horizon ports; our fork's BOP compatibility is separate from upstream validation. Tectonic registers no keys and does not intercept keyboard input.

See [validation](docs/VALIDATION.md) for the release's checks and their scope. The public source and packaged mixins are identical; `python3 tools/package.py` reproduces the source-only `.hnmod`.

License: [CC0-1.0](LICENSE). Original Tectonic by Apollo; Horizon adaptation by eltanschauung with Codex assistance.
