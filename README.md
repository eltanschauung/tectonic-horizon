# Tectonic-Horizon

This is a remake of the [Tectonic](https://github.com/Apollounknowndev/tectonic) mod for the Horizon project as a native mod.

---

View the full description on the Modrinth page here: https://modrinth.com/mod/tectonic

Version 0.3.0 targets upstream Horizon `31d5f62db` or newer, including its fix for
sneak rebound away from Shift being cleared each frame. Tectonic registers no keys
and does not intercept keyboard input. Rebuild the game after updating the native mod.

On upstream, toggle Tectonic in Options > Mods before opening a world. Changing the
switch invalidates the cached generator, so an already loaded terrain configuration
is not reused. Keep the same selection when reopening an existing world to avoid
terrain seams. Our Horizon fork also saves the selection per world and keeps the
component in launcher builds while its switch is off.

Configuration file edits require restarting the game.
