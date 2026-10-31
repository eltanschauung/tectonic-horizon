# Third-party notices

Terrain definitions and configuration defaults are adapted from **Tectonic** by
Apollo (Apollounknowndev), version 3.0.1, commit
[`0761b561062de01b701d2571401f625c31059a9a`](https://github.com/Apollounknowndev/tectonic/tree/0761b561062de01b701d2571401f625c31059a9a).
That revision carries the CC0-1.0 public-domain dedication, reproduced in
[LICENSE](LICENSE). `upstream.json` records the SHA-256 of every embedded source
definition. Java `ConfigState`, `ConfigConstant`, `ConfigNoise`, `NoisesMixin`,
`StructurePieceMixin`, and `BiomeMixin` were read to implement their behavior
in Rust. No Java classes or Minecraft resources are distributed.

Changes: native Rust configuration and density-schema translation for Horizon
26.3, compiled-in terrain registries, native river decoration, current aquifer
and material-rule integration, and source mixin adapters. Third-party mod
compatibility overlays are not included.

The implementation uses **Horizon** (MIT) and **horizon-mixins** (MIT), fetched
separately at the revisions in `compatibility.json`. They are not vendored into
this repository. The MIT Horizon native mod template and official native-mod
documentation were consulted for the bundle/packaging format. The scripts here
are written for this project.
