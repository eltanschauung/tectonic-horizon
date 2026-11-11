use std::{collections::BTreeMap, fs, path::Path};
fn main() {
    let root = std::env::args().nth(1).expect("worldgen resources");
    let mut out = BTreeMap::new();
    for name in [
        "noises",
        "densities",
        "settings",
        "rules",
        "biomes",
        "dimension_types",
    ] {
        let file = Path::new(&root).join(format!("{name}.json"));
        let mut bundle: BTreeMap<String, String> = fs::read_to_string(file)
            .ok()
            .and_then(|s| serde_json::from_str(&s).ok())
            .unwrap_or_default();
        tectonic_horizon::runtime::populate(name, &mut bundle, &Default::default());
        out.insert(name, bundle);
    }
    println!("{}", serde_json::to_string(&out).unwrap());
}
