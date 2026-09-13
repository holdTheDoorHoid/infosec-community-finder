"""Merge candidate lists into data/communities.json.

Input: one or more JSON files, each a list of candidates:
  {"name", "invite_url" (or "invite_code"), "source_url", "category_hint", "notes", "confidence", ...}
Every invite is resolved through Discord's public invite preview; candidates are
deduplicated by guild id (the true identity of a server), then by invite code.
Existing entries are updated (stats + new sources), never dropped.
"""
import json, sys, re, datetime, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from discordapi import lookup_invite, invite_code, resolve_shortlink
from refresh import size_tier

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "communities.json"

def slugify(s):
    s = re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")
    return s[:60] or "server"

def load_db():
    if DATA.exists(): return json.loads(DATA.read_text())
    return {"communities": [], "unresolved": []}

def main(paths):
    db = load_db(); today = datetime.date.today().isoformat()
    by_guild = {c["guild_id"]: c for c in db["communities"] if c.get("guild_id")}
    by_code = {c["invite_code"].lower(): c for c in db["communities"] if c.get("invite_code")}
    cache = {}
    added = updated = dead = unresolved = 0
    for p in paths:
        cands = json.loads(pathlib.Path(p).read_text())
        if isinstance(cands, dict): cands = cands.get("merged") or cands.get("communities") or cands.get("seeds") or []
        for cand in cands:
            raw_url = cand.get("invite_url") or cand.get("discord_url") or cand.get("url")
            code = cand.get("invite_code") or invite_code(raw_url)
            if not code and raw_url and raw_url.startswith("http"):
                resolved = resolve_shortlink(raw_url); code = invite_code(resolved)
                if code: cand["notes"] = (cand.get("notes") or "") + f" | shortlink {raw_url} -> {resolved}"
            src = cand.get("source_url") or cand.get("source") or p
            if not code:
                db["unresolved"].append({"name": cand.get("name"), "notes": cand.get("notes"), "source_url": src, "category_hint": cand.get("category_hint"), "guild_id": cand.get("guild_id")})
                unresolved += 1; continue
            if code.lower() in by_code:
                c = by_code[code.lower()]
                if src not in c["sources"]: c["sources"].append(src)
                updated += 1; continue
            r = cache.get(code.lower()) or lookup_invite(code); cache[code.lower()] = r
            if r["status"] != "ok":
                db["unresolved"].append({"name": cand.get("name"), "invite_code": code, "status": r["status"], "error": r.get("error"), "source_url": src, "category_hint": cand.get("category_hint"), "notes": cand.get("notes")})
                dead += 1; continue
            gid = r["guild_id"]
            if gid in by_guild:
                c = by_guild[gid]
                if src not in c["sources"]: c["sources"].append(src)
                c.setdefault("alt_invites", [])
                if code not in c["alt_invites"] and code != c.get("invite_code"): c["alt_invites"].append(code)
                if cand.get("category_hint") and cand["category_hint"] not in c.get("category_hints", []): c.setdefault("category_hints", []).append(cand["category_hint"])
                updated += 1; continue
            base = slugify(r["discord_name"] or cand.get("name")); slug = base; n = 2
            while any(x["id"] == slug for x in db["communities"]): slug = f"{base}-{n}"; n += 1
            c = {
                "id": slug, "name": r["discord_name"] or cand.get("name"), "candidate_name": cand.get("name"),
                "invite_url": f"https://discord.gg/{r['vanity'] or code}", "invite_code": r["vanity"] or code,
                "guild_id": gid, "discord_name": r["discord_name"], "discord_description": r["discord_description"],
                "members": r["members"], "online": r["online"], "size_tier": size_tier(r["members"]),
                "verified": r["verified"], "partnered": r["partnered"], "discoverable": r["discoverable"], "community_features": r["community"],
                "verification_level": r["verification_level"], "vanity": r["vanity"], "icon_url": r["icon_url"], "invite_expires_at": r["expires_at"], "nsfw": r["nsfw"],
                "invite_status": "ok", "first_seen": today, "last_checked": today,
                "sources": [src], "category_hints": [cand["category_hint"]] if cand.get("category_hint") else [], "candidate_notes": cand.get("notes") or "",
                "confidence": cand.get("confidence"), "history": [{"date": today, "members": r["members"], "online": r["online"]}],
                # editorial fields filled in by the recon pass
                "category": None, "tags": [], "summary": None, "run_by": None, "website": None, "beginner_friendly": None, "audience": [], "activities": [], "region": None, "language": "en", "year_round": None, "event": None,
            }
            db["communities"].append(c); by_guild[gid] = c; by_code[code.lower()] = c; added += 1
    db["last_import"] = today
    DATA.write_text(json.dumps(db, indent=1, ensure_ascii=False) + "\n")
    print(f"added={added} updated={updated} dead/unresolvable={dead} no-invite={unresolved} total={len(db['communities'])}")

if __name__ == "__main__":
    main(sys.argv[1:])
