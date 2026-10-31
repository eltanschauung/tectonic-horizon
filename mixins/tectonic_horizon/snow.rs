fn snow(value: i32) -> i32 {
    let config = crate::worldgen::overrides::tectonic_horizon::config();
    value.saturating_add(if config.general.mod_enabled {
        config.general.snow_start_offset
    } else {
        0
    })
}
