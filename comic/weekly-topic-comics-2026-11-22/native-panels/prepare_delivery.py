from pathlib import Path
import json, shutil, hashlib, html, datetime
import sys
R=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(R))
from thinktank_watch.brief import _inline_markdown_to_html
def markdown_html(s):
 return ''.join('<h3>'+_inline_markdown_to_html(p[4:])+'</h3>' if p.startswith('### ') else '<p>'+_inline_markdown_to_html(p)+'</p>' for p in s.split('\n\n'))
D='2026-11-22'
B=R/f'comic/weekly-topic-comics-{D}/native-panels'
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
items=load(R/f'docs/run_receipts/{D}_items.json')
order=['brookings-cti','ceps','fas','oecd-sti','eic','mext']
features=[next(x for x in items if x['institution_slug']==s and x['priority']=='P1') for s in order]
old=R/f'docs/run_receipts/{D}_image_manifest.json'
history=old.with_name(D+'_web_candidate_image_manifest.json')
if not history.exists():shutil.copyfile(old,history)
manifest=load(history)
layouts=load(B/'layout_manifest.json')
assert len(layouts)==12,'All 12 comic layouts must exist'
qa=load(B/'visual_review.json')
assert qa['status']=='passed' and qa['pages']==12 and qa['panels']==42
final=[]
for m in manifest:
 i=m['index'];edition=m['edition'];src=B/f'layouts/{i:02d}-{edition}.jpg'
 m['file']=f'comic/weekly-topic-comics-{D}/pages/{m["basename"]}.jpg' if edition=='pc' else f'briefs/weekly/2026/{D}_手机版/漫画/{i:02d}-手机漫画.jpg'
 dest=R/m['file']
 if dest.exists() and sha(dest)!=sha(src):
  quarantine=R/'reports/2026-11-22_unapproved_web_candidates'/f'{i:02d}-{edition}.jpg'
  quarantine.parent.mkdir(parents=True,exist_ok=True)
  if not quarantine.exists():shutil.copyfile(dest,quarantine)
 dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest)
 if edition=='pc':
  pc=R/f'briefs/weekly/2026/{D}_漫画版/漫画/{i:02d}-PC漫画-01.jpg';pc.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,pc)
 layout=next(x for x in layouts if x['topic']==i and x['edition']==edition)
 final.append({k:m[k] for k in ['index','edition','url','title','basename','file']}|{'generator':'ChatGPT session built-in image_gen','generation_method':'independent native single-scene illustrations, typeset with approved captions','actual_generation_records':[str((B/f'results/{ident}.json').relative_to(R)) for ident in layout['panels']],'sha256':sha(dest),'review':'passed_actual_visual_and_source_check','publication_ready':True,'native_panel_ids':layout['panels']})
write(old,final)

W=Path('C:/Users/WINDOWS/.codex/automations/automation-4/wechat')/(D+'-source')
W.mkdir(parents=True,exist_ok=True);(W/'images').mkdir(exist_ok=True)
e=lambda s:html.escape(s,quote=True)
editorial=load(R/f'briefs/weekly/2026/{D}_editorial.json')
briefs=load(R/f'briefs/weekly/2026/{D}_手机版/简讯编选.json')
guide='<section><p>2026年11月16—22日 · 26篇收录 · 6篇重点 · 16家机构</p>'
guide+='<p>'+e(editorial['lead'])+'</p><h2>本期发现</h2>'
for q in editorial['discoveries']:guide+='<p><strong>'+e(q['title'])+'</strong>。'+e(q['text'])+'</p>'
guide+='<h2>六篇重点解读</h2>'
for i,x in enumerate(features,1):guide+=f'<h3>{i:02d}｜{e(x["chinese_title"])}</h3><p>{e(x["institution_name"])} · {x["published_date"]}</p><p>{e(x["chinese_summary"])}</p>'
guide+='<h2>20则简讯</h2>'
for b in briefs:
 x=next(x for x in items if x['url']==b['url'])
 guide+=f'<h3>{b["index"]:02d}｜{e(b["title"])}</h3><p>{e(x["institution_name"])} · {x["published_date"]}</p>'
 guide+=''.join('<p>'+e(p)+'</p>' for p in b['paragraphs'])
guide+='</section>'
(W/'guide.html').write_text(guide,encoding='utf-8')
articles=[{'order':1,'slug':'guide','kind':'guide','title':'本周研究｜长期合作、融资评价与数据质量','summary':editorial['headline'],'content_html_file':'guide.html','content_source_url':'','source_url':'','source_urls':[x['url'] for x in items],'images':[],'cover_file':'images/01-pc.jpg'}]
spec={'guide':{'phrases':[q['title'] for q in editorial['discoveries']]}}
for i,x in enumerate(features,1):
 image=f'{i:02d}-pc.jpg';shutil.copyfile(B/f'layouts/{image}',W/'images'/image)
 slug=x['institution_slug'];body=markdown_html(x['highlights_markdown'])
 content=f'<section><p>{e(x["institution_name"])} · {x["published_date"]}</p><p><img src="images/{image}" alt="{e(x["chinese_title"])}漫画"></p>'+body+'</section>'
 (W/f'{slug}.html').write_text(content,encoding='utf-8')
 articles.append({'order':i+1,'slug':slug,'kind':'feature','title':x['chinese_title'],'summary':x['chinese_summary'],'content_html_file':f'{slug}.html','content_source_url':x['url'],'source_url':x['url'],'source_urls':[x['url']],'images':['images/'+image],'cover_file':'images/'+image})
 # Exact substantive sentence selected from approved prose; no inferred emphasis.
 first=x['highlights_markdown'].split('\n\n')[0]
 phrases={'brookings-cti':'调查并不等于定罪','ceps':'','fas':'','oecd-sti':'','eic':'182份有效回答','mext':'企业应明确资金与人员投入'}
 phrase=phrases[slug]
 spec[slug]={'phrases':[phrase] if phrase and phrase in x['highlights_markdown'] else [],'evidence_paragraphs':[first[:35]]}
write(W/'manifest.json',{'account_name':'这事有研究','business_date':D,'window':['2026-11-16',D],'articles':articles})
write(W/'editorial_emphasis.json',spec)
print(json.dumps({'images_installed':len(final),'wechat_source_articles':len(articles),'source_manifest':str(W/'manifest.json')},ensure_ascii=False))
