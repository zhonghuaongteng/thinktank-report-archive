"""Typeset native-generated illustrations as comic pages; originals stay intact."""
from pathlib import Path
import json,hashlib,shutil,argparse,unicodedata,math,re
import pymupdf as fitz
from PIL import Image,ImageOps,ImageDraw
root=Path(__file__).resolve().parents[3];base=root/'comic/weekly-topic-comics-2026-11-22/native-panels'
jobs=json.loads((base/'jobs.json').read_text(encoding='utf-8'))
byid={x['id']:x for x in jobs}
for p in (base/'results').glob('*.json'):
    result=json.loads(p.read_text(encoding='utf-8'));byid[result['id']].update(result)
jobs=list(byid.values());images=base/'images';images.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for j in jobs:
    if j.get('status')!='generated':continue
    source=Path(j['source']);dest=images/(j['id']+'.jpg')
    if not dest.exists() or j.get('source_sha256')!=sha(source):
        with Image.open(source) as im:im.convert('RGB').save(dest,quality=91,subsampling=0)
    j.update(file=str(dest.relative_to(root)),source_sha256=sha(source),sha256=sha(dest))
(base/'jobs.json').write_text(json.dumps(jobs,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
titles={1:'科研合作，争论在哪里',2:'产业政策，工具怎样选',3:'跨部门服务，怎样长期承接',4:'数据进入AI之后',5:'企业怎样评价EIC基金',6:'大学与企业的长期承诺'}
sources={1:'Brookings · 2026-11-17',2:'CEPS · 2026-11-19',3:'FAS · 2026-11-18',4:'OECD · 2026-11-18',5:'EIC · 2026-11-17',6:'MEXT · 2026-11-16'}
fontpath='C:/Windows/Fonts/msyh.ttc';font=fitz.Font(fontfile=fontpath)
def wrap(s,size,width):
    rows=[]
    for paragraph in s.split('\n'):
        weight=lambda c:size*(1.0 if unicodedata.east_asian_width(c) in ('W','F') else .6)
        total=sum(weight(c) for c in paragraph)
        lines=max(1,math.ceil(total/width))
        balanced=min(width,total/lines+size*.5)
        tokens=re.findall(r'[A-Za-z0-9]+(?:\.[0-9]+)*%?|.',paragraph)
        while True:
            row='';units=0;candidate=[]
            for char in tokens:
                advance=sum(weight(c) for c in char)
                if row and units+advance>balanced and char not in '，。；：！？、）':candidate.append(row);row='';units=0
                row+=char;units+=advance
            if row:candidate.append(row)
            if len(candidate)<=lines or balanced>=width:break
            balanced=min(width,balanced+size*.25)
        rows.extend(candidate)
    return rows

def text(page,rect,s,size,color=(.08,.2,.27)):
    rows=wrap(s,size,rect.width)
    assert len(rows)*size*1.32<=rect.height,(s,rows,rect.height)
    for i,row in enumerate(rows):
        page.insert_text(fitz.Point(rect.x0,rect.y0+size*1.10+i*size*1.32),row,fontname='yahei',fontsize=size,color=color)
complete=[]
out=base/'layouts';out.mkdir(exist_ok=True)
for topic in range(1,7):
 for edition,count in [('pc',4),('mobile',3)]:
    panel=[x for x in jobs if x['topic']==topic and x['edition']==edition]
    if len(panel)!=count or not all(x.get('file') for x in panel):continue
    width,height=(1600,1430) if edition=='pc' else (900,1820)
    doc=fitz.open();p=doc.new_page(width=width,height=height);p.insert_font(fontname='yahei',fontfile=fontpath)
    p.draw_rect(p.rect,fill=(.98,.97,.93),color=None)
    p.draw_rect(fitz.Rect(0,0,width,12),fill=(.08,.37,.4),color=None)
    text(p,fitz.Rect(42,29,width-35,119),titles[topic],52 if edition=='pc' else 47)
    for n,j in enumerate(panel):
        if edition=='pc':
            x=42+(n%2)*780;y=120+(n//2)*625;w=738;ih=492;size=32;ch=112
        else:
            x=38;y=126+n*530;w=824;ih=360;size=43;ch=160
        p.draw_rect(fitz.Rect(x,y,x+w,y+ih+ch),color=(.7,.77,.74),fill=(1,1,.99),width=1.5)
        p.insert_image(fitz.Rect(x+2,y+2,x+w-2,y+ih-2),filename=str(root/j['file']),keep_proportion=True)
        text(p,fitz.Rect(x+16,y+ih+9,x+w-16,y+ih+ch-4),j['caption'],size)
    text(p,fitz.Rect(42,height-64,width-30,height-8),sources[topic],28 if edition=='pc' else 30,color=(.21,.4,.43))
    doc.subset_fonts()
    pdf=out/f'{topic:02d}-{edition}.pdf';doc.save(pdf,garbage=4,deflate=True)
    jpg=out/f'{topic:02d}-{edition}.jpg';p.get_pixmap(matrix=fitz.Matrix(1,1)).save(jpg,jpg_quality=91)
    expected=[j['caption'] for j in panel]
    norm=lambda s:''.join(s.split())
    content=norm(p.get_text());assert all(norm(s) in content for s in expected)
    complete.append({'topic':topic,'edition':edition,'jpg':str(jpg.relative_to(root)),'pdf':str(pdf.relative_to(root)),'sha256':sha(jpg),'panels':[j['id'] for j in panel],'visual_review':'pending','all_caption_text_present':True})
    doc.close()
(base/'layout_manifest.json').write_text(json.dumps(complete,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Small review sheets are inspection aids, never reader deliverables.
review=root/'reports/2026-11-22_native_review';review.mkdir(exist_ok=True)
for topic in range(1,7):
    ready=[j for j in jobs if j['topic']==topic and j.get('file')]
    if not ready:continue
    sheet=Image.new('RGB',(1200,((len(ready)+1)//2)*430),'white');draw=ImageDraw.Draw(sheet)
    for k,j in enumerate(ready):
        im=Image.open(root/j['file']);im.thumbnail((590,394));x=(k%2)*600;y=(k//2)*430
        sheet.paste(im,(x,y+27));draw.text((x+10,y+5),j['id'],fill='black')
    sheet.save(review/f'topic-{topic:02d}.jpg',quality=90)
print(json.dumps({'generated':sum('file' in j for j in jobs),'total':len(jobs),'complete_comic_pages':len(complete),'review_dir':str(review)},ensure_ascii=False))
