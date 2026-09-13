"""Regenerate research/REPORT.md — a provenance summary of the database."""
import json, pathlib, datetime
from collections import Counter
ROOT = pathlib.Path(__file__).resolve().parent.parent
db = json.loads((ROOT / "data/communities.json").read_text())
cs = db["communities"]; vis = [c for c in cs if not c.get("hidden") and c.get("invite_status") in ("ok","unchecked")]
nd = json.loads((ROOT / "research/confirmed_no_discord.json").read_text()) if (ROOT / "research/confirmed_no_discord.json").exists() else []
L = []
L.append(f"# Research report\n\nGenerated {datetime.date.today().isoformat()}.\n")
L.append(f"- Servers in database: **{len(cs)}** (visible {len(vis)}, hidden as off-topic/rejected {sum(1 for c in cs if c.get('hidden'))}, dead invites {sum(1 for c in cs if c.get('invite_status')=='dead')})")
L.append(f"- Name-only leads that could not be resolved to a working invite: {len(db.get('unresolved', []))}")
L.append(f"- Organizations checked and confirmed to have no public Discord (Slack/Matrix/forum instead, or none): {len(nd)}\n")
L.append("## Visible servers by category\n")
for k, v in Counter(c.get("category") for c in vis).most_common(): L.append(f"- {k}: {v}")
L.append("\n## Visible by platform\n")
for k, v in Counter(c.get("platform","discord") for c in vis).most_common(): L.append(f"- {k}: {v}")
L.append("\n## Beginner-friendliness distribution (visible)\n")
for k, v in sorted(Counter(c.get("beginner_friendly") for c in vis).items(), key=lambda x: str(x[0])): L.append(f"- {k}: {v}")
L.append("\n## Languages (visible)\n")
for k, v in Counter(c.get("language") for c in vis).most_common(): L.append(f"- {k}: {v}")
L.append("\n## Largest 25 (members)\n")
for c in sorted(vis, key=lambda c: -(c.get("members") or 0))[:25]: L.append(f"- {c['name']} — {c.get('members') or 0:,} members, {c.get('online') or 0:,} online — {c.get('category')} ({c.get('platform','discord')})")
L.append("\n## Hidden (rejected) servers and why\n")
for c in sorted([c for c in cs if c.get("hidden")], key=lambda c: c["name"].lower()): L.append(f"- {c['name']}: {(c.get('exclude_reason') or '')[:160]}")
L.append("\n## Confirmed without a public Discord\n")
for n in sorted(nd, key=str.lower): L.append(f"- {n}")
L.append("\n## Sources\n\nSeed file from the maintainer; LSOH conference tracker (82 Discord links); Discord server directory (`discord.com/servers?query=`, 35 queries); Disboard and top.gg listings (names only, Cloudflare-gated); GitHub lists (mhxion awesome-discord-communities, web3Gurung, UberGuidoZ, johnnyxmas gist); flare.io, Stefan Bargan, Olivia Gallucci, Blue Team Academy, Jordan Snapper (LinkedIn) roundups; topical web research across 13 clusters; a per-conference pass over 182 conferences; DEF CON villages; an invite-recovery pass over 170 dead/name-only leads; a gap pass over 7 thin categories; a notables check. Every invite was resolved through Discord's public invite preview and de-duplicated by guild id.\n")
(ROOT / "research/REPORT.md").write_text("\n".join(L) + "\n")
print("report written:", len(cs), "servers")
