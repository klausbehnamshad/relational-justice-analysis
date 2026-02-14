# relational-justice-analysis
A theory-driven, rule-based infrastructure for modeling social (in)justice as structured tension between normative claims and structural constraints in qualitative interview data.
GitHub README – Strategisch formuliert
Repository Title
Relational Justice Analysis (RJA)
A theory-driven, rule-based infrastructure for modeling social (in)justice in qualitative interview data
Kurzbeschreibung (oben im README)
Relational Justice Analysis (RJA) is a transparent, theory-driven analytical infrastructure for the systematic study of social (in)justice in qualitative interview data.
Instead of treating justice as a thematic category, RJA models injustice as structured tension between normative claims and structural constraints.
The system operationalizes sociological theory in reproducible, rule-based form and enables cross-context comparison (e.g., housing, care, migration, education, health).

Theoretical Foundation
RJA is based on three core premises:
1.	Justice is relational, not thematic.
It emerges where normative claim-frames (e.g., legitimacy, autonomy, solidarity) collide with structural frames (e.g., economization, bureaucracy, exclusion).
2.	Inequality is structured tension.
Social injustice becomes empirically observable as patterned co-occurrence between claims and constraints.
3.	Transparency over black-box modeling.
All analytical steps are rule-based, inspectable, and theoretically grounded.
The architecture integrates:
•	Discursive frame analysis
•	Agency modeling
•	Affective intensification
•	Structured conflict logic
•	Turn-level segmentation
•	Cross-interview comparability

Architecture Overview

The system consists of four layers:

1. Meta-Frame Layer
Universally defined analytical categories (e.g., OEKONOMISIERUNG, EXKLUSION_OTHERING, LEGITIMITAET_GERECHTIGKEIT).
These remain constant across contexts.

2. Overlay Layer
Context-specific refinements (e.g., housing, care, language regimes).
Overlay frames never distort the meta-level comparability.

3. Module Layer
Four analytical modules:
•	Narrative Structure (A)
•	Subject Positioning (B)
•	Discursive Framing (C)
•	Affective Dimension (D)

4. Justice Layer
The JusticeAnalyzer models injustice as:
Justice Intensity ∝
√(Normative Frame × Structural Frame)
× Agency Factor
× Affective Intensification
(normalized per text length)

This produces:
•	Justice Score
•	Justice Density
•	Dominant Tension Axis
•	Trajectory
•	Peak Turns

What This Infrastructure Enables
•	Transparent operationalization of sociological theory
•	Cross-interview comparability
•	Multilingual extensibility
•	Batch-level corpus comparison
•	Export for statistical analysis
•	Explicit tension modeling
•	Reproducible justice profiling

Why Rule-Based?
RJA deliberately avoids black-box machine learning.
The goal is not predictive classification but:
•	interpretability
•	epistemic traceability
•	theoretical accountability

All annotations can be traced back to:
•	rule_id
•	pattern
•	turn_id
•	matched_text

Example Output
The system generates:
•	Turn-level justice intensity
•	Structured tension axes (e.g., Fairness vs Market Logic)
•	Cross-module triangulation
•	Corpus-level justice comparison
•	Exportable CSV/JSON outputs

Intended Use
•	Comparative inequality research
•	Digital humanities
•	Computational social science
•	Theory-driven qualitative research
•	Methodological experimentation
Status
Version: v3.1
Current focus:
•	Multilingual extension
•	Corpus-level comparison
•	Sensitivity validation
•	Interrater comparison studies


(Preprint forthcoming.)

Klaus Behnam Shad
Social & Cultural Anthropology
Digital Humanities 

klaus.behnamshad@uni.lu 

Luxembourg Center for Contemporary and Digital History (C2DH)
University of Luxembourg

<img width="454" height="713" alt="image" src="https://github.com/user-attachments/assets/73971e05-b177-4600-908a-e4aaa3b83171" />
