// Integration checks run only with the user's locally prepared resources.
// No world is opened or saved; generated chunks remain in memory.
use horizon_core::{
    geometry::Direction,
    position::{BlockPos, ChunkPos},
    random::{PositionalRandom, RandomSource, XoroshiroRandom},
};
use horizon_world::worldgen::{
    generator::{GeneratorData, OverworldGenerator},
    overrides::WorldgenOverrides,
};
use std::path::PathBuf;

fn fingerprint(
    worker: &mut horizon_world::worldgen::generator::GeneratorWorker,
    p: ChunkPos,
) -> u64 {
    let chunk = worker.generate_proto(p).expect("generate terrain");
    chunk_hash(&chunk)
}

fn chunk_hash(chunk: &horizon_world::worldgen::generator::ProtoChunk) -> u64 {
    let mut hash = 0xcbf29ce484222325u64;
    for y in chunk.terrain.min_y()..chunk.terrain.min_y() + chunk.terrain.height() {
        for z in 0..16 {
            for x in 0..16 {
                hash = (hash ^ u64::from(chunk.block(x, y, z).0)).wrapping_mul(0x100000001b3);
            }
        }
    }
    hash
}

fn main() {
    let root = PathBuf::from(std::env::var_os("HORIZON_RESOURCES").expect("HORIZON_RESOURCES"));
    let registry = Box::leak(Box::new(
        horizon_world::level::data::load_registry(&root).expect("registry"),
    ));
    for name in [
        "minecraft:iron_chain",
        "minecraft:lantern",
        "minecraft:glow_lichen",
    ] {
        assert!(
            registry.default_state(name).is_some(),
            "river decoration block: {name}"
        );
    }
    let data =
        GeneratorData::load(&root.join("worldgen"), registry).expect("load native registries");
    let generator = OverworldGenerator::without_structures(data.clone(), 1234)
        .expect("compile native generator");
    let expected_height = if std::env::var_os("TECTONIC_TEST_TALL").is_some() {
        704
    } else {
        384
    };
    assert_eq!(generator.level(), (-64, expected_height));
    let mut first = generator.worker();
    let mut hashes = Vec::new();
    let positions = [
        ChunkPos::new(0, 0),
        ChunkPos::new(-1, 0),
        ChunkPos::new(12, -17),
    ];
    for p in positions {
        let a = fingerprint(&mut first, p);
        hashes.push(a);
    }
    let mut second = generator.worker();
    for (p, expected) in positions.into_iter().zip(&hashes).rev() {
        assert_eq!(
            *expected,
            fingerprint(&mut second, p),
            "worker/order determinism"
        );
    }
    assert!(hashes.windows(2).any(|h| h[0] != h[1]));
    let another = OverworldGenerator::without_structures(data.clone(), -9182).expect("second seed");
    assert_ne!(
        hashes[0],
        fingerprint(&mut another.worker(), ChunkPos::new(0, 0))
    );
    // Exercise the native decoration adapter and repeated-call behavior.
    let mut neighborhood = std::array::from_fn(|i| {
        first
            .generate_proto(ChunkPos::new(i as i32 % 3 - 1, i as i32 / 3 - 1))
            .unwrap()
    });
    first
        .decorate(&mut neighborhood)
        .expect("decorate native river features and host features");
    assert!(neighborhood[4].is_decorated());
    let decorated = chunk_hash(&neighborhood[4]);
    first
        .decorate(&mut neighborhood)
        .expect("decoration idempotency");
    assert_eq!(decorated, chunk_hash(&neighborhood[4]));
    let mut heights = Vec::new();
    for z in (-16000..=16000).step_by(1000) {
        for x in (-16000..=16000).step_by(1000) {
            if let Some(surface) = first.surface_sample(x, z) {
                heights.push(surface.height);
            }
        }
    }
    let min = *heights.iter().min().expect("surface samples");
    let max = *heights.iter().max().unwrap();
    if std::env::var_os("TECTONIC_TEST_DISABLED").is_none() {
        assert!(
            min < 63 && max > 160,
            "ocean and mountain relief: {min}..{max}"
        );
    }
    // The generator must still resolve the other dimensions.
    let mut dimension_hashes = Vec::new();
    for dim in ["minecraft:the_nether", "minecraft:the_end"] {
        let other =
            OverworldGenerator::for_world(data.clone(), 1234, "minecraft:normal", dim, false)
                .expect("other dimension");
        dimension_hashes.push(fingerprint(&mut other.worker(), ChunkPos::new(0, 0)));
    }
    let mut packed = WorldgenOverrides::default();
    packed.set(
        "densities",
        "tectonic:__constants/vertical_scale",
        "0.9".into(),
    );
    let merged = packed.apply("densities", Default::default());
    assert_eq!(
        merged["tectonic:__constants/vertical_scale"], "0.9",
        "user packs take precedence"
    );
    let factory = XoroshiroRandom::new(1234).fork_positional();
    for key in ["continentalness", "erosion", "ridge"] {
        assert_eq!(
            factory
                .from_hash_of(&format!("tectonic:parameter/{key}"))
                .next_long(),
            factory
                .from_hash_of(&format!("minecraft:{key}"))
                .next_long()
        );
    }
    let enabled = std::env::var_os("TECTONIC_TEST_DISABLED").is_none();
    let box_y = if enabled { 9 } else { 39 };
    use horizon_world::worldgen::structure::{legacy::LegacyPiece, monument::MonumentBuilding};
    for direction in [
        Direction::North,
        Direction::South,
        Direction::East,
        Direction::West,
    ] {
        let building = MonumentBuilding::new(&mut XoroshiroRandom::new(42), 0, 0, direction);
        assert_eq!(building.bounding_box().min[1], box_y, "monument depth");
    }
    use horizon_world::worldgen::biome_temperature::{
        BiomeTemperatureSettings, TemperatureModifier,
    };
    let temperature = BiomeTemperatureSettings {
        base_temperature: 0.5,
        modifier: TemperatureModifier::None,
        has_precipitation: true,
        downfall: 0.5,
    };
    let snow_y = if enabled { 208 } else { 80 };
    assert_eq!(
        temperature.height_adjusted(BlockPos::new(0, snow_y, 0), 63),
        0.5,
        "snow start"
    );
    let custom = std::collections::BTreeMap::from([(
        "minecraft:overworld".into(),
        r#"{"min_y":-64,"height":512,"logical_height":512}"#.into(),
    )]);
    assert_eq!(
        horizon_world::worldgen::overrides::LevelHeight::of_type(
            &serde_json::json!("minecraft:overworld"),
            &custom
        )
        .unwrap()
        .height,
        512,
        "explicit dimension types win"
    );
    println!(
        "{}",
        serde_json::json!({"height":expected_height, "min_surface":min, "max_surface":max,
        "terrain":hashes, "other_dimensions":dimension_hashes})
    );
}
