# RJA v1.1 → v1.2 — reliability delta

Same 10 turns, same coder design (two blind LLM runs, fictional data — caveats unchanged),
schema changed. So differences are attributable to the schema, not the data.

## The targeted fixes: 2 of 3 collapses decisively repaired

| field | v1.1 | v1.2 | verdict |
|---|---|---|---|
| **relation_type** | κ 0.242 / PABAK 0.0 — COLLAPSE | **κ 1.000** — STRONG | ✅ fixed |
| **vulnerability** | `vulnerability.valence` κ 0.0 / **PABAK −1.0** (100% opposite) — COLLAPSE | removed valence; `vuln_presence` **κ 1.0**, `vuln.exposure` PABAK 0.78, `vuln.salience` κ 0.77 — OK/STRONG | ✅ fixed |
| **speaker stance** | `speaker_stance` κ 0.545 — WEAK | `stance_primary` **κ 0.815** — STRONG | ✅ improved |

The `relation_type` repair is the important one: for an architecture centred on *relation*, the relational core went from the single worst field to perfect agreement. The cause was the ordered decision rule + the three new types — **`anticipatory_gatekeeping` absorbed exactly the T4–T8 turns that split the coders in v1.1** (both now code T4/T5 as anticipatory_gatekeeping, T7/T8 as multi_institutional_configuration, T10 as supportive_recognition). The disagreement was a definitional gap, and closing the definition closed the gap.

Removing valence from vulnerability eliminated the ontological-mismatch field entirely; the exposure/source object is reliable.

## The new problem: the max-2 cap moved sprawl into *ranking*

| field | v1.2 | reading |
|---|---|---|
| primary_presence: recognition | κ −0.235 | coders agree recognition is *present* but disagree whether it makes the **top-2 primary** slot |
| primary_presence: voice | κ −0.30 | same |
| primary_presence: dignity | κ 0.0 | same |

v1.1's "how many dimensions to list" noise became v1.2's "which two are *primary*" noise. Forcing a hard rank-into-exactly-2 is itself a low-reliability judgment: both coders see recognition + dignity + justification + voice in a turn, but A elevates {recognition, justification} while B elevates {recognition, dignity}. The *merged* presence (primary+secondary) is fine (dignity PABAK 0.25→ via %0.625; voice PABAK 0.43) — it is the **ranking** that is unreliable, not the detection.

## Other movements
- `asymmetry_type` slipped 0.718 → 0.565 (still WEAK, not collapse): definitional_power / recognition_asymmetry / justification_asymmetry overlap needs a decision rule like relation_type got.
- `voice` is the chronically weakest dimension across both versions (confidence κ −0.43, salience/valence weak whenever both list it). Candidate for a tighter definition or a merge in this domain.
- Robust across both versions: recognition (valence/salience), justification (all), dignity.valence, residue-type agreement (Jaccard 0.63→ stable), audit.overall_uncertainty (PABAK 0.80).

## Verdict
The diagnostic→fix loop works: targeted, measured changes moved the two worst fields from collapse to strong **under identical conditions**. That is exactly the evidence a methods paper needs — not "it works," but "we predicted the failure points, fixed them, and the fix is measurable."

But v1.2 is **not** done: the primary/secondary cap is the wrong instrument. The detection of dimensions is reliable; forcing a 2-slot ranking is not.

## v1.3 recommendation (one change, then re-test)
Replace the hard max-2 *ranking* with a **rule-based** primary criterion, removing coder discretion:
- A dimension is **primary** iff `salience == high` (and explicitly articulated); everything else is secondary. No count cap.
- This keeps the anti-sprawl goal (high bar for primary) but makes "primary" a *consequence* of the salience call (which is reliable: recognition.salience κ 1.0) rather than a separate ranking judgment.
- Alternatively: a single `central_dimension` (max 1 — easier to agree than top-2) + a flat list.

Also give `asymmetry_type` a short ordered decision rule (as relation_type got), and tighten or merge `voice`.

**Still the real gate:** human second coder on real (non-fictional) excerpts. The LLM–LLM / fictional caveats are unchanged; relation_type 1.0 partly reflects coders following an explicit rule mechanically and will be lower with a human on messy data. The valid signal is the *relative* movement under constant conditions.
