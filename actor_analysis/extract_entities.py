#!/usr/bin/env python3
"""Run local French/English spaCy NER on the selected full articles."""
import hashlib
import json
import re
import sys
from pathlib import Path
import spacy

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT.parent / 'Presse_LL_été_2025'
CORPORA = {
    'France': ('FR', SOURCE / 'France/france/FR_pol.txt', 'fr_core_news_sm'),
    'Ireland': ('IE', SOURCE / 'Irlande/irish/IR_pol.txt', 'en_core_web_sm'),
}

def main():
    selected = {r['id'] for r in json.loads((ROOT/'dashboard_data.json').read_text())}
    output = {'spacy_version': spacy.__version__, 'models': {}, 'articles': {}}
    for country, (prefix, path, model) in CORPORA.items():
        nlp = spacy.load(model)
        nlp.select_pipes(enable=[p for p in nlp.pipe_names if p in ('tok2vec', 'ner')])
        output['models'][country] = {'name': model, 'version': nlp.meta['version']}
        articles = []
        for i, block in enumerate(re.split(r'(?m)^\*\*\*\*\s+', path.read_text(encoding='utf-8-sig'))[1:], 1):
            aid = f'{prefix}-{i:05d}'
            if aid in selected:
                text = re.sub(r'\s+', ' ', block.split('\n', 1)[1]).strip()
                articles.append((aid, text))
        for n, ((aid, text), doc) in enumerate(zip(articles, nlp.pipe((t for _,t in articles), batch_size=8)), 1):
            output['articles'][aid] = {'text_sha256': hashlib.sha256(text.encode()).hexdigest(),
                'entities': [{'text': e.text, 'start': e.start_char, 'end': e.end_char, 'label': e.label_}
                             for e in doc.ents if e.label_ in ('PER','PERSON','ORG')]}
            if n % 100 == 0:
                print(country, n, '/', len(articles), flush=True)
        print(country, 'complete', len(articles), flush=True)
    assert len(output['articles']) == len(selected)
    (ROOT/'actor_analysis/ner_raw.json').write_text(json.dumps(output, ensure_ascii=False, separators=(',', ':')))
    print('Saved actor_analysis/ner_raw.json', flush=True)

if __name__ == '__main__':
    main()
