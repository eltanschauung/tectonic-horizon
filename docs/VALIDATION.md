# Validation

Validated on the desktop over SSH, using the fork's Rust environment and the
exact Horizon/mixin revisions in [compatibility.json](../compatibility.json).

- Standalone Rust: formatting, Clippy with warnings denied, six unit tests and
  doc tests, plus an integration test of native menu registration.
- Clippy also passes with warnings denied for the actual patched
  `horizon-world` library, including the injected decoration and adapters.
- The real mixin engine plans/applies seven injections and three support modules
  against an isolated committed source export.
- The source-only `.hnmod` is reproducible byte for byte.
- The compiled, patched world generator loads locally prepared resources and
  generates terrain in memory; no player world is opened or saved.
- Independent workers produce identical chunk fingerprints in reversed order,
  and a second seed produces different terrain.
- Default terrain uses 384-block dimensions; increased height uses 704.
- Across a 33 by 33 grid spanning -16,000 through 16,000 on each horizontal
  axis, sampled Tectonic surface heights ranged from Y=-8 to Y=259. With the
  mod disabled, the same sample ranged from Y=26 to Y=181.
- Nether and End chunk fingerprints are identical with default settings,
  increased height, and the mod disabled.
- Native river decoration runs through the real decoration pipeline and
  repeated decoration is idempotent.
- Ocean monuments start 30 blocks lower in all four orientations; disabling
  the mod restores the original height. Snow height also follows enablement.
- Explicit world-pack density entries and custom dimension types retain
  priority over the built-in mod settings.

These checks establish native compilation and terrain integration. They do
not establish block-for-block parity with Java Tectonic, compatibility with
unported biome mods, or interactive GUI behavior. See [INSTALL.md](INSTALL.md)
for the configuration and compatibility scope.
