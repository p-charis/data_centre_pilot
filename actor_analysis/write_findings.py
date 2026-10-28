#!/usr/bin/env python3
"""Write descriptive pilot tables from the current actor exports."""
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
actors=json.loads((ROOT/'actors_data.json').read_text())
freq=list(csv.DictReader((ROOT/'actor_frequencies.csv').open()))
edges=list(csv.DictReader((ROOT/'actor_edges.csv').open()))
lookup={(r['country'],r['scope'],r['actor']):r for r in freq}
lines=['# Named actors: exploratory reading note', '',
 'Generated from the 796 screened articles (642 France, 154 Ireland). These are descriptive mention counts, before systematic manual validation. Corpus country identifies the newspaper collection, not the actor’s nationality or the location discussed.', '',
 'The actor layer combines local spaCy named-entity extraction with an editable dictionary. The dictionary resolves selected names and supplements model omissions; the remaining model outputs are unreviewed candidates. The dashboard defaults to dictionary identities. This is not a census of all relevant actors, a measure of voice, or a relational network of actual cooperation.', '',
 f"The current output contains {len(actors['actors'])} distinct candidate/dictionary identities, including {sum(a['status']=='registry' for a in actors['actors'].values())} dictionary identities that occur at least once. The candidate count is not an estimate of the number of real actors: unresolved variants and model errors remain.", '',
 '## Actors near data-centre mentions', '',
 'Each count is the number of distinct articles containing at least one actor name within 500 characters of a data-centre mention. Percentages use all screened articles in the relevant country as the denominator. The dashboard calls this “Near a data-centre mention”. The actor proximity areas use whitespace-collapsed article text; the original theme flags use raw article text.', '',
 '| Actor | France, n / 642 (%) | Ireland, n / 154 (%) |','|---|---:|---:|']
for name in ['Microsoft','Google / Alphabet','Amazon / AWS','Nvidia','OpenAI','Meta / Facebook','Emmanuel Macron','Élysée','Donald Trump','European Union','European Commission','International Energy Agency','EirGrid','Commission for Regulation of Utilities','Micheál Martin','Eamon Ryan','South Dublin County Council']:
 vals=[]
 for country in ['France','Ireland']:
  r=lookup.get((country,'near',name));vals.append(f"{r['articles']} ({float(r['percent']):.1f}%)" if r else '0 (0.0%)')
 lines.append('| '+name+' | '+' | '.join(vals)+' |')
lines += ['', '## Reading leads', '',
 'Large technology companies are visible in both collections. Start by examining whether these mentions concern owners/operators, cloud services, chip supply, investment announcements or comparisons with projects abroad; a company name alone does not identify its role in an argument.', '',
 'The French material provides a lead around named national executives and industrial/AI investment announcements. The Irish material provides a lead around grid management, regulation, planning and government choices. These are directions for reading, not findings that one country prioritises sovereignty and the other ecology. The actor vocabulary and country sample sizes differ, and newspaper composition can shape the contrast.', '',
 'The European Union and European Commission are separate identities. Neither is automatically coded as sovereignty. Likewise, EirGrid and energy companies are not automatically coded as environmental criticism. The detail panel reports article-level overlap with existing theme flags, which must not be attributed to an actor as their position.', '',
 '## Most frequent dictionary-actor connections near data centres', '',
 'An edge counts each supporting article once and requires both actor names within 500 characters of the same data-centre mention. Repeated mentions/areas within an article do not increase its edge weight. These are co-mentions, not ties established by the text.', '']
for country in ['France','Ireland']:
 lines += ['', f'### {country}', '', '| Pair | Supporting articles | Example article IDs |','|---|---:|---|']
 selected=[r for r in edges if r['country']==country and r['scope']=='near' and actors['actors'][r['actor_a_id']]['status']=='registry' and actors['actors'][r['actor_b_id']]['status']=='registry'][:10]
 for r in selected:lines.append(f"| {r['actor_a']} ↔ {r['actor_b']} | {r['articles']} | {', '.join(r['article_ids'].split('|')[:3])} |")
lines += ['', '## How to inspect the evidence', '',
 'In the main explorer, select the corpus and language, then an actor type. Clicking an actor gives country-specific article counts and supporting extracts; clicking a connection gives the texts supporting that exact edge. Open an article to see the selected names highlighted in purple. Switching from names near a data-centre mention to names anywhere in the article shows how sensitive a connection is to the unit of analysis. Two names near separate data-centre mentions in one article do not by themselves produce a nearby edge.', '',
 'Use the unreviewed-candidates option to find missing actors. Review identities, aliases and categories in registry.json, including uncertain country labels, before any inferential comparison. There is no automatic pronoun/coreference resolution. Generic government references are mostly absent; journalist names in article bodies can appear among candidates. Abbreviations, surnames, corporate brands and institutional metonyms require checking.', '',
 '## Files and reproducibility', '',
 '- `ner_raw.json`: cached original model spans (PER/PERSON/ORG).',
 '- `registry.json`: editable named actors, aliases, types, exclusions and grouping notes.',
 '- `actor_mentions.csv`: one detected mention per row with article ID, offsets, surface form, method and a short context. Contains press extracts; team use.',
 '- `actor_frequencies.csv`: counts by corpus and scope, with denominators.',
 '- `actor_edges.csv`: edge counts and all supporting article IDs, suitable for external network tools.',
 '- `actors_data.json`: dashboard input with model versions and source/registry hashes.',
 '- `METHOD.md`: extraction, interpretation and rebuild instructions.',
 '', 'All counts and rankings are exploratory. No held-out precision/recall estimate or substantive actor/stance coding has been completed.']
(ROOT/'ACTOR_FINDINGS.md').write_text('\n'.join(lines)+'\n')
print(ROOT/'ACTOR_FINDINGS.md')
