"""Given a JSON list of {name, website, ...}, fetch each site (+ common subpages) and extract chat-community links.
Usage: python3 research/crawl_sites.py in.json out.json"""
import json,re,sys,time,urllib.request,ssl,concurrent.futures,html as H
ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36 infosec-community-finder/1.0'
PATS={
 'discord':re.compile(r'https?://(?:www\.)?(?:discord(?:\.gg|\.com/invite|app\.com/invite)/[A-Za-z0-9_\-]+)'),
 'slack':re.compile(r'https?://(?:join\.slack\.com/t/[^\s"\'<>)]+|[A-Za-z0-9\-]+\.slack\.com/(?:join|signup|shared_invite)[^\s"\'<>)]*|[A-Za-z0-9\-]+\.herokuapp\.com/?)'),
 'matrix':re.compile(r'https?://matrix\.to/#/[^\s"\'<>)]+|matrix:[^\s"\'<>)]+'),
 'irc':re.compile(r'ircs?://[^\s"\'<>)]+|https?://web\.libera\.chat/[^\s"\'<>)]*|https?://kiwiirc\.com/[^\s"\'<>)]*'),
 'mattermost':re.compile(r'https?://[^\s"\'<>)]*mattermost[^\s"\'<>)]*'),
 'forum':re.compile(r'https?://(?:forum|forums|discourse|community|discuss)\.[^\s"\'<>)/]+/?'),
 'mastodon':re.compile(r'https?://(?:[a-z0-9\-]+\.)?(?:chaos\.social|mastodon\.[a-z]+|infosec\.exchange|fosstodon\.org|social\.[a-z0-9\-]+\.[a-z]+)/@[A-Za-z0-9_\-]+'),
 'meetup':re.compile(r'https?://(?:www\.)?meetup\.com/[A-Za-z0-9_\-]+/?'),
 'github':re.compile(r'https?://github\.com/[A-Za-z0-9_\-]+/?'),
}
SUBS=('','/discord','/community','/join','/contact','/about','/chat','/links','/get-involved','/membership')
def fetch(u):
    try:
        req=urllib.request.Request(u,headers={'User-Agent':UA,'Accept-Language':'en'})
        with urllib.request.urlopen(req,timeout=15,context=ctx) as r:
            if 'html' not in (r.headers.get('content-type') or 'html'): return ''
            return r.read(600000).decode('utf-8','replace')
    except Exception: return ''
def crawl(rec):
    w=(rec.get('website') or '').strip()
    if not w.startswith('http'): rec['crawl']='no-site'; return rec
    found={}
    for sub in SUBS:
        h=fetch(w.rstrip('/')+sub) if sub else fetch(w)
        if not h: 
            if not sub: rec['crawl']='unreachable'; return rec
            continue
        h=H.unescape(h)
        for k,p in PATS.items():
            for m in p.findall(h): found.setdefault(k,[]).append(m)
        if sub=='' :
            # also follow an on-site link that mentions discord/slack/matrix/chat/community
            for m in re.findall(r'href="([^"]+)"',h):
                if re.search(r'discord|slack|matrix|chat|community|join|mitglied|beitreten|comunidad|rejoindre|forum',m,re.I) and m.startswith(('/','http')) and not any(x in m for x in ('facebook','twitter','instagram')):
                    u2=m if m.startswith('http') else w.rstrip('/')+'/'+m.lstrip('/')
                    if u2.startswith(w.rstrip('/')[:25]) or 'discord' in u2 or 'slack' in u2 or 'matrix' in u2:
                        h2=H.unescape(fetch(u2))
                        for k,p in PATS.items():
                            for mm in p.findall(h2): found.setdefault(k,[]).append(mm)
                    if len(found.get('discord',[]))+len(found.get('slack',[]))+len(found.get('matrix',[]))>0: break
        if any(found.get(k) for k in ('discord','slack','matrix','mattermost')): break
    rec['found']={k:sorted(set(v))[:5] for k,v in found.items()}
    rec['crawl']='ok'
    return rec
rows=json.load(open(sys.argv[1]))
with concurrent.futures.ThreadPoolExecutor(12) as ex: out=list(ex.map(crawl,rows))
json.dump(out,open(sys.argv[2],'w'),indent=1,ensure_ascii=False)
from collections import Counter
print('sites',len(out),Counter(o.get('crawl') for o in out).most_common(),'| with chat:',sum(1 for o in out if any((o.get('found') or {}).get(k) for k in ('discord','slack','matrix','irc','mattermost'))))
print(Counter(k for o in out for k in (o.get('found') or {})).most_common())
