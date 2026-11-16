from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import json, urllib.parse
P = Path(__file__).resolve().parent
class H(BaseHTTPRequestHandler):
 def do_GET(self):
  self.send_response(200); self.send_header('Content-Type','text/html; charset=utf-8'); self.end_headers()
  self.wfile.write(b'<form method="post"><textarea name="payload" aria-label="Review JSON"></textarea><button>Save locally</button></form>')
 def do_POST(self):
  raw=self.rfile.read(int(self.headers['Content-Length']))
  j=json.loads(urllib.parse.parse_qs(raw.decode())['payload'][0])
  path=P/(j['station'].replace(' ','_')+'.json')
  old=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
  rows={r['review_id']:r for r in old.get('reviews',[])}
  for r in j['reviews']:
   prev=rows.get(r['review_id'])
   if prev and len(prev.get('text',''))>len(r.get('text','')): r['text']=prev['text']
   rows[r['review_id']]=r
  j['reviews']=list(rows.values()); j['complete']=len(rows)==j['displayed_total']
  path.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')
  self.send_response(200); self.end_headers(); self.wfile.write(('Saved '+str(len(rows))+' unique records').encode())
HTTPServer(('127.0.0.1',8768),H).serve_forever()
