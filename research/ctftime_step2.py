"""Step 2: for academic-looking CTFtime teams, fetch the team page for its website/social links; write crawl input."""
import json,re,time,sys,urllib.request,concurrent.futures,html as H
UA='Mozilla/5.0 (X11; Linux x86_64) infosec-community-finder/1.0 (+https://github.com/holdTheDoorHoid/infosec-community-finder)'
teams=json.load(open('research/ctftime_teams.json'))
KW=re.compile(r'univ|universit|college|institute|polytech|politec|school|campus|student|hochschule|\bIIT\b|\bNIT\b|\bTU\b|\bETH\b|\bEPFL\b|\bMIT\b|\bUC[A-Z]{1,3}\b|\bKTH\b|\bNTU\b|\bNUS\b|\bKAIST\b|\bUNSW\b|\bUQ\b|\bUW\b|academy|faculty|\bctf club|sec ?soc|cyber ?soc|hacking club|security club',re.I)
sel=[t for t in teams if t.get('academic') or KW.search(t['name']+' '+' '.join(t.get('aliases') or []))]
print('teams',len(teams),'selected academic/keyword',len(sel),file=sys.stderr)
def get(u):
    try:
        req=urllib.request.Request(u,headers={'User-Agent':UA})
        return urllib.request.urlopen(req,timeout=30).read().decode('utf-8','replace')
    except Exception: return ''
def page(t):
    time.sleep(0.5)
    h=get(f"https://ctftime.org/team/{t['id']}")
    if not h: t['page_error']=True; return t
    links=[l for l in re.findall(r'href="(https?://[^"]+)"',h) if 'ctftime.org' not in l]
    t['ext_links']=sorted(set(links))[:15]
    m=re.search(r'Academic team',h); t['academic_badge']=bool(m)
    site=[l for l in links if not re.search(r'twitter\.com|x\.com|facebook|instagram|github\.com|discord|t\.me|youtube|linkedin',l)]
    t['website']=site[0] if site else None
    gh=[l for l in links if 'github.com' in l]; t['github']=gh[0] if gh else None
    dc=[l for l in links if re.search(r'discord\.(gg|com/invite)',l)]; t['discord_on_page']=dc[0] if dc else None
    return t
with concurrent.futures.ThreadPoolExecutor(2) as ex: out=list(ex.map(page,sel))
json.dump(out,open('research/ctftime_academic.json','w'),indent=1,ensure_ascii=False)
print('done',len(out),'with website',sum(1 for t in out if t.get('website')),'discord on page',sum(1 for t in out if t.get('discord_on_page')),'errors',sum(1 for t in out if t.get('page_error')),file=sys.stderr)
