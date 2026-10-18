"""Render an authored weekly reader edition as a phone-width PDF and HTML.

The input is the approved reader HTML. Collection, archive and delivery are
deliberately outside this renderer. Portrait comics and edited briefs are
provided as separate, reviewed inputs.
"""
from pathlib import Path
import argparse, base64, hashlib, html, json, re, sys
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from thinktank_watch.brief import write_pdf_from_html

CSS = '''
@page { size:92mm 164mm; margin:6mm 6mm 9mm; }
* { box-sizing:border-box; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
html { scroll-behavior:smooth; }
body { margin:0; color:#182b38; background:#fff; font:12.2pt/1.58 "Microsoft YaHei",sans-serif; }
main { margin:0 auto; }
a { color:#155a7e; text-decoration:none; overflow-wrap:anywhere; }
h1,h2,h3,h4,h5,h6 { line-height:1.38; margin:0 0 3mm; break-after:avoid; font-weight:700; }
h1 { font-size:21pt; } h2 { font-size:16pt; } h3,h4,h5,h6 { font-size:14pt; color:#155a7e; }
p { margin:0 0 3.2mm; orphans:2; widows:2; }
.kicker { font-size:10pt; letter-spacing:.06em; color:#b04d36; margin-bottom:3mm; }
.meta,.source { font-size:10pt; line-height:1.55; color:#52616c; }
.meta { break-after:avoid; margin-bottom:4mm; }
.opening { border-top:2mm solid #155a7e; padding-top:4mm; }
.opening .stats { margin:4mm 0; padding:3mm 0; border-top:.3mm solid #b8c7d2; border-bottom:.3mm solid #b8c7d2; font-size:11pt; }
.intro { margin:4mm 0; }
.navigation { break-before:page; }
.navigation a { display:block; padding:2.2mm 0; border-bottom:.2mm solid #dce4ea; }
.navigation h2 { margin-bottom:2mm; }
.comic-page { break-before:page; break-after:page; height:147mm; display:block; }
.comic-page img { width:100%; height:136mm; object-fit:contain; display:block; }
.comic-page .jump { display:block; text-align:center; font-size:10pt; margin-top:2mm; }
.feature { break-before:page; }
.brief { break-before:page; }
.brief h2 { font-size:16pt; }
.summary { border-left:1mm solid #b04d36; padding:0 0 0 3mm; margin-bottom:5mm; }
.article-source { font-size:10pt; margin-top:4mm; }
.back { font-size:10pt; margin-top:4mm; }
.brief-index { break-before:page; }
.brief-index a { display:block; padding:2mm 0; line-height:1.45; font-size:11.5pt; break-inside:avoid; border-bottom:.2mm solid #dce4ea; }
table { width:100%; border-collapse:collapse; font-size:10pt; }
th,td { padding:2mm; border:.2mm solid #cbd5dd; }
img { max-width:100%; }
@media screen {
  body { background:#edf1f4; font-size:18px; line-height:1.7; }
  main { background:white; max-width:520px; padding:24px 20px; }
  h1 { font-size:30px; } h2 { font-size:25px; } h3,h4,h5,h6 { font-size:22px; }
  .comic-page { height:auto; padding:28px 0; }
  .comic-page img { height:auto; width:100%; }
  .feature,.brief,.navigation,.brief-index { margin-top:32px; }
  .meta,.source,.kicker,.back,.article-source,.comic-page .jump { font-size:15px; }
  .brief-index a { font-size:17px; }
}
'''

def norm(t):
    return re.sub(r'\s+', '', t).replace('\u00ad', '')

def build(source, output, comic_dir, briefs_path, date, edition_path):
    import pymupdf as fitz
    output.mkdir(parents=True, exist_ok=True)
    soup = BeautifulSoup(source.read_text(encoding='utf-8'), 'html.parser')
    features = soup.select('.topic-primary')
    selections = soup.select('.report-highlights')
    original_briefs = soup.select('.short-brief')
    edited = json.loads(briefs_path.read_text(encoding='utf-8'))
    edition = json.loads(edition_path.read_text(encoding='utf-8'))
    assert edition['date'] == date, 'Edition date must match the requested issue'
    assert len(features) == len(selections) > 0
    assert len(original_briefs) == len(edited)
    assert [x['index'] for x in edited] == list(range(1,len(edited)+1))
    short_titles = edition['navigation_titles']
    assert len(short_titles) == len(features)
    feature_count,brief_count=len(features),len(edited)
    e = html.escape
    parts = [f'''<section class="opening" id="start"><p class="kicker">{e(date)} · 手机阅读版</p>
<h1>国际科技<br>智库周报</h1><div class="stats">{e(edition['window_label'])}<br>{feature_count}篇重点 · {brief_count}则简讯 · {edition['institution_count']}家机构</div>
<p class="intro">{e(edition['intro'])}</p><p>{e(edition['additional_intro'])}</p>
<p><a href="#contents">进入阅读导航 →</a></p><p><a href="#brief-index">直接读{brief_count}则简讯 →</a></p></section>''']
    parts.append('<nav class="navigation" id="contents"><p class="kicker">阅读导航</p><h2>重点解读</h2>')
    for i, t in enumerate(short_titles, 1):
        parts.append(f'<a href="#feature-{i:02d}">{i:02d}　{e(t)}</a>')
    parts.append(f'<a href="#brief-index">{brief_count}则简讯 →</a></nav>')
    entries = []
    expected = []
    for i, (feature, selection) in enumerate(zip(features, selections), 1):
        title = feature.h3.get_text(strip=True)
        url = feature.h3.a['href']
        meta = feature.select_one('.meta').get_text(strip=True)
        summary = feature.select_one('.judgment-box').get_text(' ', strip=True).removeprefix('摘要导读').strip()
        expected.extend([title,meta,summary])
        image_path = comic_dir / f'{i:02d}-手机漫画.jpg'
        b64 = base64.b64encode(image_path.read_bytes()).decode()
        parts.append(f'<section class="comic-page" id="comic-{i:02d}"><img alt="{e(short_titles[i-1])}竖版漫画" src="data:image/jpeg;base64,{b64}"><a class="jump" href="#feature-{i:02d}">向后阅读完整解读 →</a></section>')
        parts.append(f'<article class="feature" id="feature-{i:02d}"><p class="kicker">{i:02d} · 重点解读</p><h2>{e(title)}</h2><p class="meta">{e(meta)}</p><p class="summary">{e(summary)}</p>')
        body = BeautifulSoup(str(selection), 'html.parser').select_one('.report-highlights')
        for heading in body.find_all(['h4','h5','h6']):
            if heading.get_text(strip=True) == '精华选编': heading.decompose()
            else: heading.name = 'h3'
        for para in body.find_all('p'):
            expected.append(para.get_text())
            if para.get_text().startswith(('来源：','本篇为改编','本文据')):
                para['class'] = 'source'
        expected.extend(x.get_text() for x in body.select('h3,li,th,td'))
        parts.append(body.decode_contents())
        parts.append(f'<p class="article-source"><a href="{e(url)}">打开原文 ↗</a></p><p class="back"><a href="#contents">返回阅读导航</a> · <a href="#comic-{i:02d}">查看漫画</a></p></article>')
        entries.append([1, title, f'feature-{i:02d}'])
    parts.append(f'<nav class="brief-index" id="brief-index"><p class="kicker">{brief_count}则简讯</p><h2>按题选读</h2>')
    for item in edited:
        parts.append(f'<a href="#brief-{item["index"]:02d}">{item["index"]:02d}　{e(item["title"])}</a>')
    parts.append('</nav>')
    entries.append([1, '本期简讯', 'brief-index'])
    for original, item in zip(original_briefs, edited):
        assert original.h3.a['href'] == item['url']
        i=item['index']; title=item['title']; meta=original.select_one('.meta').get_text(strip=True)
        parts.append(f'<article class="brief" id="brief-{i:02d}"><p class="kicker">简讯 {i:02d} / {brief_count}</p><h2>{e(title)}</h2><p class="meta">{e(meta)}</p>')
        expected.extend([title,meta])
        for paragraph in item['paragraphs']:
            parts.append(f'<p>{e(paragraph)}</p>');expected.append(paragraph)
        parts.append(f'<p class="article-source"><a href="{e(item["url"])}">打开原文 ↗</a></p><p class="back"><a href="#brief-index">返回简讯目录</a> · <a href="#contents">重点解读</a></p></article>')
        entries.append([2, title, f'brief-{i:02d}'])
    doc_html = '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>国际科技智库周报｜手机阅读版</title><style>'+CSS+'</style></head><body><main>'+''.join(parts)+'</main></body></html>'
    hp=output/f'{date}_国际科技智库周报_手机版.html';hp.write_text(doc_html,encoding='utf-8')
    pdf=hp.with_suffix('.pdf')
    assert write_pdf_from_html(hp,pdf), 'Browser PDF rendering failed'
    doc=fitz.open(pdf)
    full=norm(''.join(pg.get_text() for pg in doc))
    missing=[p for p in expected if norm(p) not in full]
    assert not missing, f'Missing paragraphs: {missing}'
    # Resolve the actual rendered target page from full titles, skipping navigation.
    destinations={link['nameddest']:link['page'] for page in doc for link in page.get_links() if link.get('nameddest') and link.get('page',-1)>=0}
    assert 'contents' in destinations, 'Missing rendered contents destination'
    contents_page=destinations['contents']
    toc=[[1,'阅读导航',contents_page+1]]
    last_page=contents_page+1
    for level,title,ident in entries:
        if ident=='brief-index':
            found=[i for i,pg in enumerate(doc) if '按题选读' in pg.get_text()]
        else:
            found=[i for i,pg in enumerate(doc) if i>=last_page and norm(title) in norm(pg.get_text()) and ('重点解读' if level==1 else '简讯') in pg.get_text()]
            if level==2:
                found=[i for i in found if re.search(r'简讯\s*\d+\s*/\s*'+str(brief_count),doc[i].get_text())]
        assert found, f'Cannot locate rendered title: {title}'
        page=found[0]
        assert destinations.get(ident)==page, f'Destination mismatch: {ident}'
        toc.append([level,title,page+1]);last_page=page
    doc.set_toc(toc)
    # Explicit destinations work in more phone readers than Chromium's named links.
    for page in doc:
        for link in list(page.get_links()):
            if link.get('kind') == fitz.LINK_NAMED and link.get('page',-1) >= 0:
                target=link['page']; rect=link['from'];page.delete_link(link)
                page.insert_link({'kind':fitz.LINK_GOTO,'from':rect,'page':target,'to':fitz.Point(0,0)})
    # Footer links and page numbers are added only after actual pagination is known.
    for i,page in enumerate(doc):
        w,h=page.rect.width,page.rect.height
        page.insert_text((17,h-10),'目录',fontsize=8,fontname='china-s',color=(.3,.4,.45))
        page.insert_link({'kind':fitz.LINK_GOTO,'from':fitz.Rect(14,h-22,44,h-5),'page':contents_page,'to':fitz.Point(0,0)})
        page.insert_text((w-52,h-10),f'{i+1} / {len(doc)}',fontsize=8,color=(.3,.4,.45))
    page_count=len(doc)
    tmp=pdf.with_name(pdf.stem+'.checked.pdf');doc.save(tmp,garbage=4,deflate=True);doc.close();tmp.replace(pdf)
    check=fitz.open(pdf)
    report={'issue_date':date,'page_size_mm':[92,164],'body_font_pt':12.2,'pages':page_count,'features':feature_count,'briefs':brief_count,'comics':feature_count,'text_blocks_checked':len(expected),'missing_text_blocks':missing,'bookmarks':check.get_toc(),'internal_links':sum(x.get('kind')==fitz.LINK_GOTO for p in check for x in p.get_links()),'producer':check.metadata['producer'],'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'output_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [hp,pdf]},'visual_review':'pending'}
    (output/'手机排版核验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ['bookmarks','output_sha256']},ensure_ascii=False))

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--comics',type=Path,required=True)
    parser.add_argument('--briefs',type=Path,required=True)
    parser.add_argument('--date',required=True)
    parser.add_argument('--edition-json',type=Path,required=True)
    a=parser.parse_args();build(a.source,a.output_dir,a.comics,a.briefs,a.date,a.edition_json)
