#!/usr/bin/env python3
"""Local-first authoring workflow. Python 3.12+. No network during build/check/export."""
from pathlib import Path
import argparse,base64,datetime,hashlib,http.server,json,mimetypes,re,shutil,subprocess,sys,urllib.parse
from lxml import html
ROOT=Path(__file__).resolve().parents[1]
def dump(value):print(json.dumps(value,ensure_ascii=False,indent=2))
def build(source):
 subprocess.run([sys.executable,str(ROOT/'recipes/build.py'),str(source.resolve())],check=True)
def resource(source,url):
 if not url or url.startswith(('data:','blob:','#')):return None
 if urllib.parse.urlsplit(url).scheme:raise ValueError('External resource is not offline: '+url)
 p=(source.parent/urllib.parse.unquote(url.split('?',1)[0].split('#',1)[0])).resolve()
 if not p.is_file():raise FileNotFoundError(p)
 return p
CSS_URL=re.compile(r'url\(\s*[\'"]?([^\'"\s)]+)[\'"]?\s*\)')
def inspect(source):
 doc=html.fromstring(source.read_text());missing=[];draft=[]
 for el in doc.xpath('//*[@src or @data-audio]'):
  for key in ['src','data-audio']:
   url=el.get(key)
   if not url:continue
   try:resource(source,url)
   except (ValueError,FileNotFoundError):missing.append(url)
   if 'placeholder.svg' in url:draft.append('placeholder image')
 for style in doc.xpath('//style | //*[@style]'):
  css=style.text if style.tag=='style' else style.get('style')
  for m in CSS_URL.finditer(css or ''):
   try:resource(source,m[1])
   except (ValueError,FileNotFoundError):missing.append(m[1])
 if doc.xpath('//button[@disabled and contains(@class,"sound-hit")]'):draft.append('missing audio')
 ids=[e.get('data-edit-id') for e in doc.xpath('//*[@data-edit-id]')]
 if len(set(ids))!=len(ids):missing.append('duplicate editable IDs')
 return {'slides':len(doc.xpath('//section[contains(concat(" ",normalize-space(@class)," ")," slide ")]')),'missing':sorted(set(missing)),'draft_reasons':sorted(set(draft)),'sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
def export(source,target,allow_draft=False):
 report=inspect(source)
 if report['missing'] or (report['draft_reasons'] and not allow_draft):raise ValueError('Cannot export: '+json.dumps(report,ensure_ascii=False))
 doc=html.fromstring(source.read_text())
 def inline(url):
  p=resource(source,url)
  if p is None:return url
  mime=mimetypes.guess_type(p.name)[0] or 'application/octet-stream'
  return 'data:'+mime+';base64,'+base64.b64encode(p.read_bytes()).decode()
 for e in doc.xpath('//*[@src or @data-audio]'):
  for key in ['src','data-audio']:
   if e.get(key):e.set(key,inline(e.get(key)))
 for e in doc.xpath('//style | //*[@style]'):
  if e.tag=='style':e.text=CSS_URL.sub(lambda m:'url("'+inline(m[1])+'")',e.text or '')
  else:e.set('style',CSS_URL.sub(lambda m:'url("'+inline(m[1])+'")',e.get('style')))
 target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists():shutil.copy2(target,target.with_name(target.name+'.'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.bak'))
 target.write_text('<!doctype html>\n'+html.tostring(doc,encoding='unicode',method='html'))
 after=inspect(target)
 if after['missing']:raise ValueError(after)
 return {'output':str(target),'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'draft':bool(report['draft_reasons'])}
def main():
 p=argparse.ArgumentParser();sub=p.add_subparsers(dest='cmd',required=True)
 q=sub.add_parser('init-unit');q.add_argument('destination',type=Path);q.add_argument('--unit',type=int)
 q=sub.add_parser('build');q.add_argument('source',type=Path)
 q=sub.add_parser('check');q.add_argument('html',type=Path)
 q=sub.add_parser('export');q.add_argument('html',type=Path);q.add_argument('output',type=Path);q.add_argument('--approved',action='store_true');q.add_argument('--allow-draft',action='store_true')
 q=sub.add_parser('snapshot');q.add_argument('source',type=Path)
 q=sub.add_parser('serve');q.add_argument('--port',type=int,default=8766);q.add_argument('--directory',type=Path,default=ROOT)
 a=p.parse_args()
 if sys.version_info<(3,12):p.error('Use Python 3.12 or newer')
 if a.cmd=='init-unit':
  if a.destination.exists():raise FileExistsError(a.destination)
  shutil.copytree(ROOT/'examples/Unit2-Mau/source',a.destination,ignore=shutil.ignore_patterns('preview*','practice-review.json','__pycache__'))
  data=json.loads((a.destination/'lesson.json').read_text());match=re.search(r'Unit(\d+)',str(a.destination),re.I);data['unit']=a.unit if a.unit is not None else int(match[1]) if match else 2;data['storage_id']=a.destination.parent.name+'-'+a.destination.name;(a.destination/'lesson.json').write_text(json.dumps(data,ensure_ascii=False,indent=2));print(a.destination)
 elif a.cmd=='build':build(a.source)
 elif a.cmd=='check':
  report=inspect(a.html);dump(report)
  if report['missing']:raise SystemExit(1)
 elif a.cmd=='export':
  if not a.approved:p.error('Preview and get teacher approval first; then pass --approved')
  dump(export(a.html,a.output,a.allow_draft))
 elif a.cmd=='snapshot':
  target=a.source/'.snapshots'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S');target.mkdir(parents=True)
  for f in ['lesson.json','audio-manifest.json','layout.json','preview.html']:
   if (a.source/f).exists():shutil.copy2(a.source/f,target/f)
  print(target)
 else:
  import functools
  handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(a.directory.resolve()))
  print(f'Preview: http://127.0.0.1:{a.port}/')
  http.server.ThreadingHTTPServer(('127.0.0.1',a.port),handler).serve_forever()
if __name__=='__main__':main()
