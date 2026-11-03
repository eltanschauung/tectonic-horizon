#[derive(Default)]
struct NativeMod {
    id: String,
    title: String,
    description: String,
    keys: Vec<[String; 3]>,
}

include!("../mixins/tectonic_horizon/menu.rs");

#[test]
fn menu_registration_lists_the_mod_once_and_preserves_other_mods() {
    let mut mods = vec![NativeMod {
        id: "other_mod".into(),
        ..NativeMod::default()
    }];
    register(&mut mods);
    register(&mut mods);
    assert_eq!(mods.len(), 2);
    assert_eq!(mods[0].id, "other_mod");
    assert_eq!(mods[1].id, "tectonic_horizon");
    assert_eq!(mods[1].title, format!("Tectonic-Horizon {}", env!("CARGO_PKG_VERSION")));
    assert!(mods[1].description.contains("Settings page"));
    assert!(mods[1].keys.is_empty());
}
