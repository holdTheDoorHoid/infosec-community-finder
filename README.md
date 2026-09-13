# Infosec Community Finder

A directory of cybersecurity, hacking, CTF, hardware, OSINT, career, local-group and conference **communities**, mostly on Discord and also on Slack, Matrix, IRC, forums, Reddit and Mastodon, with live member counts where the platform exposes them and a short questionnaire that matches beginners and intermediates to the right one.

**Live site:** https://holdTheDoorHoid.github.io/infosec-community-finder/

## What is here

| Path | What it is |
| --- | --- |
| `index.html`, `quiz.html`, `about.html`, `assets/` | The static site (no build step, no framework). GitHub Pages serves the repo root. |
| `data/communities.json` | The database. One object per community: platform, identity, live stats, editorial tags, location, sources, history. |
| `data/vocab.json` | The controlled vocabulary for categories, tags, activities, audiences and regions. |
| `scripts/refresh.py` | Re-checks every invite through Discord's public invite preview and updates counts and status. Run weekly by the GitHub Action. |
| `scripts/import_candidates.py` | Merges new candidate lists into the database, resolving invites and de-duplicating by Discord guild id. |
| `scripts/discordapi.py` | The tiny unauthenticated client both scripts share. |
| `research/` | Raw discovery output: seed lists, directory scrapes, agent findings. Kept for provenance. |
| `.github/workflows/refresh.yml` | Weekly refresh (Mondays 06:17 UTC) plus a manual "Run workflow" button. |
| `.github/ISSUE_TEMPLATE/` | Forms for submitting a server or reporting a dead link. |

## How the data is collected

1. **Discovery** – seed lists (user-supplied, LinkedIn/Medium/blog roundups, GitHub awesome-lists, Discord's own server directory, Disboard, top.gg and other listing sites), topical web research per cluster (CTF, creators and podcasts, open-source tools, hardware, blue team, careers, OSINT, affinity groups, appsec, adjacent hobbies, non-English communities), university clubs by region, every DEF CON Group on the official list plus hackerspaces and Meetup groups by region, a pass over every conference in the LSOH conference tracker plus DEF CON villages, a scan of the READMEs of 3,400 popular security repositories on GitHub, and a curated pass over non-Discord platforms (Slack workspaces with durable signup pages, Matrix/IRC/Mattermost, forums, subreddits, Mastodon instances).
2. **Resolution** – every Discord invite is looked up through `https://discord.com/api/v10/invites/<code>?with_counts=true`. That is public, needs no login, and returns the server name, description, approximate member and online counts, and feature flags (verified, partnered, discoverable). Duplicates collapse by guild id. Non-Discord links get a liveness check (HTTP status plus the known "invite expired" pages); Mastodon instances expose a public user count; Reddit blocks automated checks and is marked "not auto-checked".
3. **Reconnaissance** – each community gets a category, topic tags, an audience and beginner-friendliness rating, the activities you will find there, who runs it, where it is (region, country, state/province, city for local groups and conferences), language, and a plain-English summary. A second review pass checks each category group for consistency. These are editorial and can be wrong; fix them with a PR or an issue.
4. **Refresh** – weekly, automatically. Dead invites are flagged, not deleted, so they can be replaced.

Nobody joins servers on your behalf, ever. Only public information is used.

## Adding a server

Open a [submission issue](https://github.com/holdTheDoorHoid/infosec-community-finder/issues/new?template=submit-community.yml), or add a candidate file and run:

```bash
python3 scripts/import_candidates.py my_candidates.json
```

Candidate format: a JSON list of `{"name", "invite_url", "source_url", "category_hint", "notes", "confidence"}`.

## Running locally

```bash
python3 -m http.server 8080
```

then open http://localhost:8080/. (Opening `index.html` directly from disk will not load the JSON because browsers block `fetch` on `file://`.)

## What is excluded

Servers selling cheats, accounts or "hacking services"; anything illegal; NSFW servers; and invites that could not be verified as belonging to the community they claim.

## License

Code: MIT. Data in `data/`: CC BY 4.0.
