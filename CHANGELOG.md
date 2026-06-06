# Changelog

All notable changes to RJA. Package follows semantic versioning; the **charter** is versioned
independently (currently v1.3).

## [2.0.0] — 2026-06-06

### Changed (breaking)
- **Replaced the scalar intensity model** (`√(A×S)×affect×agency×context`) with a disaggregated,
  relational, self-auditing model. There is no longer an aggregate `justice_score`; cross-dimension
  summation is prohibited (incommensurability, Fraser).
- Output is now: per-turn **justice dimensions** `{type, salience, valence, confidence}` +
  **relational configuration** + **vulnerability** object + **typed residue** + **audit trail**.

### Added
- **Layer 0 paradigm / Layer 1 Justice Charter**: the framebook is no longer "universal"; it is a
  declared, versioned normative grammar (provenance, privileged register, blind spots, aggregation bans).
- **Relational Configuration Engine** (Layer 3): three positioning levels (Bamberg), `relation_type`
  (gatekeeping, anticipatory_gatekeeping, dependency, multi_institutional_configuration,
  supportive_recognition, unspecified), `asymmetry_type`, `stance_primary` + `stance_flags`.
- **`vulnerability`** as an exposure/source object (no valence) — fixes the v1.1 valence-on-condition incoherence.
- **Residue** layer with a corpus-level charter-revision gate.
- **Reliability tooling** (`tools/reliability.py`): Cohen's κ + **PABAK** + prevalence (kappa-paradox aware).
- **Empirical reliability study** (`pilot/`): 2 blind LLM coders + 2 independent human coders, 10 turns,
  with the three-tier reliability profile and the LLM-overstates-reliability finding.
- **Coding kit** (`docs/`): quick reference, worked calibration examples, numbering-locked template.

### Charter history (independent track)
- charter v1.1 → v1.2 (vulnerability out of valence; relation types extended; dimensions primary/secondary;
  stance simplified; residue repetition gate) → v1.3 (rule-based primacy replaces the max-2 ranking;
  asymmetry tie-break; voice tightened).

### Deprecated
- `core/justice.py` (scalar `JusticeAnalyzer`) and `framebook_v3.1.yaml` — retained for provenance only.

## [3.1.0] — prior
- Scalar intensity model (FREEZE). Superseded by 2.0.0.
