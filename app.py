from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json, mimetypes, threading, time
from twin.config import ROOT, HOST, PORT, PROFILE_PATH, SOURCES_PATH, REFRESH_MINUTES, load_profile, load_sources
from twin.db import init_db, add_feedback, last_run, list_stories, toggle_bookmark, list_bookmarks, add_engagement, diet_today
from twin.ingest import refresh
from twin.digest import build_digest, hydrate
from twin.emailer import email_newsmarks
STATIC=ROOT/'static'

def send_json(h,obj,status=200):
    data=json.dumps(obj,ensure_ascii=False).encode(); h.send_response(status); h.send_header('Content-Type','application/json; charset=utf-8'); h.send_header('Content-Length',str(len(data))); h.end_headers(); h.wfile.write(data)
def read_json(h):
    n=int(h.headers.get('Content-Length','0') or 0); return json.loads(h.rfile.read(n) or b'{}')
class Handler(SimpleHTTPRequestHandler):
    def log_message(self,fmt,*args): print('[twin]',fmt%args)
    def end_headers(self):
        origin=self.headers.get('Origin','')
        if origin.startswith('chrome-extension://'):
            self.send_header('Access-Control-Allow-Origin',origin)
            self.send_header('Access-Control-Allow-Headers','Content-Type')
            self.send_header('Access-Control-Allow-Methods','GET, POST, OPTIONS')
            self.send_header('Vary','Origin')
        super().end_headers()
    def do_OPTIONS(self):
        self.send_response(204); self.end_headers()
    def do_GET(self):
        p=urlparse(self.path)
        if p.path=='/api/digest': return send_json(self,build_digest())
        if p.path=='/api/status': return send_json(self,{'last_run':last_run(),'profile':load_profile(),'sources':load_sources()})
        if p.path=='/api/stories':
            q=parse_qs(p.query); return send_json(self,[hydrate(x) for x in list_stories(int(q.get('limit',[100])[0]))])
        if p.path=='/api/profile': return send_json(self,load_profile())
        if p.path=='/api/sources': return send_json(self,load_sources())
        if p.path=='/api/bookmarks': return send_json(self,[hydrate(x) for x in list_bookmarks()])
        if p.path=='/api/diet': return send_json(self,diet_today())
        if p.path=='/api/podcasts':
            return send_json(self,[
                {'name':'Hard Fork','note':'A sharp, conversational weekly scan of AI and the technology industry.','url':'https://www.nytimes.com/column/hard-fork'},
                {'name':'No Priors','note':'AI founders, researchers and investors on what is being built next.','url':'https://www.nopriors.com/'},
                {'name':'Nature Podcast','note':'New research across life sciences, neuroscience and the physical sciences.','url':'https://www.nature.com/nature/articles?type=nature-podcast'},
            ])
        rel=p.path.lstrip('/') or 'index.html'; f=(STATIC/rel).resolve()
        if not str(f).startswith(str(STATIC.resolve())) or not f.exists(): self.send_error(404); return
        data=f.read_bytes(); self.send_response(200); self.send_header('Content-Type',mimetypes.guess_type(f.name)[0] or 'application/octet-stream'); self.send_header('Content-Length',str(len(data))); self.end_headers(); self.wfile.write(data)
    def do_POST(self):
        p=urlparse(self.path)
        if p.path=='/api/refresh':
            try: return send_json(self,refresh())
            except Exception as e: return send_json(self,{'error':str(e)},500)
        body=read_json(self)
        if p.path=='/api/feedback':
            action=body.get('action'); sid=body.get('story_id')
            if action not in {'more','less','important','surprised'} or not sid: return send_json(self,{'error':'invalid feedback'},400)
            add_feedback(sid,action); add_engagement(sid,'feedback:'+action); return send_json(self,{'ok':True})
        if p.path=='/api/bookmark':
            sid=body.get('story_id'); state=toggle_bookmark(sid); add_engagement(sid,'newsmark' if state else 'unnewsmark'); return send_json(self,{'newsmarked':state})
        if p.path=='/api/newsmarks/email':
            try: return send_json(self,email_newsmarks(body.get('to',''), preview=bool(body.get('preview'))))
            except ValueError as e: return send_json(self,{'error':str(e)},400)
            except RuntimeError as e: return send_json(self,{'error':str(e)},503)
        if p.path=='/api/engage': add_engagement(body.get('story_id'),body.get('action','open')); return send_json(self,{'ok':True})
        if p.path=='/api/profile': PROFILE_PATH.write_text(json.dumps(body,indent=2,ensure_ascii=False)+'\n',encoding='utf-8'); return send_json(self,{'ok':True})
        if p.path=='/api/sources': SOURCES_PATH.write_text(json.dumps(body,indent=2,ensure_ascii=False)+'\n',encoding='utf-8'); return send_json(self,{'ok':True})
        self.send_error(404)
def scheduler_loop(minutes=REFRESH_MINUTES):
    while True:
        try: refresh()
        except Exception as e: print('[twin] scheduled refresh failed:',e)
        time.sleep(minutes*60)
def main():
    init_db(); threading.Thread(target=scheduler_loop,daemon=True).start(); print(f'TwinTimes running at http://{HOST}:{PORT}'); ThreadingHTTPServer((HOST,PORT),Handler).serve_forever()
if __name__=='__main__': main()
