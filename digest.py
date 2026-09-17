import json
from .db import list_stories, feedback_map, bookmark_ids

CATS=[
    ('AI',['artificial_intelligence','computer_science']),
    ('Hardware & Robotics',['hardware','semiconductors','robotics']),
    ('VC & Startups',['venture_capital','startups']),
    ('Neuroscience',['neuroscience']),
    ('Life Sciences',['life_sciences','science']),
    ('Technology',['technology'])
]

def hydrate(r):
    x=dict(r)
    for k in ('topics','entities','score_detail'):
        try: x[k]=json.loads(x.get(k) or ('{}' if k=='score_detail' else '[]'))
        except: x[k]={} if k=='score_detail' else []
    return x

def _dedupe(rows):
    selected=[]; seen=[]
    def sig(t): return set(w.strip('.,:;!?()[]').lower() for w in t.split() if len(w)>4)
    for r in rows:
        s=sig(r['title'])
        if any(len(s & old)/max(1,len(s|old)) > .62 for old in seen): continue
        selected.append(r); seen.append(s)
    return selected

def _is_research_source(row):
    source=(row.get('source') or '').lower()
    return 'arxiv' in source or 'nature' in source

def build_digest(limit=32, hours=48):
    rows=[hydrate(r) for r in list_stories(300,0,hours)]; fb=feedback_map(); marks=bookmark_ids()
    rows=[r for r in rows if 'less' not in fb.get(r['id'],[])]; selected=_dedupe(rows)
    for r in selected: r['newsmarked']=r['id'] in marks

    # Academic feeds have a dedicated editorial lane. They are deliberately
    # excluded from the general briefing even when their relevance score is high.
    news=[r for r in selected if not _is_research_source(r)]
    research=[r for r in selected if _is_research_source(r)]
    top=news[:10]

    # Important: Top stories must also exist in the detailed category feed so the
    # Today list can scroll to and expand the corresponding story.
    categorized=set(); sections=[]
    for name, topics in CATS:
        arr=[r for r in news if r['id'] not in categorized and any(t in r['topics'] for t in topics)][:7]
        categorized.update(r['id'] for r in arr)
        if arr: sections.append({'name':name,'items':arr})

    # Give high-ranking uncategorized stories a home too, rather than making
    # them impossible to reach from Today.
    top_ids={r['id'] for r in top}
    missing_top=[r for r in top if r['id'] not in categorized]
    if missing_top:
        sections.insert(0, {'name':'Top Stories','items':missing_top})
        categorized.update(r['id'] for r in missing_top)

    outside=[r for r in news if r['id'] not in categorized][:3]
    deep=sorted(research,key=lambda r:r.get('published_at') or r.get('created_at') or '',reverse=True)[:8]
    return {'top':top,'sections':sections,'outside':outside,'deep':deep,'count':len(news[:limit])}
