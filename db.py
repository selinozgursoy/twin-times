import sqlite3, json, hashlib
from datetime import datetime, timezone
from .config import DB_PATH, DATA_DIR

SCHEMA = """
CREATE TABLE IF NOT EXISTS stories (
  id TEXT PRIMARY KEY,
  source TEXT NOT NULL,
  title TEXT NOT NULL,
  url TEXT NOT NULL,
  published_at TEXT,
  summary TEXT,
  author TEXT,
  image_url TEXT,
  topics TEXT NOT NULL DEFAULT '[]',
  entities TEXT NOT NULL DEFAULT '[]',
  score REAL NOT NULL DEFAULT 0,
  score_detail TEXT NOT NULL DEFAULT '{}',
  why TEXT,
  created_at TEXT NOT NULL,
  UNIQUE(url)
);
CREATE INDEX IF NOT EXISTS idx_stories_score ON stories(score DESC);
CREATE INDEX IF NOT EXISTS idx_stories_published ON stories(published_at DESC);
CREATE TABLE IF NOT EXISTS feedback (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  story_id TEXT NOT NULL,
  action TEXT NOT NULL,
  created_at TEXT NOT NULL,
  UNIQUE(story_id, action)
);
CREATE TABLE IF NOT EXISTS bookmarks (
  story_id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS engagement (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  story_id TEXT NOT NULL,
  action TEXT NOT NULL,
  source TEXT,
  topics TEXT NOT NULL DEFAULT '[]',
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  started_at TEXT NOT NULL,
  finished_at TEXT,
  fetched INTEGER NOT NULL DEFAULT 0,
  inserted INTEGER NOT NULL DEFAULT 0,
  error_count INTEGER NOT NULL DEFAULT 0,
  errors TEXT NOT NULL DEFAULT '[]'
);
"""

def connect():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with connect() as con:
        con.executescript(SCHEMA)
        cols={r['name'] for r in con.execute('PRAGMA table_info(stories)').fetchall()}
        if 'image_url' not in cols: con.execute('ALTER TABLE stories ADD COLUMN image_url TEXT')

def story_id(url: str, title: str) -> str:
    return hashlib.sha256((url or title).encode()).hexdigest()[:24]

def upsert_story(item):
    now = datetime.now(timezone.utc).isoformat(); sid = story_id(item.get("url", ""), item.get("title", ""))
    with connect() as con:
        cur = con.execute("""
        INSERT OR IGNORE INTO stories
        (id,source,title,url,published_at,summary,author,image_url,topics,entities,score,score_detail,why,created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (sid, item.get("source","Unknown"), item.get("title","")[:1000], item.get("url","")[:3000],
              item.get("published_at"), item.get("summary","")[:5000], item.get("author","")[:500], item.get('image_url'),
              json.dumps(item.get("topics",[])), json.dumps(item.get("entities",[])), float(item.get("score",0)),
              json.dumps(item.get("score_detail",{})), item.get("why","")[:2000], now))
        return cur.rowcount

def update_score(sid, score, detail, topics, entities, why):
    with connect() as con:
        con.execute("UPDATE stories SET score=?, score_detail=?, topics=?, entities=?, why=? WHERE id=?",
                    (score, json.dumps(detail), json.dumps(topics), json.dumps(entities), why, sid))

def list_stories(limit=100, min_score=0, hours=None):
    sql = "SELECT * FROM stories WHERE score >= ?"; params = [min_score]
    if hours:
        sql += " AND datetime(COALESCE(published_at, created_at)) >= datetime('now', ?)"; params.append(f"-{int(hours)} hours")
    sql += " ORDER BY score DESC, datetime(COALESCE(published_at, created_at)) DESC LIMIT ?"; params.append(limit)
    with connect() as con: return [dict(r) for r in con.execute(sql, params).fetchall()]

def get_story(sid):
    with connect() as con:
        r=con.execute('SELECT * FROM stories WHERE id=?',(sid,)).fetchone(); return dict(r) if r else None

def all_unscored(limit=1000):
    with connect() as con: return [dict(r) for r in con.execute("SELECT * FROM stories ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()]

def add_feedback(story_id, action):
    now = datetime.now(timezone.utc).isoformat()
    with connect() as con: con.execute("INSERT OR IGNORE INTO feedback(story_id,action,created_at) VALUES (?,?,?)", (story_id,action,now))

def feedback_map():
    with connect() as con: rows = con.execute("SELECT story_id, action FROM feedback").fetchall()
    out = {}
    for r in rows: out.setdefault(r["story_id"], []).append(r["action"])
    return out

def toggle_bookmark(story_id):
    now=datetime.now(timezone.utc).isoformat()
    with connect() as con:
        exists=con.execute('SELECT 1 FROM bookmarks WHERE story_id=?',(story_id,)).fetchone()
        if exists: con.execute('DELETE FROM bookmarks WHERE story_id=?',(story_id,)); return False
        con.execute('INSERT INTO bookmarks(story_id,created_at) VALUES (?,?)',(story_id,now)); return True

def bookmark_ids():
    with connect() as con: return {r['story_id'] for r in con.execute('SELECT story_id FROM bookmarks').fetchall()}

def list_bookmarks():
    with connect() as con:
        return [dict(r) for r in con.execute('SELECT s.*, b.created_at AS newsmarked_at FROM bookmarks b JOIN stories s ON s.id=b.story_id ORDER BY b.created_at DESC').fetchall()]

def list_bookmarks_today():
    with connect() as con:
        return [dict(r) for r in con.execute("SELECT s.*, b.created_at AS newsmarked_at FROM bookmarks b JOIN stories s ON s.id=b.story_id WHERE date(b.created_at,'localtime')=date('now','localtime') ORDER BY b.created_at DESC").fetchall()]

def add_engagement(story_id, action):
    s=get_story(story_id)
    if not s: return
    now=datetime.now(timezone.utc).isoformat()
    with connect() as con: con.execute('INSERT INTO engagement(story_id,action,source,topics,created_at) VALUES (?,?,?,?,?)',(story_id,action,s['source'],s['topics'],now))

def diet_today():
    with connect() as con:
        rows=con.execute("SELECT * FROM engagement WHERE date(created_at,'localtime')=date('now','localtime') ORDER BY created_at").fetchall()
    source={}; topics={}; actions={}
    for r in rows:
        source[r['source']]=source.get(r['source'],0)+1; actions[r['action']]=actions.get(r['action'],0)+1
        try: ts=json.loads(r['topics'] or '[]')
        except: ts=[]
        for t in ts: topics[t]=topics.get(t,0)+1
    return {'total':len(rows),'sources':sorted(source.items(),key=lambda x:-x[1])[:8],'topics':sorted(topics.items(),key=lambda x:-x[1])[:10],'actions':actions}

def start_run():
    now = datetime.now(timezone.utc).isoformat()
    with connect() as con: return con.execute("INSERT INTO runs(started_at) VALUES (?)", (now,)).lastrowid

def finish_run(run_id, fetched, inserted, errors):
    now = datetime.now(timezone.utc).isoformat()
    with connect() as con: con.execute("UPDATE runs SET finished_at=?, fetched=?, inserted=?, error_count=?, errors=? WHERE id=?",(now,fetched,inserted,len(errors),json.dumps(errors),run_id))

def last_run():
    with connect() as con:
        r=con.execute("SELECT * FROM runs ORDER BY id DESC LIMIT 1").fetchone(); return dict(r) if r else None
