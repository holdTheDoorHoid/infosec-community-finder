import json,re,subprocess,time
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36'
rows=json.load(open('research/dcg_sites.json')); out=[]
for r in rows:
    u=r['website']
    html=subprocess.run(['curl','-s','-L','-m','20','-A',UA,u],capture_output=True,text=True).stdout
    inv=sorted(set(re.findall(r'https?://(?:www\.)?discord(?:\.gg|\.com/invite)/[A-Za-z0-9_\-]+',html)))
    if not inv:
        # try common subpages
        for sub in ('/discord','/community','/join','/contact','/about'):
            h2=subprocess.run(['curl','-s','-L','-m','15','-A',UA,u.rstrip('/')+sub],capture_output=True,text=True).stdout
            inv=sorted(set(re.findall(r'https?://(?:www\.)?discord(?:\.gg|\.com/invite)/[A-Za-z0-9_\-]+',h2)))
            if inv: break
    slack=re.findall(r'https?://[^"\s]*slack\.com[^"\s]*',html)
    if inv: out.append({'name':r['name'],'invite_url':inv[0],'website':u,'source_url':u,'category_hint':'regional','notes':f"DEF CON Group, {r['location']}; invite found on the group's own site",'confidence':'official'})
    elif slack: out.append({'name':r['name'],'invite_url':slack[0],'platform':'slack','website':u,'source_url':u,'category_hint':'regional','notes':f"DEF CON Group, {r['location']}; Slack link on the group's site",'confidence':'official'})
    time.sleep(0.4)
json.dump(out,open('research/dcg_site_candidates.json','w'),indent=1,ensure_ascii=False)
print('done; sites',len(rows),'with chat links',len(out))
