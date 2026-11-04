use std::sync::atomic::{AtomicUsize, Ordering};
use tectonic_horizon::runtime::{Config, load_config};

fn check(contents: Option<&[u8]>, expect_defaults: bool) {
    static NEXT: AtomicUsize = AtomicUsize::new(0);
    let dir = std::env::temp_dir().join(format!(
        "tectonic-config-{}-{}",
        std::process::id(),
        NEXT.fetch_add(1, Ordering::Relaxed)
    ));
    std::fs::create_dir_all(&dir).unwrap();
    let path = dir.join("config.json");
    if let Some(bytes) = contents {
        std::fs::write(&path, bytes).unwrap();
    }
    let result = load_config(&path);
    if expect_defaults {
        assert_eq!(
            serde_json::to_value(result).unwrap(),
            serde_json::to_value(Config::default()).unwrap()
        );
    } else {
        assert!(!result.general.mod_enabled);
    }
    std::fs::remove_dir_all(dir).unwrap();
}
#[test]
fn missing_uses_defaults() {
    check(None, true);
}
#[test]
fn malformed_uses_defaults() {
    check(Some(b"{broken"), true);
}
#[test]
fn oversized_uses_defaults() {
    check(Some(&vec![b' '; 65537]), true);
}
#[test]
fn invalid_encoding_uses_defaults() {
    check(Some(&[255, 254]), true);
}
#[test]
fn valid_configuration_is_preserved() {
    check(Some(br#"{"general":{"mod_enabled":false}}"#), false);
}
#[test]
fn unreadable_configuration_uses_defaults() {
    let config = load_config(&std::env::temp_dir());
    assert_eq!(
        serde_json::to_value(config).unwrap(),
        serde_json::to_value(Config::default()).unwrap()
    );
}
