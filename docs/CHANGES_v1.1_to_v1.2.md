# RJA v1.1 → v1.2 — what changed and why

v1.2 is a **hardening / slimming**, not a theoretical expansion. Every change is
driven by a measured collapse in the v1.1 pilot (`../v1.1/pilot/PILOT_FINDINGS_v1.1.md`).

| # | Change | Driven by pilot finding |
|---|---|---|
| 1 | `vulnerability` removed from the dimension/valence system; becomes its own object `{exposure: acute/chronic/latent, source[], salience, confidence}` — **no valence** | `vulnerability.valence` PABAK = −1.0 (coders coded affirmed vs denied 100% oppositely). Valence is incoherent for a position/exposure category. |
| 2 | `relation_type` redefined + extended: adds **anticipatory_gatekeeping**, **supportive_recognition**, **multi_institutional_configuration**; ordered decision rule added to manual | `relation_type` κ 0.24 / PABAK 0.0. Disagreement localized to T4–T8 (ongoing self-management → A:dependency vs B:gatekeeping) and multi-site turns both coders flagged as misfit. |
| 3 | Dimensions split into **primary (max 2)** + **secondary (max 2)**; a dimension may be primary only if explicitly articulated or forced by the central relational pattern | Secondary-dimension sprawl: core dims reliable, marginal dims drove most presence disagreement. |
| 4 | `speaker_stance` (4-way) → **stance_primary** (contesting/accommodating/affirming/ambivalent) + optional **stance_flags** (enduring/legitimating/desiring/resigned/strategic); decision rule: describing an injury without challenging it = accommodating | `speaker_stance` κ 0.55 (weak); contesting/enduring boundary unstable at T1, T7, T9. |
| 5 | `residue.charter_revision_candidate` is a **nomination only**; becomes a real charter change only via the **repetition gate** (≥3 independent turns or ≥2 independent interviews, not explained by existing categories) | The v1.1 codings nominated 8+ new categories; without a gate, residue inflates into endless dimensions. |
| 6 | Reliability tooling reports **PABAK + prevalence** alongside Cohen's κ | The pilot exposed the kappa paradox in the v1.1 harness (high agreement + skew → κ≈0). |

## Preserved on purpose
- **Bamberg positioning** (self/other/analyst) and the **audit trail** (evidence_quote, rationale, overall_uncertainty) — auditability is the method's core asset. v1.1's robust cores (`recognition`, `justification`, `asymmetry_type`) are unchanged.
- The paradigm/engine split, the charter, the abductive loop, the `turn_id` + `relation_to_previous` anchors.

## Still open (the real validity gate)
v1.2 is tested below on the **same fictional turns** as v1.1 (data held constant, schema changed → clean delta). This shows whether the fixes raise reliability; it does **not** establish construct validity. Real interview excerpts + a human second coder remain the required next step before the charter is declared usable.
