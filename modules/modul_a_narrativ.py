"""
modules/modul_a_narrativ.py – Narrative Struktur (Schütze, Ricoeur)

Analysiert:
    - Textsorten (Narration, Argumentation, Beschreibung) pro Satz
    - Sequenzen und Übergänge (N→A→A→N)
    - Prozessstrukturen (Handlungsschema, Verlaufskurve, Wandlung)
    - Top-N Wendepunkt-Kandidaten
"""

import re

from core.base_module import AnalyseModul
from core.datamodel import Annotation


class ModulNarrativ(AnalyseModul):
    """Modul A: Narrative Struktur."""
    
    def __init__(self, language_gate, textsorten_config, prozessstrukturen_config):
        super().__init__(
            modul_id="A_narrative",
            name="Narrative Struktur",
            language_gate=language_gate,
            framebook_section={'textsorten': textsorten_config, 
                              'prozessstrukturen': prozessstrukturen_config},
        )
        self.textsorten = textsorten_config
        self.prozessstrukturen = prozessstrukturen_config
    
    def analyse(self, document):
        """
        Führt die narrative Analyse durch:
        1. Klassifiziert jeden Satz nach Textsorte
        2. Erkennt Prozessstrukturen pro Turn
        3. Identifiziert Übergänge/Wendepunkte
        """
        n_annotations = 0
        turns = document.get_befragte_turns()
        
        for turn in turns:
            # 1. Textsorten pro Satz
            for satz in turn.saetze:
                ts, indikatoren = self._klassifiziere_textsorte(satz)
                if ts != 'UNBESTIMMT':
                    for pattern, matched in indikatoren:
                        ann = Annotation(
                            modul=self.modul_id,
                            kategorie=f"TS_{ts}",
                            regel_id=f"ts_{ts.lower()}",
                            pattern=pattern,
                            matched_text=matched,
                            matched_start=0,
                            matched_end=len(matched),
                            satz=satz,
                            turn_id=turn.turn_id,
                            confidence="pattern",
                        )
                        document.add_annotation(ann)
                        n_annotations += 1
            
            # 2. Prozessstrukturen pro Turn
            for struktur_name, config in self.prozessstrukturen.items():
                patterns = self.gate.get_patterns(config)
                anns = self._pattern_search(
                    turn.text, struktur_name, patterns, turn.turn_id,
                    regel_prefix=f"ps_{struktur_name.lower()}"
                )
                for ann in anns:
                    document.add_annotation(ann)
                    n_annotations += 1
        
        return n_annotations
    
    def _klassifiziere_textsorte(self, satz):
        """
        Klassifiziert einen Satz nach Textsorte.
        Returns: (textsorte_name, [(pattern, matched_text), ...])
        """
        satz_lower = satz.lower()
        best_ts = 'UNBESTIMMT'
        best_score = 0
        best_indikatoren = []
        
        for ts_name, config in self.textsorten.items():
            patterns = self.gate.get_patterns(config)
            treffer = []
            for pattern in patterns:
                for match in re.finditer(pattern, satz_lower):
                    treffer.append((pattern, match.group(0)))
            
            if len(treffer) > best_score:
                best_score = len(treffer)
                best_ts = ts_name
                best_indikatoren = treffer
        
        return best_ts, best_indikatoren
    
    def zusammenfassung(self, document):
        """Turn-Level-Zusammenfassung: Textsorten-Sequenz und Prozessstrukturen."""
        turns = document.get_befragte_turns()
        rows = []
        
        for turn in turns:
            # Textsorten-Sequenz
            sequenz = []
            for satz in turn.saetze:
                ts, _ = self._klassifiziere_textsorte(satz)
                sequenz.append(ts)
            
            # Prozessstrukturen
            ps_anns = document.get_annotations(modul=self.modul_id, turn_id=turn.turn_id)
            ps_found = set()
            for a in ps_anns:
                if not a.kategorie.startswith('TS_'):
                    ps_found.add(a.kategorie)
            
            # Übergänge zählen
            transitions = 0
            for i in range(1, len(sequenz)):
                if sequenz[i] != sequenz[i-1] and sequenz[i] != 'UNBESTIMMT' and sequenz[i-1] != 'UNBESTIMMT':
                    transitions += 1
            
            rows.append({
                'turn_id': turn.turn_id,
                'n_saetze': len(turn.saetze),
                'sequenz': ' → '.join(sequenz),
                'sequenz_kurz': ''.join(s[0] for s in sequenz),  # N→A→B wird "NAB"
                'n_transitions': transitions,
                'prozessstrukturen': ', '.join(ps_found) if ps_found else '-',
                'n_annotations': len(ps_anns),
            })
        
        return rows
    
    def wendepunkt_kandidaten(self, document, n=5):
        """
        Identifiziert die Top-N Wendepunkt-Kandidaten.
        
        Ein Wendepunkt ist eine Stelle, an der:
        - Die Textsorte wechselt (N→A oder A→N)
        - Prozessstrukturen sich überlagern
        - Die Annotation-Dichte hoch ist
        """
        turns = document.get_befragte_turns()
        kandidaten = []
        
        for turn in turns:
            score = 0
            reasons = []
            
            # Textsorten-Wechsel
            sequenz = []
            for satz in turn.saetze:
                ts, _ = self._klassifiziere_textsorte(satz)
                sequenz.append(ts)
            
            transitions = 0
            for i in range(1, len(sequenz)):
                if sequenz[i] != sequenz[i-1] and 'UNBESTIMMT' not in (sequenz[i], sequenz[i-1]):
                    transitions += 1
            
            if transitions > 0:
                score += transitions * 2
                reasons.append(f"{transitions} Textsorten-Wechsel")
            
            # Prozessstruktur-Marker
            ps_anns = [a for a in document.get_annotations(modul=self.modul_id, turn_id=turn.turn_id)
                       if not a.kategorie.startswith('TS_')]
            
            ps_types = set(a.kategorie for a in ps_anns)
            if len(ps_types) > 1:
                score += len(ps_types) * 3  # Überlagerung = stark
                reasons.append(f"Überlagerung: {', '.join(ps_types)}")
            elif len(ps_types) == 1:
                score += 1
                reasons.append(f"Prozessstruktur: {list(ps_types)[0]}")
            
            if 'VERLAUFSKURVE' in ps_types:
                score += 2  # Extra-Gewicht für Verlaufskurve
                reasons.append("⚡ Verlaufskurve erkannt")
            
            if score > 0:
                kandidaten.append({
                    'turn_id': turn.turn_id,
                    'score': score,
                    'reasons': reasons,
                    'sequenz': ' → '.join(sequenz),
                    'text_vorschau': turn.text[:200] + '...' if len(turn.text) > 200 else turn.text,
                })
        
        kandidaten.sort(key=lambda x: -x['score'])
        return kandidaten[:n]
