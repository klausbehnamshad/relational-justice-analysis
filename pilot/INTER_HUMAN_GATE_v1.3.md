# RJA v1.3 — The real validity gate: two independent human coders (10 turns)

H1 and H2 independently coded all 10 RJA-I turns (v1.3, pilot-aligned numbering, both checked:
T1 = Jobcenter). H2's file needed only comma/fence repair (no analytic change). This is the
inter-human reliability the whole project was building toward — the test inter-LLM agreement
cannot substitute for.

## The headline number, across all three comparison types

| relation_type (the central field) | κ | reading |
|---|---|---|
| LLM ↔ LLM | **0.87** | two runs of one model applying the rule — inflated |
| Human ↔ LLM | **0.64** | the LLM follows the explicit rule |
| **Human ↔ Human** | **0.52** | **the true reliability** |

> **Inter-LLM agreement overstated genuine (human) reliability by ≈ 0.35 on the central field.**
> This is the project's sharpest methodological contribution: a clean, quantified demonstration
> that inter-LLM agreement is necessary diagnostics but **not** a proxy for human reliability —
> and the gap sits exactly in the interpretively rich field.

## Three reliability tiers (inter-human, the honest verdict)

**TIER 1 — robust across two independent humans (publishable as reliable):**
- `stance_primary` κ 0.80
- `vulnerability`: presence κ 1.0, exposure κ 1.0, salience PABAK 0.8
- **valence / direction** of any dimension both coders name: κ 1.0 (recognition, dignity, justification, voice, representation)
→ The method reliably captures: the speaker's *stance*, the *vulnerability/exposure* profile, and the
*direction* (denied / affirmed / at-stake) of whichever justice dimensions are in play.

**TIER 2 — moderate, usable with adjudication:**
- `relation_type` κ 0.52 (6/10; of 9 turns both coded, 6 agree). The *clear* relation types agree
  perfectly across both humans AND the LLM — T1, T5, T7, T8, T10 (discrete gatekeeping,
  multi_institutional, supportive_recognition). Disagreement clusters entirely in the
  **gatekeeping ↔ anticipatory_gatekeeping ↔ dependency ↔ unspecified** mid-band (T3, T4, T9).
  Notably on T6 the two humans agreed (`dependency`) where the LLM diverged (`unspecified`) — so
  here human–human beat human–LLM.

**TIER 3 — not yet reliable (interpretive):**
- `asymmetry_type` κ 0.38 — least reliable even human–human; the "which mechanism" judgment.
- **dimension presence / selection** κ ≈ 0 — both humans are parsimonious (1–2 dims/turn) but pick
  *different* ones. They agree on *direction* once a dimension is chosen (Tier 1), but not on *which*
  dimensions are present. The selection step, not the rating step, is the weak link.

## What this means
The method has a genuine, demonstrable reliable core (stance, vulnerability, dimensional direction),
a moderate relational core (the clear relation types), and two honestly-interpretive residues
(asymmetry typing, dimension selection). That is a defensible, publishable profile — *because* it is
specific about what is reliable and what is not, validated against real independent human coders.

## Concrete v1.4 targets (now evidence-based)
1. **Relation mid-band:** give gatekeeping / anticipatory_gatekeeping / dependency / unspecified the
   same ordered-decision-rule + worked-example treatment that already pushed the boundary turns to
   agreement; T3, T4, T9 are the training cases.
2. **asymmetry_type:** either an ordered tie-break rule with examples, or collapse to a coarser set
   (e.g. 3 classes) — κ 0.38 says the current 6-way set is too fine to code reliably.
3. **dimension selection:** the rating is reliable, the selection is not → consider coding a single
   *central* dimension (κ would likely rise) plus an optional unranked list, rather than asking
   coders to choose "primary" among several.

## Caveats (unchanged honesty)
- Fictional material; H1's file required typo/structure repair (logged in FULL_HUMAN_GATE_v1.3.md);
  H1 left T2's relation blank. Two coders is the minimum for inter-human κ — more would tighten the estimate.
- These κ are on n = 10 turns; treat as indicative, not definitive, magnitudes.

## Status
The empirical arc is complete: v1.1 (scalar, three collapses) → v1.2 (two fixed, one displaced) →
v1.3 (displaced one fixed) → calibration (boundary turns converge) → **full inter-human gate
(reliable core demonstrated, residues named)**. The method is now characterized, not just asserted.
