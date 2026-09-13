import re,subprocess,json,time
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36'
def get(u): return subprocess.run(['curl','-s','-L','-m','25','-A',UA,u],capture_output=True,text=True).stdout
groups={}
for page in range(1,40):
    u='https://forum.defcon.org/social-groups' + (f'/page{page}' if page>1 else '')
    html=get(u)
    pairs=re.findall(r'href="(https://forum\.defcon\.org/node/\d+)"[^>]*>\s*(DC[0-9A-Za-z]{2,6}[^<]{0,80})<',html)
    new=0
    for href,name in pairs:
        name=re.sub(r'\s+',' ',name).strip()
        if href not in groups: groups[href]=name; new+=1
    if new==0: break
    time.sleep(0.6)
print('groups',len(groups))
out=[]
for i,(href,name) in enumerate(groups.items()):
    html=get(href)
    inv=sorted(set(re.findall(r'https?://(?:www\.)?discord(?:\.gg|\.com/invite)/[A-Za-z0-9_\-]+',html)))
    links=sorted(set(l for l in re.findall(r'href="(https?://[^"]+)"',html) if 'defcon.org' not in l and not any(x in l for x in ('vbulletin','gravatar','twitter.com/defcon','facebook.com/defcon','cloudflare'))))
    desc=re.search(r'<meta name="description" content="([^"]*)"',html)
    out.append({'name':name,'forum_url':href,'invite_url':inv[0] if inv else None,'all_invites':inv,'links':links[:12],'desc':(desc.group(1) if desc else '')[:300]})
    time.sleep(0.5)
json.dump(out,open('research/dcg_list.json','w'),indent=1,ensure_ascii=False)
print('done; with discord',sum(1 for o in out if o['invite_url']),'with any external link',sum(1 for o in out if o['links']))
