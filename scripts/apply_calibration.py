"""Apply calibration-review changes (from the calibration workflow) to data/communities.json."""
import json, sys, pathlib, datetime
ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "communities.json"
def main(path):
    d = json.loads(pathlib.Path(path).read_text()); d = d.get("result", d)
    db = json.loads(DATA.read_text()); by_id = {c["id"]: c for c in db["communities"]}
    n = h = dup = 0; today = datetime.date.today().isoformat()
    for ch in d.get("changes", []):
        c = by_id.get(ch["id"]);
        if not c: continue
        for f in ("category", "beginner_friendly", "tags", "audience", "summary", "language", "region"):
            if ch.get(f) not in (None, [], ""): c[f] = ch[f]
        if ch.get("hide"): c["hidden"] = True; c["exclude_reason"] = ch.get("exclude_reason") or ch.get("reason"); h += 1
        c.setdefault("review_log", []).append({"date": today, "reason": ch.get("reason")}); n += 1
    for dp in d.get("duplicates", []):
        c = by_id.get(dp["hide_id"]); k = by_id.get(dp["keep_id"])
        if c and k and c is not k:
            c["hidden"] = True; c["exclude_reason"] = f"duplicate of {k['name']}: {dp.get('reason','')}"; dup += 1
    DATA.write_text(json.dumps(db, indent=1, ensure_ascii=False) + "\n")
    print(f"changes applied={n} hidden={h} duplicates_hidden={dup}")
if __name__ == "__main__": main(sys.argv[1])
