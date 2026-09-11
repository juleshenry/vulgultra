use clap::Parser;
use cyberlatin_cli::{
    compute_energy, format_output, generate_legal_endings, init_genome,
    mutate_in_place, undo_mutation,
    phonemes_to_ortho, verb_slots, PipelineInput, EnergyCache,
    NOUN_SLOTS, ADJ_SLOTS,
};
use indicatif::{ProgressBar, ProgressStyle};
use rand::rngs::StdRng;
use rand::SeedableRng;
use std::collections::HashMap;
use std::fs;

#[derive(Parser)]
#[command(
    name = "lacyo",
    version = "2.0",
    about = "Lacyo — Simulated Annealing optimizer for a computationally designed fusional language"
)]
struct Cli {
    /// Path to candidates JSON (output from Python pipeline)
    #[arg(short, long)]
    input: String,

    /// Output JSON path
    #[arg(short, long, default_value = "data/lacyo_lexicon.json")]
    output: String,

    /// Max SA iterations
    #[arg(short = 'n', long, default_value_t = 2_000_000)]
    iterations: u64,

    /// Initial temperature
    #[arg(long, default_value_t = 10_000.0)]
    temp: f64,

    /// Cooling rate
    #[arg(long, default_value_t = 0.999_997)]
    cooling: f64,

    /// Minimum temperature
    #[arg(long, default_value_t = 0.01)]
    min_temp: f64,

    /// Random seed
    #[arg(short, long, default_value_t = 42)]
    seed: u64,
}

fn main() {
    let cli = Cli::parse();

    // Load candidates
    println!("Loading candidates from {}...", cli.input);
    let json_str = fs::read_to_string(&cli.input)
        .unwrap_or_else(|e| { eprintln!("Failed to read {}: {}", cli.input, e); std::process::exit(1); });
    let input: PipelineInput = serde_json::from_str(&json_str)
        .unwrap_or_else(|e| { eprintln!("Failed to parse JSON {}: {}", cli.input, e); std::process::exit(1); });

    println!("  {} concepts loaded", input.concepts.len());

    // Generate legal endings pool
    let legal_endings = generate_legal_endings();
    println!("  {} legal 1-syllable endings in pool", legal_endings.len());

    // Init RNG, genome, candidate DB
    let mut rng = StdRng::seed_from_u64(cli.seed);
    let (mut genome, db) = init_genome(&input, &legal_endings, &mut rng);
    let mut cache = EnergyCache::from_genome(&genome, &db);
    let mut energy = cache.energy();
    let initial_energy = energy;

    // Keep track of best state
    let mut best_genome = genome.clone();
    let mut best_energy = energy;

    println!("  Initial energy: {:.0}", energy);
    println!("\nRunning simulated annealing ({} iterations)...\n", cli.iterations);

    // Progress bar
    let pb = ProgressBar::new(cli.iterations);
    pb.set_style(
        ProgressStyle::with_template(
            "  {spinner:.green} [{elapsed_precise}] [{bar:40.cyan/blue}] {pos}/{len} ({eta}) E={msg}"
        )
        .unwrap()
        .progress_chars("█▓▒░  "),
    );

    let mut temp = cli.temp;
    let mut accepted = 0u64;
    let mut iterations = 0u64;

    for it in 0..cli.iterations {
        if temp < cli.min_temp {
            iterations = it;
            break;
        }

        // Mutate in place, get undo info
        let undo = mutate_in_place(&mut genome, &db, &mut cache, &legal_endings, &mut rng);
        let new_energy = cache.energy();
        let delta = new_energy - energy;

        if delta < 0.0 || rand::Rng::gen::<f64>(&mut rng) < (-delta / temp).exp() {
            // Accept
            energy = new_energy;
            accepted += 1;

            if energy < best_energy {
                best_genome = genome.clone();
                best_energy = energy;
            }
        } else {
            // Reject — undo the mutation
            undo_mutation(&mut genome, &db, &mut cache, undo);
        }

        temp *= cli.cooling;
        iterations = it + 1;

        if it % 10000 == 0 {
            pb.set_position(it);
            pb.set_message(format!("{:.0}", best_energy));
        }
    }

    pb.set_position(iterations);
    pb.set_message(format!("{:.0}", best_energy));
    pb.finish_with_message(format!("DONE — best energy: {:.0}", best_energy));

    // Final energy breakdown for output
    let breakdown = compute_energy(&best_genome, &db);

    // Output
    let output = format_output(&best_genome, &db, &breakdown, iterations, accepted, initial_energy);
    let json_out = serde_json::to_string_pretty(&output).expect("Failed to serialize output");
    fs::write(&cli.output, &json_out)
        .unwrap_or_else(|e| { eprintln!("Failed to write {}: {}", cli.output, e); std::process::exit(1); });
    println!("\n  Output written to {}", cli.output);

    // Print summary
    print_summary(&best_genome, &db, &breakdown, iterations, accepted);
}

fn print_summary(
    genome: &cyberlatin_cli::Genome,
    db: &cyberlatin_cli::CandidateDB,
    breakdown: &cyberlatin_cli::EnergyBreakdown,
    iterations: u64,
    accepted: u64,
) {
    let n = genome.n_concepts();

    println!("\n{}", "═".repeat(70));
    println!("  LACYO LEXICON — OPTIMIZATION RESULT");
    println!("{}", "═".repeat(70));

    println!("\n  Concepts:       {}", n);
    println!("  Iterations:     {}", iterations);
    println!("  Accept rate:    {:.1}%", if iterations > 0 { accepted as f64 / iterations as f64 * 100.0 } else { 0.0 });
    println!("  Total energy:   {:.0}", breakdown.total);

    println!("\n  Energy breakdown:");
    println!("    E_root       {:>12.0}", breakdown.e_root);
    println!("    E_norm       {:>12.0}", breakdown.e_norm);
    println!("    E_phon       {:>12.0}", breakdown.e_phon);
    println!("    E_end        {:>12.0}", breakdown.e_end);
    println!("    E_coll       {:>12.0}", breakdown.e_coll);
    println!("    E_tact       {:>12.0}", breakdown.e_tact);
    println!("    E_dist       {:>12.0}", breakdown.e_dist);

    // Syllable distribution
    let mut syl_dist: HashMap<u32, usize> = HashMap::new();
    let mut total_syls = 0u64;
    let mut total_viols = 0u64;
    for i in 0..n {
        let r = genome.get_root(i, db);
        *syl_dist.entry(r.syllables).or_insert(0) += 1;
        total_syls += r.syllables as u64;
        total_viols += r.violations as u64;
    }

    println!("\n  Root syllable distribution:");
    let mut keys: Vec<u32> = syl_dist.keys().copied().collect();
    keys.sort();
    for s in &keys {
        let count = syl_dist[s];
        let pct = count as f64 / n as f64 * 100.0;
        let bar: String = "█".repeat((pct / 2.0) as usize);
        println!("    {} syl: {:>4} ({:>5.1}%) {}", s, count, pct, bar);
    }
    println!("    avg:  {:.2} syllables", total_syls as f64 / n as f64);
    println!("    violations: {}", total_viols);

    // Noun endings
    println!("\n  Noun endings:");
    for (ci, cls) in genome.noun_endings.iter().enumerate() {
        println!("    class {}:", ci + 1);
        for (si, seq) in cls.iter().enumerate() {
            let slot = NOUN_SLOTS.get(si).unwrap_or(&"?");
            println!("      {:8} → -{}", slot, phonemes_to_ortho(seq));
        }
    }

    // Verb endings (present indicative only for display)
    let v_slots = verb_slots();
    println!("\n  Verb endings (present indicative):");
    for (ci, cls) in genome.verb_endings.iter().enumerate() {
        println!("    class {}:", ci + 1);
        for (si, seq) in cls.iter().enumerate().take(6) {
            let slot = v_slots.get(si).map(|s| s.as_str()).unwrap_or("?");
            println!("      {:12} → -{}", slot, phonemes_to_ortho(seq));
        }
    }

    // Adj endings
    println!("\n  Adjective endings:");
    for (si, seq) in genome.adj_endings.iter().enumerate() {
        let slot = ADJ_SLOTS.get(si).unwrap_or(&"?");
        println!("    {:8} → -{}", slot, phonemes_to_ortho(seq));
    }

    // Sample roots (shortest first)
    println!("\n  Sample roots (30 shortest):");
    let mut root_info: Vec<(String, u32, String, String)> = (0..n)
        .map(|i| {
            let r = genome.get_root(i, db);
            (r.orthography.clone(), r.syllables, r.source_lang.clone(), r.source_word.clone())
        })
        .collect();
    root_info.sort_by_key(|x| x.1);
    for (ortho, syls, lang, src) in root_info.iter().take(30) {
        println!("    {:12}  ({}σ)  ← {}:{}", ortho, syls, lang, src);
    }

    // Emergent phoneme inventory
    let mut all_phonemes: std::collections::HashSet<String> = std::collections::HashSet::new();
    for i in 0..n {
        let r = genome.get_root(i, db);
        for p in &r.lacyo_phonemes {
            all_phonemes.insert(p.clone());
        }
    }
    let mut inv: Vec<&String> = all_phonemes.iter().collect();
    inv.sort();
    println!("\n  Emergent phoneme inventory ({} phonemes):", inv.len());
    println!("    {}", inv.iter().map(|p| p.as_str()).collect::<Vec<_>>().join(" "));

    println!("\n{}", "═".repeat(70));
}
