#!/usr/bin/env python3
"""
tools/reliability.py — Inter-coder agreement for RJA v1.3.

v1.3 uses a FLAT justice_dimensions list (no primary/secondary cap). 'Primary' is
derived = the subset with salience == 'high'. This tool reports presence agreement
on (a) the full listed set and (b) the derived high-salience (primary) subset, so we
can see whether rule-based primacy fixed the v1.2 ranking collapse.
Cohen's kappa + PABAK + prevalence, kappa-paradox aware. Works for human-vs-LLM too.

Usage: python tools/reliability.py coderA.json coderB.json --md report.md
"""
import json, argparse
from collections import defaultdict, Counter

DIMCATS = ("salience", "valence", "confidence")


def load(path):
    with open(path) as f:
        data = json.load(f)
    if isinstance(data, dict):
        data = list(data.values())
    return {int(a["turn_id"]): a for a in data}


def cohen_kappa(pairs):
    n = len(pairs)
    if n == 0:
        return (None, None, 0)
    labels = sorted({x for p in pairs for x in p}, key=str)
    po = sum(1 for a, b in pairs if a == b) / n
    ca, cb = defaultdict(int), defaultdict(int)
    for a, b in pairs:
        ca[a] += 1; cb[b] += 1
    pe = sum((ca[l] / n) * (cb[l] / n) for l in labels)
    kappa = 1.0 if pe == 1.0 else (po - pe) / (1 - pe)
    return (round(kappa, 3), round(po, 3), n)


def pabak(po):
    return None if po is None else round(2 * po - 1, 3)


def prevalence(pairs):
    if not pairs:
        return None
    c = Counter(x for p in pairs for x in p)
    return round(c.most_common(1)[0][1] / (2 * len(pairs)), 3)


def jaccard(a, b):
    a, b = set(a), set(b)
    return 1.0 if not a and not b else len(a & b) / len(a | b)


def grade(kappa, po):
    if kappa is None:
        return "n/a"
    score = max(kappa, pabak(po))
    v = ("STRONG  (keep)" if score >= 0.80 else "OK      (keep)" if score >= 0.60
         else "WEAK    (re-define)" if score >= 0.40 else "COLLAPSE (drop/split)")
    if pabak(po) - kappa >= 0.40:
        v += " [skew: trust PABAK]"
    return v


def dims(turn):
    return {d["type"]: d for d in turn.get("justice_dimensions", [])}


def collect(A, B):
    shared = sorted(set(A) & set(B))
    fields = defaultdict(list)
    residue_jacc, stanceflag_jacc = [], []
    for t in shared:
        a, b = A[t], B[t]
        rca, rcb = a.get("relational_configuration", {}), b.get("relational_configuration", {})
        fields["relation_type"].append((rca.get("relation_type"), rcb.get("relation_type")))
        fields["asymmetry_type"].append((rca.get("asymmetry_type"), rcb.get("asymmetry_type")))
        fields["stance_primary"].append((rca.get("stance_primary"), rcb.get("stance_primary")))
        fields["audit.overall_uncertainty"].append((a.get("audit", {}).get("overall_uncertainty"), b.get("audit", {}).get("overall_uncertainty")))
        da, db = dims(a), dims(b)
        for dim in set(da) | set(db):
            fields["dim_presence:" + dim].append((dim in da, dim in db))
            if dim in da and dim in db:
                for k in DIMCATS:
                    fields[f"dim:{dim}.{k}"].append((da[dim].get(k), db[dim].get(k)))
        # derived primary = salience high
        pa = {d["type"] for d in a.get("justice_dimensions", []) if d.get("salience") == "high"}
        pb = {d["type"] for d in b.get("justice_dimensions", []) if d.get("salience") == "high"}
        for dim in pa | pb:
            fields["primary(high)_presence:" + dim].append((dim in pa, dim in pb))
        va, vb = a.get("vulnerability"), b.get("vulnerability")
        fields["vuln_presence"].append((va is not None, vb is not None))
        if va and vb:
            fields["vuln.exposure"].append((va.get("exposure"), vb.get("exposure")))
            fields["vuln.salience"].append((va.get("salience"), vb.get("salience")))
        residue_jacc.append(jaccard([r["type"] for r in a.get("residue", [])],
                                     [r["type"] for r in b.get("residue", [])]))
        stanceflag_jacc.append(jaccard(rca.get("stance_flags", []), rcb.get("stance_flags", [])))
    return shared, fields, residue_jacc, stanceflag_jacc


def report(A, B, label="v1.3"):
    shared, fields, residue_jacc, stanceflag_jacc = collect(A, B)
    L = [f"# RJA {label} inter-coder reliability",
         f"\nShared turns: {len(shared)}  (A={len(A)}, B={len(B)})\n",
         "> Verdict uses max(kappa, PABAK). 'primary(high)' = dims a coder marked salience=high.\n",
         "| field | kappa | PABAK | % agree | prev | n | verdict |",
         "|---|---|---|---|---|---|---|"]
    rows = []
    for fname, pairs in fields.items():
        k, po, n = cohen_kappa(pairs)
        rows.append((k if k is not None else -9, fname, k, po, n, prevalence(pairs)))
    for _, fname, k, po, n, prev in sorted(rows, key=lambda r: r[0]):
        L.append(f"| {fname} | {k} | {pabak(po)} | {po} | {prev} | {n} | {grade(k, po)} |")
    if residue_jacc:
        L.append(f"\n**Residue-type set agreement (mean Jaccard):** {round(sum(residue_jacc)/len(residue_jacc),3)}")
    if stanceflag_jacc:
        L.append(f"**stance_flags set agreement (mean Jaccard):** {round(sum(stanceflag_jacc)/len(stanceflag_jacc),3)}")
    genuine = [fn for _, fn, k, po, _, _ in sorted(rows) if k is not None and max(k, pabak(po)) < 0.40]
    L.append("\n## Genuinely collapsing (max(kappa,PABAK) < 0.40)")
    L.append("\n" + ("\n".join(f"- {c}" for c in genuine) if genuine else "_none_"))
    return "\n".join(L)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("coderA"); ap.add_argument("coderB")
    ap.add_argument("--label", default="v1.3"); ap.add_argument("--md", default=None)
    args = ap.parse_args()
    out = report(load(args.coderA), load(args.coderB), args.label)
    print(out)
    if args.md:
        open(args.md, "w").write(out)
        print(f"\n[written: {args.md}]")
