"""
modules/modul_c_diskurs.py – Diskursive Rahmung (Foucault, Goffman, Entman)

UPGRADE v4: Erzeugt nicht nur Annotations, sondern CLAIMS:
    - Hypothesen-Kandidaten
    - Spannungsindikatoren  
    - Frame-Trajektorien (Dominanzverschiebung über Interview)
"""

import re

from core.base_module import AnalyseModul


class ModulDiskurs(AnalyseModul):
    """Modul C: Diskursive Rahmung – mit Claims."""
    
    def __init__(self, language_gate, frames_config, topoi_config,
                 frame_spannungen=None, frame_priorities=None, frame_conflicts=None):
        super().__init__(
            modul_id="C_diskurs",
            name="Diskursive Rahmung",
            language_gate=language_gate,
            framebook_section={'frames': frames_config, 'topoi': topoi_config},
        )
        self.frames = frames_config
        self.topoi = topoi_config
        self.frame_spannungen = frame_spannungen or []
        self.frame_priorities = frame_priorities or {}
        self.frame_conflicts = frame_conflicts or []
    
    def analyse(self, document):
        """Frames und Topoi erkennen, Annotations schreiben."""
        n_annotations = 0
        turns = document.get_befragte_turns()
        
        for turn in turns:
            for frame_name, config in self.frames.items():
                patterns = self.gate.get_patterns(config)
                anns = self._pattern_search(
                    turn.text, frame_name, patterns, turn.turn_id,
                    regel_prefix=f"frame_{frame_name.lower()}")
                for ann in anns:
                    document.add_annotation(ann)
                    n_annotations += 1
            
            for topos_name, config in self.topoi.items():
                patterns = self.gate.get_patterns(config)
                anns = self._pattern_search(
                    turn.text, f"TOPOS_{topos_name}", patterns, turn.turn_id,
                    regel_prefix=f"topos_{topos_name.lower()}")
                for ann in anns:
                    document.add_annotation(ann)
                    n_annotations += 1
        
        return n_annotations
    
    def zusammenfassung(self, document):
        """Turn-Level-Zusammenfassung mit Priority/Conflict-Gewichtung."""
        rows = []
        for turn in document.get_befragte_turns():
            anns = document.get_annotations(modul=self.modul_id, turn_id=turn.turn_id)
            frame_counts = {}
            topos_counts = {}
            for a in anns:
                if a.kategorie.startswith('TOPOS_'):
                    topos_counts[a.kategorie] = topos_counts.get(a.kategorie, 0) + 1
                else:
                    frame_counts[a.kategorie] = frame_counts.get(a.kategorie, 0) + 1

            # Adjusted counts: Conflict-Regeln anwenden
            adjusted = self._apply_conflicts(frame_counts)

            # Dominant: höchster adjusted count; bei Tie → höhere Priority gewinnt
            if adjusted:
                dominant = max(
                    adjusted,
                    key=lambda f: (adjusted[f], self.frame_priorities.get(f, 10))
                )
            else:
                dominant = '-'

            rows.append({
                'turn_id': turn.turn_id,
                'frames': frame_counts,
                'frames_adjusted': adjusted,
                'topoi': topos_counts,
                'dominant_frame': dominant,
                'n_frames_aktiv': len(frame_counts),
                'frame_dichte': self._compute_density(sum(frame_counts.values()), turn.n_woerter),
            })
        return rows

    def _apply_conflicts(self, frame_counts):
        """Wendet frame_conflicts auf raw counts an.

        Logik: Wenn ein höherprioritärer Frame im selben Turn präsent ist,
        wird der niedrigprioritäre Frame heruntergewichtet.

        Gibt adjusted counts zurück (float → für Dominanzvergleich).
        Raw counts in frame_counts bleiben unverändert (für Audit Trail).
        """
        if not self.frame_conflicts or not frame_counts:
            return dict(frame_counts)

        adjusted = {f: float(c) for f, c in frame_counts.items()}
        present_frames = set(frame_counts.keys())

        for conflict in self.frame_conflicts:
            trigger = conflict.get('if_present', '')
            target = conflict.get('downweight', '')
            factor = conflict.get('downweight_factor', 1.0)

            if trigger in present_frames and target in adjusted:
                adjusted[target] *= factor

        return adjusted
    
    # ================================================================
    # CLAIMS – Analytische Verdichtung
    # ================================================================
    
    def generate_claims(self, document):
        """
        Erzeugt analytische Claims aus den Annotations.
        
        Ein Claim ist KEIN Befund. Er ist ein begründeter Vorschlag
        zur Prüfung durch die Forschenden.
        
        Returns:
            Liste von Claim-Dicts mit: typ, beschreibung, evidenz, turns, prüffrage
        """
        claims = []
        
        # 1. Ko-Okkurrenz-Claims
        claims.extend(self._claims_ko_okkurrenz(document))
        
        # 2. Trajektorien-Claims
        claims.extend(self._claims_trajektorie(document))
        
        # 3. Spannungs-Claims
        claims.extend(self._claims_spannungen(document))
        
        # 4. Dominanz-Claims
        claims.extend(self._claims_dominanz(document))
        
        return claims
    
    def _claims_ko_okkurrenz(self, document):
        """Welche Frames treten wiederholt gemeinsam auf?"""
        claims = []
        turns = document.get_befragte_turns()
        
        # Zähle Frame-Paare über alle Turns
        paar_counts = {}
        paar_turns = {}
        
        for turn in turns:
            anns = document.get_annotations(modul=self.modul_id, turn_id=turn.turn_id)
            frames_in_turn = set(a.kategorie for a in anns if not a.kategorie.startswith('TOPOS_'))
            
            frame_list = sorted(frames_in_turn)
            for i in range(len(frame_list)):
                for j in range(i + 1, len(frame_list)):
                    paar = (frame_list[i], frame_list[j])
                    paar_counts[paar] = paar_counts.get(paar, 0) + 1
                    if paar not in paar_turns:
                        paar_turns[paar] = []
                    paar_turns[paar].append(turn.turn_id)
        
        for paar, count in paar_counts.items():
            if count >= 2:
                claims.append({
                    'typ': 'KO_OKKURRENZ',
                    'beschreibung': f"Frames {paar[0]} und {paar[1]} treten in {count} Turns gemeinsam auf",
                    'evidenz': f"Turns: {paar_turns[paar]}",
                    'turns': paar_turns[paar],
                    'frames': list(paar),
                    'staerke': count,
                    'prueffrage': f"Stehen {paar[0]} und {paar[1]} in einem systematischen "
                                  f"Zusammenhang? Verstärken sie sich oder stehen sie in Spannung?",
                })
        
        return claims
    
    def _claims_trajektorie(self, document):
        """Verschiebt sich die Frame-Dominanz über das Interview?"""
        claims = []
        summary = self.zusammenfassung(document)
        
        if len(summary) < 3:
            return claims
        
        # Interview in Drittel teilen
        n = len(summary)
        drittel_1 = summary[:n // 3] if n >= 3 else summary[:1]
        drittel_3 = summary[-(n // 3):] if n >= 3 else summary[-1:]
        
        def dominant_frames(rows):
            counts = {}
            for r in rows:
                for f, c in r['frames'].items():
                    counts[f] = counts.get(f, 0) + c
            return counts
        
        frames_anfang = dominant_frames(drittel_1)
        frames_ende = dominant_frames(drittel_3)
        
        # Frames, die nur am Anfang oder Ende dominieren
        nur_anfang = set(frames_anfang.keys()) - set(frames_ende.keys())
        nur_ende = set(frames_ende.keys()) - set(frames_anfang.keys())
        
        if nur_anfang or nur_ende:
            claims.append({
                'typ': 'TRAJEKTORIE',
                'beschreibung': f"Frame-Verschiebung im Interviewverlauf erkennbar",
                'evidenz': f"Erstes Drittel dominiert: {frames_anfang}. "
                          f"Letztes Drittel dominiert: {frames_ende}.",
                'turns': [],
                'frames': list(nur_anfang | nur_ende),
                'staerke': len(nur_anfang) + len(nur_ende),
                'prueffrage': "Korreliert die Frame-Verschiebung mit einem narrativen "
                             "Wendepunkt (Modul A) oder einer Agency-Verschiebung (Modul B)?",
            })
        
        # Frames die wachsen oder schrumpfen
        alle_frames = set(frames_anfang.keys()) | set(frames_ende.keys())
        for frame in alle_frames:
            a = frames_anfang.get(frame, 0)
            e = frames_ende.get(frame, 0)
            if e > a + 1:
                claims.append({
                    'typ': 'TRAJEKTORIE_WACHSEND',
                    'beschreibung': f"Frame {frame} nimmt im Verlauf zu ({a}→{e})",
                    'evidenz': f"Erstes Drittel: {a}, Letztes Drittel: {e}",
                    'turns': [],
                    'frames': [frame],
                    'staerke': e - a,
                    'prueffrage': f"Warum gewinnt {frame} im Verlauf an Bedeutung? "
                                 f"Reaktion auf die Interviewfragen oder innere Dynamik?",
                })
            elif a > e + 1:
                claims.append({
                    'typ': 'TRAJEKTORIE_SCHRUMPFEND',
                    'beschreibung': f"Frame {frame} nimmt im Verlauf ab ({a}→{e})",
                    'evidenz': f"Erstes Drittel: {a}, Letztes Drittel: {e}",
                    'turns': [],
                    'frames': [frame],
                    'staerke': a - e,
                    'prueffrage': f"Warum verliert {frame} an Präsenz? Wird der Frame "
                                 f"durch einen anderen abgelöst?",
                })
        
        return claims
    
    def _claims_spannungen(self, document):
        """Prüft auf theoretisch definierte Frame-Spannungen."""
        claims = []
        turns = document.get_befragte_turns()
        
        for sp in self.frame_spannungen:
            fa = sp.get('frame_a', sp.get('frame_1', ''))
            fb = sp.get('frame_b', sp.get('frame_2', ''))
            beschr = sp.get('beschreibung', f'{fa} vs. {fb}')
            
            ko_turns = []
            for turn in turns:
                anns = document.get_annotations(modul=self.modul_id, turn_id=turn.turn_id)
                frames_here = set(a.kategorie for a in anns)
                if fa in frames_here and fb in frames_here:
                    ko_turns.append(turn.turn_id)
            
            if ko_turns:
                claims.append({
                    'typ': 'SPANNUNG',
                    'beschreibung': f"Frame-Spannung: {beschr}",
                    'evidenz': f"Beide Frames ko-okkurrieren in Turns: {ko_turns}",
                    'turns': ko_turns,
                    'frames': [fa, fb],
                    'staerke': len(ko_turns),
                    'prueffrage': f"Wie geht die befragte Person mit der Spannung zwischen "
                                 f"{fa} und {fb} um? Auflösung, Aushalten, Verdrängung?",
                })
        
        return claims
    
    def _claims_dominanz(self, document):
        """Welcher Frame dominiert das gesamte Interview? (mit Conflict-Gewichtung)"""
        claims = []
        all_anns = document.get_annotations(modul=self.modul_id)

        frame_total = {}
        for a in all_anns:
            if not a.kategorie.startswith('TOPOS_'):
                frame_total[a.kategorie] = frame_total.get(a.kategorie, 0) + 1

        if not frame_total:
            return claims

        # Adjusted counts über das gesamte Interview
        adjusted = self._apply_conflicts(frame_total)
        total_adj = sum(adjusted.values())
        if total_adj == 0:
            return claims

        dominant = max(
            adjusted,
            key=lambda f: (adjusted[f], self.frame_priorities.get(f, 10))
        )
        pct = adjusted[dominant] / total_adj * 100

        if pct > 40:
            # Prüfe ob Dominanz durch Downweighting verändert wurde
            raw_dominant = max(frame_total, key=frame_total.get)
            raw_pct = frame_total[raw_dominant] / sum(frame_total.values()) * 100

            note = ""
            if raw_dominant != dominant:
                note = (f" (Hinweis: Ohne Conflict-Gewichtung wäre {raw_dominant} "
                        f"dominant mit {raw_pct:.0f}%.)")

            claims.append({
                'typ': 'DOMINANZ',
                'beschreibung': (
                    f"Frame {dominant} dominiert das Interview "
                    f"({pct:.0f}% der gewichteten Frame-Marker){note}"
                ),
                'evidenz': f"Raw: {frame_total} | Adjusted: "
                           f"{{{k}: {v:.1f} for k, v in adjusted.items()}}",
                'turns': [],
                'frames': [dominant],
                'staerke': round(pct),
                'prueffrage': f"Ist {dominant} der zentrale Deutungsrahmen der befragten Person? "
                             f"Oder ein Artefakt der Interviewführung?",
            })

        return claims
    
    def frame_verlauf(self, document):
        """Frame-Verteilung über Turns (für Visualisierung)."""
        summary = self.zusammenfassung(document)
        all_frames = set()
        for row in summary:
            all_frames.update(row['frames'].keys())
        verlauf = []
        for row in summary:
            entry = {'turn_id': row['turn_id']}
            for frame in all_frames:
                entry[frame] = row['frames'].get(frame, 0)
            verlauf.append(entry)
        return verlauf, list(all_frames)
