fn register(mods: &mut Vec<NativeMod>) {
    if mods.iter().any(|entry| entry.id == "tectonic_horizon") {
        return;
    }
    mods.push(NativeMod {
        id: "tectonic_horizon".into(),
        title: "Tectonic-Horizon 0.1.0".into(),
        description: "Native terrain generation with continents, mountain ranges, deep oceans, underground rivers and lava tunnels. Configuration: config/tectonic-horizon.json (restart after editing).".into(),
        keys: Vec::new(),
    });
}
