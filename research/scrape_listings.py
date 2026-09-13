import re,json,subprocess,time
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36'
def get(u):
    r=subprocess.run(['curl','-s','-L','-m','25','-A',UA,u],capture_output=True,text=True); return r.stdout
out={}
tags=['hacking','cybersecurity','cyber-security','infosec','ctf','pentesting','osint','malware','reverse-engineering','security','hacker','ethical-hacking','bug-bounty','red-team','blue-team','flipper-zero','sdr','lockpicking','privacy','linux']
for t in tags:
    for base in [f'https://discords.com/servers/tag/{t}',f'https://discordservers.com/search/{t.replace("-","%20")}']:
        html=get(base)
        for m in re.finditer(r'href="(/servers?/[^"]+|https://discords\.com/servers/[^"]+|https://discordservers\.com/server/[^"]+)"',html):
            h=m.group(1)
            if '/tag/' in h or '/search' in h: continue
            u=h if h.startswith('http') else ('https://discords.com'+h if 'discords.com' in base else 'https://discordservers.com'+h)
            out.setdefault(u,set()).add(t)
        time.sleep(0.8)
print('server pages',len(out))
cands=[]
for i,(u,ts) in enumerate(list(out.items())[:400]):
    html=get(u)
    inv=sorted(set(re.findall(r'https?://(?:www\.)?discord(?:\.gg|\.com/invite)/[A-Za-z0-9_\-]+',html)))
    title=re.search(r'<title>([^<]*)</title>',html)
    if inv: cands.append({'name':(title.group(1) if title else u)[:80],'invite_url':inv[0],'source_url':u,'category_hint':'general','notes':'Listing site tags: '+', '.join(sorted(ts)),'confidence':'listed'})
    time.sleep(0.6)
json.dump(cands,open('research/listing_sites_candidates.json','w'),indent=1,ensure_ascii=False)
print('with invites',len(cands))
