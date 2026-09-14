"""Find university security clubs / CTF teams on GitHub via repo search, then pull community links from org profiles and READMEs."""
import json,subprocess,re,base64,time,sys
QUERIES=['"cybersecurity club"','"cyber security club"','"cyber club" university','"ctf team" university','"ctf club"','"hacking club"','"security club" university','"cybersecurity society"','"cyber security society"','"cybersec society"','"infosec club"','"cyber defense club"','"cybersecurity association" student','"computer security club"','"ethical hacking club"','"cyber security student"','"ccdc team"','"cyber student"','"security society" university','"hack club" university','"ctf" "student club"','"cyber security association" university','"cybersecurity club" college','"ctf team" college','"hacking society"','"infosec society"','"cyber society"','"ctf" "university" "discord"','"student cyber"','"cyber security" "student society"']
RE=re.compile(r'https?://(?:www\.)?(?:discord(?:\.gg|\.com/invite|app\.com/invite)/[A-Za-z0-9_\-]+|[A-Za-z0-9\-]+\.slack\.com/[^\s\)"\'<>]*|join\.slack\.com/[^\s\)"\'<>]*|matrix\.to/#/[^\s\)"\'<>]+)')
repos={}
for q in QUERIES:
    for match in ('name,description','readme'):
        r=subprocess.run(['gh','search','repos',q,'--match',match,'--limit','100','--json','fullName,description,url,owner'],capture_output=True,text=True)
        try: items=json.loads(r.stdout)
        except Exception: items=[]
        for it in items: repos.setdefault(it['fullName'],{**it,'queries':[]})['queries'].append(q)
        time.sleep(2.5)
    print(q,len(repos),file=sys.stderr,flush=True)
owners={}
for name,it in repos.items():
    owners.setdefault(it['owner']['login'],{'login':it['owner']['login'],'type':it['owner'].get('type'),'repos':[]})['repos'].append({'fullName':name,'description':(it.get('description') or '')[:200],'url':it['url']})
print('repos',len(repos),'owners',len(owners),file=sys.stderr,flush=True)
def readme(path):
    r=subprocess.run(['gh','api',f'repos/{path}/readme','--jq','.content'],capture_output=True,text=True)
    if r.returncode!=0: return ''
    try: return base64.b64decode(r.stdout.strip()).decode('utf-8','replace')
    except Exception: return ''
import concurrent.futures
json.dump(list(owners.values()),open('research/github_campus_owners.json','w'))
def scan(o):
    login=o['login']
    r=subprocess.run(['gh','api',f'users/{login}','--jq','{blog:.blog,location:.location,type:.type,name:.name,bio:.bio,description:.description,html_url:.html_url}'],capture_output=True,text=True)
    try: prof=json.loads(r.stdout)
    except Exception: prof={}
    texts=[readme(f'{login}/.github')]
    if prof.get('type')=='User': texts.append(readme(f'{login}/{login}'))
    for rp in o['repos'][:2]: texts.append(readme(rp['fullName']))
    links=sorted(set(l for t in texts for l in RE.findall(t)))
    return {**o,**prof,'links':links}
with concurrent.futures.ThreadPoolExecutor(6) as ex: out=list(ex.map(scan,list(owners.values())))
json.dump(out,open('research/github_campus.json','w'),indent=1,ensure_ascii=False)
print('done owners',len(out),'with links',sum(1 for x in out if x['links']),file=sys.stderr)
