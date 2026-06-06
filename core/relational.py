"""
core/relational.py — RJA v1.1 Relational Annotation Datenmodell.

Loest das skalare Intensitaetsmodell von v3.1 (core/justice.py:
intensity = sqrt(A*S)*affekt*agency*k) ab.

Grundprinzip (siehe justice_charter_v1.1.yaml):
    - KEIN aggregierter justice_score. Gerechtigkeitsdimensionen sind
      inkommensurabel und werden NIE ueber Dimensionen hinweg summiert.
    - Output = Justice Profile (disaggregiert, mit Valenz)
             + Relational Configuration (Bamberg: self/other/analyst)
             + typisiertes Residuum (Befund, kein Fehler)
             + Audit Trail (Beleg, Begruendung, Unsicherheit).
    - Relational Justice ist das Paradigma (Layer 0), die Relational
      Configuration Engine ist die Operation (Layer 3).

Konsistent mit core/datamodel.py: dataclasses + to_dict(), turn_id-Anker,
Annotationen sind prueffbar, versionierbar, exportierbar.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Any
from datetime import datetime

CHARTER_VERSION = "1.1"

# Erlaubte Werte (Spiegel des Charters; Validierung gegen JSON-Schema separat)
DIMENSIONS = ("recognition", "redistribution", "representation", "dignity",
              "voice", "access", "vulnerability", "justification")
SALIENCE = ("absent", "low", "medium", "high")
VALENCE = ("affirmed", "at_stake", "denied", "ambivalent")
CONFIDENCE = ("low", "medium", "high")
RELATION_TYPES = ("dependency", "gatekeeping", "peer", "custodial",
                  "contractual", "kinship_obligation", "unspecified")
ASYMMETRY_TYPES = ("justification_asymmetry", "recognition_asymmetry",
                   "voice_asymmetry", "resource_asymmetry",
                   "definitional_power", "none")
SPEAKER_STANCE = ("contesting", "enduring", "legitimating", "desiring", "ambivalent")
RESIDUE_TYPES = ("disfluency", "register_mismatch", "hermeneutical_gap",
                 "strategic_reticence", "affective_overload", "relation_type_misfit")


@dataclass
class JusticeDimension:
    """Eine aktivierte Gerechtigkeitsdimension. Wird NIE mit anderen summiert."""
    type: str          # DIMENSIONS
    salience: str      # SALIENCE
    valence: str       # VALENCE  -- Richtung: affirmed/at_stake/denied/ambivalent
    confidence: str    # CONFIDENCE (feldweise)

    def to_dict(self):
        return {"type": self.type, "salience": self.salience,
                "valence": self.valence, "confidence": self.confidence}


@dataclass
class Asymmetry:
    """Beziehungs-Schieflage MIT Richtung und Sprecher-Haltung."""
    type: str                  # ASYMMETRY_TYPES
    beneficiary: str = ""      # zu wessen Gunsten (wie erzaehlt)
    speaker_stance: str = "ambivalent"  # SPEAKER_STANCE (legitimating/desiring = Foucault/Berlant)

    def to_dict(self):
        return {"type": self.type, "beneficiary": self.beneficiary,
                "speaker_stance": self.speaker_stance}


@dataclass
class RelationalConfiguration:
    """Layer 3. Drei Positionierungsebenen getrennt halten (Bamberg)."""
    self_positioning: str = ""      # wie der Sprecher sich positioniert
    other_positioning: str = ""     # ERZAEHLTE Relation (Sprecher ueber Institution/Gegenueber)
    analyst_positioning: str = ""   # Rekonstruktion des Analysten, EXPLIZIT als solche markiert
    relation_type: str = "unspecified"   # RELATION_TYPES
    asymmetry: Asymmetry = field(default_factory=lambda: Asymmetry("none"))
    relation_residue: Optional[str] = None  # gesetzt, wenn kein relation_type passt

    def to_dict(self):
        return {"self_positioning": self.self_positioning,
                "other_positioning": self.other_positioning,
                "analyst_positioning": self.analyst_positioning,
                "relation_type": self.relation_type,
                "asymmetry": self.asymmetry.to_dict(),
                "relation_residue": self.relation_residue}


@dataclass
class Residue:
    """Befund, kein Fehler. MUSS typisiert sein (siehe Charter residue_policy)."""
    type: str                                  # RESIDUE_TYPES
    explanation: str = ""
    possible_charter_revision: Optional[str] = None  # speist Versionierungs-Loop

    def to_dict(self):
        return {"type": self.type, "explanation": self.explanation,
                "possible_charter_revision": self.possible_charter_revision}


@dataclass
class Audit:
    """Beleg, Begruendung, Unsicherheit. revision_history bei automatischer Schleife Pflicht."""
    evidence_quote: str = ""
    rationale: str = ""
    overall_uncertainty: str = "medium"   # CONFIDENCE -- turn-weite Gesamtunsicherheit (!= dimension.confidence)
    coder_id: str = ""
    revision_history: List[dict] = field(default_factory=list)

    def to_dict(self):
        return {"evidence_quote": self.evidence_quote, "rationale": self.rationale,
                "overall_uncertainty": self.overall_uncertainty,
                "coder_id": self.coder_id, "revision_history": self.revision_history}


@dataclass
class RelationalAnnotation:
    """Vollstaendige Turn-Annotation v1.1. Ein Objekt pro Befragten-Turn."""
    turn_id: int
    justice_dimensions: List[JusticeDimension] = field(default_factory=list)
    relational_configuration: RelationalConfiguration = field(default_factory=RelationalConfiguration)
    residue: List[Residue] = field(default_factory=list)
    audit: Audit = field(default_factory=Audit)
    doc_id: str = ""
    relation_to_previous: Optional[str] = None   # deferred trajectory anchor
    charter_version: str = CHARTER_VERSION
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self):
        return {
            "turn_id": self.turn_id,
            "doc_id": self.doc_id,
            "charter_version": self.charter_version,
            "relation_to_previous": self.relation_to_previous,
            "justice_dimensions": [d.to_dict() for d in self.justice_dimensions],
            "relational_configuration": self.relational_configuration.to_dict(),
            "residue": [r.to_dict() for r in self.residue],
            "audit": self.audit.to_dict(),
        }


def validate(annotation_dict: dict, schema_path: str) -> List[str]:
    """Optionale Validierung gegen das JSON-Schema. Gibt Liste von Fehlern zurueck (leer = ok)."""
    try:
        import json, jsonschema
    except ImportError:
        return ["jsonschema not installed (pip install jsonschema)"]
    with open(schema_path) as f:
        schema = json.load(f)
    v = jsonschema.Draft7Validator(schema)
    return [f"{list(e.path)}: {e.message}" for e in v.iter_errors(annotation_dict)]
