from pathlib import Path
import json,sys,html as H,re,copy,random,os
from lxml import html,etree as E
RUNTIME=Path(__file__).resolve().parents[1]/'runtime'
if len(sys.argv)!=2:raise SystemExit('Usage: python recipes/build.py path/to/unit/source')
W=Path(sys.argv[1]).resolve();B=W.parent;U1=B.parent/'Unit1-Chaohoi/nguon-chinh-sua'
sys.path.insert(0,str(RUNTIME/'pinyin'));import build_deck as b
b.bl.SINGLE.update({'教':'jiāo','谁':'shéi'});b.bl.WORDS.update({'认识':'rèn shi','高兴':'gāo xìng','名字':'míng zi','朋友':'péng you','留学生':'liú xué shēng','李英男':'lǐ yīng nán','麦克':'mài kè','阮清河':'ruǎn qīng hé','陈林':'chén lín','西蒙':'xī méng','北京语言大学':'běi jīng yǔ yán dà xué'})
D=json.loads((W/'lesson.json').read_text());AUD={x['key']:x for x in json.loads((W/'audio-manifest.json').read_text() if (W/'audio-manifest.json').exists() else '[]')}
def R(s):
 names={'阮清河':'{阮清河|Ruǎn Qīng hé}','陈林':'{陈|Chén}{林|Lín}','麦克':'{麦克|Mài kè}','越南':'{越南|Yuè nán}','中国':'{中国|Zhōng guó}','德国':'{德国|Dé guó}','法国':'{法国|Fǎ guó}','美国':'{美国|Měi guó}','日本':'{日本|Rì běn}','韩国':'{韩国|Hán guó}','陈':'{陈|Chén}','阮':'{阮|Ruǎn}','王':'{王|Wáng}','李':'{李|Lǐ}'}
 text=str(s).replace('哪儿','{哪儿|nǎr}').replace('一下儿','{一下儿|yí xiàr}')
 text=re.sub('|'.join(re.escape(k) for k in sorted(names,key=len,reverse=True)),lambda m:names[m[0]],text)
 return b.rich(text)

base=html.fromstring((RUNTIME/'frame.html').read_text());css=base.find('.//style').text;bodyattrs=base.find('body').attrib;nav=html.tostring(base.xpath('//nav')[0],encoding='unicode');css=css.replace("../../Tai-nguyen-chung/fonts/", "../../../Tai-nguyen-chung/fonts/")
slides=[];model=[]
def add(title,body,part=0,kind='content',attrs=''):
 n=len(slides)+1;head=f'<header><strong>{"Phần "+str(part) if part else "UNIT "+str(D.get("unit",2))}</strong><h2>{title}</h2></header>'
 slides.append(f'<section class="slide u2" data-source="u2-{n}" {attrs}>{head}{body}</section>');model.append({'number':n,'part':part,'kind':kind,'title':title});return n
def pic(key):
 key={'陈林':'王伟','阮清河':'阮秋香','麦克':'保罗'}.get(key,key)
 candidates=[W/'assets/photos'/(key+ext) for ext in ['.png','.jpg','.jpeg','.svg']]+[W/'assets'/(key+'.svg')]
 return os.path.relpath(next((p for p in candidates if p.exists()),RUNTIME/'placeholder.svg'),W)
def photo(key,cls='',alt=''):
 return f'<img class="{cls}" src="{H.escape(pic(key))}" alt="{H.escape(alt or {'阮秋香':'阮清河','王伟':'陈林','保罗':'麦克'}.get(key,key))}">'
def sound(key,auto=False):
 row=AUD.get(key);
 if not row:return '<button class="sound-hit u2-sound" disabled title="Chưa có audio: '+H.escape(key)+'">🔇</button>'
 row={**row,'file':row['file']+'?v='+D['revision']};attr=' data-auto="1"' if auto else ''
 return f'<button class="sound-hit u2-sound" data-audio="{H.escape(row["file"])}" aria-label="Nghe phát âm" title="Nghe phát âm"{attr}>🔊</button>'
def sentence(z,vi,cls=''):
 return f'<div class="u2-sentence {cls}"><div>{R(z)}</div><div class="vi-text">{vi}</div></div>'
def role_icon(role,dialogue=None):
 icons={'A':('👩🏻','Nhân vật nữ'), 'B':('👨🏻','Nhân vật nam'), 'C':('🧑🏼','Nhân vật thứ ba')}
 icon,label=icons.get(role,('👤','Nhân vật'))
 if dialogue:icon=dialogue.get('characters',{}).get(role,icon)
 label='Nhân vật nữ' if '👩' in icon else ('Nhân vật nam' if '👨' in icon else 'Nhân vật hội thoại')
 return '<span class="character-icon" role="img" aria-label="'+label+'">'+icon+'</span>'
def highlighted(z,targets,cls):
 if not targets:return R(z)
 return ''.join('<span class="'+cls+'">'+R(t)+'</span>' if i%2 else R(t) for i,t in enumerate(re.split('('+ '|'.join(re.escape(x) for x in sorted(set(targets),key=len,reverse=True))+')',z)))
# Explicit three-tier text for chat and grammar. All pinyin is derived from rich().
PY_WORDS={'不是':'bú shì','阮清河':'Ruǎn Qīnghé','陈林':'Chén Lín','麦克':'Màikè','越南':'Yuènán','中国':'Zhōngguó','德国':'Déguó','法国':'Fǎguó','美国':'Měiguó','日本':'Rìběn','韩国':'Hánguó','什么':'shénme','名字':'míngzi','认识':'rènshi','高兴':'gāoxìng','朋友':'péngyou','老师':'lǎoshī','你们':'nǐmen','我们':'wǒmen','他们':'tāmen','她们':'tāmen','请问':'qǐngwèn','贵姓':'guìxìng'}
def py_text(z):
 out=[]
 for token in re.findall('|'.join(re.escape(x) for x in sorted(PY_WORDS,key=len,reverse=True))+'|.',z):
  if token in PY_WORDS:out.append(PY_WORDS[token]);continue
  node=html.fragment_fromstring(R(token),create_parent='div');rts=node.xpath('.//rt');out.append(' '.join(x.text_content() for x in rts) if rts else token)
 return ' '.join(out).replace(' 。','。').replace(' ？','？').replace(' ，','，').replace(' 、','、')
def tiers(z,vi,targets=(),cls='grammar-target'):
 chunks=re.split('('+'|'.join(re.escape(x) for x in sorted(set(targets),key=len,reverse=True))+')',z) if targets else [z]
 han=[];py=[]
 for i,t in enumerate(chunks):
  if not t:continue
  cl=' class="'+cls+'"' if targets and i%2 else ''
  han.append('<span'+cl+'>'+H.escape(t)+'</span>');py.append('<span'+cl+'>'+H.escape(py_text(t))+'</span>')
 return '<div class="tier-pinyin">'+' '.join(py)+'</div><div class="tier-hanzi">'+''.join(han)+'</div><div class="tier-vi vi-text">'+H.escape(vi)+'</div>'
def managed(content,id,label,base=42,cls=''):
 return '<div class="managed-box '+cls+'" data-edit-id="'+id+'" data-edit-label="'+H.escape(label)+'" data-base-font="'+str(base)+'"><button class="edit-grip" aria-label="Kéo khung">⠿</button>'+content+'</div>'
def book_turns(col,dialogue,column):
 groups=[]
 for index,t in enumerate(col):
  if groups and groups[-1][0]==t[0]:groups[-1][1].append((index,t))
  else:groups.append((t[0],[(index,t)]))
 out=[]
 for gi,(role,items) in enumerate(groups):
  z=''.join(t[1] for index,t in items);vi=' '.join(t[2] for index,t in items)
  links=[link for index,t in items for link in dialogue['replacement_links'] if link['column']==column and link['turn']==index]
  text=tiers(z,vi,[],'replace-term')
  node=html.fragment_fromstring(text,create_parent='div');han=node.xpath('.//*[@class="tier-hanzi"]')[0];han.clear();han.set('class','tier-hanzi');han.append(html.fragment_fromstring('<span>'+book_source(z,links)+'</span>'));text=''.join(html.tostring(e,encoding='unicode') for e in node)
  content='<div class="chat-person">'+role_icon(role,dialogue)+'</div><div class="chat-content">'+text+'</div>'
  out.append(managed(content,dialogue['_id']+'-chat-'+str(column)+'-'+str(gi),'Lời thoại '+role,42,'chat-card'))
 return ''.join(out)
def book_source(z,links):
 names=[];targets=sorted(set([x['source'] for x in links]),key=len,reverse=True);out=[];at=0;used=set()
 for m in (re.finditer('|'.join(re.escape(t) for t in targets),z) if targets else []):
  out.append(H.escape(z[at:m.start()]));link=next((x for x in links if x['source']==m[0] and x['id'] not in used),None)
  if link:used.add(link['id']);out.append('<span class="replace-term connected-source" data-replacement-anchor="'+link['id']+'" role="button" tabindex="0" title="Bấm để hiện khung thay thế">'+H.escape(m[0])+'</span>')
  else:out.append(H.escape(m[0]))
  at=m.end()
 return ''.join(out)+H.escape(z[at:])
def book_reference(dialogue):
 text=' '.join(t[1] for col in dialogue['cols'] for t in col)+' '+ ' '.join(x['alternatives'] for x in dialogue['replacement_links'])
 names=[(z,vi) for z,vi in [('阮清河','Nguyễn Thanh Hà'),('陈林','Trần Lâm'),('麦克','Mike')] if z in text]
 if not names:return ''
 content='<h3>TÊN RIÊNG</h3>'+''.join('<div class="reference-name">'+R(z)+'<div class="vi-text">'+vi+'</div></div>' for z,vi in names)
 return managed(content,dialogue['_id']+'-reference','Tên riêng',31,'book-reference')
def book_callouts(dialogue):
 out='<svg class="editable-lines connected-lines" viewBox="0 0 1920 1080"><defs><marker id="'+dialogue['_id']+'-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="context-stroke"/></marker></defs>'
 cards=''
 for link in dialogue['replacement_links']:
  bid=link['id']+'-box';lid=link['id']+'-line'
  content='<div class="callout-content">'+R(link['alternatives'])+'</div>'
  box=html.fragment_fromstring(managed(content,bid,'Thay thế: '+link['source'],37,'substitution linked-callout'),create_parent='div')[0];box.set('data-callout-key',link['id']);box.set('data-column',str(link['column']));cards+=html.tostring(box,encoding='unicode')
  out+='<g data-edit-line="'+lid+'" data-edit-label="Mũi tên: '+link['source']+'" data-linked-box="'+bid+'" data-anchor="'+link['id']+'"><line x1="0" y1="0" x2="0" y2="0" stroke="#f15922" stroke-width="2.5"/><path class="connector-route" fill="none" marker-end="url(#'+dialogue['_id']+'-arrow)"/><circle class="line-grip" data-end="1" r="13"/><circle class="line-grip" data-end="2" r="13"/><circle class="line-grip bend-grip" data-end="bend" r="13"/></g>'
 return out+'</svg>'+cards
def word_visual(word):
 kind=word.get('visual')
 if not kind:return photo(word['photo'],'word-picture',word['vi'])
 if kind=='near':return '<div class="concept-visual near-scene" role="img" aria-label="Người nói chỉ vào vật ở gần"><div class="near-person">🧑🏻</div><div class="near-arrow">➜</div><div class="near-item">●<small>Ở GẦN</small></div><div class="far-item">○<small>Ở XA</small></div><div class="near-label">'+R('这')+'<div class="vi-text">Đây · cái này</div></div></div>'
 if kind=='which':return '<div class="concept-visual choice-scene"><div class="concept-question">?</div><div class="visual-flags">'+photo('flag-vn')+photo('flag-cn')+photo('flag-jp')+'</div><div class="vi-text">Nào?</div></div>'
 if kind=='who':return '<div class="concept-visual"><div class="concept-question">?</div><div class="people-symbols">👩🏻　👨🏻　🧑🏼</div><div class="concept-caption vi-text">Ai?</div></div>'
 if kind=='identity':return '<div class="concept-visual"><div class="identity-symbols">👩🏻　＝　🧑🏻‍🏫</div><div class="identity-check">✓</div><div class="concept-caption">'+R('她是老师。')+'</div></div>'
 return '<div class="concept-visual"><div class="concept-question">?</div><div class="shape-symbols">●　◆　■</div><div class="concept-caption vi-text">Gì?</div></div>'
def formula_parts(point):
 parts=point['formula'].split(' + ')
 return ' <span class="formula-plus">+</span> '.join('<span class="formula-chip chip-'+str(min(i,2))+'">'+R(t)+'</span>' for i,t in enumerate(parts))
def grammar_page(g):
 gid=g['id'];point=g['points'][0]
 content=managed('<h3>'+R(point['title'].upper())+'</h3>',gid+'-title','Tên điểm ngữ pháp',32,'grammar-title-box')
 content+=managed('<div class="formula-components">'+formula_parts(point)+'</div>',gid+'-formula','Công thức',42,'pastel-formula')
 content+=managed(R(point['explain']),gid+'-usage','Cách dùng',30,'single-usage')
 content+='<div class="single-examples">'
 for j,(z,vi) in enumerate(point['examples']):content+=managed(tiers(z,vi,point['targets']),gid+'-example-'+str(j),'Ví dụ '+str(j+1),50,'single-example example-'+str(j))
 return '<main class="u2-grammar grammar-single">'+content+'</div>'+managed(R(g['note']),gid+'-note','Chú ý',28,'grammar-note single-note')+'</main>'
def grammar_practice(g):
 gid=g.get('practice_id',g['id']);body='<main class="practice-page fly-practice '+('four-fly' if len(g['practice'])==4 else '')+'"><h3>'+g.get('practice_title','Luyện tập · Điền từ vào chỗ trống')+'</h3><div class="token-bank">'
 qs=list(enumerate(g['practice']));random.Random(g['id']).shuffle(qs)
 for i,q in qs:
  body+='<div class="bank-source"><button class="word-token" data-fly-id="'+gid+'-q'+str(i)+'" aria-label="Điền '+H.escape(q['answer'])+'">'+R(q['answer'])+'</button></div>'
 body+='</div><div class="fly-questions">'
 for i,q in enumerate(g['practice'],1):
  a=q['answer'];left,right=q['zh'].split(a,1);fid=gid+'-q'+str(i-1)
  body+='<article><div class="drill-vi vi-text">'+str(i)+'. '+q['vi']+'</div><div class="fly-zh">'+R(left)+'<span class="fly-slot" data-fly-target="'+fid+'" role="button" tabindex="0" aria-label="Chỗ trống câu '+str(i)+'"><span class="slot-sizing">'+R(a)+'</span></span>'+R(right)+sound(q['audio_key'])+'</div></article>'
 return body+'</div></main>'
def answer(z):
 m=re.search(r'([。？！.!?]+)$',z);punct=m[0] if m else '';core=z[:-len(punct)] if punct else z
 return R('[['+core+']]')+punct
def matching(words,part,title='Tổng kết từ vựng · Nối cặp',audio_kind='word'):
 half=(len(words)+1)//2;markup='<main class="matching-main"><p class="instruction">Chọn từ tiếng Trung rồi chọn nghĩa tiếng Việt tương ứng.</p><div class="matching-board">'
 for gi,g in enumerate([words[:half],words[half:]]):
  shuffled=list(enumerate(g));random.Random(part*21+len(slides)+gi).shuffle(shuffled)
  if len(shuffled)>1 and [i for i,w in shuffled]==list(range(len(g))):shuffled=shuffled[1:]+shuffled[:1]
  markup+='<div class="match-group"><div class="match-words">'
  for i,word in enumerate(g):
   a=AUD.get('word-'+word['zh'],{'file':''});markup+=f'<button class="match-item" data-side="word" data-key="{gi}-{i}" data-audio="{a["file"]}">{R(word["zh"])}</button>'
  markup+='</div><svg class="match-lines" viewBox="0 0 100 600" preserveAspectRatio="none" aria-hidden="true"></svg><div class="match-meanings">'+''.join(f'<button class="match-item vi-text" data-side="meaning" data-key="{gi}-{i}">{word["vi"]}</button>' for i,word in shuffled)+'</div></div>'
 markup+='</div><div class="match-counter" aria-live="polite">Đã nối 0/'+str(len(words))+' cặp</div></main>';add(title,markup,part,'matching')
# Cover and the two review slides retained from the teacher's Unit1 decisions.
add(D.get('title_vi','Tên và quốc tịch'),'<main class="u2-cover"><div><div class="unit-label">UNIT '+str(D.get('unit',2))+'</div><h1>'+R(D['title_zh'])+'</h1><p class="vi-text">'+H.escape(D.get('title_vi','Tên và quốc tịch'))+'</p></div>'+photo('cover',alt='Hai người làm quen')+'</main>',0,'cover')
review=[('她','cô ấy'),('累','mệt'),('饿','đói'),('很','rất'),('老师','thầy cô'),('渴','khát')]
add('Kiểm tra bài cũ','<main><p class="instruction">Nói nghĩa tiếng Việt của từ rồi đọc một câu có từ đó.</p><div class="review-six">'+''.join('<article>'+R(z)+'<div class="vi-text">'+R('[['+vi+']]')+'</div></article>' for z,vi in review)+'</div></main>',0,'review')
add('Kiểm tra bài cũ','<main><div class="review-scenes">'+''.join('<article>'+photo(im,alt=vi)+sentence(q,vi)+sentence(a,av,'stage')+'</article>' for im,q,vi,a,av in [('tired-face','你累吗？','Bạn mệt không?','我不累。','Tôi không mệt.'),('hungry','你饿吗？','Bạn đói không?','我很饿。','Tôi rất đói.'),('thirsty','你渴吗？','Bạn khát không?','我不渴。','Tôi không khát.')])+'</div></main>',0,'review')
for part in D['parts']:
 no=part['no'];add(part['title'],'<main class="u2-divider"><p>Phần '+str(no)+'</p><h1>'+part['title']+'</h1></main>',no,'divider')
 for word in part['words']:
  ex='<div class="word-example"><div>'+R(word['example'])+'</div><div class="example-meaning vi-text">'+word['example_vi']+'</div></div>' if word['example'] else ''
  body='<main class="u2-vocab"><div class="word-card">'+sound('word-'+word['zh'],True)+'<div class="word-title">'+R(word['zh'])+'</div><div class="word-pos">'+word['pos']+'</div><div class="word-meaning vi-text">'+word['vi']+'</div>'+ex+'</div>'+word_visual(word)+'</main>'
  add('Từ mới',body,no,'word',f'data-word="{word["zh"]}"')
 for idx,dialogue in enumerate(part['dialogues']):
  dialogue['_id']='book-'+str(no)+'-'+str(idx)
  cols=['<article class="dialogue-col">'+book_turns(col,dialogue,j)+'</article>' for j,col in enumerate(dialogue['cols'])]
  attrs='data-book="'+dialogue['_id']+'"'
  reference=book_reference(dialogue)
  add('Bài khoá','<div class="book-sound">'+sound(f'book-{no}-{idx}')+'</div><main class="u2-book chat-book"><div class="topic">'+dialogue['title']+'</div><div class="chat-book-layout '+('no-reference' if not reference else '')+'"><div class="u2-dialogue">'+''.join(cols)+'</div>'+reference+'</div></main>'+book_callouts(dialogue),no,'dialogue',attrs)
 for g in part['grammar_pages']:
  add('Ngữ pháp',grammar_page(g),no,'grammar',f'data-grammar="{g["id"]}"')
  if g.get('practice_after',True):add('Luyện tập ngữ pháp',grammar_practice(g),no,'grammar-practice',f'data-grammar-practice="{g.get("practice_id",g["id"])}"')
 if no==2:
  branches=[('flag-vn','越南','我是越南人。','Tôi là người Việt Nam.'),('flag-cn','中国','我是中国人。','Tôi là người Trung Quốc.'),('flag-kr','韩国','我是韩国人。','Tôi là người Hàn Quốc.')]
  add('Mở rộng','<main class="u2-branches"><div class="branch-root">'+R('你是哪国人？')+'</div><svg class="branch-arrow" viewBox="0 0 1700 90"><path d="M850 0L180 85M850 0V85M850 0L1520 85" fill="none" stroke="#275389" stroke-width="3"/></svg><div class="branch-grid">'+''.join('<article><div class="stage branch-head">'+photo(im)+R(z)+'</div><div class="stage">'+sentence(ans,vi)+'</div></article>' for im,z,ans,vi in branches)+'</div></main>',no,'expansion')
 words=part['words'];pages=(len(words)+11)//12;chunk=(len(words)+pages-1)//pages
 for start in range(0,len(words),chunk):matching(words[start:start+chunk],no)
# Seven practice pages mirror the teacher's latest approved format.
part=3;add('Luyện tập','<main class="u2-divider"><p>Phần 3</p><h1>Luyện tập và vận dụng</h1></main>',3,'divider')
rows=D['practice']['rows']
body='<main class="practice-page"><h3>Từ vựng</h3><p class="practice-instruction">Nói tiếng Trung hoặc nghĩa tiếng Việt vào ô trống.</p><div class="split-tables">'
for group in [rows[:4],rows[4:]]:
 body+='<table><thead><tr><th>Tiếng Trung</th><th>Nghĩa tiếng Việt</th></tr></thead><tbody>'+''.join('<tr><td>'+R(z if i%2==0 else '[['+z+']]')+'</td><td>'+R('[['+vi+']]' if i%2==0 else vi)+'</td></tr>' for i,(z,vi) in enumerate(group))+'</tbody></table>'
add('Luyện tập',body+'</div></main>',3,'practice','data-practice="1"')
fills=D['practice']['fill']
add('Luyện tập','<main class="practice-page"><h3>Hoàn thành câu</h3><div class="fill-six">'+''.join('<article><div class="fill-meaning">'+str(i)+'. '+vi+'</div><div class="fill-question">'+R(z)+'</div></article>' for i,(vi,z) in enumerate(fills,1))+'</div></main>',3,'practice','data-practice="2"')
orders=D['practice']['order']
translations=D['practice']['translate']
body='<main class="practice-page five-practice"><h3>Sắp xếp câu</h3><div class="five-rows">'+''.join('<article><div class="five-prompt">'+str(i)+'. '+R(q)+'</div><div class="five-answer">→ '+answer(a)+'</div></article>' for i,(q,a) in enumerate(orders,1))+'</div></main>'
add('Luyện tập',body,3,'practice','data-practice="order"')
body='<main class="practice-page five-practice"><h3>Dịch Việt → Trung</h3><div class="five-rows translate-five">'+''.join('<article><div class="five-prompt">'+str(i)+'. '+q+'</div><div class="five-answer">'+answer(a)+'</div></article>' for i,(q,a) in enumerate(translations,1))+'</div></main>'
add('Luyện tập',body,3,'practice','data-practice="translate"')
pics=D['practice']['picture']
add('Luyện tập','<main class="practice-page"><h3>Hoàn thành hội thoại theo tranh</h3><div class="picture-four">'+''.join('<article><span class="picture-number">'+str(i)+'.</span>'+photo(im)+'<div class="picture-dialogue">'+R(z).replace('A:',role_icon('A')).replace('B:',role_icon('B'))+'</div></article>' for i,(im,z) in enumerate(pics,1))+'</div></main>',3,'practice','data-practice="4"')
longs=D['practice']['long']
add('Luyện tập','<main class="long-dialogue-page"><h3>Hoàn thành hội thoại theo tranh</h3><div class="long-dialogue-columns">'+''.join('<article><div class="long-photo"><span>'+str(i)+'.</span>'+photo(im)+'</div><div class="long-turns">'+''.join('<div class="long-turn"><span class="long-role">'+role_icon(role)+'</span><div>'+R(z)+'</div></div>' for role,z in turns)+'</div></article>' for i,(im,turns) in enumerate(longs,1))+'</div></main>',3,'practice','data-practice="long"')
reflex=copy.deepcopy(base.xpath('//section[@data-practice="5"]//main')[0]);reflex.xpath('.//audio')[0].set('src',AUD.get('reflex',{'file':''})['file']);reflex.xpath('.//*[@id="reflex-duration"]')[0].text='0:00'
add('Luyện tập',html.tostring(reflex,encoding='unicode'),3,'practice','data-practice="5"')
situations=D['practice']['situations']
add('Luyện tập','<main class="practice-page"><h3>Tự luyện tập thực tế</h3><div class="real-life">'+''.join('<article><div class="situation">• '+vi+'</div><div class="hint-label">Gợi ý</div><div class="situation-hints">'+R(hints)+'</div></article>' for vi,hints in situations)+'</div></main>',3,'practice','data-practice="6"')
# The notes and matching histories are separate from Unit1.
ui=(RUNTIME/'base-ui.js').read_text().replace('mono-unit1-notes-v1','mono-unit2-teacher-v5-notes-v1')
ui=ui.replace('main *,.card-pinyin,.example-box,.shi-photo','main *,.card-pinyin,.example-box,.shi-photo')
# Keep scroll's current visible slide, rather than the slide active before scrolling.
old_scroll="$('scroll-toggle').onclick=()=>{scrollMode=!scrollMode;document.body.classList.toggle('scroll',scrollMode);$('scroll-toggle').setAttribute('aria-pressed',scrollMode);fit();if(scrollMode)slides[at].parentElement.scrollIntoView({block:'start'})};"
new_scroll="function visibleSlide(){const vr=viewport.getBoundingClientRect(),center=vr.top+vr.height/2;let best=at,distance=Infinity;slides.forEach((s,i)=>{const r=s.parentElement.getBoundingClientRect(),d=center<r.top?r.top-center:center>r.bottom?center-r.bottom:0;if(d<distance){distance=d;best=i}});return best}let scrollFrame=false;viewport.addEventListener('scroll',()=>{if(!scrollMode||qaRunning||scrollFrame)return;scrollFrame=true;requestAnimationFrame(()=>{scrollFrame=false;if(scrollMode&&!qaRunning){const n=visibleSlide();if(n!==at)show(n,{auto:false,align:false})}})},{passive:true});$('scroll-toggle').onclick=()=>{const target=scrollMode?visibleSlide():at;scrollMode=!scrollMode;document.body.classList.toggle('scroll',scrollMode);$('scroll-toggle').setAttribute('aria-pressed',scrollMode);if(!scrollMode)viewport.scrollTop=0;fit();show(target,{auto:false,align:false});if(scrollMode)slides[target].parentElement.scrollIntoView({block:'start'})};"
assert old_scroll in ui;ui=ui.replace(old_scroll,new_scroll)
ui=ui.replace("btn.classList.add('playing');btn.setAttribute('aria-pressed','true')","btn.classList.add('playing');btn.setAttribute('aria-pressed','true');btn.dataset.playCount=String(Number(btn.dataset.playCount||0)+1)")
ui=ui.replace("function show(n,{auto=true,align=true}={})","window.addEventListener('unit2-play-cue',e=>{if(e.detail?.closest('.slide')?.classList.contains('active'))play(e.detail)});function show(n,{auto=true,align=true}={})")
ui+='\n'+(RUNTIME/'layout-editor.js').read_text()+'\n'+(RUNTIME/'fly-words.js').read_text()
namespace=re.sub(r'[^a-zA-Z0-9_-]','-',D.get('storage_id',B.name))
ui=ui.replace('mono-unit2-teacher-v5-notes-v1','mono-'+namespace+'-notes-v1').replace('mono-unit2-editable-layout-v5','mono-'+namespace+'-layout-v5')
extra=(RUNTIME/'lesson.css').read_text()
body=''.join(f' {k}="{H.escape(v,quote=True)}"' for k,v in bodyattrs.items())
out='<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+H.escape(D.get('title_vi','Bài giảng'))+' · Xem trước</title><style>'+css+'\n'+extra+'</style></head><body'+body+'><div class="viewport"><div class="frame">'+''.join(slides)+'</div></div>'+nav+'<script type="application/json" id="replacement-layout-defaults">'+((W/'layout.json').read_text() if (W/'layout.json').exists() else '{}')+'</script><script>'+ui+'</script></body></html>'
(W/'preview.html').write_text(out);(W/'preview-model.json').write_text(json.dumps(model,ensure_ascii=False,indent=2));(W/'preview-ui.js').write_text(ui)
(W/'practice-review.json').write_text(json.dumps({'fill':fills,'order':orders,'translate':translations,'picture':pics,'long':longs,'situations':situations},ensure_ascii=False,indent=2));print('Preview:',len(slides),'slides; no canonical export changed')
