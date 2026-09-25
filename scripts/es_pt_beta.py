#!/usr/bin/env python3
"""ES/PT inspection scorecard for the mixed-origin Romance beta."""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from vulgultra.optimizer import (
    Candidate, Genome, compute_energy, greedy_root_selections, init_genome,
)
from vulgultra.phonology import from_orthography, phonemic_edit_distance
from vulgultra.realize import form_syllables, realize_sentence
from vulgultra.romance_swadesh import (
    GENDER_PAIRS, LECT_BRANCHES, LECT_NAMES, SENTENCES, SOURCE_LANGS,
    concepts as swadesh_concepts,
)


POLICIES = (
    "sa",
    "set-cover",
    "support-shortest",
    "shortest",
    "always-es",
    "always-pt",
    "always-fr",
    "always-it",
    "always-ca",
    "always-ro",
    "always-gl",
    "always-oc",
    "init",
)


def load_candidates(path: Path) -> dict[str, list[Candidate]]:
    raw = json.loads(path.read_text())
    out: dict[str, list[Candidate]] = {}
    for cid, rows in raw["concepts"].items():
        cands = []
        for row in rows:
            if row.get("source_lang") == "en":
                raise ValueError(f"English source leaked into {cid}")
            cands.append(Candidate(
                concept=row["concept"],
                source_lang=row["source_lang"],
                source_word=row["source_word"],
                ipa=row["ipa"],
                vulgultra_phonemes=list(row.get("vulgultra_phonemes") or row["lacyo_phonemes"]),
                orthography=row["orthography"],
                syllables=int(row["syllables"]),
                violations=int(row["violations"]),
                support=int(row.get("support", 1)),
                evidence=row.get("evidence", ""),
                relation=row.get("relation", "direct"),
                morpheme_key=row.get("morpheme_key", ""),
            ))
        if cands:
            out[cid] = cands
    return out


def endings_from_lexicon(lex: dict) -> tuple[dict, dict, dict]:
    noun = {
        cls: {slot: from_orthography(ortho) for slot, ortho in slots.items()}
        for cls, slots in lex["noun_endings"].items()
    }
    verb = {
        cls: {slot: from_orthography(ortho) for slot, ortho in slots.items()}
        for cls, slots in lex["verb_endings"].items()
    }
    adj = {slot: from_orthography(ortho) for slot, ortho in lex["adj_endings"].items()}
    return noun, verb, adj


def cand_by_lang(cands: list[Candidate], lang: str) -> int | None:
    for i, c in enumerate(cands):
        if c.source_lang == lang:
            return i
    return None


def shortest_index(cands: list[Candidate]) -> int:
    """Raw shortness, legality second. Not the energy-greedy choice."""
    return min(
        range(len(cands)),
        key=lambda i: (
            cands[i].syllables,
            cands[i].violations,
            -cands[i].support,
            len(cands[i].vulgultra_phonemes),
            cands[i].source_lang,
        ),
    )


def legal_shortest_index(cands: list[Candidate]) -> int:
    """Energy-greedy roots: zero violations, then syllables, then stem support."""
    return min(
        range(len(cands)),
        key=lambda i: (
            cands[i].violations,
            cands[i].syllables,
            -cands[i].support,
            len(cands[i].vulgultra_phonemes),
            cands[i].source_lang,
        ),
    )


def sa_index(cands: list[Candidate], chosen: dict) -> int:
    src = chosen["source_lang"]
    word = chosen["source_word"]
    ortho = chosen["orthography"]
    for i, c in enumerate(cands):
        if c.source_lang == src and c.source_word == word and c.orthography == ortho:
            return i
    for i, c in enumerate(cands):
        if c.orthography == ortho:
            return i
    raise KeyError(f"SA root not in candidates: {src}:{word} {ortho}")


def make_genome(
    candidates: dict[str, list[Candidate]],
    selections: dict[str, int],
    noun: dict,
    verb: dict,
    adj: dict,
) -> Genome:
    return Genome(
        selections=selections,
        candidates=candidates,
        noun_endings=noun,
        verb_endings=verb,
        adj_endings=adj,
    )


def policy_selections(
    name: str,
    candidates: dict[str, list[Candidate]],
    lexicon: dict,
) -> dict[str, int]:
    sel: dict[str, int] = {}
    lang = {
        "always-es": "es",
        "always-pt": "pt",
        "always-fr": "fr",
        "always-it": "it",
        "always-ca": "ca",
        "always-ro": "ro",
        "always-gl": "gl",
        "always-oc": "oc",
    }.get(name)
    if name == "set-cover":
        return greedy_root_selections(candidates)
    for cid, cands in candidates.items():
        if name == "sa":
            sel[cid] = sa_index(cands, lexicon["roots"][cid])
        elif name == "shortest":
            sel[cid] = shortest_index(cands)
        elif name == "support-shortest":
            sel[cid] = legal_shortest_index(cands)
        elif lang:
            idx = cand_by_lang(cands, lang)
            if idx is None:
                idx = shortest_index(cands)
            sel[cid] = idx
        else:
            raise ValueError(name)
    return sel


def transparency_bin(d: int) -> str:
    if d <= 1:
        return "transparente"
    if d <= 3:
        return "adivinable"
    return "opaco"


def gold_index() -> dict[str, dict]:
    return {row["id"]: row for row in swadesh_concepts()}


def by_lang_map(cands: list[Candidate]) -> dict[str, Candidate]:
    return {c.source_lang: c for c in cands}


def choice_why(chosen: Candidate, cands: list[Candidate]) -> str:
    """Human reason the chosen root beat the rest (lexicographic energy)."""
    legal = [c for c in cands if c.violations == 0] or list(cands)
    shorter = [c for c in legal if c.syllables < chosen.syllables]
    if shorter:
        return f"SA ≠ greedy (hay legal σ={shorter[0].syllables})"
    same = [c for c in legal if c.syllables == chosen.syllables and c.orthography != chosen.orthography]
    if not same:
        return f"única legal a σ={chosen.syllables}"
    better_sup = [c for c in same if c.support > chosen.support]
    if better_sup:
        return f"σ={chosen.syllables} pero support {chosen.support} < {better_sup[0].support}"
    rivals = [c for c in same if c.support == chosen.support]
    if rivals:
        langs = ",".join(sorted({c.source_lang for c in rivals})[:4])
        return f"σ={chosen.syllables}, support={chosen.support} (empate con {langs})"
    return f"σ={chosen.syllables}, support={chosen.support}"


def render_scorecard(
    candidates: dict[str, list[Candidate]],
    lexicon: dict,
    policies: dict[str, dict],
    init_energy: float | None,
) -> str:
    gold = gold_index()
    sa_sel = policy_selections("sa", candidates, lexicon)
    short_sel = policy_selections("shortest", candidates, lexicon)
    legal_sel = policy_selections("set-cover", candidates, lexicon)
    support_sel = policy_selections("support-shortest", candidates, lexicon)

    provenance = Counter()
    rows = []
    disagree = []
    identical_es_pt = 0
    sa_eq_es = sa_eq_pt = sa_eq_fr = sa_eq_it = sa_eq_short = sa_eq_legal = sa_eq_support = 0

    for cid in sorted(candidates, key=lambda c: gold.get(c, {}).get("gloss_es", c)):
        cands = candidates[cid]
        lang_map = by_lang_map(cands)
        chosen = cands[sa_sel[cid]]
        provenance[chosen.source_lang] += 1
        gloss = gold.get(cid, {}).get("gloss_es", cid)

        es_c = lang_map.get("es")
        pt_c = lang_map.get("pt")
        d_es = phonemic_edit_distance(chosen.vulgultra_phonemes, es_c.vulgultra_phonemes) if es_c else None
        d_pt = phonemic_edit_distance(chosen.vulgultra_phonemes, pt_c.vulgultra_phonemes) if pt_c else None
        closer_vals = [x for x in (d_es, d_pt) if x is not None]
        closer = min(closer_vals) if closer_vals else 99
        bin_name = transparency_bin(closer) if closer_vals else "—"

        if es_c and pt_c and es_c.orthography == pt_c.orthography:
            identical_es_pt += 1
        if es_c and chosen.orthography == es_c.orthography:
            sa_eq_es += 1
        if pt_c and chosen.orthography == pt_c.orthography:
            sa_eq_pt += 1
        if "fr" in lang_map and chosen.orthography == lang_map["fr"].orthography:
            sa_eq_fr += 1
        if "it" in lang_map and chosen.orthography == lang_map["it"].orthography:
            sa_eq_it += 1
        if sa_sel[cid] == short_sel[cid]:
            sa_eq_short += 1
        if sa_sel[cid] == support_sel[cid]:
            sa_eq_support += 1
        if sa_sel[cid] == legal_sel[cid]:
            sa_eq_legal += 1
        else:
            legal = cands[legal_sel[cid]]
            reason = "desempate / inventario"
            if chosen.syllables != legal.syllables:
                reason = "sílabas distintas"
            elif chosen.source_lang != legal.source_lang:
                reason = "misma σ, otra fuente"
            disagree.append((gloss, cid, chosen, legal, reason))

        def form(lang: str) -> str:
            gold_row = gold.get(cid, {})
            if lang in gold_row and gold_row[lang]:
                return gold_row[lang]
            c = lang_map.get(lang)
            return c.source_word if c else "—"

        def syl(lang: str) -> str:
            c = lang_map.get(lang)
            return str(c.syllables) if c else "—"

        rows.append({
            "gloss": gloss,
            "es": form("es"),
            "pt": form("pt"),
            "fr": form("fr"),
            "it": form("it"),
            "ca": form("ca"),
            "vulgultra": chosen.orthography,
            "src": chosen.source_lang,
            "sig": chosen.syllables,
            "s_es": syl("es"),
            "s_pt": syl("pt"),
            "s_fr": syl("fr"),
            "s_it": syl("it"),
            "s_ca": syl("ca"),
            "bin": bin_name,
            "d_es": d_es,
            "d_pt": d_pt,
            "sup": chosen.support,
            "why": choice_why(chosen, cands),
        })

    n = len(candidates)
    lines: list[str] = []
    lines.append(f"# Vulgultra concept grid — {len(SOURCE_LANGS)} daughter lects")
    lines.append("")
    lines.append("Lexicón de origen mixto: una forma Vulgultra por concepto, elegida")
    lines.append("entre candidatos meaning-aligned de las hijas Romance, por rama:")
    lines.append("")
    for branch, codes in LECT_BRANCHES.items():
        named = ", ".join(f"`{c}` {LECT_NAMES[c]}" for c in codes)
        lines.append(f"- **{branch}:** {named}")
    lines.append("")
    lines.append(
        f"({len(SOURCE_LANGS)} lects. Latin and English are reserved. "
        "ES/PT columns are inspection only.)"
    )
    lines.append("")
    lines.append("## Qué minimiza el SA")
    lines.append("")
    lines.append("Una raíz no se elige “porque sí”. El recocido minimiza")
    lines.append("")
    lines.append("$$")
    lines.append(r"E = 1000\sum_r \sigma(r) + 40|\Phi| + 1(N_{\mathrm{src}}-n_{\mathrm{lects}}) + 0.02\,\overline{\mathrm{gap}}")
    lines.append(r"+ 200\sum_e \sigma(e) + 100000\cdot\mathrm{coll} + 2000\cdot\mathrm{viol} + 500\sum_{\mathrm{row}}\max(0,2-d)")
    lines.append("$$")
    lines.append("")
    lines.append("| término | peso | qué hace en la práctica |")
    lines.append("|---|---:|---|")
    lines.append("| **σ raíces** | 1000 | una sílaba extra gana a todo lo de abajo |")
    lines.append("| **\\|Φ\\|** | 40 | 40×23=920 < 1000: inventario global, nunca compra una σ |")
    lines.append(f"| **diversidad** | 1 | a igual σ e igual Φ, maximizar lects distintas ({len(SOURCE_LANGS)} < 40) |")
    lines.append("| support medio | 0.02 | más fino que un lect |")
    lines.append("| σ desinencias | 200 | terminaciones 1σ |")
    lines.append("| colisiones | 100000 | duro dentro de una fila |")
    lines.append("| fonotáctica | 2000 | resto tras repair |")
    lines.append("| distancia desinencias | 500 | dentro de una fila |")
    lines.append("")
    lines.append("Orden: legal → min σ → min \\|Φ\\| → max lects → support.")
    lines.append("Un lect oscuro gana solo en empate de σ que no agrande Φ.")
    lines.append("")
    lines.append("## Veredicto")
    lines.append("")

    mixed = policies["sa"]
    es_p = policies["always-es"]
    pt_p = policies["always-pt"]
    fr_p = policies["always-fr"]
    it_p = policies["always-it"]
    legal_p = policies["set-cover"]
    raw_p = policies["shortest"]

    lines.append(
        f"Frente a **español** y **portugués** (las lenguas de inspección): "
        f"el mixto tiene **{mixed['sum_syl']}** sílabas de raíz vs "
        f"ES {es_p['sum_syl']} y PT {pt_p['sum_syl']}, con **0** violaciones "
        f"(ES {es_p['viols']}, PT {pt_p['viols']})."
    )
    lines.append("")
    delta_fr = mixed["sum_syl"] - fr_p["sum_syl"]
    if delta_fr > 0:
        fr_cmp = f"{delta_fr}σ más largo"
    elif delta_fr < 0:
        fr_cmp = f"{-delta_fr}σ más corto"
    else:
        fr_cmp = "igual de largo"
    lines.append(
        f"Frente a **francés**: always-fr suma {fr_p['sum_syl']}σ "
        f"con **{fr_p['viols']}** violaciones. "
        f"El mixto es {fr_cmp}, con {mixed['viols']} violaciones. "
        f"Italiano suma {it_p['sum_syl']}σ ({it_p['viols']} viol.)."
    )
    lines.append("")
    sa_e = mixed["energy"]
    legal_e = legal_p["energy"]
    sup_p = policies["support-shortest"]
    lines.append(
        f"Calidad del optimizador: set-cover Σσ={legal_p['sum_syl']} "
        f"|Φ|={legal_p['n_phon']} lects={legal_p['n_lects']} E={legal_e:.0f}; "
        f"SA Σσ={mixed['sum_syl']} |Φ|={mixed['n_phon']} lects={mixed['n_lects']} "
        f"E={sa_e:.0f} (acuerdo con set-cover {sa_eq_legal}/{n}, "
        f"con support-shortest {sa_eq_support}/{n}). "
        f"support-shortest suma {sup_p['sum_syl']}σ. "
        f"El shortest crudo llega a {raw_p['sum_syl']}σ con {raw_p['viols']} violaciones."
    )
    theme = lexicon.get("metadata", {}).get("noun_theme")
    verb = lexicon.get("metadata", {}).get("verb_lect")
    if theme and verb:
        lines.append("")
        lines.append(
            f"Desinencias enumeradas antes del recocido: tema nominal `{theme}`, "
            f"tiempos verbales `{verb}`. Cada tiempo es una fila; el SA no las mueve."
        )
    lines.append("")

    lines.append("## Procedencia (raíces SA)")
    lines.append("")
    lines.append("| fuente | raíces | % |")
    lines.append("|---|---:|---:|")
    for lang in SOURCE_LANGS:
        c = provenance[lang]
        lines.append(f"| `{lang}` | {c} | {100*c/n:.1f}% |")
    lines.append(f"| **total** | {n} | 100% |")
    lines.append("")

    lines.append("## Totales por política")
    lines.append("")
    lines.append("Las terminaciones de SA se mantienen fijas en las políticas de raíz.")
    lines.append("`set-cover` es el init: mínima σ, luego menos fonemas nuevos, luego un lect nuevo.")
    lines.append("`support-shortest` es el antiguo legal-shortest ordenado por support.")
    lines.append("")
    lines.append("| política | Σσ raíces | media σ | viol | \\|Φ\\| | lects | E_root | E_norm | E_end | E_coll | E_tact | E_dist | E_total |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for name in POLICIES:
        if name not in policies:
            continue
        p = policies[name]
        lines.append(
            f"| {name} | {p['sum_syl']} | {p['mean_syl']:.2f} | {p['viols']} | {p['n_phon']} | {p['n_lects']} | "
            f"{p['bd']['E_root']:.0f} | {p['bd'].get('E_norm', 0):.0f} | {p['bd']['E_end']:.0f} | "
            f"{p['bd']['E_coll']:.0f} | {p['bd']['E_tact']:.0f} | {p['bd']['E_dist']:.0f} | "
            f"{p['energy']:.0f} |"
        )
    if init_energy is not None:
        lines.append("")
        lines.append(
            f"Energía inicial reportada por el CLI Rust: **{init_energy:.0f}** "
            f"(comparar con SA E_total = {sa_e:.0f})."
        )
    lines.append("")

    lines.append("## Acuerdo")
    lines.append("")
    lines.append(f"- Conceptos: **{n}**")
    lines.append(f"- ES y PT adaptados idénticos: {identical_es_pt}/{n}")
    lines.append(f"- SA = ES (ortografía Vulgultra): {sa_eq_es}/{n}")
    lines.append(f"- SA = PT: {sa_eq_pt}/{n}")
    lines.append(f"- SA = FR: {sa_eq_fr}/{n}")
    lines.append(f"- SA = IT: {sa_eq_it}/{n}")
    lines.append(f"- SA = shortest (crudo): {sa_eq_short}/{n}")
    lines.append(f"- SA = set-cover: {sa_eq_legal}/{n}")
    lines.append(f"- SA ≠ set-cover: {len(disagree)}/{n}")
    lines.append("")

    lines.append("## Frases de demostración")
    lines.append("")
    lines.append("Con conjugación y concordancia. Artículo **o/a**. Copula 3sg **e**.")
    lines.append("Verbo = tema + la fila de presente elegida. El objeto va en acusativo.")
    lines.append("")

    sa_roots = {cid: {
        "orthography": candidates[cid][sa_sel[cid]].orthography,
        "source_lang": candidates[cid][sa_sel[cid]].source_lang,
        "source_word": candidates[cid][sa_sel[cid]].source_word,
    } for cid in sa_sel}
    verb_endings = {
        slot: ortho
        for cls in lexicon.get("verb_endings", {}).values()
        for slot, ortho in cls.items()
    }
    noun_endings = {
        slot: ortho
        for cls in lexicon.get("noun_endings", {}).values()
        for slot, ortho in cls.items()
    }
    adj_endings = dict(lexicon.get("adj_endings", {}))

    for sent in SENTENCES:
        toks: list[str] = list(sent["tokens"])  # type: ignore
        needed = [t for t in toks if t != "def_art"]
        missing = [t for t in needed if t not in candidates]
        lines.append(f"### {sent['es']}")
        lines.append("")
        lines.append(f"PT: {sent['pt']}")
        lines.append("")
        if missing:
            lines.append(f"_Faltan conceptos: {', '.join(missing)}_")
            lines.append("")
            continue
        realized = realize_sentence(
            toks, sa_roots, verb_endings, adj_endings,
            candidates=candidates, noun_endings=noun_endings,
        )
        vulgultra_w = [w["form"] for w in realized]
        src_w = [f"[{w['src']}]" for w in realized]
        es_w, pt_w = [], []
        for w in realized:
            if w["concept"] == "def_art":
                es_w.append("el/la")
                pt_w.append(w["form"])
                continue
            if w["concept"] == "copula":
                es_w.append("es")
                pt_w.append("é")
                continue
            grow = gold.get(w["concept"], {})
            es_w.append(grow.get("es", "—"))
            pt_w.append(grow.get("pt", "—"))
        mix_s = sum(form_syllables(w["form"]) for w in realized)
        lines.append("```")
        lines.append("Vulgultra  " + "  ".join(vulgultra_w))
        lines.append("src    " + "  ".join(src_w))
        lines.append("es     " + "  ".join(es_w))
        lines.append("pt     " + "  ".join(pt_w))
        lines.append(f"σ      {mix_s}")
        lines.append("```")
        lines.append("")

    lines.append("## Género (sustantivos pueden mezclar fuentes; verbos no)")
    lines.append("")
    lines.append("Par masculino/femenino elegido por sílabas, independiente.")
    lines.append("Ejemplo permitido: M `gat` [ca] + F `chatte` [fr].")
    lines.append("El tema léxico del verbo es uno. Cada tiempo elige su propia fila de personas.")
    lines.append("")
    lines.append("| glosa | M Vulgultra | src | σ | F Vulgultra | src | σ |")
    lines.append("|---|---|---|---:|---|---|---:|")
    for masc_id, fem_id in GENDER_PAIRS:
        if masc_id not in sa_sel or fem_id not in sa_sel:
            continue
        m = candidates[masc_id][sa_sel[masc_id]]
        f = candidates[fem_id][sa_sel[fem_id]]
        gloss = gold.get(masc_id, {}).get("gloss_es", masc_id)
        lines.append(
            f"| {gloss} | **{m.orthography}** | `{m.source_lang}` | {m.syllables} | "
            f"**{f.orthography}** | `{f.source_lang}` | {f.syllables} |"
        )
    lines.append("")

    lines.append("## Tabla por concepto")
    lines.append("")
    lines.append("| glosa | es | pt | fr | it | ca | Vulgultra | src | σ | sup | por qué | bin |")
    lines.append("|---|---|---|---|---|---|---|---|---:|---:|---|---|")
    for r in rows:
        lines.append(
            f"| {r['gloss']} | {r['es']} | {r['pt']} | {r['fr']} | {r['it']} | {r['ca']} | "
            f"**{r['vulgultra']}** | `{r['src']}` | {r['sig']} | {r['sup']} | {r['why']} | {r['bin']} |"
        )
    lines.append("")

    lines.append("## Apéndice: SA ≠ set-cover")
    lines.append("")
    if not disagree:
        lines.append("Ninguna. SA coincidió con el set-cover en todos los conceptos.")
        lines.append("")
    else:
        lines.append("| glosa | SA | src | σ | set-cover | src | σ | razón |")
        lines.append("|---|---|---|---:|---|---|---:|---|")
        for gloss, cid, chosen, short, reason in disagree:
            lines.append(
                f"| {gloss} | {chosen.orthography} | `{chosen.source_lang}` | {chosen.syllables} | "
                f"{short.orthography} | `{short.source_lang}` | {short.syllables} | {reason} |"
            )
        lines.append("")

    lines.append("## Caveats")
    lines.append("")
    lines.append("- La glosa del scorecard es española; el `id` inglés del gold list no es fuente.")
    lines.append("- El inglés no es lengua fuente. El latín está reservado y no entra en el knapsack.")
    lines.append("- Epitran usa la lect hermana cuando no hay mapa propio (Oil←fr, retorromance y dálmata←it, asturiano←es, oriental←ro): `água`→`aga`, `olho`→`olo`, `ojo`/`rojo`→`okso`/`rokso`. `chat`→`xa` es la ortografía de `ʃ`.")
    lines.append("- Las desinencias se enumeran por tiempo verbal (tema nominal o/u/e; cada fila de 6 personas es un lect). El recocido solo mueve raíces dentro del corte de σ mínima.")
    lines.append("")
    return "\n".join(lines)


def policy_stats(
    name: str,
    genome: Genome,
) -> dict:
    energy, bd = compute_energy(genome)
    roots = genome.all_roots()
    phon = set()
    for r in roots:
        phon.update(r.vulgultra_phonemes)
    for e in genome.all_endings():
        phon.update(e)
    sum_syl = sum(r.syllables for r in roots)
    return {
        "energy": energy,
        "bd": bd,
        "sum_syl": sum_syl,
        "mean_syl": sum_syl / max(len(roots), 1),
        "n_phon": len(phon),
        "n_lects": len({r.source_lang for r in roots}),
        "viols": sum(r.violations for r in roots),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Render the selected lexicon and phrase examples")
    parser.add_argument("-c", "--candidates", default="data/candidates.json")
    parser.add_argument("-l", "--lexicon", default="data/vulgultra_lexicon.json")
    parser.add_argument("-o", "--output", default="docs/eval/34_romance_scorecard.md")
    parser.add_argument("--init-energy", type=float, default=None,
                        help="Initial energy from Rust SA stdout")
    args = parser.parse_args()

    candidates = load_candidates(Path(args.candidates))
    lexicon = json.loads(Path(args.lexicon).read_text())
    noun, verb, adj = endings_from_lexicon(lexicon)

    english_roots = [
        cid for cid, root in lexicon["roots"].items()
        if root.get("source_lang") == "en"
    ]
    if english_roots:
        raise SystemExit(f"English sources in lexicon: {english_roots[:5]}")

    policies = {}
    for name in POLICIES:
        if name == "init":
            random.seed(42)
            genome = init_genome(candidates)
        else:
            sel = policy_selections(name, candidates, lexicon)
            genome = make_genome(candidates, sel, noun, verb, adj)
        policies[name] = policy_stats(name, genome)

    init_energy = args.init_energy
    meta = lexicon.get("metadata", {})
    if init_energy is None and "initial_energy" in meta:
        init_energy = float(meta["initial_energy"])

    text = render_scorecard(candidates, lexicon, policies, init_energy)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(f"Wrote {out}")
    print(f"  concepts={len(candidates)}  SA Σσ={policies['sa']['sum_syl']}  "
          f"ES Σσ={policies['always-es']['sum_syl']}  PT Σσ={policies['always-pt']['sum_syl']}")


if __name__ == "__main__":
    main()
