"""Harvest CTFtime teams by country for recent years, then fetch each team via the API to get the academic flag.
Output: research/ctftime_teams.json"""
import re, json, time, sys, urllib.request, concurrent.futures, threading
UA='Mozilla/5.0 (X11; Linux x86_64) infosec-community-finder/1.0 (+https://github.com/holdTheDoorHoid/infosec-community-finder)'
YEARS=[2026,2025]
CC="AD AE AF AG AI AL AM AO AQ AR AS AT AU AW AX AZ BA BB BD BE BF BG BH BI BJ BL BM BN BO BQ BR BS BT BV BW BY BZ CA CC CD CF CG CH CI CK CL CM CN CO CR CU CV CW CX CY CZ DE DJ DK DM DO DZ EC EE EG EH ER ES ET FI FJ FK FM FO FR GA GB GD GE GF GG GH GI GL GM GN GP GQ GR GS GT GU GW GY HK HM HN HR HT HU ID IE IL IM IN IO IQ IR IS IT JE JM JO JP KE KG KH KI KM KN KP KR KW KY KZ LA LB LC LI LK LR LS LT LU LV LY MA MC MD ME MF MG MH MK ML MM MN MO MP MQ MR MS MT MU MV MW MX MY MZ NA NC NE NF NG NI NL NO NP NR NU NZ OM PA PE PF PG PH PK PL PM PN PR PS PT PW PY QA RE RO RS RU RW SA SB SC SD SE SG SH SI SJ SK SL SM SN SO SR SS ST SV SX SY SZ TC TD TF TG TH TJ TK TL TM TN TO TR TT TV TW TZ UA UG UM US UY UZ VA VC VE VG VI VN VU WF WS YE YT ZA ZM ZW".split()
lock=threading.Lock()
def get(url,tries=3):
    for i in range(tries):
        try:
            req=urllib.request.Request(url,headers={'User-Agent':UA})
            return urllib.request.urlopen(req,timeout=30).read().decode('utf-8','replace')
        except urllib.error.HTTPError as e:
            if e.code==404: return None
            time.sleep(5*(i+1))
        except Exception:
            time.sleep(3*(i+1))
    return None
teams={}
def country(cc):
    for y in YEARS:
        page=1
        while page<20:
            time.sleep(0.4)
            h=get(f'https://ctftime.org/stats/{y}/{cc}?page={page}')
            if not h: break
            found=re.findall(r'href="/team/(\d+)">([^<]*)</a>',h)
            with lock:
                for tid,name in found:
                    t=teams.setdefault(tid,{'id':int(tid),'name':name.strip(),'cc':cc,'years':[]})
                    if y not in t['years']: t['years'].append(y)
            if len(found)<50: break
            page+=1
with concurrent.futures.ThreadPoolExecutor(3) as ex: list(ex.map(country,CC))
print('teams from country pages:',len(teams),file=sys.stderr,flush=True)
def api(t):
    time.sleep(0.35)
    raw=get(f"https://ctftime.org/api/v1/teams/{t['id']}/")
    if raw:
        try:
            j=json.loads(raw); t['academic']=j.get('academic'); t['aliases']=j.get('aliases'); t['country']=j.get('country'); t['logo']=j.get('logo')
        except Exception: t['api_error']=True
    else: t['api_error']=True
    return t
with concurrent.futures.ThreadPoolExecutor(3) as ex: out=list(ex.map(api,list(teams.values())))
json.dump(out,open('research/ctftime_teams.json','w'),indent=1,ensure_ascii=False)
from collections import Counter
print('done',len(out),'academic',sum(1 for t in out if t.get('academic')),'errors',sum(1 for t in out if t.get('api_error')))
print(Counter(t['cc'] for t in out if t.get('academic')).most_common(30))
