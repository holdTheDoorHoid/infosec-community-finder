import json,re,subprocess,time
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36'
hits=json.load(open('research/discovery_hits.json'))
out=[]
for gid,h in hits.items():
    url=f"https://discord.com/servers/{h['slug']}"
    r=subprocess.run(['curl','-s','-m','25','-A',UA,url],capture_output=True,text=True)
    html=r.stdout
    codes=sorted(set(re.findall(r'discord(?:\.gg|\.com/invite)/([A-Za-z0-9\-_]+)',html)))
    codes=[c for c in codes if c.lower() not in ('discord','invite')]
    # name from title
    t=re.search(r'<title>([^<]*)</title>',html)
    name=(t.group(1) if t else '').replace(' | Discord','').replace('Discord Server','').strip()
    desc=re.search(r'<meta name="description" content="([^"]*)"',html)
    out.append({'guild_id':gid,'slug':h['slug'],'queries':h['queries'],'name':name,'invite_codes':codes,'meta_desc':(desc.group(1) if desc else '')[:300],'source':'discord-discovery','source_url':url})
    time.sleep(0.5)
json.dump(out,open('research/discovery_resolved.json','w'),indent=1,ensure_ascii=False)
print(len(out),'pages;',sum(1 for o in out if o['invite_codes']),'with invite codes')
