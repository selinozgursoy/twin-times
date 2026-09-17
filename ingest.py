from .config import load_sources, load_profile
from .db import upsert_story, all_unscored, update_score, start_run, finish_run
from .feeds import fetch_source
from .rank import score_story
from concurrent.futures import ThreadPoolExecutor, as_completed

def refresh():
    run_id=start_run(); fetched=inserted=0; errors=[]
    sources=[src for src in load_sources() if src.get("enabled",True)]
    # Feeds are independent network requests; fetch them concurrently, then
    # write to SQLite in this thread to keep refreshes fast and predictable.
    with ThreadPoolExecutor(max_workers=min(8, max(1, len(sources)))) as pool:
        futures={pool.submit(fetch_source,src):src for src in sources}
        for future in as_completed(futures):
            src=futures[future]
            try:
                items=future.result(); fetched+=len(items)
                for item in items: inserted += upsert_story(item)
            except Exception as e:
                errors.append({"source":src.get("name","?"),"error":str(e)[:500]})
    profile=load_profile()
    for row in all_unscored(1500):
        score, detail, topics, entities, why=score_story(row,profile)
        update_score(row["id"],score,detail,topics,entities,why)
    finish_run(run_id,fetched,inserted,errors)
    return {"run_id":run_id,"fetched":fetched,"inserted":inserted,"errors":errors}
