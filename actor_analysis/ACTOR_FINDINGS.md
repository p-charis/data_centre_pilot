# Named actors: exploratory reading note

Generated from the 796 screened articles (642 France, 154 Ireland). These are descriptive mention counts, before systematic manual validation. Corpus country identifies the newspaper collection, not the actor’s nationality or the location discussed.

The actor layer combines local spaCy named-entity extraction with an editable dictionary. The dictionary resolves selected names and supplements model omissions; the remaining model outputs are unreviewed candidates. The dashboard defaults to dictionary identities. This is not a census of all relevant actors, a measure of voice, or a relational network of actual cooperation.

The current output contains 5719 distinct candidate/dictionary identities, including 148 dictionary identities that occur at least once. The candidate count is not an estimate of the number of real actors: unresolved variants and model errors remain.

## Actors near data-centre mentions

Each count is the number of distinct articles containing at least one actor name within 500 characters of a data-centre mention. Percentages use all screened articles in the relevant country as the denominator. The dashboard calls this “Near a data-centre mention”. The actor proximity areas use whitespace-collapsed article text; the original theme flags use raw article text.

| Actor | France, n / 642 (%) | Ireland, n / 154 (%) |
|---|---:|---:|
| Microsoft | 176 (27.4%) | 40 (26.0%) |
| Google / Alphabet | 142 (22.1%) | 41 (26.6%) |
| Amazon / AWS | 124 (19.3%) | 28 (18.2%) |
| Nvidia | 134 (20.9%) | 21 (13.6%) |
| OpenAI | 100 (15.6%) | 16 (10.4%) |
| Meta / Facebook | 76 (11.8%) | 24 (15.6%) |
| Emmanuel Macron | 54 (8.4%) | 3 (1.9%) |
| Élysée | 31 (4.8%) | 0 (0.0%) |
| Donald Trump | 82 (12.8%) | 9 (5.8%) |
| European Union | 22 (3.4%) | 17 (11.0%) |
| European Commission | 12 (1.9%) | 3 (1.9%) |
| International Energy Agency | 40 (6.2%) | 8 (5.2%) |
| EirGrid | 2 (0.3%) | 17 (11.0%) |
| Commission for Regulation of Utilities | 0 (0.0%) | 9 (5.8%) |
| Micheál Martin | 0 (0.0%) | 13 (8.4%) |
| Eamon Ryan | 0 (0.0%) | 7 (4.5%) |
| South Dublin County Council | 0 (0.0%) | 6 (3.9%) |

## Reading leads

Large technology companies are visible in both collections. Start by examining whether these mentions concern owners/operators, cloud services, chip supply, investment announcements or comparisons with projects abroad; a company name alone does not identify its role in an argument.

The French material provides a lead around named national executives and industrial/AI investment announcements. The Irish material provides a lead around grid management, regulation, planning and government choices. These are directions for reading, not findings that one country prioritises sovereignty and the other ecology. The actor vocabulary and country sample sizes differ, and newspaper composition can shape the contrast.

The European Union and European Commission are separate identities. Neither is automatically coded as sovereignty. Likewise, EirGrid and energy companies are not automatically coded as environmental criticism. The detail panel reports article-level overlap with existing theme flags, which must not be attributed to an actor as their position.

## Most frequent dictionary-actor connections near data centres

An edge counts each supporting article once and requires both actor names within 500 characters of the same data-centre mention. Repeated mentions/areas within an article do not increase its edge weight. These are co-mentions, not ties established by the text.


### France

| Pair | Supporting articles | Example article IDs |
|---|---:|---|
| Google / Alphabet ↔ Microsoft | 91 | FR-00132, FR-00498, FR-01161 |
| Amazon / AWS ↔ Microsoft | 86 | FR-00132, FR-00498, FR-01161 |
| Amazon / AWS ↔ Google / Alphabet | 77 | FR-00132, FR-00498, FR-01161 |
| Nvidia ↔ Microsoft | 51 | FR-01981, FR-02086, FR-02149 |
| Google / Alphabet ↔ Meta / Facebook | 45 | FR-03087, FR-03717, FR-03720 |
| Nvidia ↔ Google / Alphabet | 44 | FR-01317, FR-01981, FR-02149 |
| OpenAI ↔ Microsoft | 44 | FR-01981, FR-03133, FR-03680 |
| Meta / Facebook ↔ Microsoft | 41 | FR-02086, FR-03087, FR-03717 |
| OpenAI ↔ Sam Altman | 33 | FR-03680, FR-03731, FR-05195 |
| Nvidia ↔ Amazon / AWS | 31 | FR-02149, FR-02358, FR-03033 |

### Ireland

| Pair | Supporting articles | Example article IDs |
|---|---:|---|
| Google / Alphabet ↔ Microsoft | 23 | IE-00175, IE-00372, IE-00795 |
| Amazon / AWS ↔ Microsoft | 18 | IE-00075, IE-00108, IE-00175 |
| Amazon / AWS ↔ Google / Alphabet | 14 | IE-00175, IE-00562, IE-00795 |
| Google / Alphabet ↔ Meta / Facebook | 12 | IE-00562, IE-00811, IE-00817 |
| Meta / Facebook ↔ Microsoft | 11 | IE-00817, IE-00833, IE-01266 |
| Nvidia ↔ Microsoft | 11 | IE-01133, IE-01266, IE-01276 |
| Amazon / AWS ↔ Meta / Facebook | 10 | IE-00562, IE-00817, IE-00881 |
| OpenAI ↔ Microsoft | 8 | IE-00795, IE-01133, IE-01235 |
| Nvidia ↔ Intel | 8 | IE-00900, IE-01266, IE-01304 |
| Nvidia ↔ Jensen Huang | 7 | IE-00900, IE-01266, IE-01451 |

## How to inspect the evidence

In the main explorer, select the corpus and language, then an actor type. Clicking an actor gives country-specific article counts and supporting extracts; clicking a connection gives the texts supporting that exact edge. Open an article to see the selected names highlighted in purple. Switching from names near a data-centre mention to names anywhere in the article shows how sensitive a connection is to the unit of analysis. Two names near separate data-centre mentions in one article do not by themselves produce a nearby edge.

Use the unreviewed-candidates option to find missing actors. Review identities, aliases and categories in registry.json, including uncertain country labels, before any inferential comparison. There is no automatic pronoun/coreference resolution. Generic government references are mostly absent; journalist names in article bodies can appear among candidates. Abbreviations, surnames, corporate brands and institutional metonyms require checking.

## Files and reproducibility

- `ner_raw.json`: cached original model spans (PER/PERSON/ORG).
- `registry.json`: editable named actors, aliases, types, exclusions and grouping notes.
- `actor_mentions.csv`: one detected mention per row with article ID, offsets, surface form, method and a short context. Contains press extracts; team use.
- `actor_frequencies.csv`: counts by corpus and scope, with denominators.
- `actor_edges.csv`: edge counts and all supporting article IDs, suitable for external network tools.
- `actors_data.json`: dashboard input with model versions and source/registry hashes.
- `METHOD.md`: extraction, interpretation and rebuild instructions.

All counts and rankings are exploratory. No held-out precision/recall estimate or substantive actor/stance coding has been completed.
