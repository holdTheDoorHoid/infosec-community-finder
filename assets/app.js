/* Infosec Community Finder — shared front-end. Vanilla JS, no build step. */
const ICF = (() => {
  const CAT_LABEL = {general:'General infosec',learning:'Learning & study',ctf:'CTF & challenges',creator:'Creator community',tool:'Tool / project',hardware:'Hardware & RF',blueteam:'Blue team & DFIR',redteam:'Red team',appsec:'AppSec & bug bounty',osint:'OSINT & privacy',careers:'Careers & certs',affinity:'Affinity group',regional:'Local / regional',conference:'Conference',village:'Village',adjacent:'Adjacent hobby'};
  const SIZE_LABEL = {tiny:'Tiny (<500)',small:'Small (500–3k)',medium:'Medium (3k–15k)',large:'Large (15k–50k)',huge:'Huge (50k+)',unknown:'Unknown'};
  const REGION_LABEL = {global:'Global / online',us:'United States','us-northeast':'US Northeast','us-southeast':'US Southeast','us-midwest':'US Midwest','us-south':'US South / Texas','us-west':'US West',canada:'Canada','uk-ireland':'UK & Ireland',europe:'Europe',india:'India',asia:'Asia','australia-nz':'Australia / NZ','latin-america':'Latin America',africa:'Africa','middle-east':'Middle East'};
  let DB = null;

  async function load() {
    if (DB) return DB;
    const r = await fetch('data/communities.json', {cache:'no-cache'});
    DB = await r.json();
    DB.communities = (DB.communities || []).filter(c => !c.hidden);
    for (const c of DB.communities) {
      c.category = c.category || (c.category_hints && c.category_hints[0]) || 'general';
      c.tags = c.tags || []; c.activities = c.activities || []; c.audience = c.audience || [];
      c.summary = c.summary || c.discord_description || c.candidate_notes || '';
      c.size_tier = c.size_tier || 'unknown';
      c.region = c.region || 'global';
    }
    return DB;
  }
  const fmt = n => n == null ? '—' : n >= 1e6 ? (n/1e6).toFixed(n >= 1e7 ? 0 : 1) + 'M' : n >= 1000 ? (n/1000).toFixed(n >= 10000 ? 0 : 1) + 'k' : String(n);
  const esc = s => String(s ?? '').replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
  const stars = n => n ? '★'.repeat(n) + '☆'.repeat(5 - n) : '';
  const initials = name => (name || '?').split(/\s+/).slice(0,2).map(w => w[0]).join('').toUpperCase();

  function cardHTML(c) {
    const icon = c.icon_url ? `<img class="icon" loading="lazy" src="${esc(c.icon_url)}" alt="">` : `<div class="ph">${esc(initials(c.name))}</div>`;
    const status = c.invite_status === 'ok' ? '' : `<span class="badge dead">${c.invite_status === 'dead' ? 'invite dead' : 'unchecked'}</span>`;
    return `<article class="card" data-id="${esc(c.id)}" tabindex="0" role="button" aria-label="${esc(c.name)}">
      <div class="head">${icon}<div><h2>${esc(c.name)}</h2><div class="sub">${esc(CAT_LABEL[c.category] || c.category)}${c.run_by ? ' · ' + esc(c.run_by) : ''}</div></div></div>
      <p class="desc">${esc(c.summary)}</p>
      <div class="chips">${c.tags.slice(0,5).map(t => `<span class="chip">${esc(t)}</span>`).join('')}</div>
      <div class="meta"><span><b>${fmt(c.members)}</b> members</span><span><span class="dot"></span><b>${fmt(c.online)}</b> online</span>${c.beginner_friendly ? `<span class="stars" title="beginner friendliness ${c.beginner_friendly}/5">${stars(c.beginner_friendly)}</span>` : ''}${c.verified ? '<span class="badge verified">verified</span>' : ''}${c.partnered ? '<span class="badge verified">partnered</span>' : ''}${status}</div>
    </article>`;
  }

  function sparkline(hist) {
    if (!hist || hist.length < 2) return '';
    const v = hist.map(h => h.members || 0), min = Math.min(...v), max = Math.max(...v), w = 160, h = 36;
    const pts = v.map((y, i) => `${(i/(v.length-1))*w},${h - 3 - (max === min ? h/2 : ((y-min)/(max-min))*(h-6))}`).join(' ');
    return `<svg class="spark" viewBox="0 0 ${w} ${h}" aria-label="member history"><polyline fill="none" stroke="currentColor" stroke-width="1.5" points="${pts}"/></svg>`;
  }

  function detailHTML(c) {
    const icon = c.icon_url ? `<img class="icon" src="${esc(c.icon_url)}" alt="">` : `<div class="ph">${esc(initials(c.name))}</div>`;
    const links = [];
    if (c.website) links.push(`<a href="${esc(c.website)}" target="_blank" rel="noopener">Website</a>`);
    for (const [k, label] of [['github','GitHub'],['youtube','YouTube'],['twitter','X / Twitter']]) if (c[k]) links.push(`<a href="${esc(c[k])}" target="_blank" rel="noopener">${label}</a>`);
    const dead = c.invite_status === 'dead';
    return `<button class="close" aria-label="Close">✕</button>
      <div class="head">${icon}<div><h2>${esc(c.name)}</h2><div class="sub"><span class="chip cat">${esc(CAT_LABEL[c.category] || c.category)}</span> ${c.run_by ? '· run by ' + esc(c.run_by) : ''}</div></div></div>
      <p>${esc(c.summary)}</p>
      ${c.discord_description && c.summary !== c.discord_description ? `<p class="note">Server's own description: “${esc(c.discord_description)}”</p>` : ''}
      <div class="chips">${c.tags.map(t => `<span class="chip">${esc(t)}</span>`).join('')}</div>
      <dl class="kv">
        <dt>Members</dt><dd><b>${fmt(c.members)}</b> total · <b>${fmt(c.online)}</b> online now ${sparkline(c.history)}</dd>
        <dt>Size</dt><dd>${esc(SIZE_LABEL[c.size_tier] || c.size_tier)}</dd>
        ${c.beginner_friendly ? `<dt>Beginner friendly</dt><dd><span class="stars">${stars(c.beginner_friendly)}</span> ${c.beginner_friendly}/5${c.audience.length ? ' · for ' + esc(c.audience.join(', ')) : ''}</dd>` : ''}
        ${c.activities.length ? `<dt>What happens there</dt><dd>${esc(c.activities.join(', '))}</dd>` : ''}
        ${c.region && c.region !== 'global' ? `<dt>Region</dt><dd>${esc(REGION_LABEL[c.region] || c.region)}</dd>` : ''}
        ${c.language && c.language !== 'en' ? `<dt>Language</dt><dd>${esc(c.language)}</dd>` : ''}
        ${c.event ? `<dt>Event</dt><dd>${esc(c.event)}${c.year_round === false ? ' (active mainly around the event)' : c.year_round ? ' (active year-round)' : ''}</dd>` : ''}
        ${c.rules_note ? `<dt>Good to know</dt><dd>${esc(c.rules_note)}</dd>` : ''}
        <dt>Discord flags</dt><dd>${[c.verified && 'Verified', c.partnered && 'Partnered', c.discoverable && 'In Discord discovery', c.community_features && 'Community server', c.verification_level >= 3 && 'Phone/email verification required'].filter(Boolean).join(' · ') || '—'}</dd>
        ${links.length ? `<dt>Links</dt><dd>${links.join(' · ')}</dd>` : ''}
        <dt>Last checked</dt><dd>${esc(c.last_checked || '—')} · <span class="badge ${dead ? 'dead' : 'ok'}">${dead ? 'invite dead' : 'invite works'}</span></dd>
      </dl>
      <div class="join">${dead ? `<span class="note">This invite stopped working${c.dead_since ? ' on ' + esc(c.dead_since) : ''}. <a href="https://github.com/holdTheDoorHoid/infosec-community-finder/issues/new?template=report-problem.yml&title=${encodeURIComponent('[Fix] ' + c.name)}" target="_blank" rel="noopener">Know a new one?</a></span>` : `<a class="btn primary" href="${esc(c.invite_url)}" target="_blank" rel="noopener">Join on Discord ↗</a><span class="note">Opens Discord. Read the rules channel first; most servers require it.</span>`}</div>`;
  }

  function openModal(c) {
    let bg = document.querySelector('.modal-bg');
    if (!bg) { bg = document.createElement('div'); bg.className = 'modal-bg'; bg.innerHTML = '<div class="modal" role="dialog" aria-modal="true"></div>'; document.body.appendChild(bg);
      bg.addEventListener('click', e => { if (e.target === bg || e.target.closest('.close')) closeModal(); });
      document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); }); }
    bg.querySelector('.modal').innerHTML = detailHTML(c);
    bg.classList.add('open'); document.body.style.overflow = 'hidden';
    if (location.hash !== '#' + c.id) history.replaceState(null, '', '#' + c.id);
  }
  function closeModal() { const bg = document.querySelector('.modal-bg'); if (bg) bg.classList.remove('open'); document.body.style.overflow = ''; if (location.hash) history.replaceState(null, '', location.pathname + location.search); }

  return {load, cardHTML, detailHTML, openModal, closeModal, fmt, esc, CAT_LABEL, SIZE_LABEL, REGION_LABEL, stars};
})();

/* ---------- Browse page ---------- */
async function initBrowse() {
  const db = await ICF.load();
  const all = db.communities;
  const $ = s => document.querySelector(s);
  const state = {q:'', cat:new Set(), tag:new Set(), size:new Set(), region:new Set(), beginner:false, alive:true, sort:'online'};
  const params = new URLSearchParams(location.search);
  if (params.get('cat')) state.cat.add(params.get('cat'));
  if (params.get('tag')) state.tag.add(params.get('tag'));
  if (params.get('q')) state.q = params.get('q');

  const count = (key, arr) => { const m = {}; for (const c of arr) for (const v of (Array.isArray(c[key]) ? c[key] : [c[key]])) if (v) m[v] = (m[v]||0)+1; return m; };
  function facet(title, key, labels, set, limit) {
    const counts = count(key, all); const keys = Object.keys(counts).sort((a,b) => counts[b]-counts[a]).slice(0, limit || 99);
    return `<h3>${title}</h3>` + keys.map(k => `<label><input type="checkbox" data-facet="${key}" value="${ICF.esc(k)}" ${set.has(k)?'checked':''}> ${ICF.esc(labels ? (labels[k]||k) : k)}<span class="n">${counts[k]}</span></label>`).join('');
  }
  $('.filters').innerHTML = `<input class="search" type="search" placeholder="Search names, tags, descriptions…" value="${ICF.esc(state.q)}" aria-label="Search">
    <h3>Quick</h3><label><input type="checkbox" id="f-beginner"> Beginner friendly (4★+)</label><label><input type="checkbox" id="f-alive" checked> Hide dead invites</label>
    ${facet('Category','category',ICF.CAT_LABEL,state.cat)}${facet('Topics','tags',null,state.tag,28)}${facet('Size','size_tier',ICF.SIZE_LABEL,state.size)}${facet('Region','region',ICF.REGION_LABEL,state.region)}`;
  $('.filters').addEventListener('change', e => {
    const t = e.target; if (t.id === 'f-beginner') state.beginner = t.checked; else if (t.id === 'f-alive') state.alive = t.checked;
    else if (t.dataset.facet) { const set = state[{category:'cat',tags:'tag',size_tier:'size',region:'region'}[t.dataset.facet]]; t.checked ? set.add(t.value) : set.delete(t.value); }
    render();
  });
  $('.filters .search').addEventListener('input', e => { state.q = e.target.value; render(); });
  $('#sort').addEventListener('change', e => { state.sort = e.target.value; render(); });

  function matches(c) {
    if (state.alive && c.invite_status === 'dead') return false;
    if (state.beginner && !(c.beginner_friendly >= 4)) return false;
    if (state.cat.size && !state.cat.has(c.category)) return false;
    if (state.tag.size && ![...state.tag].every(t => c.tags.includes(t))) return false;
    if (state.size.size && !state.size.has(c.size_tier)) return false;
    if (state.region.size && !state.region.has(c.region)) return false;
    if (state.q) { const q = state.q.toLowerCase(); const hay = [c.name, c.summary, c.discord_description, c.run_by, c.event, ...c.tags].join(' ').toLowerCase(); if (!hay.includes(q)) return false; }
    return true;
  }
  const sorters = {online:(a,b)=>(b.online||0)-(a.online||0), members:(a,b)=>(b.members||0)-(a.members||0), beginner:(a,b)=>(b.beginner_friendly||0)-(a.beginner_friendly||0)||(b.online||0)-(a.online||0), name:(a,b)=>a.name.localeCompare(b.name), newest:(a,b)=>(b.first_seen||'').localeCompare(a.first_seen||'')};
  function render() {
    const list = all.filter(matches).sort(sorters[state.sort]);
    $('#count').textContent = `${list.length} of ${all.length} communities`;
    $('#grid').innerHTML = list.length ? list.map(ICF.cardHTML).join('') : '<div class="empty">Nothing matches. Loosen a filter or try the <a href="quiz.html">questionnaire</a>.</div>';
  }
  $('#grid').addEventListener('click', e => { const el = e.target.closest('.card'); if (el) ICF.openModal(all.find(c => c.id === el.dataset.id)); });
  $('#grid').addEventListener('keydown', e => { if (e.key === 'Enter') { const el = e.target.closest('.card'); if (el) ICF.openModal(all.find(c => c.id === el.dataset.id)); } });
  const s = db.stats || {}; const alive = all.filter(c => c.invite_status === 'ok');
  $('#stats').innerHTML = `<span><b>${all.length}</b> communities</span><span><b>${ICF.fmt(alive.reduce((a,c)=>a+(c.members||0),0))}</b> combined members</span><span><b>${ICF.fmt(alive.reduce((a,c)=>a+(c.online||0),0))}</b> online right now</span><span>invites re-checked weekly · last <b>${ICF.esc(db.last_refresh || db.last_import || '—')}</b></span>`;
  render();
  if (location.hash) { const c = all.find(x => x.id === location.hash.slice(1)); if (c) ICF.openModal(c); }
}

/* ---------- Quiz page ---------- */
const QUIZ = [
  {id:'level', title:'Where are you right now?', help:'Be honest; it only changes which servers we rank first.', type:'single', opts:[
    ['new','Brand new','Curious, maybe watched some videos'],['basics','Know the basics','Some Linux, networking, a course or cert in progress'],['intermediate','Intermediate','Done CTFs or labs, or work in IT'],['advanced','Advanced','Work in security or close to it']]},
  {id:'interests', title:'What pulls you in?', help:'Pick up to three.', type:'multi', max:3, opts:[
    ['offense','Offensive & pentesting',''],['defense','Defense, SOC & incident response',''],['ctf','CTFs & challenge sites',''],['hardware','Hardware, RF & gadgets','Flipper, SDR, RFID, badges'],['web','Web app security & bug bounty',''],['malware','Malware & reverse engineering',''],['osint','OSINT & investigations',''],['privacy','Privacy & digital rights',''],['careers','Careers, certs & job hunting',''],['cloud','Cloud & AI security',''],['physical','Lockpicking & physical security',''],['culture','Hacker culture & general chat','']]},
  {id:'wants', title:'What do you want from a community?', help:'Pick everything that applies.', type:'multi', opts:[
    ['help','Ask questions and get help',''],['learn','Structured learning & study groups',''],['team','Find a CTF team',''],['jobs','Job hunting & career advice',''],['build','Build or hack hardware with others',''],['irl','Meet people in person','Local groups and conferences'],['mentor','Mentorship',''],['news','Keep up with news, CVEs & research','']]},
  {id:'size', title:'What size feels right?', help:'', type:'single', opts:[
    ['big','Big & busy','Thousands online, fast answers, more noise'],['mid','Mid-size','Hundreds online'],['small','Small & tight-knit','You will be recognized'],['any','No preference','']]},
  {id:'region', title:'Where are you based?', help:'Only used to suggest local groups and conference servers.', type:'single', opts:[
    ['us-northeast','US Northeast',''],['us-southeast','US Southeast',''],['us-midwest','US Midwest',''],['us-south','US South / Texas',''],['us-west','US West',''],['canada','Canada',''],['uk-ireland','UK & Ireland',''],['europe','Europe',''],['india','India',''],['asia','Asia',''],['australia-nz','Australia / NZ',''],['latin-america','Latin America',''],['africa','Africa',''],['global','Prefer online-only','']]},
  {id:'affinity', title:'Would an affinity group help?', help:'Optional. Some of the most welcoming servers are run by and for these groups.', type:'multi', opts:[
    ['affinity-women','Women in security',''],['affinity-veterans','Veterans & military',''],['affinity-lgbtq','LGBTQ+',''],['affinity-bipoc','Black, Latino & BIPOC',''],['affinity-neurodivergent','Neurodivergent',''],['youth','Student or under 18','']]},
];
const INTEREST_TAGS = {offense:['red-team','pentesting','social-engineering'], defense:['blue-team','soc','dfir','detection-engineering','threat-intel','forensics'], ctf:['ctf','wargames','binary-exploitation'], hardware:['hardware-hacking','rf-sdr','wireless','rfid-nfc','iot-embedded','flipper-zero','badgelife-maker','car-hacking','ics-ot'], web:['web-appsec','bug-bounty'], malware:['malware-analysis','reverse-engineering','binary-exploitation'], osint:['osint'], privacy:['privacy'], careers:['careers','certifications','jobs','study-group'], cloud:['cloud-security','ai-security'], physical:['lockpicking-physical'], culture:['hacker-culture','general-infosec']};
const WANT_ACT = {help:['q-and-a','chat'], learn:['study-groups','workshops','challenges'], team:['ctf-events','challenges'], jobs:['job-board','mentorship'], build:['hardware-help','project-showcase'], irl:['local-meetups'], mentor:['mentorship'], news:['news-feed','writeups']};
const US = new Set(['us-northeast','us-southeast','us-midwest','us-south','us-west']);

function scoreCommunity(c, a) {
  const why = []; let s = 0;
  const tags = new Set(c.tags), acts = new Set(c.activities);
  // interests
  const hits = [];
  for (const i of a.interests) { const n = INTEREST_TAGS[i].filter(t => tags.has(t)).length; if (n) { s += 3 + Math.min(n-1, 2); hits.push(i); } }
  if (hits.length) why.push(`Matches your interest in ${hits.map(h => QUIZ[1].opts.find(o => o[0]===h)[1].toLowerCase()).join(', ')}`);
  if (a.interests.length && !hits.length) s -= 4;
  // wants
  const wh = a.wants.filter(w => WANT_ACT[w].some(x => acts.has(x)));
  if (wh.length) { s += 2 * wh.length; why.push(`Offers ${wh.map(w => QUIZ[2].opts.find(o => o[0]===w)[1].toLowerCase()).join(', ')}`); }
  // level
  const bf = c.beginner_friendly || 3;
  if (a.level === 'new') { s += (bf - 3) * 2.5; if (bf >= 4) why.push('Known for welcoming complete beginners'); if (bf <= 2) s -= 6; }
  else if (a.level === 'basics') { s += (bf - 3) * 1.5; if (bf >= 4) why.push('Beginner friendly'); }
  else if (a.level === 'intermediate') { if (c.audience.includes('intermediate')) { s += 2; } if (bf === 5 && !c.audience.includes('intermediate')) s -= 1; }
  else if (a.level === 'advanced') { if (c.audience.includes('advanced')) { s += 3; why.push('Has an advanced crowd'); } if (bf === 5 && !c.audience.includes('advanced')) s -= 3; }
  // size
  const tier = c.size_tier;
  if (a.size === 'big' && (tier === 'large' || tier === 'huge')) { s += 2; why.push('Big, busy server'); }
  if (a.size === 'mid' && (tier === 'medium' || tier === 'small')) { s += 2; }
  if (a.size === 'small' && (tier === 'tiny' || tier === 'small')) { s += 3; why.push('Small enough to get known'); }
  if (a.size === 'small' && tier === 'huge') s -= 2;
  if (a.size === 'big' && tier === 'tiny') s -= 2;
  // activity signal: online count matters for getting answers
  s += Math.min(Math.log10((c.online || 1)) , 4) * 0.8;
  // region
  const local = c.category === 'regional' || c.category === 'conference' || c.category === 'village';
  if (local) {
    const r = c.region || 'global';
    const near = r === a.region || (US.has(a.region) && r === 'us') || r === 'global' && c.category === 'village';
    if (a.wants.includes('irl') && near && r !== 'global') { s += 5; why.push('Near you, with real-world meetups or events'); }
    else if (near && r !== 'global') { s += 1.5; why.push('In your region'); }
    else if (c.category !== 'village') s -= 5; // far-away local group
  }
  // affinity
  const af = a.affinity.filter(t => tags.has(t));
  if (af.length) { s += 5; why.push('Run for ' + af.map(t => QUIZ[5].opts.find(o => o[0]===t)[1].toLowerCase()).join(', ')); }
  if (c.category === 'affinity' && !af.length) s -= 6;
  // adjacent hobby only if hardware interest
  if (c.category === 'adjacent' && !a.interests.includes('hardware')) s -= 4;
  if (c.category === 'tool' && !a.interests.includes('hardware') && !a.wants.includes('build')) s -= 2;
  if (c.language && c.language !== 'en') s -= 4;
  return {s, why};
}

async function initQuiz() {
  const db = await ICF.load();
  const form = document.querySelector('#quiz');
  form.innerHTML = QUIZ.map(q => `<section class="q" data-q="${q.id}"><h2>${q.title}</h2>${q.help ? `<p class="help">${q.help}</p>` : ''}<div class="opts">${q.opts.map(([v,l,h]) => `<label class="opt"><input type="${q.type==='single'?'radio':'checkbox'}" name="${q.id}" value="${v}"><span>${l}${h?`<small>${h}</small>`:''}</span></label>`).join('')}</div></section>`).join('') + '<button class="btn primary" type="submit">Show my matches</button>';
  form.addEventListener('change', e => { const q = QUIZ.find(x => x.id === e.target.name); if (q && q.max) { const boxes = [...form.querySelectorAll(`input[name=${q.id}]:checked`)]; if (boxes.length > q.max) { e.target.checked = false; } } });
  form.addEventListener('submit', e => {
    e.preventDefault();
    const a = {}; for (const q of QUIZ) { const v = [...form.querySelectorAll(`input[name=${q.id}]:checked`)].map(i => i.value); a[q.id] = q.type === 'single' ? (v[0] || (q.id==='region'?'global':q.id==='size'?'any':'basics')) : v; }
    const alive = db.communities.filter(c => c.invite_status !== 'dead' && c.category !== 'conference' && c.category !== 'village' && c.category !== 'regional');
    const scored = alive.map(c => ({c, ...scoreCommunity(c, a)})).sort((x,y) => y.s - x.s);
    // diversify: avoid 5 servers of the same category
    const picks = []; const catCount = {};
    for (const x of scored) { if ((catCount[x.c.category]||0) >= 2 && picks.length >= 2) continue; picks.push(x); catCount[x.c.category] = (catCount[x.c.category]||0)+1; if (picks.length === 5) break; }
    for (const x of scored) { if (picks.length >= 5) break; if (!picks.includes(x)) picks.push(x); }
    const localPool = db.communities.filter(c => c.invite_status !== 'dead' && (c.category === 'conference' || c.category === 'village' || c.category === 'regional'));
    const local = localPool.map(c => ({c, ...scoreCommunity(c, a)})).filter(x => x.s > 0).sort((x,y) => y.s - x.s).slice(0, 4);
    const out = document.querySelector('#results');
    const row = (x, i) => `<div class="result"><div class="rank">${i+1}</div><div style="flex:1"><h3><a href="#" data-id="${ICF.esc(x.c.id)}">${ICF.esc(x.c.name)}</a> <span class="chip">${ICF.esc(ICF.CAT_LABEL[x.c.category]||x.c.category)}</span></h3><div class="note">${ICF.fmt(x.c.members)} members · ${ICF.fmt(x.c.online)} online${x.c.beginner_friendly?` · <span class="stars">${ICF.stars(x.c.beginner_friendly)}</span>`:''}</div><p style="margin:6px 0 0">${ICF.esc(x.c.summary)}</p>${x.why.length?`<ul class="why">${x.why.map(w=>`<li>${ICF.esc(w)}</li>`).join('')}</ul>`:''}<div class="join" style="margin-top:8px"><a class="btn sm primary" href="${ICF.esc(x.c.invite_url)}" target="_blank" rel="noopener">Join ↗</a><a class="btn sm" href="#" data-id="${ICF.esc(x.c.id)}">Details</a></div></div></div>`;
    out.innerHTML = `<h2>Your best matches</h2><p class="note">Join two or three, lurk for a week, then keep the one where you actually talk. Every server has a rules channel; read it first.</p>${picks.map(row).join('')}` +
      (local.length ? `<h2>Near you: local groups, conferences & villages</h2>${local.map(row).join('')}` : `<p class="note">No local group in the directory for your region yet. <a href="https://github.com/holdTheDoorHoid/infosec-community-finder/issues/new?template=submit-community.yml" target="_blank" rel="noopener">Know one?</a></p>`) +
      `<p class="note" style="margin-top:14px"><a href="#" id="retake">Change answers</a> · <a href="index.html">Browse everything</a></p>`;
    out.querySelectorAll('a[data-id]').forEach(el => el.addEventListener('click', ev => { ev.preventDefault(); ICF.openModal(db.communities.find(c => c.id === el.dataset.id)); }));
    out.querySelector('#retake').addEventListener('click', ev => { ev.preventDefault(); out.innerHTML=''; form.hidden = false; window.scrollTo({top:0,behavior:'smooth'}); });
    form.hidden = true; window.scrollTo({top:0,behavior:'smooth'});
  });
}
