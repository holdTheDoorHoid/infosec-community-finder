"""Hide GitHub-harvested entries whose repo is clearly not security-related, so recon tokens are not wasted."""
import json,re
db=json.load(open('data/communities.json'))
SEC=re.compile(r'(secur|hack|pentest|penetration|exploit|vulnerab|malware|forensic|osint|reverse|reversing|ctf|red.?team|blue.?team|threat|intel|privacy|encrypt|crypto(?!currency)|password|firewall|ids\b|siem|edr|soc\b|c2\b|payload|phish|recon|scanner|fuzz|sdr\b|rfid|nfc|flipper|wifi|wireless|bluetooth|firmware|hardware|badusb|proxmark|pwn|ghidra|radare|binary|disassembl|debugger|honeypot|yara|sigma|suricata|zeek|wireshark|nmap|burp|kali|tor\b|vpn|anonym|opsec|lockpick|jtag|uart|esp32|meshtastic|lora|ham radio|ads-?b)',re.I)
n=0
for c in db['communities']:
    if c.get('recon_date') or c.get('hidden'): continue
    srcs=' '.join(c.get('sources',[]))
    if 'github.com' not in srcs: continue
    blob=(c.get('candidate_notes') or '')+' '+(c.get('discord_description') or '')+' '+(c.get('name') or '')
    if not SEC.search(blob):
        c['hidden']=True; c['exclude_reason']='auto: GitHub repo with no security-related description/topics'; c['recon_date']='auto'; n+=1
json.dump(db,open('data/communities.json','w'),indent=1,ensure_ascii=False)
print('auto-hidden off-topic GitHub entries:',n)
