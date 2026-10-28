#!/usr/bin/env python3
"""Build a full-text local explorer and a text-free public Pages preview."""
import html
import base64
import csv
import hashlib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

# Importing analyse refreshes screening and reuses the exact dictionaries.
from analyse import FILES, PAT, clean
from theme_info import theme_dictionary

root = Path(__file__).resolve().parent
template = (root / "explorer.template").read_text(encoding="utf-8")
records = json.loads((root / "dashboard_data.json").read_text(encoding="utf-8"))
actor_data = json.loads((root / "actor_analysis/actors_data.json").read_text(encoding="utf-8"))
assert set(actor_data['articles']) == {r['id'] for r in records}, 'Rebuild actor analysis for this selection.'
assert actor_data['method']['registry_sha256'] == hashlib.sha256((root / 'actor_analysis/registry.json').read_bytes()).hexdigest(), 'Actor registry changed: run actor_analysis/build_actors.py.'
outlet_names = {"la_croix": "La Croix", "le_monde": "Le Monde", "le_figaro": "Le Figaro",
                "les_echos": "Les Échos", "aujourdhui_en_france": "Aujourd'hui en France",
                "libération": "Libération", "lhumanité": "L'Humanité",
                "TheIrishTimes": "The Irish Times", "IrishIndependent": "Irish Independent",
                "IrishDailyMail": "Irish Daily Mail", "irishmirrorie": "Irish Mirror"}

dendrograms = [
    {"slug":"france_with_les_echos", "title": "France · including Les Échos", "n": 642, "classes": 11, "classified": "97.2%",
     "image": "iramuteq_subcorpora/FR_data_centres_all_corpus_1/FR_data_centres_all_alceste_2/dendrogramme_1.png",
     "profiles_csv": "iramuteq_subcorpora/FR_data_centres_all_corpus_1/FR_data_centres_all_alceste_2/profiles.csv",
     "tip_order": [4,10,11,5,8,9,6,7,2,3,1],
     "edges": [[12,13],[13,14],[14,15],[15,1],[15,16],[16,2],[16,3],[14,17],[17,4],[17,18],[18,5],[18,6],[13,19],[19,7],[19,8],[12,20],[20,21],[21,9],[21,10],[20,11]],
     "profiles": [
      (1,"11.5%","AI investment and venture capital","Billion, euros, funds, investment, OpenAI"),
      (2,"11.7%","Company results and markets","Quarter, revenue, results, analysts, stock market"),
      (3,"14.3%","Semiconductors and technology firms","Chips, NVIDIA, Microsoft, processors, Intel, AMD"),
      (4,"4.6%","Research and higher education","Universities, students, laboratories, researchers"),
      (5,"4.0%","French political summits","Macron, ministers, summits, events"),
      (6,"5.6%","Data cables and connectivity","Data centres, Marseille, cables, submarine links"),
      (7,"14.1%","Energy and environmental costs","Electricity, consumption, carbon, gas, water"),
      (8,"6.7%","European regulation and law","European Union, Commission, decrees, public policy"),
      (9,"10.9%","China, Europe and geopolitics","China, United States, Europe, political, military"),
      (10,"12.9%","AI, work and human tasks","AI, tools, tasks, people, work, responses"),
      (11,"3.7%","Generative media","Images, video, voice, text, recognition, artists") ]},
    {"slug":"france_without_les_echos", "title": "France · excluding Les Échos", "n": 348, "classes": 8, "classified": "96.3%",
     "image": "iramuteq_subcorpora/FR_data_centres_all_excluding_les_echos_corpus_1/FR_data_centres_all_excluding_les_echos_alceste_1/dendrogramme_1.png",
     "profiles_csv": "iramuteq_subcorpora/FR_data_centres_all_excluding_les_echos_corpus_1/FR_data_centres_all_excluding_les_echos_alceste_1/profiles.csv",
     "tip_order": [1,3,8,6,7,4,5,2],
     "edges": [[9,10],[10,1],[10,11],[11,12],[12,2],[12,3],[11,13],[13,4],[13,5],[9,14],[14,15],[15,6],[15,7],[14,8]],
     "profiles": [
      (1,"14.3%","Electricity and resource consumption","Electricity, consumption, energy, water, carbon"),
      (2,"11.8%","French and Gulf investment summits","Euros, Macron, France, investment, Paris, Gulf"),
      (3,"8.0%","Digital governance and EU regulation","Digital, democracy, privacy, regulation, ethics"),
      (4,"15.1%","Markets and semiconductor firms","NVIDIA, revenue, business, quarter, stock market"),
      (5,"11.9%","US political leadership and trade","Trump, Biden, administration, tariffs, president"),
      (6,"16.1%","AI models, cloud and computing","Models, computing, AI, clients, training, cloud"),
      (7,"3.9%","Generative images and media","Images, video, text, voice, Midjourney"),
      (8,"18.9%","Omitted from interpretation · function-word class","French function words (e.g. ‘ne’, ‘pas’, ‘nous’); likely residual/noise") ]},
    {"slug":"ireland", "title": "Ireland", "n": 154, "classes": 8, "classified": "81.5%",
     "image": "iramuteq_subcorpora/IE_data_centres_all_corpus_1/IE_data_centres_all_alceste_1/dendrogramme_1.png",
     "profiles_csv": "iramuteq_subcorpora/IE_data_centres_all_corpus_1/IE_data_centres_all_alceste_1/profiles.csv",
     "tip_order": [6,2,1,4,5,3,7,8],
     "edges": [[9,10],[10,11],[11,1],[11,2],[10,12],[12,3],[12,13],[13,4],[13,5],[9,14],[14,15],[15,6],[15,7],[14,8]],
     "profiles": [
      (1,"7.7%","EU rules and regulation","EU, regulation, legislation, law, directives"),
      (2,"8.1%","Fossil fuels and climate","Gas, emissions, carbon, climate, energy"),
      (3,"13.0%","Semiconductors and chip firms","Chips, Intel, NVIDIA, Taiwan, technology firms"),
      (4,"13.5%","Skills and regional workforce","Skills, training, talent, regional programmes, engineers"),
      (5,"12.4%","Foreign investment and the economy","Investment, tax, foreign firms, economy"),
      (6,"17.4%","Data centres, electricity and the grid","Data centres, electricity, grid, demand, energy"),
      (7,"12.1%","Technology company earnings","Revenue, profits, Microsoft, quarterly results"),
      (8,"15.8%","Generative AI and language models","ChatGPT, language, models, AI, OpenAI") ]}
]


def english_tree_svg(item):
    """Render IRaMuTeQ's saved class-tree topology with English class summaries."""
    row_h, label_x, width = 74, 410, 1700
    top, height = 112, 142 + row_h * len(item["tip_order"])
    leaf_class = {i + 1: value for i, value in enumerate(item["tip_order"])}
    profile = {row[0]: row[1:] for row in item["profiles"]}
    children = {}
    for parent, child in item["edges"]:
        children.setdefault(parent, []).append(child)
    parent_nodes = {parent for parent, _ in item["edges"]}
    child_nodes = {child for _, child in item["edges"]}
    root_node = next(iter(parent_nodes - child_nodes))
    y_pos, depth = {}, {}
    def layout(node, level=0):
        depth[node] = level
        if node in leaf_class:
            y_pos[node] = top + (node - 1) * row_h
            return y_pos[node]
        ys = [layout(child, level + 1) for child in children[node]]
        y_pos[node] = sum(ys) / len(ys)
        return y_pos[node]
    layout(root_node)
    x_pos = {node: 42 + depth[node] * 46 for node in y_pos}
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="title desc" viewBox="0 0 {width} {height}" width="{width}" height="{height}">',
             '<title id="title">English-labelled class tree: '+html.escape(item["title"])+'</title>',
             '<desc id="desc">IRaMuTeQ hierarchical class-tree topology. Each leaf shows an English summary of leading class terms and its share of classified segments.</desc>',
             f'<rect width="{width}" height="{height}" rx="14" fill="#fbfcfb"/>',
             f'<text x="32" y="38" font-family="system-ui,sans-serif" font-size="25" font-weight="700" fill="#18383d">{html.escape(item["title"])}</text>',
             f'<text x="32" y="65" font-family="system-ui,sans-serif" font-size="14" fill="#5d7276">{item["n"]} articles · {item["classes"]} classes · {item["classified"]} of text segments classified</text>',
             f'<text x="{label_x}" y="94" font-family="system-ui,sans-serif" font-size="12" fill="#607478">ENGLISH CLASS SUMMARIES · SHARE OF CLASSIFIED SEGMENTS</text>']
    # Draw the saved branching topology. The RData object contains no edge lengths.
    for parent, nodes in children.items():
        ys = [y_pos[child] for child in nodes]
        parts.append(f'<path d="M{x_pos[parent]} {min(ys):.1f} V{max(ys):.1f}" fill="none" stroke="#76918f" stroke-width="2"/>')
        for child in nodes:
            parts.append(f'<path d="M{x_pos[parent]} {y_pos[child]:.1f} H{x_pos[child]}" fill="none" stroke="#76918f" stroke-width="2"/>')
    for leaf, class_id in leaf_class.items():
        share, label, terms = profile[class_id]
        y = y_pos[leaf]
        row_top = y - row_h / 2 + 3
        parts.append(f'<path d="M{x_pos[leaf]} {y:.1f} H{label_x - 22}" fill="none" stroke="#76918f" stroke-width="2"/>')
        parts.append(f'<rect x="{label_x}" y="{row_top:.1f}" width="{width-label_x-24}" height="{row_h-5}" rx="8" fill="#f0f5f3"/>')
        parts.append(f'<text x="{label_x+13}" y="{y-9:.1f}" font-family="system-ui,sans-serif" font-size="13" font-weight="700" fill="#17645e">CLASS {class_id} · {share}</text>')
        parts.append(f'<text x="{label_x+145}" y="{y-9:.1f}" font-family="system-ui,sans-serif" font-size="16" font-weight="650" fill="#20383c">{html.escape(label)}</text>')
        parts.append(f'<text x="{label_x+145}" y="{y+14:.1f}" font-family="system-ui,sans-serif" font-size="13" fill="#53696d">{html.escape(terms)}</text>')
    parts.append(f'<text x="32" y="{height-18}" font-family="system-ui,sans-serif" font-size="12" fill="#66797c">Branch layout shows the saved class-tree topology only; the exported tree has no branch-length or distance values. English terms are concise translations/summaries of leading class words.</text>')
    parts.append('</svg>')
    return ''.join(parts)


def dendrogram_section():
    tabs, panels = [], []
    output_dir = root / "iramuteq_subcorpora/translated_dendrograms_en"
    output_dir.mkdir(exist_ok=True)
    for index, item in enumerate(dendrograms):
        svg = english_tree_svg(item)
        (output_dir / f'{item["slug"]}.svg').write_text(svg, encoding="utf-8")
        image = base64.b64encode(svg.encode("utf-8")).decode("ascii")
        raw_image = base64.b64encode((root / item["image"]).read_bytes()).decode("ascii")
        class_stats = {}
        current_class = None
        with (root / item["profiles_csv"]).open(encoding="utf-8-sig", newline="") as source:
            for row in csv.reader(source, delimiter=";"):
                if len(row) > 2 and row[1] == "classe":
                    current_class = int(row[2].strip())
                elif current_class is not None and len(row) > 3 and row[0] == "****":
                    class_stats[current_class] = (int(row[1].strip()), float(row[3].strip()))
                    current_class = None
        warning = ('<p class="small class-caveat">Class 8 (18.9% of classified segments) is dominated by French function words. It remains visible in the tree but is omitted from substantive interpretation as likely residual/noise.</p>'
                   if item["title"].endswith("excluding Les Échos") else '')
        classified_warning = ('<p class="small class-caveat">Only 81.5% of segments were classified; interpret this solution more cautiously than the French runs.</p>'
                              if item["title"] == "Ireland" else '')
        rows = []
        for number, share, label, terms in item["profiles"]:
            count, exact_share = class_stats[number]
            status = '<span class="class-status">Likely noise · excluded from interpretation</span>' if number == 8 and item["title"].endswith("excluding Les Échos") else ''
            rows.append(f'<tr{" class=\"class-noise\"" if status else ""}><th scope="row">Class {number}</th><td>{count:,} <span class="small">({exact_share:.1f}%)</span></td><td>{html.escape(terms)}</td><td><strong>{html.escape(label)}</strong>{status}</td></tr>')
        tab_selected = 'true' if index == 0 else 'false'
        tabs.append(f'<button type="button" role="tab" id="tab-{item["slug"]}" aria-selected="{tab_selected}" aria-controls="panel-{item["slug"]}" data-profile="{item["slug"]}">{html.escape(item["title"])}</button>')
        hidden = '' if index == 0 else ' hidden'
        panels.append(f'<div class="profile-panel" id="panel-{item["slug"]}" role="tabpanel" aria-labelledby="tab-{item["slug"]}"{hidden}><p class="profile-meta">{item["n"]} articles · {item["classes"]} classes · {item["classified"]} of text segments classified</p>{warning}{classified_warning}<div class="table-scroll"><table class="class-table"><thead><tr><th>Thematic class</th><th>Size</th><th>Leading words and phrases · English</th><th>Working summary</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div><details class="tree-details"><summary>View branching tree</summary><img class="english-tree" src="data:image/svg+xml;base64,{image}" alt="English-labelled IRaMuTeQ class tree for {html.escape(item["title"])}"></details><details class="raw-dendro"><summary>Original IRaMuTeQ class profile</summary><img src="data:image/png;base64,{raw_image}" alt="Original IRaMuTeQ class profile for {html.escape(item["title"])}"></details></div>')
    return '<section id="dendrograms"><h2>IRaMuTeQ class profiles</h2><div class="profile-tabs" id="profileTabs" role="tablist" aria-label="Choose corpus">'+''.join(tabs)+'</div><p class="small profile-note">English translations summarize leading class terms; working summaries are interpretive labels, not official IRaMuTeQ class names. “Size” is the number and share of classified segments.</p>'+''.join(panels)+'</section>'


def card(label, n, total=0):
    suffix = f" · {100*n/total:.1f}%" if total else ""
    return f'<div class="card"><strong>{n:,}</strong><span>{label}{suffix}</span></div>'


def bar(label, count, maximum, total=0, cls="", outlet=False):
    width = 100 * count / maximum if maximum else 0
    share = f" · {100*count/total:.1f}%" if outlet and total else ""
    return (f'<div class="barrow{" outlet" if outlet else ""}"><span class="label">{html.escape(label)}</span>'
            f'<div class="track"><div class="fill {cls}" style="width:{width:.1f}%"></div></div>'
            f'<span class="value">{count}{share}</span></div>')


def article_card(r, has_full):
    tags = [r["id"], r["country"], r["date"], outlet_names.get(r["source"], r["source"]),
            f'{r["dc_mentions"]} DC mentions']
    head = ''.join(f'<span class="tag">{html.escape(str(t))}</span>' for t in tags)
    for key, label, cls in (("ecology_near", "Ecology", "eco"), ("energy_near", "Energy", "energy"),
                            ("sovereignty_near", "Sovereignty", "sov")):
        if r[key]:
            head += f'<span class="tag {cls}">{label}</span>'
    title = (f'<h3>{html.escape(r["opening"][:230])}{"…" if len(r["opening"]) > 230 else ""}</h3>'
             if r.get("opening") else "")
    button = (f'<button class="read-button" data-id="{r["id"]}">Read full article with highlighted matches</button>'
              if has_full else "")
    return f'<article class="result" id="{r["id"]}"><div class="tags">{head}</div>{title}{button}</article>'


def highlighted_article(body, country):
    text = clean(body)
    dc = list(re.finditer(PAT[country]["dc"], text, re.I))
    spans = [(m.start(), m.end(), "dc", 0) for m in dc]
    for priority, theme in enumerate(("ecology", "energy", "sovereignty"), 1):
        for match in re.finditer(PAT[country][theme], text, re.I):
            if any(match.start() < d.end() + 500 and match.end() > d.start() - 500 for d in dc):
                spans.append((match.start(), match.end(), theme, priority))
    spans.sort(key=lambda span: (span[0], span[3], -span[1]))
    result = []
    cursor = 0
    for start, end, theme, _ in spans:
        if start < cursor:
            continue
        result.append(html.escape(text[cursor:start]))
        result.append(f'<mark class="hit-{theme}" title="{theme}">{html.escape(text[start:end])}</mark>')
        cursor = end
    result.append(html.escape(text[cursor:]))
    return ''.join(result)


def normalize_search(text):
    text = ''.join(ch for ch in unicodedata.normalize('NFKD', text) if not unicodedata.category(ch).startswith('M'))
    return re.sub(r'\s+', ' ', re.sub(r'[^\w]+|_', ' ', text.casefold())).strip()


def full_articles():
    selected = {r["id"] for r in records}
    output = {}
    search_index = {}
    for country, file in FILES.items():
        prefix = "FR" if country == "France" else "IE"
        raw = file.read_text(encoding="utf-8-sig", errors="replace")
        articles = re.split(r"(?m)^\*\*\*\*\s+", raw)[1:]
        for index, article in enumerate(articles, 1):
            article_id = f"{prefix}-{index:05d}"
            if article_id in selected:
                body = article.split("\n", 1)[1]
                assert actor_data['articles'][article_id]['text_sha256'] == hashlib.sha256(clean(body).encode()).hexdigest(), f'Stale actor data: {article_id}'
                output[article_id] = highlighted_article(body, country)
                search_index[article_id] = normalize_search(body)
    assert len(output) == len(records)
    return output, search_index


def json_for_script(data):
    return json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def build(records_for_site, bodies, search_index, notice, actor_payload):
    n = len(records_for_site)
    eco = sum(r["ecology_near"] for r in records_for_site)
    energy = sum(r["energy_near"] for r in records_for_site)
    sov = sum(r["sovereignty_near"] for r in records_for_site)
    ai = sum(r["ai_near"] for r in records_for_site)
    years = [(year, sum(r["date"].startswith(year) for r in records_for_site))
             for year in ("2022", "2023", "2024", "2025")]
    outlets = Counter(r["source"] for r in records_for_site).most_common()
    page = template.replace("__MODE_NOTICE__", notice)
    page = page.replace("__DENDROGRAM_SECTION__", dendrogram_section())
    page = page.replace("__INITIAL_STATS__", card("matching articles", n) + card("ecology nearby", eco, n)
                        + card("energy / grid nearby", energy, n) + card("sovereignty nearby", sov, n))
    page = page.replace("__INITIAL_YEARS__", ''.join(bar(year, count, max(c for _, c in years))
                                                      for year, count in years))
    page = page.replace("__INITIAL_THEMES__", ''.join(bar(name, count, n, cls="sov" if name == "Sovereignty" else "")
                                                       for name, count in (("Ecology", eco), ("Energy", energy),
                                                                           ("Sovereignty", sov), ("AI", ai))))
    page = page.replace("__INITIAL_NEWSPAPERS__", ''.join(
        bar(outlet_names.get(source, source), count, outlets[0][1], n, outlet=True)
        for source, count in outlets))
    ordered = sorted(records_for_site, key=lambda r: (-r["dc_mentions"], r["date"]))
    page = page.replace("__INITIAL_RESULTS__", ''.join(article_card(r, r["id"] in bodies) for r in ordered[:30]))
    page = page.replace("__DATA__", json_for_script(records_for_site))
    page = page.replace("__FULL_ARTICLES__", json_for_script(bodies))
    page = page.replace("__SEARCH_INDEX__", json_for_script(search_index))
    page = page.replace("__THEME_DICTIONARY__", json_for_script(theme_dictionary(PAT)))
    page = page.replace("__ACTOR_DATA__", json_for_script(actor_payload))
    page = page.replace("__ACTOR_JS__", (root / 'actor_ui.js').read_text(encoding='utf-8'))
    assert '__ACTOR_' not in page and '__THEME_DICTIONARY__' not in page
    assert "__INITIAL_" not in page and "__DATA__" not in page and "__FULL_ARTICLES__" not in page and "__SEARCH_INDEX__" not in page
    return page


bodies, search_index = full_articles()
local_notice = ("<strong>Team reading copy.</strong> Each card represents one newspaper article. "
                "Open it once to read the whole text; yellow highlights data-centre terms, green ecological terms, "
                "blue energy/grid terms, and orange explicit sovereignty terms. Theme highlights appear only near a data-centre mention. "
                "Use the buttons in the reader to jump between matches. This file contains full press extracts and is for authorised team sharing.")
local_page = build(records, bodies, search_index, local_notice, actor_data)
for name in ("forsee_press_explorer.html", "dashboard.html"):
    (root / name).write_text(local_page, encoding="utf-8")

# Complete offline index using native HTML details when scripts are blocked.
style = template.split("<style>", 1)[1].split("</style>", 1)[0]
parts = ['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
         '<title>FORSEE full-text article index</title><style>', style, '</style>',
         '<header><h1>FORSEE full-text article index</h1><p>All 796 screened articles · script-free team reading copy</p></header><main>',
         '<div class="notice">Each entry is one newspaper article. The colour highlights mark dictionary matches. This file contains full press extracts and is for authorised team sharing.</div>']
for country in ("France", "Ireland"):
    parts.append(f'<h2>{country}</h2>')
    for year in ("2025", "2024", "2023", "2022"):
        subset = [r for r in records if r["country"] == country and r["date"].startswith(year)]
        parts.append(f'<h3>{year} ({len(subset)})</h3>')
        for r in sorted(subset, key=lambda r: r["date"], reverse=True):
            parts.append(article_card(r, False).replace('</article>',
                f'<details><summary>Read full article with highlighted matches</summary><div class="modal-text"><p>{bodies[r["id"]]}</p></div></details></article>'))
parts.append('</main></html>')
(root / "article_index.html").write_text(''.join(parts), encoding="utf-8")

# Pages copy contains counts and metadata only: no press text or snippets.
public_records = [{**r, "opening": "", "snippets": []} for r in records]
public_notice = ("<strong>Public metadata preview.</strong> This page shows counts, newspaper distribution, dates and "
                 "dictionary flags. It contains no article text. The team reading copy is shared separately.")
pages = root / "pages_site"
pages.mkdir(exist_ok=True)
public_actors = {key:{field:value for field,value in actor.items() if field != 'aliases_observed'}
                 for key,actor in actor_data['actors'].items() if actor['status']=='registry'}
public_actor_data = {'method':actor_data['method'], 'public_preview':True, 'actors':public_actors,
    'articles':{key:{'all':[a for a in item['all'] if a in public_actors],
                     'near':[a for a in item['near'] if a in public_actors],
                     'windows':[[a for a in group if a in public_actors] for group in item['windows']]}
                for key,item in actor_data['articles'].items()}}
(pages / "index.html").write_text(build(public_records, {}, {}, public_notice, public_actor_data), encoding="utf-8")
(pages / ".nojekyll").touch()
print(f"Local full-text explorer: {root / 'forsee_press_explorer.html'}")
print(f"Script-free full-text index: {root / 'article_index.html'}")
print(f"Pages-safe preview: {pages / 'index.html'}")
