import json, math, re
from datetime import datetime, timezone

TOKEN=re.compile(r"[a-z0-9+.-]+")

def toks(s): return set(TOKEN.findall((s or "").lower()))

def phrase_hit(text, phrase):
    p=phrase.lower().strip()
    if len(p) <= 3: return p in toks(text)
    return p in text.lower()

def score_story(story, profile):
    text=f"{story.get('title','')} {story.get('summary','')}"
    topic_score=0.0; hit_topics=[]
    for topic, weight in profile.get("topics",{}).items():
        aliases=[topic.replace("_"," ")] + profile.get("topic_aliases",{}).get(topic,[])
        if any(phrase_hit(text,a) for a in aliases):
            topic_score += 30*float(weight)/max(1, len([x for x in profile.get('topics',{}) if profile['topics'][x] >= .7]))
            hit_topics.append(topic)
    topic_score=min(30, topic_score*3.2)

    entity_score=0; entities=[]
    for ent, weight in profile.get("tracked_entities",{}).items():
        if phrase_hit(text, ent):
            entity_score += 10*float(weight)
            entities.append(ent)
    entity_score=min(10, entity_score)

    src=story.get("source","").lower()
    source_quality=5
    for preferred in profile.get("preferred_sources",[]):
        if preferred.lower() in src: source_quality=10; break
    if "arxiv" in src or "nature" in src: source_quality=max(source_quality,9)

    title=(story.get("title") or "").lower(); summary=(story.get("summary") or "").lower()
    importance=7
    importance_terms={"launch":2,"release":2,"acquire":3,"acquisition":3,"breakthrough":5,"regulation":3,"funding":1,"raises":1,"chip":2,"model":2,"research":2,"trial":3,"discovery":3,"open source":2}
    for k,v in importance_terms.items():
        if k in title: importance+=v
    importance=min(20,importance)

    novelty=7
    if any(k in title for k in ["new ","first ","unveils","launches","discovers","demonstrates","introduces"]): novelty+=4
    if any(k in summary for k in ["first time","novel","new method","new architecture"]): novelty+=2
    novelty=min(15,novelty)

    depth=1
    if "arxiv" in src or any(k in text.lower() for k in ["paper","researchers","study","dataset","benchmark","theorem"]): depth=5

    geography=3
    low=text.lower()
    for region,w in profile.get("regions",{}).items():
        aliases=profile.get("region_aliases",{}).get(region,[region])
        if any(a.lower() in low for a in aliases): geography=max(geography,5*float(w))
    geography=min(5,geography)

    future=2
    if any(k in low for k in ["infrastructure","semiconductor","compute","neuroscience","foundation model","robot","quantum","biotech","energy"]): future=5

    penalty=0
    noise_terms=profile.get("noise_terms",["celebrity","sports betting","daily horoscope"])
    for term in noise_terms:
        if term.lower() in low: penalty -= 12
    if any(k in title for k in ["price target","stock rises","stock falls","shares rise","shares fall"]): penalty-=10
    if "raises" in title and topic_score < 12 and entity_score == 0: penalty-=5

    total=topic_score+importance+novelty+source_quality+entity_score+depth+geography+future+penalty
    # freshness bonus, capped and forgiving of missing dates
    try:
        dt=datetime.fromisoformat((story.get("published_at") or "").replace("Z","+00:00"))
        age=max(0,(datetime.now(timezone.utc)-dt.astimezone(timezone.utc)).total_seconds()/3600)
        total += max(0, 5-age/12)
    except Exception: pass
    total=max(0,min(100,total))
    detail={"topic":round(topic_score,1),"importance":importance,"novelty":novelty,"source_quality":source_quality,"entity":round(entity_score,1),"depth":depth,"geography":round(geography,1),"future_significance":future,"noise_penalty":penalty}
    why = _why(hit_topics, entities, story)
    return round(total,1), detail, hit_topics, entities, why

def _why(topics, entities, story):
    if entities and topics: return f"Tracks {entities[0]} and intersects with your interest in {topics[0].replace('_',' ')}."
    if entities: return f"You asked Twin to track {entities[0]} closely."
    if topics: return f"Strong match for your {topics[0].replace('_',' ')} interests."
    if "arxiv" in story.get("source","").lower(): return "Primary research that may be worth scanning before it reaches mainstream coverage."
    return "Selected for significance and potential relevance outside your usual feed."
