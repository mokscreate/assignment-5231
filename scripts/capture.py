from http.server import HTTPServer,BaseHTTPRequestHandler
from pathlib import Path
import json
P=Path('D:/Desktop/26年bps课程/5231ai/tmp/formal_reviews')
class H(BaseHTTPRequestHandler):
 def do_GET(self):
  self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.end_headers();self.wfile.write(b'<h1>Local research capture</h1><form method="post"><textarea name="payload" aria-label="Review JSON" rows="12" cols="80"></textarea><button>Save locally</button></form>')
 def do_POST(self):
  import urllib.parse
  raw=self.rfile.read(int(self.headers['Content-Length']));j=json.loads(urllib.parse.parse_qs(raw.decode())['payload'][0]);name=j['station'].replace(' ','_');(P/(name+'.json')).write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8');self.send_response(200);self.end_headers();self.wfile.write(('Saved '+str(len(j['reviews']))+' records').encode())
HTTPServer(('127.0.0.1',8767),H).serve_forever()

