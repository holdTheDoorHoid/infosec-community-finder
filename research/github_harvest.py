"""Harvest Discord invite links from READMEs of popular security repos (GitHub API, authenticated via gh)."""
import json,subprocess,re,base64,time,sys
TOPICS=['security','pentesting','hacking','cybersecurity','infosec','red-team','redteam','blue-team','blueteam','dfir','osint','reverse-engineering','ctf','malware-analysis','hardware-hacking','sdr','flipper-zero','threat-intelligence','bug-bounty','exploitation','forensics','privacy','wifi-hacking','rfid','esp32-hacking','pwnagotchi','security-tools','ethical-hacking','penetration-testing','malware','threat-hunting','detection','osint-tool','lockpicking','badusb','evil-twin','ctf-tools','wireless-security','embedded-security','firmware-analysis']
repos={}
for t in TOPICS:
    r=subprocess.run(['gh','search','repos','--topic',t,'--sort','stars','--limit','120','--json','fullName,stargazersCount,description,url'],capture_output=True,text=True)
    try: items=json.loads(r.stdout)
    except Exception: items=[]
    for it in items:
        repos.setdefault(it['fullName'],{**it,'topics':[]})['topics'].append(t)
    time.sleep(1.2)
print('repos',len(repos),file=sys.stderr)
out=[]
RE=re.compile(r'https?://(?:www\.)?discord(?:\.gg|\.com/invite|app\.com/invite)/[A-Za-z0-9_\-]+')
for i,(name,it) in enumerate(sorted(repos.items(),key=lambda kv:-kv[1]['stargazersCount'])):
    r=subprocess.run(['gh','api',f'repos/{name}/readme','--jq','.content'],capture_output=True,text=True)
    if r.returncode!=0: continue
    try: txt=base64.b64decode(r.stdout.strip()).decode('utf-8','replace')
    except Exception: continue
    links=sorted(set(RE.findall(txt)))
    if links:
        out.append({'name':name.split('/')[-1],'repo':name,'url':it['url'],'stars':it['stargazersCount'],'description':(it.get('description') or '')[:200],'topics':it['topics'],'invite_url':links[0],'all_invites':links,'source_url':it['url'],'category_hint':'tool','notes':f"GitHub README of {name} ({it['stargazersCount']} stars): {(it.get('description') or '')[:150]}",'confidence':'official'})
    if i%100==0: print(i,'scanned,',len(out),'with invites',file=sys.stderr)
    time.sleep(0.25)
json.dump(out,open('research/github_candidates.json','w'),indent=1,ensure_ascii=False)
print('done: repos',len(repos),'with invites',len(out),file=sys.stderr)
