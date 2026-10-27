#!/usr/bin/env python3
"""Generate missing sentence/word audio, keeping all teacher recordings intact."""
from pathlib import Path
import argparse,asyncio,json
async def generate(source,kind,dry_run):
 d=json.loads((source/'lesson.json').read_text());manifest=source/'audio-manifest.json';old={x['key']:x for x in json.loads(manifest.read_text() if manifest.exists() else '[]')};jobs=[]
 for part in d['parts']:
  if kind=='vocabulary':
   for word in part['words']:
    jobs.append({'key':'word-'+word['zh'],'text':word['zh']+'？' if word['zh']=='哪' else word['zh'],'voice':word.get('voice','zh-CN-YunyangNeural' if word['zh']=='哪' else 'zh-CN-XiaoxiaoNeural'),'rate':'-35%','kind':'word'})
  else:
   for g in part['grammar_pages']:
    if g.get('practice_after',True):
     for q in g['practice']:jobs.append({'key':q['audio_key'],'text':q['zh'],'voice':'zh-CN-XiaoxiaoNeural','rate':'-10%','kind':'grammar-practice'})
 if dry_run:print(json.dumps(jobs,ensure_ascii=False,indent=2));return
 import edge_tts
 folder=source/'assets/audio';folder.mkdir(parents=True,exist_ok=True);sem=asyncio.Semaphore(3)
 async def one(j):
  async with sem:
   dest=folder/(j['key']+'.mp3');prior=old.get(j['key'],{})
   if prior.get('kind')=='teacher-provided':return
   valid=dest.exists() and dest.stat().st_size>1000 and all(prior.get(k)==j[k] for k in ['text','voice','rate'])
   if not valid:
    temp=dest.with_suffix('.tmp.mp3')
    await edge_tts.Communicate(j['text'],j['voice'],rate=j['rate']).save(str(temp))
    if temp.stat().st_size<1000:raise ValueError('Audio too short: '+j['key'])
    temp.replace(dest)
   old[j['key']]={**j,'file':str(dest.relative_to(source))}
 await asyncio.gather(*(one(j) for j in jobs));temp=manifest.with_suffix('.tmp.json');temp.write_text(json.dumps(list(old.values()),ensure_ascii=False,indent=2));temp.replace(manifest)
 print('Audio ready:',len(jobs),'items. Teacher recordings preserved.')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('--kind',choices=['vocabulary','grammar'],default='vocabulary');p.add_argument('--dry-run',action='store_true');a=p.parse_args();asyncio.run(generate(a.source,a.kind,a.dry_run))
