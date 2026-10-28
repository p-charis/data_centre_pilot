#!/usr/bin/env python3
"""Check article/mention provenance, scope counts and edge denominators."""
import csv,hashlib,json,re
from collections import Counter,defaultdict
from itertools import combinations
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
p=ROOT/'actor_analysis';data=json.loads((p/'actors_data.json').read_text());records=json.loads((ROOT/'dashboard_data.json').read_text());lookup={r['id']:r for r in records}
assert set(data['articles'])==set(lookup)
texts={}
for prefix,rel in [('FR','France/france/FR_pol.txt'),('IE','Irlande/irish/IR_pol.txt')]:
 for i,block in enumerate(re.split(r'(?m)^\*\*\*\*\s+', (ROOT.parent/'Presse_LL_été_2025'/rel).read_text(encoding='utf-8-sig'))[1:],1):
  rid=f'{prefix}-{i:05d}'
  if rid in lookup:texts[rid]=re.sub(r'\s+',' ',block.split('\n',1)[1]).strip()
for rid,a in data['articles'].items():
 text=texts[rid];assert hashlib.sha256(text.encode()).hexdigest()==a['text_sha256']
 assert set(a['near'])<=set(a['all'])
 assert a['all']==sorted({s['actor'] for s in a['spans']})
 previous=0
 for s in a['spans']:
  assert 0<=s['start']<s['end']<=len(text)
  assert s['start']>=previous,'Overlapping mentions';previous=s['end']
  assert s['actor'] in data['actors']
  assert s['near']==any(s['start']<end and s['end']>start for start,end in a['window_bounds'])
 assert a['near']==sorted({s['actor'] for s in a['spans'] if s['near']})
 for ids,(start,end) in zip(a['windows'],a['window_bounds']):
  assert ids==sorted({s['actor'] for s in a['spans'] if s['start']<end and s['end']>start})
for m in csv.DictReader((p/'actor_mentions.csv').open()):assert texts[m['article_id']][int(m['start']):int(m['end'])]==m['surface']
expected=Counter()
for rid,a in data['articles'].items():
 for scope in ['all','near']:
  for aid in a[scope]:expected[(lookup[rid]['country'],scope,aid)]+=1
for row in csv.DictReader((p/'actor_frequencies.csv').open()):
 assert int(row['articles'])==expected[(row['country'],row['scope'],row['actor_id'])]
 assert int(row['denominator'])==sum(r['country']==row['country'] for r in records)
for row in csv.DictReader((p/'actor_edges.csv').open()):
 ids=row['article_ids'].split('|');assert len(ids)==len(set(ids))==int(row['articles'])
 for rid in ids:
  assert lookup[rid]['country']==row['country'];a=data['articles'][rid]
  groups=a['windows'] if row['scope']=='near' else [a['all']]
  assert any(row['actor_a_id'] in g and row['actor_b_id'] in g for g in groups)
print(f'PASS: {len(records)} article hashes; all mention offsets/surfaces; scope, frequency and edge support checks.')
