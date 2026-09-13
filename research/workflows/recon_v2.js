export const meta = {
  name: 'community-recon-v2',
  description: 'Per-community reconnaissance with locality and platform awareness — 6 communities per Sonnet agent',
  phases: [{ title: 'Recon', detail: 'one Sonnet agent per batch file' }],
}
const CATS = ['general','learning','ctf','creator','tool','hardware','blueteam','redteam','appsec','osint','careers','affinity','regional','conference','village','adjacent']
const TAGS = ["red-team","pentesting","web-appsec","bug-bounty","blue-team","soc","dfir","malware-analysis","threat-intel","detection-engineering","ctf","wargames","reverse-engineering","binary-exploitation","hardware-hacking","rf-sdr","wireless","rfid-nfc","iot-embedded","car-hacking","ics-ot","lockpicking-physical","osint","privacy","cloud-security","ai-security","mobile-security","networking","linux","careers","certifications","study-group","mentorship","jobs","homelab","programming","general-infosec","hacker-culture","badgelife-maker","aviation-tracking","ham-radio","game-hacking","cryptography","students","conference","village","regional","affinity-women","affinity-veterans","affinity-lgbtq","affinity-bipoc","affinity-neurodivergent","youth","tool-support","vendor","flipper-zero","social-engineering","forensics","news-cve"]
const ACTS = ["chat","q-and-a","ctf-events","study-groups","job-board","voice-events","workshops","hardware-help","project-showcase","news-feed","mentorship","local-meetups","challenges","writeups","giveaways"]
const AUD = ["beginner","intermediate","advanced"]
const REG = ["global","us","us-northeast","us-southeast","us-midwest","us-south","us-west","canada","uk-ireland","europe","india","asia","australia-nz","latin-america","africa","middle-east"]
const SCHEMA = { type:'object', properties:{ results:{ type:'array', items:{ type:'object', properties:{
  id:{type:'string'}, include:{type:'boolean'}, exclude_reason:{type:['string','null']},
  category:{type:'string', enum:CATS}, tags:{type:'array', items:{type:'string', enum:TAGS}, minItems:1, maxItems:8},
  audience:{type:'array', items:{type:'string', enum:AUD}}, beginner_friendly:{type:'integer', minimum:1, maximum:5},
  activities:{type:'array', items:{type:'string', enum:ACTS}}, summary:{type:'string'}, run_by:{type:['string','null']},
  website:{type:['string','null']}, github:{type:['string','null']}, youtube:{type:['string','null']},
  region:{type:'string', enum:REG}, country:{type:['string','null']}, subdivision:{type:['string','null']}, city:{type:['string','null']},
  language:{type:'string'}, year_round:{type:['boolean','null']}, event:{type:['string','null']},
  rules_note:{type:['string','null']}, red_flags:{type:['string','null']}, confidence:{type:'string', enum:['low','medium','high']} },
  required:['id','include','exclude_reason','category','tags','audience','beginner_friendly','activities','summary','run_by','website','github','youtube','region','country','subdivision','city','language','year_round','event','rules_note','red_flags','confidence'] } } }, required:['results'] }

const GUIDE = `You are writing entries for a public directory that helps beginners and intermediates find a cybersecurity community. Research each community in your batch and return one structured result per entry (same "id").
TOOLS: Read your batch file with the Read tool. Use WebSearch and WebFetch (load with ToolSearch "select:WebFetch,WebSearch" if deferred). NEVER use browser tools, never log in, never join. Budget: at most 15 WebSearch calls for the whole batch (searches are shared and scarce) and as many WebFetch calls of official pages as you need; prefer fetching the official site/GitHub/YouTube page directly over searching; the description, candidate notes and sources in the batch already tell you a lot. Well-known projects/creators/conferences need one lookup of the official site.
PLATFORM: entries have a "platform" (discord, slack, matrix, irc, mattermost, forum, reddit, mastodon). For non-Discord entries there are no live member counts; describe how people join (self-service signup page, subreddit, forum registration) in rules_note if notable. Judge beginner-friendliness from the community's own stated purpose and tone.
INCLUDE = false when the entry is not about security/hacking or a listed adjacent hobby (game fandom, generic PC help, crypto trading, general programming with no security angle), sells cheats/accounts/"hacking services", is NSFW/illegal, or is a private/members-only space with no public way in. Put the reason in exclude_reason and still fill the other fields sensibly.
CATEGORY (single best): general (broad infosec chat), learning (structured learning first), ctf (challenge platform/wargame/CTF team; university CTF clubs go here), creator (YouTuber/streamer/podcast/newsletter community), tool (support community for one product/project), hardware (hardware/RF/gadget hacking not tied to one product), blueteam, redteam, appsec (web/bug bounty), osint (OSINT/privacy/investigations), careers (certs/jobs/study groups), affinity (identity-based), regional (city/country group, DEF CON group, hackerspace, meetup), conference, village, adjacent (non-security hobby: SDR, homelab, maker, retro).
TAGS: 3-8 from the fixed list, most specific first. "students" for university clubs. affinity-*/youth only when BY/FOR that group. Use conference/village/regional tags on those categories.
AUDIENCE: who actually fits (several allowed). BEGINNER_FRIENDLY: 5 = explicitly welcomes beginners with help channels/mentors/learning paths and a friendly tone; 4 = beginner questions get answered; 3 = mixed, assumes basics; 2 = mostly intermediate/advanced or a narrow tool-support space; 1 = explicitly not for beginners, gated, or hostile. Do not give 5 just because it is big.
ACTIVITIES: from the fixed list. SUMMARY: 2-3 plain-English sentences: who runs it, what people actually do there, who it suits. Specific and honest, no marketing fluff, do NOT start with the name, do not state the member count.
RUN_BY: person/company/project/organization or "community-run". WEBSITE/GITHUB/YOUTUBE: official links if easily found, else null.
LOCATION: region "global" for online-only. For regional/conference/village/university entries give country (ISO-2), subdivision (US state / Canadian province 2-letter code, else null), city, and the matching region: us-northeast (CT DE DC MA MD ME NH NJ NY PA RI VT), us-southeast (AL FL GA KY MS NC SC TN VA WV), us-midwest (IA IL IN KS MI MN MO ND NE OH SD WI), us-south (AR LA OK TX), us-west (rest of US), canada, uk-ireland, europe, india, asia, australia-nz, latin-america, africa, middle-east. DEF CON groups are named by telephone area code (DC215 = Philadelphia PA). DEF CON villages: region global, event "DEF CON".
LANGUAGE: ISO code of the main language. Non-English entries stay include=true with the right language.
YEAR_ROUND: for conference/village/event entries: true if active outside the event, false if event-week only, null if unknown. EVENT: event name for conference/village entries, else null.
RULES_NOTE: one short line newcomers should know if notable (verification required, pick roles first, 18+, no "how do I hack X" requests, how to sign up on Slack), else null. RED_FLAGS: anything that should make us cautious, else null. CONFIDENCE: high if you saw an official source, medium if listings + description, low if mostly guessing.`

phase('Recon')
const paths = []
for (let i = args.start; i < args.start + args.count; i++) paths.push(`${args.dir}/batch_${String(i).padStart(3,'0')}.json`)
const results = await parallel(paths.map((p, i) => () => agent(
  `${GUIDE}\n\nYour batch file: ${p}\nRead it first, then research each entry, then return the structured results (one per id, all ids present).`,
  { label: `recon:${args.start + i}`, phase: 'Recon', schema: SCHEMA, model: 'sonnet', effort: 'medium' }
)))
const ok = results.filter(Boolean)
const flat = ok.flatMap(r => r.results || [])
log(`${ok.length}/${paths.length} batches returned, ${flat.length} results, ${flat.filter(r => !r.include).length} marked exclude`)
return { results: flat, batches_failed: results.map((r, i) => r ? null : args.start + i).filter(x => x !== null) }
