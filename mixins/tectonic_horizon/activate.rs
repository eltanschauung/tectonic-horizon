fn activate(overrides: &WorldgenOverrides) {
    tectonic_horizon::set_active(overrides.mod_enabled("tectonic_horizon"));
}
