"""Harvest hackerspaces from wiki.hackerspaces.org: list page -> each space's wiki template fields.
Output: research/hackerspaces_wiki.json (all rows incl. US), plus counts."""
import re, json, html, time, sys, urllib.request, urllib.parse, concurrent.futures
UA='infosec-community-finder/1.0 (+https://github.com/holdTheDoorHoid/infosec-community-finder)'
SCR='/tmp/claude-1000/-home-hoid-Desktop/745c70e6-c1cb-44ec-873c-7451b28a08ea/scratchpad'
h=open(f'{SCR}/hs_list.html').read()
rows=[]
for r in re.findall(r'<tr[^>]*>(.*?)</tr>',h,flags=re.S):
    cells=re.findall(r'<td class="([^"]*)"[^>]*>(.*?)</td>',r,flags=re.S)
    if not cells: continue
    rec={}
    for cls,body in cells:
        key=cls.split()[0]
        m=re.search(r'title="([^"]*)"',body)
        href=re.search(r'href="([^"]*)"',body)
        text=html.unescape(re.sub(r'<[^>]+>','',body)).strip()
        if key=='hackerspace':
            rec['name']=html.unescape(m.group(1)) if m else text
            rec['page']=urllib.parse.unquote(href.group(1).lstrip('/')) if href else None
        elif key=='Website': rec['website']=href.group(1) if href else text
        else: rec[key.lower()]=re.sub(r' \(page does not exist\)','',html.unescape(m.group(1))) if m else text
    rows.append(rec)
print(len(rows),'rows parsed',file=sys.stderr)
def wikitext(title):
    q=urllib.parse.urlencode({'action':'parse','page':title,'prop':'wikitext','format':'json'})
    req=urllib.request.Request('https://wiki.hackerspaces.org/w/api.php?'+q,headers={'User-Agent':UA})
    try:
        j=json.loads(urllib.request.urlopen(req,timeout=30).read().decode('utf-8','replace'))
        return j.get('parse',{}).get('wikitext',{}).get('*','')
    except Exception as e:
        return 'ERROR '+str(e)[:100]
def enrich(rec):
    time.sleep(0.25)
    wt=wikitext(rec.get('page') or rec['name'])
    if wt.startswith('ERROR'): rec['wiki_error']=wt; return rec
    m=re.search(r'\{\{Hackerspace(.*?)\n\}\}',wt,flags=re.S)
    fields={}
    if m:
        for line in m.group(1).split('\n|'):
            if '=' in line:
                k,v=line.split('=',1); fields[k.strip().lstrip('|')]=v.strip()
    rec['fields']=fields
    body=wt[m.end():] if m else wt
    rec['links']=sorted(set(re.findall(r'https?://[^\s\]\|<>"]+',body)))[:40]
    rec['snippet']=re.sub(r'\s+',' ',re.sub(r'\[\[File:[^\]]*\]\]|\{\{[^}]*\}\}','',body))[:400]
    return rec
with concurrent.futures.ThreadPoolExecutor(4) as ex:
    out=list(ex.map(enrich,rows))
json.dump(out,open('research/hackerspaces_wiki.json','w'),indent=1,ensure_ascii=False)
from collections import Counter
print('done',len(out),'errors',sum(1 for o in out if o.get('wiki_error')))
print('status',Counter((o.get('fields') or {}).get('status','?').lower()[:12] for o in out).most_common(8))
print('countries',Counter(o.get('country') for o in out).most_common(25))
keys=Counter(k for o in out for k in (o.get('fields') or {}))
print('fields',keys.most_common(40))
