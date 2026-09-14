"""Group round-3 entries (first_seen 2026-09-14, researched, visible) into calibration files under research/calib3/."""
import json,os,collections
d=json.load(open('data/communities.json'))
os.makedirs('research/calib3',exist_ok=True)
rows=[c for c in d['communities'] if c.get('first_seen')=='2026-09-14' and c.get('recon_date') and not c.get('hidden') and c.get('invite_status')!='dead']
def compact(c): return {k:c.get(k) for k in ('id','name','platform','category','beginner_friendly','audience','tags','activities','members','online','region','country','subdivision','city','language','run_by','summary','rules_note','red_flags','discord_description','candidate_notes','confidence')}
groups=collections.defaultdict(list)
for c in rows:
    cat=c.get('category')
    g='regional' if cat in ('regional','adjacent') else 'ctf' if cat in ('ctf','learning','general') else 'affinity' if cat=='affinity' else 'misc'
    groups[g].append(compact(c))
files=[]
for g,items in groups.items():
    size=60 if g=='regional' else 45
    for i in range(0,len(items),size):
        name=f'{g}-{i//size}'; json.dump(items[i:i+size],open(f'research/calib3/{name}.json','w'),indent=1,ensure_ascii=False); files.append(name)
print(len(rows),'entries ->',files)
