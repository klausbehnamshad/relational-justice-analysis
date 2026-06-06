# RJA v1.3 — Coder Quick Reference (one page)

You code each respondent (M) turn into one JSON object. You are not rating "how unjust" —
you reconstruct **what justice dimension is at stake** and **how the relation is organized**.
Fill every required field. Where unsure, code your best guess AND set confidence/uncertainty honestly.

## 1. justice_dimensions  (flat list — NO ranking, NO count limit)
List a dimension ONLY if its salience is **medium or high** (skip faint echoes). For each:
`{ "type": …, "salience": medium|high, "valence": …, "confidence": low|medium|high }`

types (pick those genuinely present):
- **recognition** — being seen/respected as a full subject
- **redistribution** — material share, resources, money, security
- **representation** — having a say in the rules/frame itself
- **dignity** — non-humiliation of the person
- **voice** — *can speak AND be heard/heeded in THIS relation* (see tight rule below)
- **access** — can reach a good/service/status/procedure
- **justification** — who owes reasons to whom

valence (direction): **affirmed** (granted/realized) · **at_stake** (claimed, open) · **denied** (violated/withheld) · **ambivalent**

> voice rule (tightened): code voice ONLY when the issue is *speaking and being heard*, or the *risk/consequence of speaking*. If M is merely silenced or her feeling dismissed, that is **dignity** or **recognition**, NOT voice. When torn between voice and recognition → choose recognition unless the turn is specifically about being heard.

## 2. vulnerability  (separate object — NO valence)  — or `null` if not present
`{ "exposure": acute|chronic|latent, "source": [legal|economic|affective|institutional|familial|health|mixed], "salience": low|medium|high, "confidence": … }`
- acute = immediate threat · chronic = sustained condition · latent = background risk.

## 3. relational_configuration
- **self_positioning** (text): how M casts herself.
- **other_positioning** (text): M's narrated framing of the institution/other (her view, not fact).
- **analyst_positioning** (text, optional): your reconstruction, marked as analytic.
- **relation_type** — pick the FIRST that applies, top to bottom:
  1. **supportive_recognition** — relation confers/realizes recognition or voice, asymmetry low/suspended.
  2. **multi_institutional_configuration** — simultaneous *contradictory* demands from 2+ uncoordinated institutions.
  3. **gatekeeping** — control over a *discrete* access decision (a decision point exists/is reported).
  4. **anticipatory_gatekeeping** — *self-regulation under expected evaluation*; no decision now, but past/future decisions shape conduct (managing tone/affect, "the right temperature").
  5. **dependency** — ongoing *structural reliance* where reliance itself is the point (e.g. relying on a child to read official letters).
  6. **unspecified** — no determinate relation (inward/systemic reflection, no interlocutor).
  - **Boundary cues (from calibration — see `calibration_examples_v1.3.md`):**
    - A *recurring pattern of soft refusals* to stated requests ("weiches Nein") = **gatekeeping** (decisions are reported), NOT anticipatory_gatekeeping.
    - **anticipatory_gatekeeping** needs the *absence* of a reported decision: rehearsal/preparation language ("vor … geübt", "ich habe mir gesagt", managing affect for an expected evaluator) is the cue.
    - **multi_institutional_configuration** needs *two or more explicitly named, contradictory* institutional demands *in the turn*. Affect-management for a single anticipated evaluator is anticipatory_gatekeeping, not multi-institutional.
- **asymmetry_type** — pick the operative mechanism; if more than one fits, use this tie-break ORDER (take the first that genuinely applies):
  1. **justification_asymmetry** — M must give reasons / prove worthiness that the other need not.
  2. **definitional_power** — the other defines the categories / "what counts as realistic" / who M is; M cannot contest the frame.
  3. **voice_asymmetry** — unequal ability to speak and be heeded / unequal consequences of speaking.
  4. **recognition_asymmetry** — unequal standing as a subject worthy of regard.
  5. **resource_asymmetry** — unequal material/resource control.
  6. **none**.
  - `beneficiary` (text): in whose favour it runs, as narrated.
- **stance_primary** — contesting (actively challenges) | accommodating (adapts/works within it, even if privately critical) | affirming (experiences it positively) | ambivalent.
  > rule: describing an injury *clearly* but NOT challenging it = **accommodating**. Code **contesting** only if there is an actual move against the asymmetry.
- **stance_flags** (optional list): enduring | legitimating | desiring | resigned | strategic.
- **relation_residue** (text or null): name any misfit with the relation types.

## 4. residue  (list; may be [])
`{ "type": …, "explanation": text, "charter_revision_candidate": true|false }`
types: disfluency | register_mismatch | hermeneutical_gap | strategic_reticence | affective_overload | relation_type_misfit.
(hermeneutical_gap needs a *collective* missing-vocabulary, not just individual inarticulacy. Not every silence is deep.)

## 5. audit  (required)
`{ "evidence_quote": "<verbatim words from the turn>", "rationale": "<1–2 sentences>", "overall_uncertainty": low|medium|high, "coder_id": "<your id, e.g. H1>" }`

Work one turn at a time. Read the interviewer's question for context but code only M's words.
