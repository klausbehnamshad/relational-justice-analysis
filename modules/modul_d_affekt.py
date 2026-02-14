"""
modules/modul_d_affekt.py – Affektive Dimension (Ahmed, Massumi, Emotionssoziologie)

Analysiert nicht "positiv/negativ", sondern:
    - Affektive Intensität (Marker-Dichte)
    - Affektive Verdichtungsstellen (wo überlagern sich mehrere Marker?)
    - Ambivalenz (widersprüchliche Affektmarker)
    - Körperliche Verweise als Affektindikatoren

Output: Stellen affektiver Aufladung + Begründung (kein "Score")
"""

import re

from core.base_module import AnalyseModul


class ModulAffekt(AnalyseModul):
    """Modul D: Affektive Dimension."""
    
    def __init__(self, language_gate, affekt_config):
        super().__init__(
            modul_id="D_affekt",
            name="Affektive Dimension",
            language_gate=language_gate,
            framebook_section=affekt_config,
        )
        self.affekt_dimensionen = affekt_config
    
    def analyse(self, document):
        """Affektmarker erkennen und als Annotations schreiben."""
        n_annotations = 0
        turns = document.get_befragte_turns()
        
        for turn in turns:
            for dim_name, config in self.affekt_dimensionen.items():
                patterns = self.gate.get_patterns(config)
                anns = self._pattern_search(
                    turn.text, dim_name, patterns, turn.turn_id,
                    regel_prefix=f"affekt_{dim_name.lower()}"
                )
                for ann in anns:
                    document.add_annotation(ann)
                    n_annotations += 1
        
        return n_annotations
    
    def zusammenfassung(self, document):
        """
        Turn-Level-Zusammenfassung.
        
        Gibt Marker-Dichte und Marker-Typen zurück (nicht einen Score!).
        """
        turns = document.get_befragte_turns()
        rows = []
        
        for turn in turns:
            anns = document.get_annotations(modul=self.modul_id, turn_id=turn.turn_id)
            
            # Zählung pro Dimension
            dim_counts = {}
            for a in anns:
                dim_counts[a.kategorie] = dim_counts.get(a.kategorie, 0) + 1
            
            n_marker = len(anns)
            dichte = self._compute_density(n_marker, turn.n_woerter)
            
            # Marker-Typen (welche Dimensionen sind aktiv?)
            aktive_dimensionen = [d for d, c in dim_counts.items() if c > 0]
            
            rows.append({
                'turn_id': turn.turn_id,
                'n_woerter': turn.n_woerter,
                'n_marker': n_marker,
                'marker_dichte': dichte,
                'dimensionen': dim_counts,
                'aktive_dimensionen': aktive_dimensionen,
                'n_dimensionen_aktiv': len(aktive_dimensionen),
            })
        
        return rows
    
    def verdichtungsstellen(self, document, n=5):
        """
        Identifiziert die Top-N Stellen affektiver Verdichtung.
        
        Kriterien:
        1. Hohe Marker-Dichte
        2. Mehrere Affekt-Dimensionen gleichzeitig aktiv
        3. Ambivalenz-Marker als besonderer Indikator
        
        Returns:
            Liste der aufschlussreichsten Stellen mit Begründung.
        """
        summary = self.zusammenfassung(document)
        turns = {t.turn_id: t for t in document.get_befragte_turns()}
        
        kandidaten = []
        for row in summary:
            if row['n_marker'] == 0:
                continue
            
            score = 0
            reasons = []
            
            # Marker-Dichte
            if row['marker_dichte'] > 5:
                score += 3
                reasons.append(f"Hohe Marker-Dichte: {row['marker_dichte']}%")
            elif row['marker_dichte'] > 2:
                score += 1
                reasons.append(f"Mittlere Marker-Dichte: {row['marker_dichte']}%")
            
            # Mehrere Dimensionen gleichzeitig
            if row['n_dimensionen_aktiv'] >= 3:
                score += 3
                reasons.append(f"Multidimensional: {row['n_dimensionen_aktiv']} Dimensionen aktiv")
            elif row['n_dimensionen_aktiv'] >= 2:
                score += 1
                reasons.append(f"{row['n_dimensionen_aktiv']} Dimensionen aktiv")
            
            # Ambivalenz als besonderer Marker
            if 'AMBIVALENZ' in row['dimensionen']:
                score += 2
                reasons.append(f"Ambivalenz erkannt ({row['dimensionen']['AMBIVALENZ']}x)")
            
            # Körperlicher Verweis
            if 'KOERPERLICHER_VERWEIS' in row['dimensionen']:
                score += 2
                reasons.append(f"Körperlicher Ausdruck ({row['dimensionen']['KOERPERLICHER_VERWEIS']}x)")
            
            # Distanzierung (Signal für schwieriges Thema)
            if 'DISTANZIERUNG' in row['dimensionen']:
                score += 1
                reasons.append(f"Distanzierungsmarker ({row['dimensionen']['DISTANZIERUNG']}x)")
            
            turn = turns.get(row['turn_id'])
            text = turn.text if turn else ""
            
            kandidaten.append({
                'turn_id': row['turn_id'],
                'score': score,
                'reasons': reasons,
                'marker_dichte': row['marker_dichte'],
                'n_marker': row['n_marker'],
                'dimensionen': row['dimensionen'],
                'text_vorschau': text[:200] + '...' if len(text) > 200 else text,
            })
        
        kandidaten.sort(key=lambda x: -x['score'])
        return kandidaten[:n]
