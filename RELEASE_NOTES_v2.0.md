# RJA v2.0.0 — Release Notes

## Highlights
- **New model.** Scalar intensity → disaggregated relational model (no aggregate score; no cross-dimension summation).
- **Declared charter** (paradigm + normative grammar) replaces the "universal framebook".
- **Relational Configuration Engine** with Bamberg positioning, six relation types, asymmetry, stance.
- **Vulnerability** redesigned as an exposure object; **typed residue** with a charter-revision gate.
- **Reliability tooling + study**: κ + PABAK; two blind LLM coders and two independent human coders.

## The headline result
`relation_type` reliability: LLM↔LLM κ 0.87, Human↔LLM κ 0.64, **Human↔Human κ 0.52**.
Inter-LLM agreement overstated human reliability by ≈ 0.35. Reliable core: stance, vulnerability,
dimension direction. Interpretive residues: asymmetry typing, dimension selection.

## Upgrade / compatibility
- v3.1 scalar outputs are **not** comparable to v2.0; treat as a new charter version.
- `core/justice.py` and `framebook_v3.1.yaml` are deprecated (retained for provenance).

## Known limitations
- Reliability figures are on n = 10 turns of **fictional** test material; one human file required
  typo/structure repair (logged). Independent validation on real multilingual data is pending.

## Acknowledgements
Test transcripts are fictional, authored for method testing. Thanks to the two human coders (H1, H2).
