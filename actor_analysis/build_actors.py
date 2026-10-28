#!/usr/bin/env python3
"""Resolve NER candidates, supplement named actors, and export auditable co-mentions."""
import csv
import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from analyse import FILES, PAT, clean
OUT = ROOT/'actor_analysis'

def norm(value):
    value = ''.join(c for c in unicodedata.normalize('NFKD', value) if not unicodedata.combining(c))
    value = re.sub(r"[’']s$", '', value.strip())
    return re.sub(r'[^\w]+', ' ', value.casefold()).strip()

def identity(name, category):
    return 'a'+hashlib.sha1((category+'|'+norm(name)).encode()).hexdigest()[:12]

def alias_pattern(alias):
    return r'(?<!\w)'+re.escape(alias).replace(r'\ ', r'\s+').replace('’', "[’']").replace("\\'", "[’']")+r'(?!\w)'

def main():
    raw=json.loads((OUT/'ner_raw.json').read_text())
    registry=json.loads((OUT/'registry.json').read_text())
    rows=json.loads((ROOT/'dashboard_data.json').read_text()); selected={r['id']:r for r in rows}
    actors={}; alias_to_id={}; rules=[]
    excluded={norm(n) for n in registry['exclude']}
    for entry in registry['actors']:
        aid=identity(entry['name'],entry['category'])
        actors[aid]={**entry,'id':aid,'status':'registry','aliases_observed':[]}
        for alias in entry['aliases']+entry.get('ner_aliases',[]):
            key=norm(alias)
            if key in alias_to_id and alias_to_id[key]!=aid:raise ValueError('Ambiguous registry alias: '+alias)
            alias_to_id[key]=aid
        for alias in entry['aliases']:
            rules.append((re.compile(alias_pattern(alias),re.I if ' ' in alias else 0),aid))
    articles={}; documents={}; observed=defaultdict(Counter); mention_rows=[]
    for country,path in FILES.items():
        prefix='FR' if country=='France' else 'IE'
        for index,block in enumerate(re.split(r'(?m)^\*\*\*\*\s+',path.read_text(encoding='utf-8-sig'))[1:],1):
            rid=f'{prefix}-{index:05d}'
            if rid not in selected:continue
            text=clean(block.split('\n',1)[1]); documents[rid]=text
            assert raw['articles'][rid]['text_sha256']==hashlib.sha256(text.encode()).hexdigest(), f'Stale NER cache: {rid}'
            dc=list(re.finditer(PAT[country]['dc'],text,re.I))
            windows=[(max(0,m.start()-500),min(len(text),m.end()+500)) for m in dc]
            spans=[]
            for rx,aid in rules:
                for m in rx.finditer(text):spans.append({'start':m.start(),'end':m.end(),'actor':aid,'method':'dictionary','label':'registry'})
            # Prefer the longest registry span at any overlapping position.
            spans.sort(key=lambda s:(-(s['end']-s['start']),s['start']))
            kept=[]
            for s in spans:
                if not any(s['start']<k['end'] and s['end']>k['start'] for k in kept):kept.append(s)
            document_people=defaultdict(set)
            for s in kept:
                actor=actors[s['actor']]
                if actor['category'] in ('Political figure','Business figure','Institutional figure'):
                    surname=norm(actor['name']).split()[-1]
                    if len(surname)>=4:document_people[surname].add(s['actor'])
            for ent in raw['articles'][rid]['entities']:
                if any(ent['start']<k['end'] and ent['end']>k['start'] for k in kept):continue
                name=ent['text'].strip(' \t\n.,;:()[]“”"')
                key=norm(name)
                if key in excluded or len(key)<3 or len(name)>100 or not any(c.isalpha() for c in name):continue
                aid=alias_to_id.get(key)
                if aid is None and len(document_people.get(key, set()))==1:
                    aid=next(iter(document_people[key]))
                if aid is None:
                    category='Person — unclassified' if ent['label'] in ('PER','PERSON') else 'Organisation — unclassified'
                    aid=identity(name,category)
                    actors.setdefault(aid,{'id':aid,'name':name,'category':category,'status':'candidate','aliases':[], 'ner_aliases':[], 'note':'Automatic NER candidate; entity identity and type need review.','aliases_observed':[]})
                kept.append({'start':ent['start'],'end':ent['end'],'actor':aid,'method':'ner','label':ent['label']})
            kept.sort(key=lambda s:s['start'])
            for s in kept:
                s['near']=any(s['start']<b and s['end']>a for a,b in windows)
                observed[s['actor']][text[s['start']:s['end']]]+=1
                mention_rows.append({'article_id':rid,'country':country,'actor_id':s['actor'],'actor':actors[s['actor']]['name'],
                    'category':actors[s['actor']]['category'],'method':s['method'],'ner_label':s['label'],
                    'start':s['start'],'end':s['end'],'near_dc':s['near'],'surface':text[s['start']:s['end']],
                    'context':text[max(0,s['start']-100):min(len(text),s['end']+100)]})
            groups=[sorted({s['actor'] for s in kept if s['start']<b and s['end']>a}) for a,b in windows]
            articles[rid]={'all':sorted({s['actor'] for s in kept}),'near':sorted({s['actor'] for s in kept if s['near']}),
                'windows':groups,'window_bounds':windows,'spans':kept,'text_sha256':raw['articles'][rid]['text_sha256']}
    used={s['actor'] for a in articles.values() for s in a['spans']}
    actors={k:v for k,v in actors.items() if k in used}
    for aid,actor in actors.items():actor['aliases_observed']=[n for n,c in observed[aid].most_common(20)]
    data={'method':{'spacy_version':raw['spacy_version'],'models':raw['models'],'scope':f'{len(rows)} screened full articles',
        'near_window_characters':500,'text_basis':'Whitespace-collapsed original article bodies; offsets are Unicode code points.',
        'edge_unit':'Each supporting article counts once; nearby edges require both actors in the same data-centre window.',
        'source_hashes':{country:hashlib.sha256(p.read_bytes()).hexdigest() for country,p in FILES.items()},
        'registry_sha256':hashlib.sha256((OUT/'registry.json').read_bytes()).hexdigest()},'actors':actors,'articles':articles}
    (OUT/'actors_data.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')))
    with (OUT/'actor_mentions.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(mention_rows[0]));w.writeheader();w.writerows(mention_rows)
    frequencies=[];edge_rows=[]
    for country in ('France','Ireland'):
        ids=[r['id'] for r in rows if r['country']==country]
        for scope in ('all','near'):
            counts=Counter(aid for rid in ids for aid in articles[rid][scope])
            for aid,count in counts.most_common():
                frequencies.append({'country':country,'scope':scope,'actor_id':aid,'actor':actors[aid]['name'],'category':actors[aid]['category'],
                    'status':actors[aid]['status'],'articles':count,'denominator':len(ids),'percent':round(count/len(ids)*100,2)})
            edge_support=defaultdict(list)
            for rid in ids:
                groups=[articles[rid]['all']] if scope=='all' else articles[rid]['windows']
                pairs={pair for group in groups for pair in combinations(sorted(set(group)),2)}
                for pair in pairs:edge_support[pair].append(rid)
            for (left,right),rids in sorted(edge_support.items(),key=lambda item:-len(item[1])):
                edge_rows.append({'country':country,'scope':scope,'actor_a':actors[left]['name'],'actor_b':actors[right]['name'],
                    'actor_a_id':left,'actor_b_id':right,'articles':len(rids),'article_ids':'|'.join(rids)})
    for name,items in [('actor_frequencies.csv',frequencies),('actor_edges.csv',edge_rows)]:
        with (OUT/name).open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=list(items[0]));w.writeheader();w.writerows(items)
    print(f'{len(actors)} actor identities; {len(mention_rows)} mentions; {len(articles)} articles')
    for country in ('France','Ireland'):
        print(country,'nearby registry actors:',[(r['actor'],r['articles']) for r in frequencies if r['country']==country and r['scope']=='near' and r['status']=='registry'][:15])

if __name__=='__main__':main()
