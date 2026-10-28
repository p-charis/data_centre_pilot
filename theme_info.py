"""Explanations shown by the clickable theme labels; patterns come from analyse.PAT."""
EXAMPLES = {
 'ecology': {'label':'Ecology', 'note':'Environmental vocabulary; a match does not establish criticism or support.',
   'France':['écologi…','environnement…','climat…','carbone','émissions','eau','durabl…','renouvelabl…'],
   'Ireland':['ecolog…','environment…','climat…','carbon…','emissions','water','sustainab…','renewab…','net zero']},
 'energy': {'label':'Energy / grid', 'note':'Electricity, energy and grid vocabulary. These terms do not by themselves establish an ecological frame.',
   'France':['énergi…','électri…','réseau électrique','nucléaire','énergivore…'],
   'Ireland':['energ…','electric…','power demand','power supply','grid','megawatt','gigawatt']},
 'sovereignty': {'label':'Sovereignty', 'note':'A narrow explicit vocabulary. Institutional names, investment and national policy do not automatically count as sovereignty.',
   'France':['souverain…','autonomie stratégique','indépendance numérique','indépendance technologique','dépendance américaine','contrôle des données'],
   'Ireland':['sovereign…','strategic autonom…','digital autonom…','technological independen…','dependence on US providers','data residency','data localisation']},
 'ai': {'label':'AI', 'note':'Explicit AI names and abbreviations.',
   'France':['intelligence artificielle','IA','AI','ChatGPT','GPT-4'],
   'Ireland':['artificial intelligence','AI','ChatGPT','GPT-4']},
}

def theme_dictionary(patterns):
    return {key:{**value,'patterns':{country:entries[key] for country,entries in patterns.items()}} for key,value in EXAMPLES.items()}
