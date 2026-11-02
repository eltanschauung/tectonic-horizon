# Tectonic-Horizon

This is a remake of the [Tectonic](https://github.com/Apollounknowndev/tectonic) mod for the Horizon project as a native mod.

---

View the full description on the Modrinth page here: https://modrinth.com/mod/tectonic

Version 0.3.0 is tested against upstream Horizon `31d5f62db`, including its fix for
sneak rebound away from Shift being cleared each frame. Tectonic registers no keys
and does not intercept keyboard input. The early 0.1.0 package pinned fork revision
`6c2ba60a`, which predates that fix; our 0.2.0 fork build already includes it.
Rebuild the game after updating the native mod.

On upstream, toggle Tectonic in Options > Mods before opening a world. Changing the
switch invalidates the cached generator, so an already loaded terrain configuration
is not reused. Keep the same selection when reopening an existing world to avoid
terrain seams. Our Horizon fork also saves the selection per world and keeps the
component in launcher builds while its switch is off.

Configuration file edits require restarting the game.

To check rebinding in a built game on Linux (Xvfb, X11 and XTest required):

```sh
python3 tools/rebind_smoke.py /path/to/installed/version
```

The check creates temporary worlds, sends real keyboard events, and verifies crouch
on C and Ctrl, jump on Shift, and sprint on X with Tectonic enabled and disabled.
