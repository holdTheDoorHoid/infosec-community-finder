"""Re-check every community's invite and refresh live stats.

Run:  python3 scripts/refresh.py            (updates data/communities.json in place)
Used by the weekly GitHub Action. Never joins servers; only reads Discord's public invite preview.
"""
import json, sys, datetime, pathlib, time
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from discordapi import lookup_invite, invite_code, check_join_url, mastodon_stats

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "communities.json"
SIZE_TIERS = [(0, "tiny"), (500, "small"), (3000, "medium"), (15000, "large"), (50000, "huge")]

def size_tier(n):
    t = "unknown"
    if n is None: return t
    for floor, name in SIZE_TIERS:
        if n >= floor: t = name
    return t

BUDGET_SECONDS = int(__import__("os").environ.get("REFRESH_BUDGET_SECONDS", "3600"))  # never run away: stop checking after this and still save

def main():
    doc = json.loads(DATA.read_text())
    today = datetime.date.today().isoformat()
    ok = dead = err = skipped = 0; throttled = 0
    t0 = time.time()
    for i, c in enumerate(doc["communities"]):
        if i % 50 == 0: print(f"[{int(time.time()-t0)}s] {i}/{len(doc['communities'])} ok={ok} dead={dead} err={err}", flush=True)
        if time.time() - t0 > BUDGET_SECONDS:
            skipped += 1; c["last_error"] = "skipped: time budget"; continue
        if c.get("platform", "discord") != "discord":
            chk = check_join_url(c.get("invite_url")); c["last_checked"] = today
            if chk["status"] == "ok":
                ok += 1; c["invite_status"] = "ok"
                if c["platform"] == "mastodon":
                    st = mastodon_stats(c["invite_url"]);
                    if st.get("members"): c["members"] = st["members"]; c["size_tier"] = size_tier(st["members"]); c.setdefault("history", []).append({"date": today, "members": st["members"], "online": None}); c["history"] = c["history"][-90:]
            elif chk["status"] == "dead": dead += 1; c["invite_status"] = "dead"; c["dead_since"] = c.get("dead_since") or today
            elif chk["status"] == "unchecked": c["invite_status"] = "unchecked"
            else: err += 1; c["last_error"] = chk.get("error")
            time.sleep(0.3); continue
        code = c.get("invite_code") or invite_code(c.get("invite_url"))
        if not code:
            c["invite_status"] = "missing"; continue
        if throttled >= 25:
            skipped += 1; c["last_error"] = "skipped: Discord rate limit persisted"; continue
        r = lookup_invite(code)
        c["last_checked"] = today
        if r["status"] == "error" and str(r.get("error", "")).startswith("429"):
            throttled += 1; err += 1; c["last_error"] = r["error"]
            time.sleep(min(60, 10 * throttled))  # back off harder each time the shared runner IP is throttled
            continue
        throttled = 0
        if r["status"] == "ok":
            ok += 1
            c["invite_status"] = "ok"
            c["guild_id"] = r["guild_id"]
            c["discord_name"] = r["discord_name"]
            c["discord_description"] = r["discord_description"]
            c["members"] = r["members"]; c["online"] = r["online"]
            c["size_tier"] = size_tier(r["members"])
            c["verified"] = r["verified"]; c["partnered"] = r["partnered"]
            c["discoverable"] = r["discoverable"]; c["community_features"] = r["community"]
            c["verification_level"] = r["verification_level"]
            c["vanity"] = r["vanity"]; c["icon_url"] = r["icon_url"]
            c["invite_expires_at"] = r["expires_at"]
            c["nsfw"] = r["nsfw"]
            c.setdefault("history", []).append({"date": today, "members": r["members"], "online": r["online"]})
            c["history"] = c["history"][-52:]
        elif r["status"] == "dead":
            dead += 1
            c["invite_status"] = "dead"
            c["dead_since"] = c.get("dead_since") or today
        else:
            err += 1
            c["invite_status"] = c.get("invite_status", "unknown")  # keep last known state on transient errors
            c["last_error"] = r.get("error")
    doc["last_refresh"] = today
    doc["stats"] = {"total": len(doc["communities"]), "ok": ok, "dead": dead, "errors": err, "skipped": skipped, "seconds": int(time.time() - t0)}
    DATA.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
    print(f"refreshed {len(doc['communities'])}: ok={ok} dead={dead} errors={err} skipped={skipped} in {int(time.time()-t0)}s")

if __name__ == "__main__":
    main()
