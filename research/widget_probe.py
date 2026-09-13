import json,sys
sys.path.insert(0,'scripts')
from discordapi import widget_invite
src=sys.argv[1]; cands=json.load(open(src))
hit=0
for c in cands:
    if c.get('invite_url') or not c.get('guild_id'): continue
    w=widget_invite(c['guild_id'])
    if w.get('instant_invite'):
        c['invite_url']=w['instant_invite']; c['confidence']='official'; c['notes']+=' | invite via widget'; hit+=1
    c['widget']=w.get('status')
json.dump(cands,open(src,'w'),indent=1,ensure_ascii=False)
print(src,'widget invites recovered:',hit,'of',len(cands))
