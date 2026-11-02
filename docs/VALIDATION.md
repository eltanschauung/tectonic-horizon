# Release 0.3.1 validation (2026-11-02)

Built the native source bundle against an isolated export of **upstream** Horizon `0409f619a6a5529c7278306a49476eafb3913e8a`, using Horizon Mixins `ddd9700b21997c95d95ac6ee5ecafe3830cf622a`. No changes from our Horizon fork were applied. The source hashes are in `compatibility.json`.

- Mixin application succeeded: eight injections, four modules and one data bundle.
- The optimized `fast` game client and `horizon-ctl` compiled successfully with the upstream lockfile.
- Horizon's native-package checker accepted `tectonic_horizon-0.3.1.hnmod`.
- Every packaged source file matches this checkout; rebuilding the package produces identical bytes. SHA-256: `b3ce7fb49c18c81390698483fe01b04e79c9feb78b961562dc0a0211fdbc8c6d`.
- The real patched world-generator probe passed for default, increased-height and disabled configurations. It checks worker-order determinism, a second seed, river decoration/idempotence, monument and snow adaptation, and explicit world-pack precedence.
- Default height is 384; increased height is 704. Surface samples span Y=-8..259 with Tectonic and Y=26..181 when disabled. Terrain fingerprints differ; Nether and End fingerprints are identical across all three configurations.
- Actual isolated game launches passed with Tectonic enabled and disabled. Physical keyboard events verified sneak on C and Ctrl, jump on Shift and sprint on X; saved world-mod selections were checked.

Numeric results are retained in [validation-0.3.1.json](validation-0.3.1.json). Test worlds, configuration and XDG homes were temporary; no player worlds, accounts or installed game selection changed. Prepared Minecraft resources were read locally and are not distributed.

Reproduction: fetch the pinned upstream commit into a local Horizon checkout, then use `tools/desktop.py build`, `tools/validate.py`, `tools/rebind_smoke.py <built-version-folder>` and `tools/package.py`. The game-launch smoke needs prepared 26.3 resources, Linux/Xvfb/XTest, and a version folder containing the built binaries plus `.local/horizon-client/26.3`. Earlier checks below describe prior releases and were not all rerun for 0.3.1.

These results establish the tested upstream build and terrain/input behavior. They do not establish exact Java block parity, all mod combinations, all platforms or all seeds. The screenshot in the README was taken on our fork on 2026-11-01 and is illustrative.

---

# Historical validation

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
