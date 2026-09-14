"""Create recon batch files for every visible entry not yet researched. Prints: start count."""
import json,glob,sys
db=json.load(open('data/communities.json'))
done=set()
for f in glob.glob('research/recon_batches/batch_*.json'):
    for x in json.load(open(f)): done.add(x['id'])
cs=[c for c in db['communities'] if c.get('invite_status') in ('ok','unknown','unchecked') and not c.get('recon_date') and c['id'] not in done]
B=6; start=len(glob.glob('research/recon_batches/batch_*.json'))
compact=[{'id':c['id'],'name':c['name'],'platform':c.get('platform','discord'),'invite_url':c['invite_url'],'discord_description':c.get('discord_description'),'members':c.get('members'),'online':c.get('online'),'verified':c.get('verified'),'partnered':c.get('partnered'),'candidate_name':c.get('candidate_name'),'candidate_notes':(c.get('candidate_notes') or '')[:400],'category_hints':c.get('category_hints'),'website':c.get('website'),'sources':c.get('sources',[])[:4]} for c in cs]
n=0
for i in range(0,len(compact),B):
    json.dump(compact[i:i+B],open(f'research/recon_batches/batch_{start+n:03d}.json','w'),indent=1,ensure_ascii=False); n+=1
print(start,n,len(cs))
