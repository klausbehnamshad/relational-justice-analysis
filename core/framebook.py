"""
core/framebook.py – Lädt und validiert das Framebook (YAML) + optionale Overlays.

Zwei-Ebenen-Modell:
  Ebene 1: framebook_v3.yaml → Meta-Frames (universell, immer aktiv)
  Ebene 2: overlays/*.yaml   → Projektspezifische Erweiterungen

Verwendung:
    # Nur Meta-Frames
    fb = Framebook("config/framebook_v3.yaml")

    # Meta-Frames + Projekt-Overlay
    fb = Framebook("config/framebook_v3.yaml", overlay="overlays/housing_lux.yaml")

    fb.frames                → Dict der (gemergedten) Frames
    fb.frame_priorities      → Dict {Frame-Name: Priorität}
    fb.frame_conflicts       → Liste der Conflict-Regeln
    fb.overlay_name          → Name des Overlays (oder None)
"""

import os
import copy
import yaml


class Framebook:
    """
    Lädt ein Framebook aus einer YAML-Datei und mergt optionales Overlay.
    """

    def __init__(self, filepath, overlay=None):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Framebook nicht gefunden: {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            self._data = yaml.safe_load(f)

        self.filepath = filepath
        self.version = self._data.get('version', 'unbekannt')
        self.beschreibung = self._data.get('beschreibung', '')

        # Sektionen laden
        self.textsorten = self._data.get('textsorten', {})
        self.prozessstrukturen = self._data.get('prozessstrukturen', {})
        self.pronomen = self._data.get('pronomen', {})
        self.agency = self._data.get('agency', {})
        self.frames = self._data.get('frames', {})
        self.topoi = self._data.get('topoi', {})
        self.frame_spannungen = self._data.get('frame_spannungen', [])
        self.affekt_dimensionen = self._data.get('affekt_dimensionen', {})

        # v3: Priority/Conflict-Regeln
        self.frame_priorities = self._data.get('frame_priorities', {})
        self.frame_conflicts = self._data.get('frame_conflicts', [])

        # v3.1: Frame-Klassifikation für JusticeAnalyzer
        self.frame_classification = self._data.get('frame_classification', {})

        # Overlay
        self.overlay_name = None
        self._overlay_data = None
        if overlay:
            self._load_overlay(overlay)

        self._validate()

    # ── Overlay-Logik ──────────────────────────────────

    def _load_overlay(self, overlay_path):
        """Lädt und mergt ein Overlay in die bestehenden Daten."""
        if not os.path.exists(overlay_path):
            raise FileNotFoundError(f"Overlay nicht gefunden: {overlay_path}")

        with open(overlay_path, 'r', encoding='utf-8') as f:
            ov = yaml.safe_load(f)

        self._overlay_data = ov
        self.overlay_name = ov.get('overlay', {}).get('name', overlay_path)

        # 1) Bestehende Frames erweitern (Indikatoren anhängen)
        for frame_name, frame_ext in ov.get('frames', {}).items():
            if frame_name in self.frames:
                self._merge_indikatoren(self.frames[frame_name], frame_ext)

        # 2) Overlay-spezifische Frames hinzufügen
        for frame_name, frame_def in ov.get('overlay_frames', {}).items():
            self.frames[frame_name] = frame_def

        # 3) Bestehende Topoi erweitern
        for topos_name, topos_ext in ov.get('topoi', {}).items():
            if topos_name in self.topoi:
                self._merge_indikatoren(self.topoi[topos_name], topos_ext)

        # 4) Overlay-spezifische Topoi hinzufügen
        for topos_name, topos_def in ov.get('overlay_topoi', {}).items():
            self.topoi[topos_name] = topos_def

        # 5) Frame-Spannungen ergänzen
        self.frame_spannungen.extend(ov.get('overlay_frame_spannungen', []))

        # 6) Overlay-Priorities/Conflicts ergänzen (falls vorhanden)
        self.frame_priorities.update(ov.get('frame_priorities', {}))
        self.frame_conflicts.extend(ov.get('frame_conflicts', []))

    def _merge_indikatoren(self, target, extension):
        """Hängt Overlay-Indikatoren an bestehende Indikatoren an."""
        ext_ind = extension.get('indikatoren', {})
        if 'indikatoren' not in target:
            target['indikatoren'] = {}
        for lang, patterns in ext_ind.items():
            if lang not in target['indikatoren']:
                target['indikatoren'][lang] = []
            # Duplikate vermeiden
            existing = set(target['indikatoren'][lang])
            for p in patterns:
                if p not in existing:
                    target['indikatoren'][lang].append(p)

    # ── Validation ─────────────────────────────────────

    @property
    def data(self):
        """Raw YAML data (read-only view)."""
        return self._data

    def _validate(self):
        """Prüft, ob die Grundstruktur vorhanden ist."""
        warnings = []
        required = ['textsorten', 'prozessstrukturen', 'frames', 'affekt_dimensionen']
        for section in required:
            if not getattr(self, section):
                warnings.append(f"Sektion '{section}' fehlt oder ist leer")

        # Validate frame_spannungen references
        known_frames = set(self.frames.keys())
        for sp in self.frame_spannungen:
            for key in ('frame_a', 'frame_b'):
                if sp.get(key) not in known_frames:
                    warnings.append(
                        f"Frame-Spannung referenziert unbekannten Frame: '{sp.get(key)}'"
                    )

        # Validate priorities reference known frames
        for frame_name in self.frame_priorities:
            if frame_name not in known_frames:
                warnings.append(
                    f"frame_priorities referenziert unbekannten Frame: '{frame_name}'"
                )

        # Validate conflicts reference known frames
        for conflict in self.frame_conflicts:
            for key in ('if_present', 'downweight'):
                if conflict.get(key) not in known_frames:
                    warnings.append(
                        f"frame_conflicts referenziert unbekannten Frame: "
                        f"'{conflict.get(key)}'"
                    )

        if warnings:
            print(f"⚠️  Framebook-Warnungen:")
            for w in warnings:
                print(f"   - {w}")

    # ── API ────────────────────────────────────────────

    def get_priority(self, frame_name):
        """Gibt die Priorität eines Frames zurück (Default: 10)."""
        return self.frame_priorities.get(frame_name, 10)

    def get_conflicts_for(self, frame_name):
        """Gibt alle Conflict-Regeln zurück, die diesen Frame downweighten."""
        return [
            c for c in self.frame_conflicts
            if c.get('downweight') == frame_name
        ]

    def get_languages(self):
        """Gibt alle Sprachen zurück, die im Framebook definiert sind."""
        langs = set()
        for section in [self.textsorten, self.prozessstrukturen,
                        self.agency, self.frames, self.topoi,
                        self.affekt_dimensionen]:
            for cat_name, cat_config in section.items():
                if 'indikatoren' in cat_config:
                    langs.update(cat_config['indikatoren'].keys())
        langs.update(self.pronomen.keys())
        return sorted(langs)

    def summary(self):
        """Übersicht über das Framebook."""
        result = {
            'version': self.version,
            'beschreibung': self.beschreibung,
            'sprachen': self.get_languages(),
            'n_textsorten': len(self.textsorten),
            'n_prozessstrukturen': len(self.prozessstrukturen),
            'n_frames': len(self.frames),
            'n_topoi': len(self.topoi),
            'n_frame_spannungen': len(self.frame_spannungen),
            'n_affekt_dimensionen': len(self.affekt_dimensionen),
            'n_frame_priorities': len(self.frame_priorities),
            'n_frame_conflicts': len(self.frame_conflicts),
            'has_frame_classification': bool(self.frame_classification),
        }
        if self.overlay_name:
            result['overlay'] = self.overlay_name
        return result

    def __repr__(self):
        ov = f" + {self.overlay_name}" if self.overlay_name else ""
        return f"Framebook(v{self.version}{ov}, {self.filepath})"
