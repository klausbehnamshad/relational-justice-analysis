"""
core/base_module.py – Basis-Klasse für alle Analysemodule.

Jedes Modul (A, B, C, D) erbt von AnalyseModul und implementiert:
    - analyse(document) → schreibt Annotations ins Document
    - zusammenfassung(document) → gibt einen Turn-Level-Summary zurück
    - top_stellen(document, n) → gibt die N aufschlussreichsten Stellen zurück
"""

import re
from abc import ABC, abstractmethod
from .datamodel import Annotation


class AnalyseModul(ABC):
    """
    Abstrakte Basisklasse für Analysemodule.
    
    Jedes Modul:
        1. Hat einen Namen und eine Modul-ID
        2. Bekommt eine LanguageGate und ein Framebook
        3. Schreibt nur Annotations (nie Rohdaten)
        4. Jede Annotation hat eine nachvollziehbare Begründung (Audit Trail)
    """
    
    def __init__(self, modul_id, name, language_gate, framebook_section):
        """
        Args:
            modul_id: z.B. "A_narrative", "B_position"
            name: z.B. "Narrative Struktur"
            language_gate: LanguageGate-Instanz
            framebook_section: Der relevante Teil des Framebooks (Dict)
        """
        self.modul_id = modul_id
        self.name = name
        self.gate = language_gate
        self.framebook = framebook_section
    
    @abstractmethod
    def analyse(self, document):
        """
        Führt die Analyse durch und schreibt Annotations ins Document.
        
        Args:
            document: Document-Objekt
        
        Returns:
            Anzahl der erzeugten Annotations
        """
        pass
    
    @abstractmethod
    def zusammenfassung(self, document):
        """
        Gibt eine Turn-Level-Zusammenfassung zurück.
        
        Returns:
            Liste von Dicts (eine Zeile pro Turn)
        """
        pass
    
    def top_stellen(self, document, n=5):
        """
        Gibt die N Stellen mit der höchsten Annotation-Dichte zurück.
        
        Das sind die Stellen, die du zuerst im Original lesen solltest.
        """
        anns = document.get_annotations(modul=self.modul_id)
        
        # Gruppieren nach Turn
        turn_counts = {}
        turn_texts = {}
        for a in anns:
            tid = a.turn_id
            turn_counts[tid] = turn_counts.get(tid, 0) + 1
            if tid not in turn_texts:
                for t in document.turns:
                    if t.turn_id == tid:
                        turn_texts[tid] = t.text
                        break
        
        # Nach Dichte sortieren (Annotations pro 100 Wörter)
        ranked = []
        for tid, count in turn_counts.items():
            text = turn_texts.get(tid, "")
            n_woerter = max(len(text.split()), 1)
            dichte = (count / n_woerter) * 100
            
            # Welche Kategorien wurden geflaggt?
            kategorien = set(a.kategorie for a in anns if a.turn_id == tid)
            
            ranked.append({
                'turn_id': tid,
                'n_annotations': count,
                'dichte': round(dichte, 1),
                'kategorien': list(kategorien),
                'text_vorschau': text[:150] + '...' if len(text) > 150 else text,
            })
        
        ranked.sort(key=lambda x: -x['dichte'])
        return ranked[:n]
    
    # ---- Hilfsmethoden für alle Module ----
    
    def _pattern_search(
        self,
        text,
        kategorie,
        patterns,
        turn_id,
        satz="",
        regel_prefix="",
        flags=re.IGNORECASE,
    ):
        """
        Durchsucht Text mit Regex-Mustern und erzeugt Annotations.
        
        Zentrale Methode: Jeder Treffer wird als Annotation mit
        vollständigem Audit Trail gespeichert.
        
        Returns:
            Liste von Annotation-Objekten
        """
        annotations = []
        
        for i, pattern in enumerate(patterns):
            regel_id = f"{regel_prefix}_{i:02d}" if regel_prefix else f"{self.modul_id}_{kategorie}_{i:02d}"
            
            # Case-insensitive matching by default (do NOT lowercase the text),
            # so that matched spans preserve original casing for auditability.
            for match in re.finditer(pattern, text, flags):
                matched_text = match.group(0)
                
                ann = Annotation(
                    modul=self.modul_id,
                    kategorie=kategorie,
                    regel_id=regel_id,
                    pattern=pattern,
                    matched_text=matched_text,
                    matched_start=match.start(),
                    matched_end=match.end(),
                    satz=satz if satz else self._find_containing_sentence(text, match.start()),
                    turn_id=turn_id,
                    confidence="pattern",
                )
                annotations.append(ann)
        
        return annotations
    
    def _find_containing_sentence(self, text, position):
        """Findet den Satz, der die Position enthält (robust für . ! ? und Zeilenumbrüche)."""
        # Boundaries: punctuation or newline
        left = text.rfind('\n', 0, position)
        for p in ('.', '!', '?'):
            left = max(left, text.rfind(p, 0, position))
        start = left + 1 if left >= 0 else 0

        # Find nearest right boundary
        right_candidates = [
            i for i in (
                text.find('.', position),
                text.find('!', position),
                text.find('?', position),
                text.find('\n', position),
            )
            if i != -1
        ]
        end = min(right_candidates) + 1 if right_candidates else len(text)
        return text[start:end].strip()
    
    def _compute_density(self, n_markers, n_woerter):
        """Berechnet Marker-Dichte pro 100 Wörter."""
        if n_woerter == 0:
            return 0.0
        return round((n_markers / n_woerter) * 100, 1)
