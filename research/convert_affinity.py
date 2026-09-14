"""Convert affinity-sweep workflow output (task .output file) into importer candidates."""
import json,sys
tid=sys.argv[1]
d=json.load(open(f'/tmp/claude-1000/-home-hoid-Desktop/745c70e6-c1cb-44ec-873c-7451b28a08ea/tasks/{tid}.output'))
r=(d.get('result') or d)
cands=r.get('candidates',[]); nopub=r.get('no_public_community',[]); missing=r.get('missing',[])
out=[]; dropped=[]
seen=set()
for c in cands:
    u=(c.get('join_url') or '').strip()
    if not u.startswith('http') and not u.startswith('irc'): dropped.append({**c,'why':'no url'}); continue
    if c.get('confidence')=='guess' and c.get('platform')!='discord': dropped.append({**c,'why':'guess on non-discord'}); continue
    k=u.lower().rstrip('/')
    if k in seen: continue
    seen.add(k)
    out.append({'name':c['name'],'invite_url':u,'platform':c.get('platform') if c.get('platform')!='other' else None,'source_url':c.get('source_url'),
      'category_hint':'affinity','country':c.get('country'),'language':c.get('language'),
      'notes':f"Affinity: {', '.join(c.get('affinity',[]))}; org: {c.get('org')}; join: {c.get('how_to_join')}; scope: {c.get('scope')}. {c.get('notes','')}",
      'confidence':c.get('confidence'),'lens':c.get('lens')})
json.dump(out,open('research/affinity_candidates.json','w'),indent=1,ensure_ascii=False)
json.dump({'no_public_community':nopub,'missing':missing,'dropped':dropped},open('research/affinity_sweep_extra.json','w'),indent=1,ensure_ascii=False)
from collections import Counter
print('candidates',len(out),'dropped',len(dropped),'no-public',len(nopub),'critic-missing',len(missing))
print(Counter(c['platform'] for c in out).most_common()); print(Counter(c['lens'] for c in out).most_common())
