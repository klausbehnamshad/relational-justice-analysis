# Relational Justice Analysis (RJA) — v2.0

**A theory-driven, rule-based and auditable infrastructure for reconstructing how justice
claims are *socially organized* in qualitative interview data — with an empirical reliability profile.**

[![DOI](https://zenodo.org/badge/DOI/REPLACE_WITH_NEW_DOI.svg)](https://doi.org/REPLACE_WITH_NEW_DOI)

---

## What changed in v2.0 (and why it is a major version)

v2.0 replaces the **scalar intensity model** of v3.1
(`intensity = √(A_count × S_count) × affect × agency × context`) with a **disaggregated,
relational, self-auditing** model. The old single score could not distinguish *what kind* of
injustice was at stake (Fraser), hid the analyst's standpoint (Haraway), modelled intersectionality
as multiplication, and missed the inarticulable (Fricker). v2.0 keeps RJA's strongest asset —
transparency and audit trail — and pushes it one layer deeper, then **tests it for reliability**.

> **Package version** is `v2.0.0`. The **charter** (the normative grammar) is independently
> versioned and currently at **v1.3** — charters are to RJA what implementation profiles are to a
> metadata core, so the two version numbers move separately by design.

## Core idea

Justice is **relationally constituted**: a claim emerges, is blocked, legitimated or displaced
*within a relation*. RJA therefore separates two questions:
- **Justice dimensions** — *what* is at stake (recognition, redistribution, representation, dignity, voice, access, justification).
- **Relational configuration** — *how* it is organized (who is positioned how; the relation type; the asymmetry; the speaker's stance).
- **Vulnerability** is modelled as an exposure/position object (not a scored dimension).
- **Residue** (silence, register-mismatch, hermeneutical gaps) is a *finding*, not noise.

There is, by design, **no aggregate "justice score"** — incommensurable dimensions are never summed.

## Architecture (v2.0)

```
Layer 0  Relational Justice Paradigm   — justice is relationally constituted (governs everything)
Layer 1  Justice Charter (v1.3)        — declared normative grammar: provenance, blind spots,
                                          admitted dimensions, relational vocabulary, aggregation bans
Layer 2  Justice Dimensions            — per-turn {type, salience, valence, confidence}, NEVER summed
Layer 3  Relational Configuration Engine— positioning (Bamberg L1–L3), relation_type, asymmetry, stance
Layer 4  Abductive loop                — dimensions ↔ relations co-revise; revisions logged
Layer 5  Output                        — disaggregated profile + relational configuration + residue + audit
```

## The empirical contribution: a measured reliability profile

RJA v2.0 ships with its own inter-coder reliability study (10 turns, two blind LLM coders + two
independent human coders, Cohen's κ + PABAK). The central finding on `relation_type`:

| comparison | κ |
|---|---|
| LLM ↔ LLM | 0.87 (inflated) |
| Human ↔ LLM | 0.64 |
| **Human ↔ Human** | **0.52** |

**Inter-LLM agreement overstated genuine human reliability by ≈ 0.35.** Inter-LLM agreement is
useful diagnostics but is *not* a substitute for human reliability testing.

Three reliability tiers (inter-human):
- **Reliable:** `stance_primary` (κ 0.80), `vulnerability` (presence/exposure κ 1.0), and the
  *direction/valence* of any dimension both coders name (κ 1.0).
- **Moderate:** `relation_type` (κ 0.52) — clear types agree; the gatekeeping/anticipatory/dependency
  mid-band splits coders.
- **Interpretive (not yet reliable):** `asymmetry_type` (κ 0.38) and *which* dimensions are selected.

Full analysis: `pilot/INTER_HUMAN_GATE_v1.3.md`.

## Repository layout (v2.0)

```
charter/         the Justice Charter (normative self-description)
schema/          rja_relational_v1.3.schema.json (current) + schema/archive/ (1.1, 1.2)
core/            relational.py — annotation dataclasses
tools/           reliability.py — κ + PABAK + prevalence inter-coder agreement
docs/            quick_reference, calibration_examples, CODER_README (the coding kit)
pilot/           coder codings (A/B = LLM, H1/H2 = human) + reliability findings
CHANGELOG.md · CITATION.cff · RELEASE_NOTES_v2.0.md
```

Legacy `core/justice.py` and `framebook_v3.1.yaml` remain in the repository history but are
**deprecated** (the scalar model); per-axis counts may serve only as a navigation aid, never as a score.

## Interoperability

Charter versions = implementation profiles: comparable *within* a version, crosswalked *across*.
RJA annotations are designed to sit as an analytic metadata layer on **IMM-Core** records
(provenance fields `tool_id`, `tool_version`, `reviewed_by` …) and to export as **QDPX** codesets
(via the IMM-Core crosswalk) into MAXQDA / ATLAS.ti.

## Epistemic status

> RJA is not a measurement instrument in the narrow positivist sense, but a theory-guided coding
> architecture with computational support, designed to make relational justice claims interpretable,
> auditable, and revisable.

## Status & roadmap (v1.4 charter)

Evidence-based next steps: ordered decision rules + worked examples for the relation mid-band and for
`asymmetry_type`; a single "central dimension" coding to fix the selection step; validation on real
(non-fictional) multilingual data (DE/FR/LB).

## Citation

See `CITATION.cff`. Released under the repository's existing license.
