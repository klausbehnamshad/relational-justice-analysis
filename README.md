# Relational Justice Analysis (RJA)

**A theory-driven, rule-based infrastructure for modeling social (in)justice as structured tension between normative claims and structural constraints in qualitative interview data.**

---

## Core Idea

RJA does not treat justice as a thematic category to be coded. Instead, it models social (in)justice as a **relational pattern**: the structured tension between what people claim *should be* (aspiration frames) and what they experience as blocking constraints (structural frames).

This renders (in)justice empirically observable, computationally traceable, and systematically comparable across contexts.

---

## Theoretical Foundation

RJA integrates discourse analysis, recognition theory, and systems theory into a single operational framework:

| Premise | Implication |
|---------|-------------|
| Justice is **relational**, not thematic | It emerges where aspiration frames collide with structural frames |
| Inequality is **structured tension** | Observable as patterned co-occurrence of claims and constraints |
| Transparency over black-box modeling | All analytical steps are rule-based, inspectable, and traceable |

Theoretical anchors include Foucault (discourse/normalization), Goffman (framing), Honneth (recognition), Fraser (redistribution/recognition), Boltanski & Thévenot (orders of justification), and Entman (frame salience).

---
## Epistemic Status

RJA does not replace qualitative interpretation.
Rather, it generates structured, theory-informed analytical proposals that require interpretive validation by the researcher.



## Architecture

```
┌─────────────────────────────────────────────────┐
│  Layer 4: JusticeAnalyzer                       │
│  Tension profiles from A×S frame relations      │
├─────────────────────────────────────────────────┤
│  Layer 3: Analysis Modules                      │
│  A: Narrative  B: Agency  C: Frames  D: Affect  │
├─────────────────────────────────────────────────┤
│  Layer 2: Overlays (optional)                   │
│  Context-specific extensions (housing, care...)  │
├─────────────────────────────────────────────────┤
│  Layer 1: Meta-Frame Architecture               │
│  Universal, theory-driven categories             │
└─────────────────────────────────────────────────┘
```

### Layer 1: Meta-Frames (universal, constant across projects)

| Type | Frames | Role |
|------|--------|------|
| **Aspiration (A)** | `LEGITIMITAET_GERECHTIGKEIT`, `AUTONOMIE_SELBSTBESTIMMUNG`, `SOLIDARITAET_GEMEINSCHAFT` | What *should* be |
| **Structural (S)** | `OEKONOMISIERUNG`, `BUEROKRATISCHE_ORDNUNG`, `EXKLUSION_OTHERING`, `INSTITUTIONELLE_LOGIK` | What *blocks* |
| **Context (K)** | `VULNERABILITAET` (amplifying), `NORMALISIERUNG` (dampening), `OEFFENTLICHER_DISKURS` (neutral) | Moderators |

### Layer 2: Overlays

Project-specific extensions that enrich meta-frames with additional indicators without breaking cross-project comparability. Overlay frames are tracked as contextual tags, never as scoring components.

### Layer 3: Analysis Modules

| Module | Domain | Theoretical Basis |
|--------|--------|-------------------|
| **A** – Narrative Structure | Text types, process structures, turning points | Schütze, Ricoeur |
| **B** – Subject Positioning | Agency, pronoun usage, positioning | Bamberg, Lucius-Hoene |
| **C** – Discursive Framing | Frames, topoi, co-occurrence, trajectory | Foucault, Goffman, Entman |
| **D** – Affective Dimension | Emotional markers, intensification, ambivalence | Ahmed, Massumi |

### Layer 4: JusticeAnalyzer

Models (in)justice intensity per turn:

```
intensity = √(A_count × S_count) × affect_mult × agency_mult × context_mult
```

Where:
- `A_count` / `S_count` = aspiration and structural frame annotations in the turn
- `affect_mult` = affective density (capped at 1.25)
- `agency_mult` = 1.2 if passive/suffering, 1.1 if morally reflective, 1.0 otherwise
- `context_mult` = 1.10 if vulnerability present, 0.90 if normalization present

All values are normalized per 1,000 characters for cross-interview comparability.

---

## Output

The system produces:

- **Turn-level tension profiles** with intensity scores and dominant tension axes
- **Interview-level justice profiles**: score, density, trajectory, peak turns
- **12 tension axes** (3 A-frames × 4 S-frames), e.g., *Fairness vs. Market Logic*, *Rights vs. Exclusion*
- **Analytical claims**: co-occurrence, trajectory shifts, dominance, frame tensions
- **Full audit trail**: every annotation traceable to rule ID, pattern, matched text, and turn
- **Exportable outputs**: CSV, JSON, XLSX

---

## Quick Start

```bash
# Clone
git clone https://github.com/klausbehnamshad/relational-justice-analysis.git
cd relational-justice-analysis

# Environment
conda env create -f environment.yml
conda activate rja
python scripts/setup_nltk.py

# Run
jupyter notebook notebooks/hauptnotebook.ipynb
# → Execute cells 1–3, then inspect results below
```

---

## Project Structure

```
relational-justice-analysis/
├── config/
│   └── framebook_v3.1.yaml        # Meta-Frame definitions + classification
├── overlays/
│   └── housing_lux.yaml           # Example overlay (Housing/Luxembourg)
├── core/
│   ├── framebook.py               # Framebook loader with overlay support
│   ├── justice.py                 # JusticeAnalyzer
│   ├── integration.py             # Cross-module integrator
│   ├── datamodel.py               # Document/Corpus/Annotation model
│   ├── language.py                # LanguageGate (multilingual pattern dispatch)
│   └── export.py                  # CSV/JSON/XLSX export
├── modules/
│   ├── modul_narrativ.py          # Module A: Narrative Structure
│   ├── modul_position.py          # Module B: Subject Positioning
│   ├── modul_diskurs.py           # Module C: Discursive Framing
│   └── modul_affekt.py            # Module D: Affective Dimension
├── notebooks/
│   └── hauptnotebook.ipynb        # Main analysis notebook
├── transkripte/
│   └── Example Interview Transcript.txt
├── output/                        # Generated exports
├── turn_splitter.py
├── diagnose.py
├── environment.yml
└── README.md
```

---

## Why Rule-Based?

RJA deliberately avoids black-box machine learning. RJA prioritizes epistemic accountability over predictive optimization.
The goal is not predictive classification but:

- **Interpretability** – every annotation is human-readable
- **Epistemic traceability** – every output links to specific rules, patterns, and text
- **Theoretical accountability** – the framebook *is* the codebook; changing a theory changes the rules
- **Reproducibility** – same framebook + same transcript = same results

This makes RJA suitable for contexts where methodological transparency is non-negotiable: peer-reviewed research, policy analysis, and interdisciplinary collaboration.

---

## Intended Use

- Comparative inequality and justice research
- Migration and integration studies
- Digital humanities
- Computational social science
- Theory-driven qualitative research
- Methodological experimentation and validation

---

## Multilingual Support

Currently supported: **German, English, French**

Planned: Spanish, Portuguese, Italian, Arabic

The framebook architecture supports any language through the indicator system — each frame carries language-specific regex patterns, dispatched via the LanguageGate.

---

## Roadmap

| Phase | Focus | Status |
|-------|-------|--------|
| 1 | Meta-Frame architecture + Justice model | ✅ Complete |
| 2 | Multilingual extension (ES, PT, IT, AR) | 🔄 In progress |
| 3 | Corpus-level comparison + batch analysis | 📋 Planned |
| 4 | Interrater validation + sensitivity analysis | 📋 Planned |

---

## Citation

If you use RJA in your research, please cite:

```
Behnam Shad, K. (2026). Relational Justice Analysis: A theory-driven infrastructure
for modeling social (in)justice in qualitative interview data. [Software].
https://github.com/klausbehnamshad/relational-justice-analysis
```

---

## License

This project is licensed under the MIT License.
See the LICENSE file for details.


---

## Author

**Klaus Behnam Shad, PhD**
Social & Cultural Anthropology
Digital Humanities & Computational Social Research

klaus.behnamshad@uni.lu

University of Luxembourg

---

*Every algorithmic annotation is an epistemic proposal, not a finding.*
