"""Apply reconnaissance results (from the recon workflow) to data/communities.json.

Usage: python3 scripts/apply_recon.py research/recon_results/*.json
Each input is a JSON list (or {"results": [...]}) of per-community editorial records keyed by "id".
Servers judged include=false are kept in the file but hidden from the site (hidden=true, exclude_reason).
"""
import json, sys, pathlib, datetime
ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "communities.json"
FIELDS = ["category","tags","audience","beginner_friendly","activities","summary","run_by","website","github","youtube","region","language","year_round","event","rules_note","red_flags"]

def main(paths):
    db = json.loads(DATA.read_text()); by_id = {c["id"]: c for c in db["communities"]}
    applied = hidden = missing = 0; today = datetime.date.today().isoformat()
    for p in paths:
        d = json.loads(pathlib.Path(p).read_text())
        if isinstance(d, dict): d = d.get("results") or d.get("result", {}).get("results") or []
        for r in d:
            c = by_id.get(r.get("id"))
            if not c: missing += 1; continue
            for f in FIELDS:
                if f in r: c[f] = r[f]
            c["recon_confidence"] = r.get("confidence"); c["recon_date"] = today
            if r.get("include") is False:
                c["hidden"] = True; c["exclude_reason"] = r.get("exclude_reason"); hidden += 1
            else:
                c.pop("hidden", None); c.pop("exclude_reason", None)
            applied += 1
    DATA.write_text(json.dumps(db, indent=1, ensure_ascii=False) + "\n")
    print(f"applied={applied} hidden={hidden} unknown_ids={missing}")

if __name__ == "__main__":
    main(sys.argv[1:])
