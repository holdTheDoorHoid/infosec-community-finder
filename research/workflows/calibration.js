export const meta = {
  name: 'calibration-review',
  description: 'Consistency review of editorial fields per category group: fix outlier ratings, wrong categories/tags, bad summaries, duplicates, and anything that should not be listed',
  phases: [{ title: 'Calibrate', detail: 'one Sonnet agent per category group' }],
}
const CATS = ['general','learning','ctf','creator','tool','hardware','blueteam','redteam','appsec','osint','careers','affinity','regional','conference','village','adjacent']
const SCHEMA = { type:'object', properties:{
  changes:{ type:'array', items:{ type:'object', properties:{
    id:{type:'string'}, category:{type:['string','null'], enum:[...CATS, null]}, beginner_friendly:{type:['integer','null'], minimum:1, maximum:5},
    tags:{type:['array','null'], items:{type:'string'}}, audience:{type:['array','null'], items:{type:'string', enum:['beginner','intermediate','advanced']}},
    summary:{type:['string','null']}, hide:{type:'boolean'}, exclude_reason:{type:['string','null']}, language:{type:['string','null']}, region:{type:['string','null']}, reason:{type:'string'} },
    required:['id','category','beginner_friendly','tags','audience','summary','hide','exclude_reason','language','region','reason'] } },
  duplicates:{ type:'array', items:{ type:'object', properties:{ keep_id:{type:'string'}, hide_id:{type:'string'}, reason:{type:'string'} }, required:['keep_id','hide_id','reason'] } },
  notes:{type:'string'} }, required:['changes','duplicates','notes'] }
const GUIDE = `You are the final reviewer for a public directory of cybersecurity Discord communities aimed at beginners and intermediates. Read your group file with the Read tool: a JSON list of entries (id, name, category, bf = beginner_friendly 1-5, audience, tags, activities, members, online, region, language, run_by, red_flags, summary). Entries were written by different researchers; your job is CONSISTENCY and PRECISION, not rewriting everything. No web lookups are needed; judge from the data.
Return a change ONLY when something is clearly wrong. For each change set only the fields that should change (others null) and give a one-line reason.
Check for:
1. Beginner-friendliness outliers versus peers. Scale: 5 = explicitly welcomes beginners with help channels/mentors/learning paths; 4 = beginner questions get answered; 3 = mixed, assumes basics; 2 = mostly intermediate/advanced or a narrow tool-support server; 1 = explicitly not for beginners/gated. A tool-support server for one product should rarely be 5; a large learning hub with mentorship should rarely be 2.
2. Wrong category. Categories: general (broad infosec chat), learning, ctf, creator, tool (one product/project support), hardware (hardware/RF not tied to one product), blueteam, redteam, appsec, osint, careers, affinity, regional, conference, village, adjacent (non-security hobby: SDR, homelab, maker, retro).
3. Tags: add an obviously missing tag or remove a wrong one; keep 3-8. Allowed tags: red-team, pentesting, web-appsec, bug-bounty, blue-team, soc, dfir, malware-analysis, threat-intel, detection-engineering, ctf, wargames, reverse-engineering, binary-exploitation, hardware-hacking, rf-sdr, wireless, rfid-nfc, iot-embedded, car-hacking, ics-ot, lockpicking-physical, osint, privacy, cloud-security, ai-security, mobile-security, networking, linux, careers, certifications, study-group, mentorship, jobs, homelab, programming, general-infosec, hacker-culture, badgelife-maker, aviation-tracking, ham-radio, game-hacking, cryptography, students, conference, village, regional, affinity-women, affinity-veterans, affinity-lgbtq, affinity-bipoc, affinity-neurodivergent, youth, tool-support, vendor, flipper-zero, social-engineering, forensics, news-cve. When you return tags, return the COMPLETE new list.
4. Summaries: rewrite only if it is marketing fluff, starts with the server name, states the member count, contradicts the tags/category, or is under 15 words. Keep 2-3 plain sentences: who runs it, what happens there, who it suits.
5. Should not be listed (hide=true with exclude_reason): not security/hacking/adjacent-hobby related; sells cheats/accounts/illegal services; scam-like; NSFW; a commercial product's marketing server with no community value; or red_flags that make it unsafe to recommend to beginners.
6. Duplicates inside your group: the same community listed twice under different names (e.g. a creator and their community server, or the same conference twice). Return keep_id (the better/larger) and hide_id.
7. Platform-aware: entries have a platform field (discord, slack, forum, reddit, mastodon...); non-Discord entries legitimately have no member/online counts — do not penalize that.
8. Region/language mislabels (e.g. a French server labeled en; a Philadelphia group labeled global).
Be conservative: expect roughly 5-20% of entries to need a change. Put anything you noticed but did not change in notes.`
phase('Calibrate')
const groups = args.files
const results = await parallel(groups.map(g => () => agent(`${GUIDE}\n\nYour group file: ${args.dir}/${g}.json`, { label: `calib:${g}`, phase: 'Calibrate', schema: SCHEMA, model: 'sonnet', effort: 'medium' })))
const ok = results.filter(Boolean)
log(`${ok.length}/${groups.length} groups; ${ok.reduce((a, r) => a + r.changes.length, 0)} changes, ${ok.reduce((a, r) => a + r.duplicates.length, 0)} duplicates`)
return { changes: ok.flatMap(r => r.changes), duplicates: ok.flatMap(r => r.duplicates), notes: ok.map((r, i) => `${groups[i]}: ${r.notes}`) }