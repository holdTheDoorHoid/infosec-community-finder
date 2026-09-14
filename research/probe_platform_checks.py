import json,sys,time
sys.path.insert(0,'scripts')
from discordapi import check_join_url, mastodon_stats
db=json.load(open('data/communities.json'))
for c in db['communities']:
    if c.get('platform','discord')=='discord': continue
    t=time.time(); r=check_join_url(c['invite_url']); dt=time.time()-t
    extra=''
    if c['platform']=='mastodon':
        t2=time.time(); m=mastodon_stats(c['invite_url']); extra=f" mastodon {time.time()-t2:.1f}s members={m.get('members')}"
    print(f"{dt:5.1f}s {r['status']:9} {c['platform']:10} {c['invite_url'][:70]}{extra}", flush=True)
