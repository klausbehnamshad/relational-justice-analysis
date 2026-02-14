"""
modules/modul_b_position.py – Subjektpositionierung (Bamberg, Lucius-Hoene)

Analysiert:
    - Pronominalstruktur (ich/wir/man/die) – nur als Subjekt (via Spacy dep)
    - Agency (aktiv/passiv/moralisch) – als normierte Skala
    - Positionierungswechsel über den Interviewverlauf
"""

import re

from core.base_module import AnalyseModul
from core.datamodel import Annotation


class ModulPosition(AnalyseModul):
    """Modul B: Subjektpositionierung."""
    
    def __init__(self, language_gate, pronomen_config, agency_config):
        super().__init__(
            modul_id="B_position",
            name="Subjektpositionierung",
            language_gate=language_gate,
            framebook_section={'pronomen': pronomen_config, 'agency': agency_config},
        )
        self.pronomen_config = pronomen_config
        self.agency_config = agency_config
    
    def analyse(self, document):
        """
        Analysiert Pronomen und Agency pro Turn.
        Schreibt Annotations mit Kontext.
        """
        n_annotations = 0
        turns = document.get_befragte_turns()
        lang = self.gate.language
        
        # Pronomen-Muster für aktuelle Sprache
        pron_patterns = self.pronomen_config.get(lang, {})
        
        for turn in turns:
            # 1. Pronomen-Analyse
            for pron_label, pattern in pron_patterns.items():
                anns = self._pronomen_search(
                    turn.text, pron_label, pattern, turn.turn_id
                )
                for ann in anns:
                    document.add_annotation(ann)
                    n_annotations += 1
            
            # 2. Agency-Analyse
            for agency_type, config in self.agency_config.items():
                patterns = self.gate.get_patterns(config)
                anns = self._pattern_search(
                    turn.text, agency_type, patterns, turn.turn_id,
                    regel_prefix=f"agency_{agency_type.lower()}"
                )
                for ann in anns:
                    document.add_annotation(ann)
                    n_annotations += 1
            
            # 3. Spacy-basierte syntaktische Analyse (wenn verfügbar)
            nlp = self.gate.get_spacy()
            if nlp:
                spacy_anns = self._syntactic_agency(nlp, turn)
                for ann in spacy_anns:
                    document.add_annotation(ann)
                    n_annotations += 1
        
        return n_annotations
    
    def _pronomen_search(self, text, label, pattern, turn_id):
        """
        Sucht Pronomen, unterscheidet aber:
        - 'strong': Pronomen ist syntaktisches Subjekt
        - 'weak': Pronomen in anderer Position
        
        Ohne Spacy: alles als 'pattern' Confidence.
        Mit Spacy: syntaktische Prüfung.
        """
        annotations = []
        text_lower = text.lower()
        
        for match in re.finditer(pattern, text_lower):
            ann = Annotation(
                modul=self.modul_id,
                kategorie=f"PRON_{label}",
                regel_id=f"pron_{label.lower()}",
                pattern=pattern,
                matched_text=match.group(0),
                matched_start=match.start(),
                matched_end=match.end(),
                satz=self._find_containing_sentence(text, match.start()),
                turn_id=turn_id,
                confidence="pattern",
            )
            annotations.append(ann)
        
        return annotations
    
    def _syntactic_agency(self, nlp, turn):
        """
        Spacy-basierte Analyse: Wer ist grammatisches Subjekt?
        
        Unterscheidet:
        - ICH als Subjekt von aktivem Verb → AGENCY_SYNTACTIC_AKTIV
        - ICH als Subjekt von passivem/modalen Verb → AGENCY_SYNTACTIC_PASSIV
        - Andere Subjekte → Fremdpositionierung
        """
        doc = nlp(turn.text)
        annotations = []
        
        ich_varianten = {'ich', 'i', 'je', 'yo'}  # Mehrsprachig
        wir_varianten = {'wir', 'we', 'nous'}
        man_varianten = {'man', 'one', 'on'}
        
        for token in doc:
            # Nur Subjekte betrachten
            if token.dep_ not in ('sb', 'nsubj', 'nsubj:pass'):
                continue
            
            token_lower = token.text.lower()
            
            # Bestimme Kategorie
            if token_lower in ich_varianten:
                subj_type = "ICH"
            elif token_lower in wir_varianten:
                subj_type = "WIR"
            elif token_lower in man_varianten:
                subj_type = "MAN"
            else:
                subj_type = "ANDERE"
            
            # Prüfe ob aktiv oder passiv
            head = token.head
            is_passive = token.dep_ == 'nsubj:pass' or any(
                child.dep_ == 'auxpass' for child in head.children
            )
            is_modal = head.pos_ == 'AUX' or any(
                child.dep_ == 'aux' and child.text.lower() in 
                {'muss', 'müssen', 'kann', 'können', 'soll', 'sollte', 'must', 'can', 'should'}
                for child in head.children
            )
            
            if is_passive:
                voice = "PASSIV"
            elif is_modal:
                voice = "MODAL"
            else:
                voice = "AKTIV"
            
            kategorie = f"SYNTACTIC_{subj_type}_{voice}"
            
            # Satz finden
            satz = ""
            for sent in doc.sents:
                if sent.start <= token.i < sent.end:
                    satz = sent.text
                    break
            
            ann = Annotation(
                modul=self.modul_id,
                kategorie=kategorie,
                regel_id=f"spacy_subj_{subj_type.lower()}_{voice.lower()}",
                pattern=f"dep={token.dep_}, head={head.text}",
                matched_text=f"{token.text} → {head.text}",
                matched_start=token.idx,
                matched_end=token.idx + len(token.text),
                satz=satz,
                turn_id=turn.turn_id,
                confidence="syntactic",
            )
            annotations.append(ann)
        
        return annotations
    
    def zusammenfassung(self, document):
        """Turn-Level-Zusammenfassung der Positionierung."""
        turns = document.get_befragte_turns()
        rows = []
        
        for turn in turns:
            anns = document.get_annotations(modul=self.modul_id, turn_id=turn.turn_id)
            
            # Pronomen-Zählung
            pron_counts = {}
            for a in anns:
                if a.kategorie.startswith('PRON_'):
                    label = a.kategorie.replace('PRON_', '')
                    pron_counts[label] = pron_counts.get(label, 0) + 1
            
            # Agency-Zählung (Regex-basiert)
            agency_counts = {}
            for a in anns:
                if a.kategorie in ('AKTIV_HANDELND', 'ERLEIDEND_PASSIV', 'MORALISCH_REFLEKTIEREND'):
                    agency_counts[a.kategorie] = agency_counts.get(a.kategorie, 0) + 1
            
            # Syntaktische Agency (Spacy-basiert)
            syntactic = {}
            for a in anns:
                if a.kategorie.startswith('SYNTACTIC_'):
                    syntactic[a.kategorie] = syntactic.get(a.kategorie, 0) + 1
            
            # Dominante Agency
            dominant_agency = '-'
            if agency_counts:
                dominant_agency = max(agency_counts, key=agency_counts.get)
            
            rows.append({
                'turn_id': turn.turn_id,
                'n_woerter': turn.n_woerter,
                'pronomen': pron_counts,
                'agency_regex': agency_counts,
                'agency_syntactic': syntactic,
                'dominant_agency': dominant_agency,
                'agency_dichte': self._compute_density(
                    sum(agency_counts.values()), turn.n_woerter
                ),
            })
        
        return rows
