"""Build data.json for the JAPANESE MMA TRACKER web app from an export of the app's database.

usage: python3 scripts/export.py <export dir> data.json

<export dir> is what ArtifactData list/get with out_dir writes:
  events/*.json, fighters/*.json, results/*.json, videos/*.json (may be missing), meta/info.json
Each file is one document; its file name (without .json) is the document id.
The script refuses to write when the export looks broken, so a bad run never replaces good data.
"""
import json
import os
import re
import sys

DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def rows(src, name):
    d = os.path.join(src, name)
    if not os.path.isdir(d):
        return []
    out = []
    for f in sorted(os.listdir(d)):
        if f.endswith(".json"):
            doc = json.load(open(os.path.join(d, f), encoding="utf-8"))
            if not isinstance(doc, dict):
                raise SystemExit(f"{name}/{f}: not an object")
            out.append(dict({"id": f[:-5]}, **{k: v for k, v in doc.items() if k != "id"}))
    return out


def order(x):
    v = x.get("order")
    return (v if isinstance(v, (int, float)) else 0, x["id"])


def check(data):
    problems = []
    if len(data["events"]) < 3:
        problems.append("events: fewer than 3")
    if len(data["fighters"]) < 3:
        problems.append("fighters: fewer than 3")
    for e in data["events"]:
        if not isinstance(e.get("title"), str) or not e["title"]:
            problems.append(f"event {e['id']}: no title")
        if e.get("dateJst") is not None and not DATE.match(str(e["dateJst"])):
            problems.append(f"event {e['id']}: bad dateJst {e.get('dateJst')!r}")
        if e.get("category") not in ("abroad", "rizin", "notable", "domestic"):
            problems.append(f"event {e['id']}: bad category {e.get('category')!r}")
        if not isinstance(e.get("bouts", []), list):
            problems.append(f"event {e['id']}: bouts is not a list")
    for f in data["fighters"]:
        if not isinstance(f.get("name"), str) or not f["name"]:
            problems.append(f"fighter {f['id']}: no name")
    if not isinstance(data["meta"].get("updated"), str) or not DATE.match(data["meta"]["updated"]):
        problems.append("meta.updated is not YYYY-MM-DD")
    return problems


def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    src, dst = sys.argv[1], sys.argv[2]
    meta = json.load(open(os.path.join(src, "meta", "info.json"), encoding="utf-8"))
    data = {
        "events": sorted(rows(src, "events"), key=order),
        "fighters": sorted(rows(src, "fighters"), key=order),
        "results": sorted(rows(src, "results"), key=order, reverse=True),
        "videos": rows(src, "videos"),
        "meta": meta,
    }
    problems = check(data)
    if problems:
        raise SystemExit("not written:\n  " + "\n  ".join(problems))
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"wrote {dst}: {len(data['events'])} events, {len(data['fighters'])} fighters, {len(data['results'])} results, updated {meta['updated']}")


if __name__ == "__main__":
    main()
