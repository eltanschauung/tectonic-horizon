# Registry review revision: 0.3.4

This release addresses the changes requested on horizon-rust/horizon-mods#160
and includes the current 0.3.3 height adapter and 0.3.2 in-game settings editor.

- Removed `mixins/tectonic_horizon/data/runtime-toggle.json`. No Rust source
  referenced it. Packaging now includes only the root native manifest and
  the mixin's Rust/TOML files, as the registry checker requires.
- Invalid, unreadable, non-UTF-8 or oversized configuration prints a diagnostic
  and uses the default configuration. Reads are bounded to 64 KiB plus one
  byte to detect an oversized file. Missing configuration retains its normal
  default behavior. Valid user settings are preserved.
- Fixed the formatting of `tests/menu_registration.rs` that failed GitHub's
  `cargo fmt --all --check` job on 0.3.3.

Validation for this revision:

- Formatting, Clippy with warnings denied, and all 13 Rust tests pass.
- Six configuration-loading regression cases cover missing, malformed,
  oversized, invalid encoding, unreadable, and valid configuration.
- Repeated packaging produces identical bytes. The archive contains no
  unsupported JSON source files. `cargo horizon-mod check` accepts it.
- All 10 injections and 5 modules plan and apply to the exact upstream Horizon
  and Mixins revisions recorded in compatibility.json.

These checks do not constitute a new interactive game test or a new terrain
parity comparison. Older runtime validation remains documented in VALIDATION.md
with its original revisions and scope.
