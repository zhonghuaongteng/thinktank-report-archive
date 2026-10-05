from pathlib import Path
import os, sys, json, dataclasses, shutil, re, base64, hashlib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from PIL import Image,ImageOps,ImageDraw
from bs4 import BeautifulSoup
import pymupdf as fitz
from thinktank_watch.models import ArticleCandidate
from thinktank_watch.brief import write_weekly_brief, write_pdf_from_html, inspect_weekly_comic_report, weekly_thin_core_items

DATE='2026-10-05'
BASE=ROOT/'briefs/revisions/2026-10-05-expanded'
GEN=Path(r'C:\Users\WINDOWS\.codex\generated_images\01a10adb-e2e3-77f0-9529-b7a15d3b3406')
PAGES=BASE/'comic/weekly-topic-comics-2026-10-05/pages'
PAGES.mkdir(parents=True,exist_ok=True)
sources=[
 (ROOT/'comic/weekly-topic-comics-2026-10-05/pages/02-topic-kyoto-vision-for-a-golden-age-of-science.jpg','01-topic-kyoto-vision-for-a-golden-age-of-science.jpg'),
 (GEN/'exec-ce24f25b-622d-4afd-8ed4-58931ed60e69.png','02-topic-collaboration-for-a-sustainable-future-pilots-and-uk-seed-fundin.jpg'),
 (ROOT/'comic/weekly-topic-comics-2026-10-05/pages/04-topic-to-finance-its-future-europe-needs-a-bigger-more-targeted-budget.jpg','03-topic-to-finance-its-future-europe-needs-a-bigger-more-targeted-budget.jpg'),
 (GEN/'exec-d6e6bae5-f771-4390-9d5a-f05497be365a.png','04-topic-the-china-challenge-is-not-the-japan-challenge-it-s-worse.jpg'),
 (GEN/'exec-a66b2040-388f-4622-9d1a-f5c33ef7ea9e.png','05-topic-can-agi-rivals-hold-back-verification-domestic-oversight-and-the.jpg'),
 (ROOT/'comic/weekly-topic-comics-2026-10-05/pages/09-topic-amaterus-ai-ai.jpg','06-topic-amaterus-ai-ai.jpg')]
for source,dest in sources:
    if source.suffix=='.jpg':shutil.copy2(source,PAGES/dest)
    else:
        with Image.open(source) as im:im.convert('RGB').save(PAGES/dest,quality=95)
data=json.loads((BASE/'items.json').read_text(encoding='utf-8'))
fields={f.name for f in dataclasses.fields(ArticleCandidate)}
items=[ArticleCandidate(**{k:v for k,v in x.items() if k in fields}) for x in data['items']]
ed=json.loads((BASE/f'{DATE}_editorial.json').read_text(encoding='utf-8'))
br=BASE/'briefs'
dest=br/'weekly/2026'
dest.mkdir(parents=True,exist_ok=True)
shutil.copy2(BASE/f'{DATE}_editorial.json',dest/f'{DATE}_editorial.json')
os.chdir(BASE)
assert not weekly_thin_core_items(items)
md,html,pdf=write_weekly_brief(br,DATE,items,editorial=ed)
s=html.read_text(encoding='utf-8')
def embed(m):
    q=(html.parent/m[1]).resolve()
    assert q.is_relative_to(BASE) and q.exists()
    return 'src="data:image/jpeg;base64,'+base64.b64encode(q.read_bytes()).decode()+'"'
s,n=re.subn(r'src="([^"]+\.jpg)"',embed,s)
assert n==6
s=s.replace('<h1>国际科技智库周报</h1>','<h1>国际科技智库周报</h1><p class="revision-label">2026年10月5日 · 扩充修订版</p>')
s=s.replace('</style>','''
.revision-label { color:#8b2f2a; font-weight:700; font-size:10pt; }
.short-briefs { padding-top:6mm; }
@media print { .short-briefs {break-inside:auto;page-break-inside:auto;break-before:page;} .short-brief {break-inside:avoid;page-break-inside:avoid;} }
</style>''')
html.write_text(s,encoding='utf-8')
md.write_text(md.read_text(encoding='utf-8').replace('# 国际科技智库周报（2026-10-05）','# 国际科技智库周报（2026-10-05）扩充修订版',1),encoding='utf-8')
assert write_pdf_from_html(html,pdf)
d=fitz.open(pdf)
screen=ROOT/'reports/2026-10-05_expanded/render'
screen.mkdir(parents=True,exist_ok=True)
for i,p in enumerate(d):p.get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save(screen/f'{i+1:02}.png')
soup=BeautifulSoup(s,'html.parser')
norm=lambda x:re.sub(r'\s+','',x)
alltext=norm(''.join(p.get_text() for p in d))
blocks=[el.get_text() for el in soup.select('.report-highlights p, .report-highlights h4, .report-highlights h5, .short-briefs p, .judgment-box p')]
missing=[t[:80] for t in blocks if norm(t) not in alltext]
ids={e['id'] for e in soup.select('[id]')}
broken=[a['href'] for a in soup.select('a[href^="#"]') if a['href'][1:] not in ids]
excluded=['铜的需求增加','铜加工','转岗','智能体试验','Workforce in motion','Formula for Agentic AI']
present=[t for t in excluded if t in soup.get_text() or t in md.read_text(encoding='utf-8')]
assert all(norm(i.chinese_title) in alltext for i in items)
check=inspect_weekly_comic_report(DATE,items,br,BASE/'comic')
result={'revision':'2026-10-05','pages':len(d),'page_characters':[len(p.get_text()) for p in d],
 'checked_text_blocks':len(blocks),'missing_paragraphs':missing,'broken_anchors':broken,'excluded_topic_hits':present,
 'embedded_images':n,'pdf_producer':d.metadata.get('producer'),'comic_check':check,
 'artifacts':{q.name:{'bytes':q.stat().st_size,'sha256':hashlib.sha256(q.read_bytes()).hexdigest()} for q in [md,html,pdf]}}
assert not missing and not broken and not present and 'Skia' in result['pdf_producer']
assert not check['missing_files'] and not check['blocked_hits'] and not check['editorial_failures']
assert check['priority_count']==check['comic_count']==check['prompt_count']==check['html_image_nodes']==check['md_image_refs']==6
assert check['pdf_image_count']>=6
(ROOT/'docs/run_receipts/2026-10-05_expanded_artifact_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
thumbs=[]
for i in range(len(d)):
    im=Image.open(screen/f'{i+1:02}.png').convert('RGB');im.thumbnail((400,575))
    tile=Image.new('RGB',(420,610),'#dfe4e9');tile.paste(im,((420-im.width)//2,20));ImageDraw.Draw(tile).text((15,590),str(i+1),fill='black');thumbs.append(tile)
sheet=Image.new('RGB',(420*3,610*((len(thumbs)+2)//3)),'#dfe4e9')
for i,im in enumerate(thumbs):sheet.paste(im,((i%3)*420,(i//3)*610))
sheet.save(screen/'contact.png')
print(json.dumps(result,ensure_ascii=True))
