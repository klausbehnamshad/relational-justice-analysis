"""
core/justice.py – JusticeAnalyzer

Modelliert soziale (Un)Gerechtigkeit als Relationsmuster zwischen
Anspruchsframes (A-Frames) und Strukturframes (S-Frames).

Keine eigene Annotation – sitzt ÜBER den Modulen B, C, D und
berechnet Spannungsprofile aus deren Ergebnissen.

Verwendung:
    from core.justice import JusticeAnalyzer

    ja = JusticeAnalyzer(doc, mod_b, mod_c, mod_d,
                         fb.frame_priorities, fb.frame_conflicts)
    profil = ja.interview_profil()
    claims = ja.generate_claims()
    ja.print_profil()

Epistemischer Status:
    Alle Outputs sind Vorschläge zur Prüfung, keine Befunde.
"""

from math import sqrt
from collections import defaultdict


# ════════════════════════════════════════════════════════
# Frame-Klassifikation: wird aus dem Framebook geladen
# ════════════════════════════════════════════════════════
# Fallback-Defaults (nur falls framebook keine classification hat)

_DEFAULT_A = {
    "LEGITIMITAET_GERECHTIGKEIT",
    "AUTONOMIE_SELBSTBESTIMMUNG",
    "SOLIDARITAET_GEMEINSCHAFT",
}
_DEFAULT_S = {
    "OEKONOMISIERUNG",
    "BUEROKRATISCHE_ORDNUNG",
    "EXKLUSION_OTHERING",
    "INSTITUTIONELLE_LOGIK",
}
_DEFAULT_K_VERST = {"VULNERABILITAET"}
_DEFAULT_K_DAEMPF = {"NORMALISIERUNG"}


# Spannungsachsen-Labels (für Lesbarkeit im Report)
AXIS_LABELS = {
    ("LEGITIMITAET_GERECHTIGKEIT", "OEKONOMISIERUNG"):
        "Fairness vs. Marktlogik",
    ("LEGITIMITAET_GERECHTIGKEIT", "EXKLUSION_OTHERING"):
        "Rechte vs. Ausgrenzung",
    ("LEGITIMITAET_GERECHTIGKEIT", "BUEROKRATISCHE_ORDNUNG"):
        "Würde vs. Verfahren",
    ("LEGITIMITAET_GERECHTIGKEIT", "INSTITUTIONELLE_LOGIK"):
        "Gerechtigkeit vs. Systemlogik",
    ("AUTONOMIE_SELBSTBESTIMMUNG", "OEKONOMISIERUNG"):
        "Selbstbestimmung vs. Kostendruck",
    ("AUTONOMIE_SELBSTBESTIMMUNG", "BUEROKRATISCHE_ORDNUNG"):
        "Handlungsfähigkeit vs. Bürokratie",
    ("AUTONOMIE_SELBSTBESTIMMUNG", "EXKLUSION_OTHERING"):
        "Teilhabe vs. Ausschluss",
    ("AUTONOMIE_SELBSTBESTIMMUNG", "INSTITUTIONELLE_LOGIK"):
        "Autonomie vs. Systemzwang",
    ("SOLIDARITAET_GEMEINSCHAFT", "OEKONOMISIERUNG"):
        "Gemeinschaft vs. Marktlogik",
    ("SOLIDARITAET_GEMEINSCHAFT", "EXKLUSION_OTHERING"):
        "Zusammenhalt vs. Spaltung",
    ("SOLIDARITAET_GEMEINSCHAFT", "BUEROKRATISCHE_ORDNUNG"):
        "Solidarität vs. Verfahrenslogik",
    ("SOLIDARITAET_GEMEINSCHAFT", "INSTITUTIONELLE_LOGIK"):
        "Gemeinschaft vs. System",
}


def _axis_key(a_frame, s_frame):
    """Kanonische Achsen-Schlüssel (A-Frame immer zuerst)."""
    return (a_frame, s_frame)


def _axis_label(a_frame, s_frame):
    """Menschenlesbares Label für eine Spannungsachse."""
    key = _axis_key(a_frame, s_frame)
    return AXIS_LABELS.get(key, f"{a_frame} × {s_frame}")


class JusticeAnalyzer:
    """
    Berechnet (Un)Gerechtigkeits-Spannungsprofile aus den
    Ergebnissen der Module B (Agency), C (Frames), D (Affekt).
    """

    def __init__(self, document, mod_b, mod_c, mod_d,
                 frame_priorities=None, frame_conflicts=None,
                 framebook=None):
        self.doc = document
        self.mod_b = mod_b
        self.mod_c = mod_c
        self.mod_d = mod_d
        self.frame_priorities = frame_priorities or {}
        self.frame_conflicts = frame_conflicts or []

        # Frame-Klassifikation aus Framebook laden (oder Defaults)
        if framebook and hasattr(framebook, 'data'):
            fc = framebook.data.get('frame_classification', {})
        elif framebook and isinstance(framebook, dict):
            fc = framebook.get('frame_classification', {})
        else:
            fc = {}

        if fc:
            self.a_frames = set(fc.get('anspruch', []))
            self.s_frames = set(fc.get('struktur', []))
            kontext = fc.get('kontext', {})
            self.k_frames_verst = set(kontext.get('verstaerkend', []))
            self.k_frames_daempf = set(kontext.get('abschwächend', []))
            self.k_frames_neutral = set(kontext.get('neutral', []))
        else:
            # Fallback auf Defaults
            self.a_frames = _DEFAULT_A
            self.s_frames = _DEFAULT_S
            self.k_frames_verst = _DEFAULT_K_VERST
            self.k_frames_daempf = _DEFAULT_K_DAEMPF
            self.k_frames_neutral = set()

        # Alle bekannten Meta-Frames (für Overlay-Erkennung)
        self._meta_frames = (self.a_frames | self.s_frames |
                             self.k_frames_verst | self.k_frames_daempf |
                             self.k_frames_neutral)

        # Vorberechnung
        self._turn_profiles = None
        self._interview_profil = None

    # ════════════════════════════════════════════════════
    # Turn-Level Analyse
    # ════════════════════════════════════════════════════

    def turn_profiles(self):
        """Berechnet Spannungsprofil für jeden Befragten-Turn."""
        if self._turn_profiles is not None:
            return self._turn_profiles

        # Hole Zusammenfassungen der Module
        c_summary = {r['turn_id']: r for r in self.mod_c.zusammenfassung(self.doc)}
        b_summary = {r['turn_id']: r for r in self.mod_b.zusammenfassung(self.doc)}
        d_sites = {}
        for s in self.mod_d.verdichtungsstellen(self.doc):
            d_sites[s['turn_id']] = s

        profiles = []
        for turn in self.doc.get_befragte_turns():
            tid = turn.turn_id
            c_row = c_summary.get(tid, {})
            b_row = b_summary.get(tid, {})
            frames = c_row.get('frames', {})

            # A- und S-Frame-Counts separieren
            a_counts = {f: c for f, c in frames.items() if f in self.a_frames}
            s_counts = {f: c for f, c in frames.items() if f in self.s_frames}
            a_total = sum(a_counts.values())
            s_total = sum(s_counts.values())

            # K-Frame-Flags
            k_frames_present = set(frames.keys()) & (
                self.k_frames_verst | self.k_frames_daempf)

            # Overlay-Tags: Frames die nicht in Meta-Klassifikation sind
            overlay_tags = {f: c for f, c in frames.items()
                           if f not in self._meta_frames}

            # ── Basis-Spannung ──
            basis = sqrt(a_total * s_total)

            if basis == 0:
                profiles.append(self._empty_profile(tid, turn, a_counts,
                                                     s_counts, overlay_tags))
                continue

            # ── Affekt-Multiplikator (Modul D) ──
            d_info = d_sites.get(tid, {})
            affekt_dichte = d_info.get('marker_dichte', 0)
            if isinstance(affekt_dichte, str):
                # manchmal als "9.5%" formatiert
                affekt_dichte = float(affekt_dichte.replace('%', ''))
            affekt_mult = min(1.0 + affekt_dichte / 100, 1.25)

            # ── Agency-Multiplikator (Modul B) ──
            dominant_agency = b_row.get('dominant_agency', '-')
            if dominant_agency == 'ERLEIDEND_PASSIV':
                agency_mult = 1.2
            elif dominant_agency == 'MORALISCH_REFLEKTIEREND':
                agency_mult = 1.1
            else:
                agency_mult = 1.0

            # ── K-Frame-Moderatoren ──
            k_mult = 1.0
            for kf in k_frames_present:
                if kf in self.k_frames_verst:
                    k_mult *= 1.10
                elif kf in self.k_frames_daempf:
                    k_mult *= 0.90

            # ── Intensität ──
            intensity = basis * affekt_mult * agency_mult * k_mult

            # Normiert auf 1000 Zeichen
            text_len = max(len(turn.text), 1)
            intensity_norm = intensity / (text_len / 1000)

            # ── Spannungsachsen ──
            tension_axes = []
            for af, ac in a_counts.items():
                for sf, sc in s_counts.items():
                    axis_intensity = sqrt(ac * sc) * affekt_mult * agency_mult * k_mult
                    tension_axes.append({
                        'a_frame': af,
                        's_frame': sf,
                        'label': _axis_label(af, sf),
                        'intensity': round(axis_intensity, 2),
                        'overlay_tags': list(overlay_tags.keys()),
                    })
            tension_axes.sort(key=lambda x: x['intensity'], reverse=True)

            profiles.append({
                'turn_id': tid,
                'a_frames': a_counts,
                's_frames': s_counts,
                'a_total': a_total,
                's_total': s_total,
                'basis': round(basis, 2),
                'affekt_mult': round(affekt_mult, 3),
                'agency_mult': agency_mult,
                'agency_label': dominant_agency,
                'k_mult': round(k_mult, 2),
                'k_frames': list(k_frames_present),
                'intensity': round(intensity, 2),
                'intensity_norm': round(intensity_norm, 2),
                'tension_axes': tension_axes,
                'overlay_tags': list(overlay_tags.keys()),
                'is_justice_site': True,
                'text_preview': turn.text[:120],
            })

        self._turn_profiles = profiles
        return profiles

    def _empty_profile(self, tid, turn, a_counts, s_counts, overlay_tags):
        """Leeres Profil für Turns ohne Spannung."""
        return {
            'turn_id': tid,
            'a_frames': a_counts,
            's_frames': s_counts,
            'a_total': sum(a_counts.values()),
            's_total': sum(s_counts.values()),
            'basis': 0,
            'affekt_mult': 1.0,
            'agency_mult': 1.0,
            'agency_label': '-',
            'k_mult': 1.0,
            'k_frames': [],
            'intensity': 0,
            'intensity_norm': 0,
            'tension_axes': [],
            'overlay_tags': list(overlay_tags.keys()),
            'is_justice_site': False,
            'text_preview': turn.text[:120],
        }

    # ════════════════════════════════════════════════════
    # Interview-Level Aggregation
    # ════════════════════════════════════════════════════

    def interview_profil(self):
        """Aggregiertes (Un)Gerechtigkeitsprofil für das gesamte Interview."""
        if self._interview_profil is not None:
            return self._interview_profil

        profiles = self.turn_profiles()
        justice_sites = [p for p in profiles if p['is_justice_site']]
        n_total = len(profiles)

        if not justice_sites:
            self._interview_profil = {
                'justice_score': 0,
                'justice_density': 0,
                'n_justice_sites': 0,
                'n_turns_total': n_total,
                'peak_turns': [],
                'dominant_tension': None,
                'trajectory': 'KEINE',
                'tension_axes': {},
                'justice_site_strong_threshold': 0,
            }
            return self._interview_profil

        # Gesamtscore
        total_intensity = sum(p['intensity_norm'] for p in justice_sites)

        # Density
        density = len(justice_sites) / n_total if n_total else 0

        # Peak turns (Top 3)
        sorted_sites = sorted(justice_sites,
                              key=lambda p: p['intensity_norm'], reverse=True)
        peak_turns = [p['turn_id'] for p in sorted_sites[:3]]

        # P75 threshold für "strong"
        intensities = sorted([p['intensity_norm'] for p in justice_sites])
        p75_idx = int(len(intensities) * 0.75)
        p75_threshold = intensities[p75_idx] if intensities else 0

        # Tag strong sites
        for p in profiles:
            p['is_justice_site_strong'] = (
                p['is_justice_site'] and p['intensity_norm'] >= p75_threshold
            )

        # Achsen aggregieren
        axis_totals = defaultdict(lambda: {'count': 0, 'total_intensity': 0,
                                           'turns': [], 'overlay_tags': set()})
        for p in justice_sites:
            for ax in p['tension_axes']:
                key = _axis_key(ax['a_frame'], ax['s_frame'])
                axis_totals[key]['count'] += 1
                axis_totals[key]['total_intensity'] += ax['intensity']
                axis_totals[key]['turns'].append(p['turn_id'])
                axis_totals[key]['overlay_tags'].update(ax['overlay_tags'])

        # Dominant tension
        dominant = None
        if axis_totals:
            dominant_key = max(axis_totals,
                               key=lambda k: axis_totals[k]['total_intensity'])
            dominant = {
                'axis': dominant_key,
                'label': _axis_label(*dominant_key),
                'count': axis_totals[dominant_key]['count'],
                'total_intensity': round(
                    axis_totals[dominant_key]['total_intensity'], 2),
            }

        # Serialisierbare Achsen
        axes_out = {}
        for key, data in axis_totals.items():
            axes_out[key] = {
                'label': _axis_label(*key),
                'count': data['count'],
                'total_intensity': round(data['total_intensity'], 2),
                'turns': data['turns'],
                'overlay_tags': sorted(data['overlay_tags']),
            }

        # Trajektorie
        trajectory = self._compute_trajectory(justice_sites, n_total)

        self._interview_profil = {
            'justice_score': round(total_intensity, 2),
            'justice_density': round(density, 2),
            'n_justice_sites': len(justice_sites),
            'n_turns_total': n_total,
            'peak_turns': peak_turns,
            'dominant_tension': dominant,
            'trajectory': trajectory,
            'tension_axes': axes_out,
            'justice_site_strong_threshold': round(p75_threshold, 2),
        }
        return self._interview_profil

    def _compute_trajectory(self, justice_sites, n_total):
        """Steigt oder fällt die Spannungsintensität im Interviewverlauf?"""
        if len(justice_sites) < 3:
            return 'ZU_WENIG_DATEN'

        # Sortiere nach turn_id
        ordered = sorted(justice_sites, key=lambda p: p['turn_id'])
        n = len(ordered)
        third = max(n // 3, 1)

        avg_first = sum(p['intensity_norm'] for p in ordered[:third]) / third
        avg_last = sum(p['intensity_norm'] for p in ordered[-third:]) / third

        if avg_last > avg_first * 1.3:
            return 'STEIGEND'
        elif avg_first > avg_last * 1.3:
            return 'FALLEND'
        else:
            return 'STABIL'

    # ════════════════════════════════════════════════════
    # Claims
    # ════════════════════════════════════════════════════

    def generate_claims(self):
        """Erzeugt analytische Claims aus dem Spannungsprofil."""
        profil = self.interview_profil()
        profiles = self.turn_profiles()
        claims = []

        # 1. Dominanz-Claim
        if profil['dominant_tension']:
            dt = profil['dominant_tension']
            tags_info = ""
            axis_data = profil['tension_axes'].get(dt['axis'], {})
            if axis_data.get('overlay_tags'):
                tags_info = (f" (kontextualisiert durch: "
                             f"{', '.join(axis_data['overlay_tags'])})")
            claims.append({
                'typ': 'JUSTICE_DOMINANZ',
                'beschreibung': (
                    f"Die zentrale Gerechtigkeitsspannung ist "
                    f"{dt['label']} ({dt['count']} Turns, "
                    f"Intensität {dt['total_intensity']}){tags_info}."
                ),
                'prueffrage': (
                    f"Wird {dt['axis'][1]} primär als Verletzung von "
                    f"{dt['axis'][0]} erlebt? Oder gibt es eine andere "
                    f"Deutung der Spannung?"
                ),
                'staerke': dt['total_intensity'],
                'turns': axis_data.get('turns', []),
            })

        # 2. Trajektorie-Claim
        if profil['trajectory'] in ('STEIGEND', 'FALLEND'):
            claims.append({
                'typ': 'JUSTICE_TRAJEKTORIE',
                'beschreibung': (
                    f"Die Gerechtigkeitsspannung ist im Interviewverlauf "
                    f"{profil['trajectory'].lower()}."
                ),
                'prueffrage': (
                    "Korreliert die Veränderung mit Frame-Verschiebungen "
                    "(Modul C) oder Agency-Wechseln (Modul B)?"
                ),
                'staerke': profil['justice_score'],
                'turns': [],
            })

        # 3. Peak-Claims (Top 3 Stellen)
        strong = [p for p in profiles if p.get('is_justice_site_strong')]
        for p in sorted(strong, key=lambda x: x['intensity_norm'],
                        reverse=True)[:3]:
            top_axis = p['tension_axes'][0] if p['tension_axes'] else None
            axis_info = f", Achse: {top_axis['label']}" if top_axis else ""
            tag_info = ""
            if p['overlay_tags']:
                tag_info = f", Kontext: {', '.join(p['overlay_tags'])}"

            claims.append({
                'typ': 'JUSTICE_PEAK',
                'beschreibung': (
                    f"Turn {p['turn_id']} ist eine intensive "
                    f"(Un)Gerechtigkeitsstelle (Intensität "
                    f"{p['intensity_norm']}/1000z, "
                    f"{p['agency_label']}{axis_info}{tag_info})."
                ),
                'prueffrage': (
                    f"Was genau wird in Turn {p['turn_id']} als "
                    f"ungerecht erlebt? Welche konkrete Situation?"
                ),
                'staerke': p['intensity_norm'],
                'turns': [p['turn_id']],
            })

        # 4. Density-Claim
        if profil['justice_density'] >= 0.5:
            claims.append({
                'typ': 'JUSTICE_DICHTE',
                'beschreibung': (
                    f"{profil['justice_density']*100:.0f}% der Turns enthalten "
                    f"Gerechtigkeitsspannungen – das Interview ist "
                    f"durchgehend von (Un)Gerechtigkeit geprägt."
                ),
                'prueffrage': (
                    "Ist das Thema (Un)Gerechtigkeit der rote Faden des "
                    "Interviews oder ein Effekt der Interviewführung?"
                ),
                'staerke': profil['justice_density'],
                'turns': [],
            })

        # 5. Overlay-Kontext-Claim (wenn Overlay-Tags die Achsen kontextualisieren)
        all_tags = set()
        for ax_data in profil['tension_axes'].values():
            all_tags.update(ax_data.get('overlay_tags', []))
        if all_tags:
            claims.append({
                'typ': 'JUSTICE_KONTEXT',
                'beschreibung': (
                    f"Die Gerechtigkeitsspannungen werden durch "
                    f"kontextspezifische Frames moduliert: "
                    f"{', '.join(sorted(all_tags))}."
                ),
                'prueffrage': (
                    "Sind diese Kontextframes Auslöser oder Verstärker "
                    "der (Un)Gerechtigkeitserfahrung?"
                ),
                'staerke': len(all_tags),
                'turns': [],
            })

        return claims

    # ════════════════════════════════════════════════════
    # Output / Reporting
    # ════════════════════════════════════════════════════

    def print_profil(self):
        """Gibt das vollständige Spannungsprofil auf der Konsole aus."""
        profil = self.interview_profil()
        profiles = self.turn_profiles()

        print("=" * 70)
        print("   (UN)GERECHTIGKEITS-SPANNUNGSPROFIL")
        print("   Epistemischer Status: Vorschläge zur Prüfung")
        print("=" * 70)

        # Klassifikationsquelle
        print(f"\n  Klassifikation: {'Framebook' if self.a_frames != _DEFAULT_A else 'Default (hardcoded)'}")
        print(f"  A-Frames (Anspruch): {sorted(self.a_frames)}")
        print(f"  S-Frames (Struktur): {sorted(self.s_frames)}")
        print(f"  K-Frames (Verstärkend): {sorted(self.k_frames_verst)}")
        print(f"  K-Frames (Abschwächend): {sorted(self.k_frames_daempf)}")

        # Interview-Level
        print(f"\n{'─'*40}")
        print(f"  INTERVIEW-PROFIL")
        print(f"{'─'*40}")
        print(f"  Justice Score:          {profil['justice_score']}")
        print(f"  Justice Density:        {profil['justice_density']*100:.0f}% "
              f"({profil['n_justice_sites']}/{profil['n_turns_total']} Turns)")
        print(f"  Trajektorie:            {profil['trajectory']}")
        print(f"  Peak Turns:             {profil['peak_turns']}")
        print(f"  Strong-Threshold (P75): {profil['justice_site_strong_threshold']}")

        if profil['dominant_tension']:
            dt = profil['dominant_tension']
            print(f"  Dominante Spannung:     {dt['label']}")
            print(f"                          ({dt['count']} Turns, "
                  f"Intensität {dt['total_intensity']})")

        # Achsen-Übersicht
        print(f"\n{'─'*40}")
        print(f"  SPANNUNGSACHSEN")
        print(f"{'─'*40}")
        axes = profil['tension_axes']
        for key in sorted(axes, key=lambda k: axes[k]['total_intensity'],
                          reverse=True):
            ax = axes[key]
            tags = f"  [{', '.join(ax['overlay_tags'])}]" if ax['overlay_tags'] else ""
            print(f"  {ax['label']:<40} "
                  f"{ax['count']:>2}× | Σ {ax['total_intensity']:>6.2f}{tags}")

        # Turn-Details (nur justice_sites)
        print(f"\n{'─'*40}")
        print(f"  TURN-DETAILS (nur Gerechtigkeitsstellen)")
        print(f"{'─'*40}")
        for p in profiles:
            if not p['is_justice_site']:
                continue
            strong = " ★" if p.get('is_justice_site_strong') else ""
            tags = f" [{', '.join(p['overlay_tags'])}]" if p['overlay_tags'] else ""
            print(f"\n  Turn {p['turn_id']}{strong}{tags}")
            print(f"    A-Frames: {p['a_frames']}")
            print(f"    S-Frames: {p['s_frames']}")
            print(f"    Basis: {p['basis']} × Affekt {p['affekt_mult']} "
                  f"× Agency {p['agency_mult']} ({p['agency_label']}) "
                  f"× K {p['k_mult']}")
            print(f"    → Intensität: {p['intensity']} "
                  f"({p['intensity_norm']}/1000z)")
            if p['tension_axes']:
                top = p['tension_axes'][0]
                print(f"    Top-Achse: {top['label']} ({top['intensity']})")
            print(f"    «{p['text_preview']}»")

        # Claims
        claims = self.generate_claims()
        if claims:
            print(f"\n{'─'*40}")
            print(f"  CLAIMS")
            print(f"{'─'*40}")
            for c in claims:
                print(f"\n  [{c['typ']}]")
                print(f"    {c['beschreibung']}")
                print(f"    → {c['prueffrage']}")

        print(f"\n{'='*70}")
