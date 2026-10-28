#!/usr/bin/env python3
"""Reproducible exploratory scan of the FORSEE France and Ireland press files.

Counts use article-level units. The near flag means a theme term falls within
500 characters of a data-centre mention; it is a screening aid, not coding.
"""
import csv
from difflib import SequenceMatcher
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT.parent / "Presse_LL_été_2025"
FILES = {
    "France": DATA / "France/france/FR_pol.txt",
    "Ireland": DATA / "Irlande/irish/IR_pol.txt",
}
# Corpus language is explicit metadata, independent of publication country.
LANGUAGES = {"France": "French", "Ireland": "English"}
PAT = {
    "France": {
        "dc": r"\b(?:centres? de donn[ée]es|data[ -]?cent(?:er|re)s?|centres? informatiques?)\b",
        "ecology": r"\b(?:[ée]cologi\w*|environnement\w*|climat\w*|carbone|carbon[ée]e?s?|d[ée]carbon\w*|[ée]missions?|gaz [àa] effet de serre|pollution|polluant\w*|eau|hydriqu\w*|durabl\w*|renouvelabl\w*|r[ée]chauffement)\b",
        "energy": r"\b(?:[ée]nergi\w*|[ée]lectri\w*|r[ée]seau [ée]lectrique|consommation [ée]lectrique|nucl[ée]aire|[ée]nergivore\w*)\b",
        "sovereignty": r"\b(?:souverain\w*|autonomi\w* strat[ée]gique|ind[ée]pendance (?:num[ée]rique|technologique)|d[ée]pendance\w* (?:technologique|num[ée]rique|am[ée]ricaine|aux (?:g[ée]ants|[ée]tats-unis))|contr[ôo]le (?:des donn[ée]es|de nos donn[ée]es))\b",
        "ai": r"\b(?:intelligence artificielle|\bIA\b|\bAI\b|ChatGPT|GPT-\d)\b",
    },
    "Ireland": {
        "dc": r"\b(?:data[ -]?cent(?:er|re)s?|server farms?)\b",
        "ecology": r"\b(?:ecolog\w*|environment\w*|climat\w*|carbon\w*|emissions?|greenhouse gas\w*|pollut\w*|water|sustainab\w*|renewab\w*|green energy|net[ -]?zero)\b",
        "energy": r"\b(?:energ\w*|electric\w*|power (?:grid|demand|supply|consumption|generation)|grid|megawatts?|gigawatts?)\b",
        "sovereignty": r"\b(?:sovereign\w*|strategic autonom\w*|digital autonom\w*|technological independen\w*|dependen\w* on (?:US|American|foreign) (?:tech\w*|compan\w*|providers?)|data (?:residen\w*|localis\w*|localiz\w*))\b",
        "ai": r"\b(?:artificial intelligence|\bAI\b|ChatGPT|GPT-\d)\b",
    },
}
RX = {country: {k: re.compile(v, re.I) for k, v in patterns.items()} for country, patterns in PAT.items()}


def metadata(header):
    tags = dict(re.findall(r"\*([^\s_]+)_(\S+)", header))
    date = re.search(r"\*date_(\d{4})[_-](\d{1,2})[_-](\d{1,2})", header)
    return {
        "date": "-".join((date.group(1), date.group(2).zfill(2), date.group(3).zfill(2))) if date else "",
        "source": tags.get("source", tags.get("s", "")),
        "category": tags.get("cat", ""),
        "political_label": tags.get("pol", ""),
    }


def clean(s):
    return re.sub(r"\s+", " ", s).strip()


rows = []
baseline = defaultdict(Counter)
source_totals = defaultdict(Counter)
for country, file in FILES.items():
    raw = file.read_text(encoding="utf-8-sig", errors="replace")
    articles = re.split(r"(?m)^\*\*\*\*\s+", raw)[1:]
    seen_openings = {}
    for index, article in enumerate(articles, 1):
        header, body = article.split("\n", 1)
        meta = metadata(header)
        baseline[country]["raw_articles"] += 1
        # Confirm matching openings against body length and text similarity;
        # some distinct newspaper extracts share a lead but differ later.
        dedup_key = (meta["date"], meta["source"], clean(body)[:100])
        previous = seen_openings.get(dedup_key)
        if (previous is not None and abs(len(body) - len(previous)) / max(len(body), len(previous)) < .1
                and SequenceMatcher(None, body[:1500], previous[:1500]).ratio() > .98):
            baseline[country]["probable_duplicates_removed"] += 1
            continue
        seen_openings[dedup_key] = body
        dc = list(RX[country]["dc"].finditer(body))
        baseline[country]["all_articles"] += 1
        baseline[country]["all_" + meta["date"][:4]] += 1
        source_totals[country][meta["source"]] += 1
        if not dc:
            continue
        baseline[country]["dc_articles"] += 1
        terms = {}
        for theme in ("ecology", "energy", "sovereignty", "ai"):
            matches = list(RX[country][theme].finditer(body))
            near = [m for m in matches if any(m.start() < d.end() + 500 and m.end() > d.start() - 500 for d in dc)]
            terms[theme + "_article"] = bool(matches)
            terms[theme + "_near"] = bool(near)
            terms[theme + "_near_count"] = len(near)
        snippets = []
        for d in dc[:4]:
            start, end = max(0, d.start() - 220), min(len(body), d.end() + 380)
            snippets.append(clean(body[start:end]))
        rows.append({"id": f"{'FR' if country == 'France' else 'IE'}-{index:05d}", "country": country,
                     **meta, "language": LANGUAGES[country], "dc_mentions": len(dc), "length": len(body), "opening": clean(body[:260]),
                     "snippets": snippets, **terms})

fields = [k for k in rows[0] if k != "snippets"]
with (ROOT / "screened_articles.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows({k: v for k, v in r.items() if k != "snippets"} for r in rows)
with (ROOT / "dashboard_data.json").open("w", encoding="utf-8") as f:
    json.dump(rows, f, ensure_ascii=False, separators=(",", ":"))

summary = {}
for country in FILES:
    subset = [r for r in rows if r["country"] == country]
    strong = [r for r in subset if r["dc_mentions"] >= 2]
    summary[country] = {
        "raw_articles": baseline[country]["raw_articles"],
        "probable_duplicates_removed": baseline[country]["probable_duplicates_removed"],
        "articles": baseline[country]["all_articles"],
        "date_min": min(r["date"] for r in subset), "date_max": max(r["date"] for r in subset),
        "dc_articles": len(subset), "dc_mentions": sum(r["dc_mentions"] for r in subset),
        "sustained_articles_2plus": len(strong),
        "by_year": {y: {"all": baseline[country]["all_" + y],
                       "dc": sum(r["date"].startswith(y) for r in subset)} for y in ("2022", "2023", "2024", "2025")},
        "sources": dict(Counter(r["source"] for r in subset)),
        "source_totals": dict(source_totals[country]),
        "themes_all": {theme: {"article": sum(r[theme + "_article"] for r in subset),
                               "near": sum(r[theme + "_near"] for r in subset)}
                       for theme in ("ecology", "energy", "sovereignty", "ai")},
        "themes_sustained": {theme: {"article": sum(r[theme + "_article"] for r in strong),
                                     "near": sum(r[theme + "_near"] for r in strong)}
                             for theme in ("ecology", "energy", "sovereignty", "ai")},
        "joint_near": {"eco_and_sov": sum(r["ecology_near"] and r["sovereignty_near"] for r in subset),
                       "eco_only": sum(r["ecology_near"] and not r["sovereignty_near"] for r in subset),
                       "sov_only": sum(r["sovereignty_near"] and not r["ecology_near"] for r in subset),
                       "neither": sum(not r["sovereignty_near"] and not r["ecology_near"] for r in subset)},
    }
with (ROOT / "summary.json").open("w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)
with (ROOT / "newspaper_distribution.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["country", "source", "all_ai_corpus_articles", "data_centre_articles",
                     "percent_of_outlet_ai_corpus", "percent_of_country_data_centre_subset"])
    for country, item in summary.items():
        for source, count in sorted(item["sources"].items(), key=lambda x: -x[1]):
            all_count = item["source_totals"][source]
            writer.writerow([country, source, all_count, count, round(100 * count / all_count, 2),
                             round(100 * count / item["dc_articles"], 2)])
print(json.dumps(summary, ensure_ascii=False, indent=2))
