# RJA v1.1 — Release Notes

## What changed and why

v1.1 replaces the **scalar intensity model** of v3.1
(`intensity = √(A_count × S_count) × affect × agency × context`, normalized /1000 chars)
with a **disaggregated, relational, self-auditing** model.

The diagnosed defect of v3.1 was **not measurement as such, but aggregation across
incommensurable dimensions**. A single number (e.g. 4.7) could not distinguish *what
kind* of injustice was at stake (Fraser), hid the analyst's standpoint (Haraway),
modelled intersectionality as multiplication (i.e. additively; Crenshaw), and
systematically missed the inarticulable (Fricker). v1.1 keeps RJA's strongest asset —
transparency / audit trail / "proposals not findings" — and pushes it one layer deeper.

## The five moves

1. **Score → profile.** No cross-dimensional aggregation. Each turn carries a
   per-dimension `{salience, valence, confidence}`. `valence` (affirmed / at_stake /
   denied / ambivalent) fixes the v3.1 defect where praising and despairing of an
   institution scored alike.
2. **Paradigm ≠ module.** *Relational Justice* is the governing paradigm (Layer 0),
   stated in the charter. The *Relational Configuration Engine* (Layer 3) is the
   operation. The word is no longer overloaded.
3. **Charter (Layer 1).** The framebook stops claiming "universal categories" and
   becomes a **declared, versioned, citable normative self-description**: theoretical
   provenance, privileged register, blind spots, allowed dimensions, relational
   vocabulary rules, and explicit aggregation prohibitions.
4. **Abductive loop, not pipeline.** Dimensions and relations co-revise (Layer 2 ↔ 3)
   to a fixed point; if automated, the revision history must be logged.
5. **Residue as finding.** Silence, vagueness, register-mismatch, affective overload
   are *typed* and recorded — and, when recurrent, feed a **charter-revision loop**
   (`residue → pattern → review → new type → next version`).

## What is intentionally deferred (no theory bloat)

- **Trajectory layer** (turn-to-turn dynamics: escalation, deflection, resignation)
  is NOT coded per turn in v1.1. Only a `relation_to_previous` anchor + `turn_id` are
  kept so the sequence layer can be assembled later *without re-coding*.
- **Corpus-level configuration harvesting** (which configurations recur, dominant
  tension axes across a corpus) is v1.2+.

## Migration from v3.1

- `core/justice.py` (the scalar `JusticeAnalyzer`) is **not deleted** but **demoted**:
  its per-axis counts may serve as a *navigation aid* only, never as "the justice level".
- New annotations use `core/relational.py` / `schema/rja_relational_v1.1.schema.json`.
- v3.1 outputs are not directly comparable to v1.1; treat the change as a new charter
  version (see below).

## Interoperability — the IMM-Core isomorphism

**Charter versions are to RJA what Implementation Profiles are to IMM-Core.** Both are
versioned specializations of a generic core; both achieve comparability *within* a
version and require **crosswalks** *across* versions. Concretely:

- RJA annotations should be stored as an **analytic metadata layer on IMM-Core records**.
  IMM-Core v2.0 provenance fields (`tool_id`, `tool_version`, `reviewed_by`,
  `reviewed_date`, `derivation`) are the direct attachment points for RJA output
  (`charter_version`, `coder_id`, `audit.revision_history`).
- The shared **multilingual / code-switching gap** (DE/FR/LB/EN/PT) is the same open
  problem in LuxOH-CMDI v2.0 and RJA; solve once, register in both.
- Export path: RJA annotations → **QDPX codesets** (via IMM-Core's QDPX crosswalk) →
  importable into MAXQDA / ATLAS.ti.

## Epistemic positioning (for the methods paper)

> RJA v1.1 is not a measurement instrument in the narrow positivist sense, but a
> theory-guided coding architecture with computational support, designed to make
> relational justice claims interpretable, auditable, and revisable.

## Files

```
justice_charter_v1.1.yaml              Layer 0 + 1: paradigm + charter
schema/rja_relational_v1.1.schema.json per-turn annotation schema (draft-07)
core/relational.py                     dataclasses (consistent with core/datamodel.py)
docs/coding_manual_v1.1.md             how to code one turn
docs/pilot_protocol_v1.1.md            reliability test design (≥2 blind coders)
tools/reliability.py                   per-field kappa / % agreement / collapse report
```

## Status

`draft`. Not frozen. The pilot (see `docs/pilot_protocol_v1.1.md`) must run on **real**
turns before this charter is declared usable; collapsing fields will be cut in v1.2.
