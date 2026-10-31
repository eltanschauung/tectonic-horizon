fn registries(bundle: &str, base: &mut BTreeMap<String, String>) {
    tectonic_horizon::populate(bundle, base, tectonic_horizon::config());
}
