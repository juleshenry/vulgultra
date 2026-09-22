#!/usr/bin/env python3
"""Low-hanging slice of plano_novo: lemma families + one-shot únicos."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from vulgultra.families import (  # noqa: E402
    build_families,
    classify_family,
    load_lemmas,
    split_false_friends,
    family_stats,
)
from vulgultra.phonology import (  # noqa: E402
    count_syllables,
    count_violations,
    ipa_to_vulgultra,
    overlay_spelling_contrasts,
    repair,
    to_orthography,
    word_to_ipa,
)
from vulgultra.skeleton import skeleton, split_frame  # noqa: E402

OUT_DIR = ROOT / "data" / "eval"


def phonemize(word: str, lang: str) -> dict:
    """Source citation in, phonemes out. Letters are a view of the phonemes."""
    ipa = word_to_ipa(word, lang)
    ph = repair(overlay_spelling_contrasts(word, ipa_to_vulgultra(ipa)))
    return {
        "citation": word,
        "lang": lang,
        "ipa": ipa,
        "phonemes": ph,
        "syllables": count_syllables(ph),
        "violations": count_violations(ph),
        "skeleton": skeleton(word),
        "frame": split_frame(word)[1],
        "render": to_orthography(ph),
    }


def pick_contest(families: dict[str, list[dict]], want: set[str]) -> dict | None:
    for sk, members in families.items():
        cites = {m["citation"].lower() for m in members}
        if want <= cites or any(w in cites for w in want) and len({m["lang"] for m in members}) >= 2:
            if any(w in cites for w in want):
                return {"skeleton": sk, "members": members}
    return None


def main() -> None:
    print("loading lemmas…")
    rows = load_lemmas()
    print(f"  {len(rows)} headwords")
    families = build_families(rows)
    stats = family_stats(families)
    print(json.dumps(stats, indent=2))

    # Sample contests: cat, obra/ópera
    cat = pick_contest(families, {"chat", "gato", "gat"})
    obra = pick_contest(families, {"obra", "ópera", "opera"})

    spelled_cat = []
    if cat:
        seen = set()
        for m in cat["members"]:
            key = (m["lang"], m["open"].lower())
            if key in seen:
                continue
            seen.add(key)
            if m["open"].lower() in {"chat", "gato", "gat", "gatto", "catt"}:
                try:
                    spelled_cat.append(phonemize(m["open"], m["lang"]))
                except Exception as e:
                    spelled_cat.append({"citation": m["open"], "lang": m["lang"], "error": str(e)})
            if len(spelled_cat) >= 8:
                break
        spelled_cat.sort(key=lambda r: (r.get("syllables", 99), r.get("lang", "")))

    spelled_obra = []
    if obra:
        for m in obra["members"]:
            if m["open"].lower() in {"obra", "opera", "ópera", "opéra"}:
                try:
                    spelled_obra.append(phonemize(m["open"], m["lang"]))
                except Exception as e:
                    spelled_obra.append({"citation": m["open"], "lang": m["lang"], "error": str(e)})
        spelled_obra.sort(key=lambda r: (r.get("syllables", 99), -len(r.get("citation", ""))))

    unico = phonemize("meteoropatico", "it")

    # A few one-lect families as únicos, no G2P flood: just list 12 citations.
    unico_cites = []
    for sk, members in families.items():
        for group in split_false_friends(members):
            if classify_family(group) == "unico" and len(group[0]["open"]) >= 8:
                unico_cites.append(group[0])
        if len(unico_cites) >= 12:
            break

    lects = Counter()
    for members in families.values():
        if classify_family(members) == "contest":
            lects.update({m["lang"] for m in members})

    preview = {
        "stats": stats,
        "lects_in_contests": dict(lects.most_common()),
        "cat_family": {
            "skeleton": cat["skeleton"] if cat else None,
            "n": len(cat["members"]) if cat else 0,
            "spelled_shortest_first": spelled_cat,
        },
        "obra_opera": {
            "skeleton": obra["skeleton"] if obra else None,
            "n": len(obra["members"]) if obra else 0,
            "spelled_shortest_first": spelled_obra,
            "winner_if_syllables": spelled_obra[0] if spelled_obra else None,
        },
        "cultismo_unico": unico,
        "unico_lemma_sample": unico_cites,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / "families_preview.json"
    path.write_text(json.dumps(preview, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {path}")
    print("único meteoropatico phonemes", " ".join(unico["phonemes"]), "render", unico["render"], f"{unico['syllables']}σ")
    if spelled_obra:
        w = spelled_obra[0]
        print("obra/ópera shortest citation", w["lang"], w["citation"], "σ", w["syllables"], "render", w["render"])
    if spelled_cat:
        w = spelled_cat[0]
        print("cat shortest citation", w["lang"], w["citation"], "σ", w["syllables"], "render", w["render"])


if __name__ == "__main__":
    main()
