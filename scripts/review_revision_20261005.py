from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
import json, httpx, sys, re
from bs4 import BeautifulSoup
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/2026-10-05_revision/sources'
OUT.mkdir(parents=True,exist_ok=True)
SOURCES={
 'rand_agi': 'https://www.rand.org/content/dam/rand/pubs/research_reports/RRA5100/RRA5163-1/RAND_RRA5163-1.pdf',
 'kyoto': 'https://www.whitehouse.gov/wp-content/uploads/2026/10/Kyoto-Vision-for-a-Golden-Age-of-Science.pdf',
 'ukri': 'https://www.ukri.org/opportunity/collaboration-for-a-sustainable-future-pilots-uk-seed-funding/',
 'ukri_coord': 'https://www.ukri.org/opportunity/collaboration-for-a-sustainable-future-coordinating-groups/',
 'nedo_ai4s': 'https://www.nedo.go.jp/news/press/AA5_101968.html',
 'dfg': 'https://www.dfg.de/de/aktuelles/neuigkeiten-themen/info-wissenschaft/2026/ifw-26-75',
 'rand_competition': 'https://www.rand.org/pubs/research_reports/RRA4254-2.html',
 'rand_policy': 'https://www.rand.org/pubs/perspectives/PEA5282-1.html',
 'bruegel': 'https://www.bruegel.org/first-glance/finance-its-future-europe-needs-bigger-more-targeted-budget',
 'anr': 'https://anr.fr/fr/actus/details/news/france-2030-le-cnrs-et-lird-lancent-un-programme-national-de-recherche-sur-lhabitabilite-de-la-t/',
 'dsit': 'https://www.gov.uk/government/publications/life-sciences-sector-plan-one-year-on',
 'itif_competition':'https://itif.org/publications/2026/10/01/china-challenge-is-not-japan-challenge-its-worse/'
}

def fetch(pair):
 key,url=pair
 try:
  with httpx.Client(follow_redirects=True,timeout=35,headers={'User-Agent':'Mozilla/5.0'}) as c:
   r=c.get(url);r.raise_for_status()
  if r.content.startswith(b'%PDF'):
   reader=PdfReader(BytesIO(r.content))
   text='\n\n'.join(f'=== PDF PAGE {i+1} ===\n'+(p.extract_text() or '') for i,p in enumerate(reader.pages))
   (OUT/(key+'.pdf')).write_bytes(r.content)
   meta={'pages':len(reader.pages)}
  else:
   soup=BeautifulSoup(r.content,'html.parser')
   for n in soup.select('script,style,nav,header,footer'):n.decompose()
   main=soup.select_one('main') or soup.select_one('article') or soup
   text=main.get_text('\n',strip=True)
   links=[{'text':a.get_text(' ',strip=True),'url':str(httpx.URL(str(r.url)).join(a['href']))} for a in main.select('a[href]') if '.pdf' in a['href']]
   meta={'pdf_links':links[:12]}
  (OUT/(key+'.txt')).write_text(text,encoding='utf-8')
  return {'key':key,'url':url,'status':r.status_code,'chars':len(text),**meta}
 except Exception as e:return {'key':key,'url':url,'error':type(e).__name__+': '+str(e)[:180]}

if __name__=='__main__':
 sys.stdout.reconfigure(encoding='utf-8')
 result=list(ThreadPoolExecutor(max_workers=4).map(fetch,SOURCES.items()))
 (OUT.parent/'refetch.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(result,ensure_ascii=False,indent=2))
