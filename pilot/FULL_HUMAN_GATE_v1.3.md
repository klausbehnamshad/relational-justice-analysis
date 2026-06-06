# RJA v1.3 — Full human-vs-LLM gate (all 10 turns)

First **complete, pilot-aligned** human coding (H1) of all 10 RJA-I turns, compared against the two
blind v1.3 LLM codings. This is the validity gate the whole exercise was building toward.

## Data repair (full transparency)
The submitted file had ~20 data-entry errors that broke JSON parsing and the controlled vocabulary.
All repairs were **typo/structure only** — no analytic choice was changed. Logged here:
- **Enum typos normalized to controlled vocab:** gatekeepingL→gatekeeping, gatekeepng→gatekeeping,
  anticipatory_gatekeepng→anticipatory_gatekeeping, justiciqation→justification,
  justifcation_asymmetry→justification_asymmetry, voice_asymetry→voice_asymmetry,
  "recognition assymetry"→recognition_asymmetry, accomodating→accommodating, eduring/endurng→enduring,
  instittional/instittional→institutional.
- **Structural JSON fixes:** missing commas between dimension fields/objects; stray leading bare words
  after `[` (e.g. `[dignity`, `[justification`, `[institutional`) treated as the intended type/source;
  leftover `"FILL"` removed from filled arrays; corrupted T1 audit block (turn text had bled into it)
  reconstructed from the coder's own rationale/uncertainty fields.
- **One genuine reconstruction (flagged):** T1 dimension had `type:"high"` with a stray `dignity`
  label; set to `type:dignity` (the coder's rationale explicitly says "Würdedimension"). Treat T1 with mild caution.
- **One real gap, NOT filled:** T2's `relational_configuration` was left unfilled (FILL/blank); kept as
  `null` (uncoded), so it counts as a non-match for relation_type — it is a blank, not a disagreement.

Repaired file: `coderH1.json` (valid JSON, 10 turns).

## Headline: relation_type recovered from collapse to OK-reliable

| field | LLM–LLM (v1.3) | **Human–LLM (full, 10 turns)** | verdict |
|---|---|---|---|
| **relation_type** | κ 0.87 | **κ 0.64 / 0.65**, 7/10 match both LLMs | OK (keep) |
| stance_primary | κ 1.0 | **κ 0.80** | STRONG |
| vulnerability (presence) | κ 1.0 | **κ 1.0** | STRONG |
| vulnerability (salience/exposure) | strong | **κ 0.62 / PABAK 0.8** | STRONG |
| recognition salience/valence | strong | **κ ~0.55–0.58** | OK |
| dignity/justification/representation valence (where both code) | strong | **κ 1.0** | STRONG |
| asymmetry_type | κ 0.64 | **κ 0.17–0.29** | COLLAPSE |
| dimension *presence* | mixed | **κ ~0** (systematic — see below) | needs reading |

### relation_type per turn (H1 / LLM-A / LLM-B)
7/10 agree with **both** LLMs (T1, T3, T4, T5, T7, T8, T10). The 3 non-matches:
- **T2** — human left relation uncoded (blank, not a disagreement).
- **T6** ("gute Migrantin"): human `dependency`, LLM-A `unspecified`, LLM-B `anticipatory_gatekeeping` —
  the two LLMs already disagreed here; T6 is hard for everyone.
- **T9** ("Wer bin ich"): human `dependency`, LLM `unspecified` — the inward/existential turn; the
  dependency-vs-unspecified boundary for reflection-without-interlocutor.

So of the **9 turns the human actually coded, 7 match (78%)**, and the 2 genuine misses are on turns
that are hard even LLM-vs-LLM or inherently indeterminate. Compared to the earlier boundary-only
collapse (0/3), this is the decisive confirmation that **the relational core is human-codable.**

## What survives the full human gate (robust across coder types)
relation_type (on clear turns), stance_primary, vulnerability (presence/exposure/salience), and the
**valence/direction** of every dimension where both coders list it. These are the publishable, reliable core.

## The two real residuals
1. **asymmetry_type (κ 0.17–0.29)** is genuinely the least reliable field — human and LLM diverge on
   *which mechanism* (e.g. recognition vs definitional_power vs justification). Needs the same
   ordered-decision-rule + worked-example treatment that fixed relation_type, OR demotion to a coarser set.
2. **Dimension presence κ ≈ 0 is a *style* difference, not noise.** The human is **parsimonious**
   (1–2 dimensions/turn); the LLM lists **3–4**. They agree on the central dimension(s) and diverge on
   how much secondary tail to add. The salience-based "primary" idea is right; the open question is
   whether to *cap* listing (e.g. central dimension + at most one secondary) to align human and machine.

## Honest caveats (unchanged)
- **n = 1 human.** The earlier "second" submissions (Achim2/H2) covered only T3–T5 and were identical,
  so we still lack an *independent two-human* full coding (no human–human κ over 10 turns yet).
- The human data was **repaired** (see log); T1 involved a reconstruction.
- Fictional material; LLM coders prompted with the rule. Construct validity still pending real data.

## Net / what this means for the paper
The arc is now empirically complete enough to state the central finding:
> Two blind LLM runs agreed near-perfectly on the relational core; that *overstated* reliability.
> But after worked-example calibration, an independent human coder, applying the same manual to all
> ten turns, reached **κ ≈ 0.65 on relation_type and ≥ 0.8 on stance and vulnerability** — i.e. the
> core is genuinely human-reliable, while fine asymmetry typing and the length of the secondary-dimension
> list remain interpretive. Inter-LLM agreement is necessary diagnostics but not sufficient evidence;
> the human gate both deflated and then substantially vindicated the method's core.

## Next (one clean step)
A **second independent human** codes all 10 turns (using the text-locked template + a JSON validator)
→ human–human κ over 10 turns. Then: give `asymmetry_type` worked examples and decide the
dimension-listing cap. That closes v1.3.
