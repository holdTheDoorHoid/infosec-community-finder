"""Tiny client for Discord's public, unauthenticated invite endpoint.

No login, no bot token, no joining. Discord exposes name, description,
approximate member/online counts and server features for any invite code.
"""
import json, re, time, urllib.request, urllib.error

UA = "infosec-community-finder/1.0 (+https://github.com/holdTheDoorHoid/infosec-community-finder)"
INVITE_RE = re.compile(r"(?:https?://)?(?:www\.)?(?:discord\.gg|discord\.com/invite|discordapp\.com/invite)/([A-Za-z0-9\-_]+)", re.I)

def invite_code(url):
    if not url: return None
    m = INVITE_RE.search(url.strip())
    return m.group(1) if m else None

def _get(url, tries=4):
    for attempt in range(tries):
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return r.status, json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")
            try: data = json.loads(body)
            except Exception: data = {"message": body[:200]}
            if e.code == 429:
                wait = float(data.get("retry_after", 2)) + 0.5
                if attempt >= 2: return 429, data  # do not stall a whole run on one hot endpoint
                time.sleep(min(wait, 15)); continue
            return e.code, data
        except Exception as ex:
            if attempt == tries - 1: return 0, {"message": str(ex)}
            time.sleep(1.5 * (attempt + 1))
    return 0, {"message": "gave up"}

def lookup_invite(code):
    """Return a normalized dict for an invite code. status: ok | dead | error."""
    status, d = _get(f"https://discord.com/api/v10/invites/{code}?with_counts=true&with_expiration=true")
    time.sleep(0.4)  # be polite; the invites endpoint is rate-limited per IP
    if status == 200 and d.get("guild"):
        g = d["guild"]; feats = set(g.get("features") or [])
        icon = g.get("icon")
        return {
            "status": "ok", "code": code, "guild_id": g.get("id"), "discord_name": g.get("name"),
            "discord_description": g.get("description"), "members": d.get("approximate_member_count"),
            "online": d.get("approximate_presence_count"), "verification_level": g.get("verification_level"),
            "vanity": g.get("vanity_url_code"), "expires_at": d.get("expires_at"),
            "verified": "VERIFIED" in feats, "partnered": "PARTNERED" in feats,
            "discoverable": "DISCOVERABLE" in feats, "community": "COMMUNITY" in feats,
            "icon_url": f"https://cdn.discordapp.com/icons/{g.get('id')}/{icon}.{'gif' if str(icon).startswith('a_') else 'png'}?size=128" if icon else None,
            "nsfw": bool(g.get("nsfw")) or (g.get("nsfw_level") in (1, 3)),
            "channel": (d.get("channel") or {}).get("name"),
        }
    if status in (404, 400) or (status == 200 and not d.get("guild")):
        return {"status": "dead", "code": code, "error": d.get("message")}
    return {"status": "error", "code": code, "error": f"{status}: {d.get('message')}"}

def widget_invite(guild_id):
    """Some servers enable the widget, which exposes an instant invite by guild id."""
    status, d = _get(f"https://discord.com/api/v10/guilds/{guild_id}/widget.json")
    time.sleep(0.4)
    if status == 200:
        return {"status": "ok", "instant_invite": d.get("instant_invite"), "name": d.get("name"), "presence_count": d.get("presence_count")}
    return {"status": "none", "error": d.get("message")}

def resolve_shortlink(url):
    """Follow public redirects (bit.ly, tinyurl, a conference's own /discord path) to a Discord invite URL."""
    if not url or invite_code(url): return url
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Chrome/120"})
        with urllib.request.urlopen(req, timeout=20) as r:
            final = r.geturl()
            if invite_code(final): return final
            body = r.read(200000).decode("utf-8", "replace")
            m = re.search(r"https?://(?:www\.)?discord(?:\.gg|\.com/invite)/[A-Za-z0-9_\-]+", body)
            return m.group(0) if m else None
    except Exception:
        return None

PLATFORM_HOSTS = {"slack.com": "slack", "join.slack.com": "slack", "matrix.to": "matrix", "reddit.com": "reddit", "old.reddit.com": "reddit", "t.me": "telegram", "telegram.me": "telegram"}
DEAD_MARKERS = ["this link is no longer active", "invite link has expired", "this invite link is no longer valid", "page not found", "invitation link is invalid", "link is invalid"]

def detect_platform(url):
    """Guess the platform from a join URL. Discord invites are handled separately."""
    if not url: return None
    if invite_code(url): return "discord"
    host = re.sub(r"^https?://(www\.)?", "", url).split("/")[0].lower()
    for h, p in PLATFORM_HOSTS.items():
        if host == h or host.endswith("." + h): return p
    return None

def check_join_url(url):
    """Liveness check for non-Discord join links: HTTP status plus known 'expired invite' phrases."""
    if re.search(r"^https?://(www\.|old\.)?reddit\.com/", url or ""):
        return {"status": "unchecked", "error": "reddit blocks automated checks"}
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Chrome/120"})
        with urllib.request.urlopen(req, timeout=20) as r:
            body = r.read(300000).decode("utf-8", "replace").lower()
            if any(m in body for m in DEAD_MARKERS): return {"status": "dead", "error": "expired-invite page"}
            return {"status": "ok", "final_url": r.geturl()}
    except urllib.error.HTTPError as e:
        return {"status": "dead" if e.code in (404, 410) else "error", "error": f"HTTP {e.code}"}
    except Exception as ex:
        return {"status": "error", "error": str(ex)[:120]}

def mastodon_stats(url):
    """Public instance stats for a Mastodon server (no auth)."""
    host = re.sub(r"^https?://", "", url).split("/")[0]
    status, d = _get(f"https://{host}/api/v1/instance")
    if status == 200 and isinstance(d, dict):
        st = d.get("stats") or {}
        return {"members": st.get("user_count"), "description": (d.get("short_description") or d.get("description") or "")[:300]}
    return {}
