# Named-entity and actor exploration method

This is a pilot extraction from the same 796 selected full articles used by the press explorer. It does not change the IRaMuTeQ subcorpora or original theme flags.

## Extraction and identity decisions

The pipeline runs spaCy 3.8.7 locally, using `fr_core_news_sm` 3.8.0 for the French source corpus and `en_core_web_sm` 3.8.0 for the English source corpus. Only the tok2vec and named-entity components are enabled. PER/PERSON and ORG spans are retained. Place names, products, nationalities and other model labels are not automatically treated as actors. See the [French](https://spacy.io/models/fr) and [English](https://spacy.io/models/en) model documentation. General NER supplies broad entity types; our substantive actor categories are assigned in the project dictionary.

Text preparation collapses whitespace while retaining spelling, case and accents. Offsets in the mention export are Unicode code-point offsets into that prepared text. The cache records a SHA-256 hash of every prepared article; the resolved output also records source-file and registry hashes. Model output is cached in `ner_raw.json` so alias/category changes do not require another model run. No corpus text is sent to an external extraction API.

`registry.json` defines canonical names, a practical actor taxonomy, spelling variants, selected corporate groupings and an exclusion list. Dictionary matching supplements NER omissions. It uses word boundaries; multiword aliases match case-insensitively, while single-token aliases are case-sensitive to reduce common-word/acronym ambiguity. For overlapping dictionary matches the longest span takes precedence. A model span overlapping an accepted dictionary match is discarded. Otherwise, its whole normalised name is mapped to a registry alias when available; unrecognised names remain separate unreviewed candidates, normalised for case/accents/punctuation. Model candidates with fewer than three normalised characters, more than 100 surface characters, or listed exclusions are removed.

A surname model span may be linked within an article when its surname uniquely matches a detected dictionary person in that article. Other ambiguous surnames and abbreviations can remain unresolved or incorrectly resolved. There is no pronoun/coreference model and no disambiguation through an external knowledge base. Generic mentions such as “the government” cannot reliably be assigned to a state from the publication country.

Some dictionary aliases aggregate a business group: Amazon/AWS, Google/Alphabet, Meta/Facebook, Digital Realty/Interxion and TikTok/ByteDance. They are explicitly labelled as aggregations rather than separate organisations. Other parent/subsidiary pairs, such as Iliad and Scaleway, remain separate. This uneven grouping is an initial research choice to review before formal network comparison. Ambiguous institutional names such as EPA, Senate or Green Party retain a “country unresolved” label. Bare titles such as Taoiseach and président de la République are excluded, to avoid creating a separate actor from a title adjacent to a named person. Energy/grid companies are grouped separately by sector, without inferring public or private ownership. The categories are editable research aids, not classifications inferred by the NER model.

The initial dashboard view includes dictionary identities. “Include unreviewed NER candidates” adds the remaining automatic output, including potential false positives, bylines, incomplete names and unresolved aliases. “Dictionary identity” does not mean that every detected mention has been manually validated. Spot checks were made for prominent actors; no accuracy score is claimed. Candidates and dictionary identities remain separately marked in the exports.

## Counts and network

- **Same full article:** each actor contributes at most one count per article. A pair contributes one edge count when both actors occur anywhere in that article.
- **Near a data-centre mention (dashboard label):** areas extend 500 characters either side of each dictionary data-centre match in the whitespace-collapsed text. A mention is nearby if its span overlaps an area. An actor contributes at most one count per article. A pair contributes one count only if both actors occur in at least one identical area; separate areas in one article do not establish that edge.
- Overlapping/repeated windows do not multiply an article's contribution. Actor mentions per article and mention frequency are distinct measures.
- The original theme flags were calculated on raw text. Actor windows use whitespace-collapsed text for consistency with the reader and NER offsets; small boundary differences are possible. Theme overlap shown for an actor is the presence of those original flags in its supporting articles, not an actor-specific theme code.
- The graph uses the top 15/25/40 actors under the current country/language/year/newspaper/theme/Boolean filters and actor controls. Minimum edge weight is selectable. At most 80 qualifying links are drawn; the strongest-connections list shows up to 20. These display limits are not analytical exclusions in the CSV exports.
- Node size increases with article count; colour indicates dictionary category or unclassified model type; line width increases with distinct supporting articles. The deterministic display layout has no substantive distance interpretation. No community detection, influence ranking or stance inference is performed.
- Country shares divide by all currently filtered articles in that newspaper corpus, including articles with no detected actor. Corpus country is not actor nationality or project geography. Find-an-actor narrows the ranking list only; it does not silently change the network population.

Click an actor or link to inspect supporting article IDs and extracts; open a full article for purple highlights on the selected names. Links represent textual co-mention only. Support, opposition, influence, cooperation, quotation and speaker roles require additional contextual coding.

## Reproduction and extension

The environment used for this run was created in `/tmp/forsee-ner-env` with Python 3.10. It is temporary; the pinned dependency list is retained in `requirements-lock.txt`. The browser itself needs no Python, network service or installation.

From the pilot folder, a new compatible Python environment can be prepared with:

```sh
python3.10 -m venv /tmp/forsee-ner-env
/tmp/forsee-ner-env/bin/python -m pip install --upgrade pip
/tmp/forsee-ner-env/bin/python -m pip install -r actor_analysis/requirements-lock.txt
```

Then run:

```sh
python3 analyse.py
/tmp/forsee-ner-env/bin/python actor_analysis/extract_entities.py
python3 actor_analysis/build_actors.py
python3 actor_analysis/write_findings.py
python3 build_dashboard.py
```

For dictionary/category edits alone, rerun only `build_actors.py`, `write_findings.py` and `build_dashboard.py`. The existing build scripts refresh the screening table through `analyse.py`; original corpus text is unchanged. If the selected texts change, rerun extraction. Hash checks reject stale actor data.

For a different corpus, update the source/model mapping in `extract_entities.py`, the screening inputs/dictionaries in `analyse.py`, and the project actor registry. The current reader and network can be reused, but source paths, country comparisons, headings and the data-centre window rule are still project-specific. This is not yet a generic drag-and-drop IRaMuTeQ importer.

## Sharing

The local explorer includes the actor data and full article text. `actor_mentions.csv` and `ner_raw.json` also contain press extracts. Keep these in the authorised team share. The generated `pages_site/index.html` contains only dictionary identities, counts and article IDs; model candidates, observed surface-form lists, mention offsets/contexts and full article bodies are omitted. No site has been published by this update.
