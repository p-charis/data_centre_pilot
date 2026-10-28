#!/usr/bin/env python3
"""Export screened data-centre articles as two IRaMuTeQ text corpora."""
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parent
source = root.parent / "Presse_LL_été_2025"
files = {
    "FR": source / "France/france/FR_pol.txt",
    "IE": source / "Irlande/irish/IR_pol.txt",
}
screened = json.loads((root / "dashboard_data.json").read_text(encoding="utf-8"))
screened_by_id = {r["id"]: r for r in screened}
selected = {country: {int(r["id"].split("-")[1]) for r in screened if r["id"].startswith(country + "-")}
            for country in files}
out = root / "iramuteq_subcorpora"
out.mkdir(exist_ok=True)
for country, path in files.items():
    articles = re.split(r"(?m)^\*\*\*\*\s+", path.read_text(encoding="utf-8-sig", errors="replace"))[1:]
    selected_articles = []
    selected_without_les_echos = []
    for number, raw in enumerate(articles, 1):
        if number not in selected[country]:
            continue
        header, body = raw.split("\n", 1)
        # Original source/date/category metadata are retained. The stable ID
        # permits class segments to be traced back to the reading dashboard.
        exported = f"**** {header.strip()} *dcid_{country}{number:05d}\n{body.strip()}\n"
        selected_articles.append(exported)
        if country == "FR" and screened_by_id[f"FR-{number:05d}"]["source"] != "les_echos":
            selected_without_les_echos.append(exported)
    assert len(selected_articles) == len(selected[country])
    destination = out / f"{country}_data_centres_all.txt"
    destination.write_text("\n".join(selected_articles), encoding="utf-8")
    print(f"{destination}: {len(selected_articles)} articles")
    if country == "FR":
        filtered_destination = out / "FR_data_centres_all_excluding_les_echos.txt"
        filtered_destination.write_text("\n".join(selected_without_les_echos), encoding="utf-8")
        print(f"{filtered_destination}: {len(selected_without_les_echos)} articles")
