"""
core/datamodel.py — Stabiles Datenmodell für qualitative Interviewanalyse.

VERSION 2.1 — mit korrigierter Sprecher-Erkennung

Grundprinzip:
    - Rohdaten (Text, Turns, Sätze) sind UNVERÄNDERLICH nach dem Parsing.
    - Jede Analyse schreibt nur ANNOTATIONEN, nie Rohdaten.
    - Annotationen haben immer: modul, regel_id, textstelle, begründung.
    - Das Corpus ist eine Liste von Documents → batch-fähig.

Fixes in dieser Version:
    - _detect_speakers_generic: prüft len(labels) >= 2 statt len(matches) >= 2
    - get_befragte_turns: nutzt != "Interviewer" statt == "Befragter"
    - Konsistente Verwendung von speaker_mapping (nicht speaker_labels)
    - Preprocessing-Option für Inline-Sprecherwechsel

Verwendung:
    from core.datamodel import Corpus, Document
    corpus = Corpus()
    doc = Document.from_text(text, doc_id="interview_01", language="de")
    corpus.add(doc)
"""

import re
import json
import hashlib
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


# ============================================================
# ANNOTATION — der Kern jeder Analyse-Ausgabe
# ============================================================

@dataclass
class Annotation:
    """
    Eine einzelne analytische Markierung.
    
    Jede Heuristik produziert Annotations — nie "Ergebnisse".
    Annotations sind prüfbar, versionierbar, exportierbar.
    """
    modul: str                    # z.B. "A_narrative", "B_position", "C_diskurs", "D_affekt"
    kategorie: str                # z.B. "NARRATION", "VERLAUFSKURVE", "OEKONOMISIERUNG"
    regel_id: str                 # z.B. "de_temporal_seq_01" — welche Regel hat gegriffen
    pattern: str                  # Das konkrete Regex-Muster
    matched_text: str             # Der gefundene Text-Span
    matched_start: int            # Startposition im Turn-Text
    matched_end: int              # Endposition im Turn-Text
    satz: str                     # Der Satz, in dem der Treffer liegt
    turn_id: int                  # In welchem Turn
    confidence: str = "pattern"   # "pattern", "syntactic", "llm_suggested"
    note: str = ""                # Optional: Forschende/r-Notiz
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self):
        """Export als Dictionary (für JSON/CSV)."""
        return {
            'modul': self.modul,
            'kategorie': self.kategorie,
            'regel_id': self.regel_id,
            'pattern': self.pattern,
            'matched_text': self.matched_text,
            'matched_start': self.matched_start,
            'matched_end': self.matched_end,
            'satz': self.satz,
            'turn_id': self.turn_id,
            'confidence': self.confidence,
            'note': self.note,
            'timestamp': self.timestamp,
        }


# ============================================================
# TURN — ein einzelner Sprechbeitrag
# ============================================================

@dataclass
class Turn:
    """Ein Sprechbeitrag im Interview."""
    turn_id: int
    sprecher: str           # Generisch: "Interviewer" oder "Befragter"
    sprecher_original: str = ""  # Original-Label aus dem Transkript (z.B. "Amara")
    text: str = ""
    saetze: list = field(default_factory=list)  # Liste von Strings
    
    @property
    def n_saetze(self):
        return len(self.saetze)
    
    @property
    def n_woerter(self):
        return len(self.text.split())
    
    @property
    def ist_befragter(self):
        """Prüft, ob dies ein Befragten-Turn ist."""
        return self.sprecher != "Interviewer"
    
    @property
    def ist_interviewer(self):
        """Prüft, ob dies ein Interviewer-Turn ist."""
        return self.sprecher == "Interviewer"


# ============================================================
# DOCUMENT — ein einzelnes Interview
# ============================================================

@dataclass
class Document:
    """
    Ein einzelnes Interview-Dokument.
    
    Enthält:
        - Metadaten (id, Sprache, Quelle)
        - Turns (Sprechbeiträge)
        - Annotations (werden von Modulen geschrieben)
    """
    doc_id: str
    language: str = "de"
    raw_text: str = ""
    turns: list = field(default_factory=list)       # Liste von Turn-Objekten
    annotations: list = field(default_factory=list)  # Liste von Annotation-Objekten
    metadata: dict = field(default_factory=dict)     # Freie Metadaten
    
    # ---- Preprocessing ----
    
    @staticmethod
    def preprocess_inline_speakers(text, known_speakers=None):
        """
        Preprocessing: Konvertiert Inline-Sprecherwechsel zu Zeilenanfängen.
        
        Wandelt um:
            "... question? Amara: Answer..."
        zu:
            "... question?
            Amara: Answer..."
        
        Args:
            text: Rohtext
            known_speakers: Optional, Liste bekannter Sprecher-Namen
        
        Returns:
            Bereinigter Text mit Sprechern am Zeilenanfang
        """
        if known_speakers is None:
            # Versuche Sprecher zu erkennen (grob)
            # Suche nach Mustern wie "Name:" die mehrfach vorkommen
            potential = re.findall(r'([A-ZÄÖÜ][a-zäöüß]+):\s', text)
            from collections import Counter
            counts = Counter(potential)
            # Nur Namen die mindestens 2x vorkommen
            known_speakers = [name for name, count in counts.items() if count >= 2]
        
        if not known_speakers:
            return text
        
        # Für jeden bekannten Sprecher: füge Zeilenumbruch vor "Name:" ein
        # aber nur wenn es NICHT bereits am Zeilenanfang steht
        for speaker in known_speakers:
            # Pattern: Nicht-Zeilenanfang + Satzende + Sprecher
            pattern = rf'([.!?])\s+({re.escape(speaker)}):\s'
            replacement = rf'\1\n\n\2: '
            text = re.sub(pattern, replacement, text)
        
        return text
    
    # ---- Parsing ----
    
    @classmethod
    def from_text(cls, text, doc_id="doc_001", language="de", 
                  speaker_mapping=None, sentence_tokenizer=None,
                  interviewer_label=None, preprocess=True):
        """
        Erzeugt ein Document aus Rohtext.
        
        Erkennt automatisch:
            - Beliebige Sprecher-Labels (Name:)
            - Klassifiziert automatisch wer Interviewer/Befragter ist
            - Fallback: Monolog (single speaker)
        
        Args:
            text: Der Rohtext des Transkripts
            doc_id: Eindeutige ID
            language: Sprachcode (de, en, fr, ...)
            speaker_mapping: Optional dict {"OriginalName": "Interviewer"/"Befragter"}
                            Wenn None: automatische Erkennung
            sentence_tokenizer: Optional, Funktion zum Satz-Splitting
            interviewer_label: Optional, explizites Interviewer-Label (z.B. "I", "Interviewer")
            preprocess: Wenn True, werden Inline-Sprecherwechsel normalisiert
        """
        doc = cls(doc_id=doc_id, language=language, raw_text=text)
        
        # Satz-Tokenisierung
        if sentence_tokenizer is None:
            sentence_tokenizer = cls._default_sentence_tokenizer(language)
        
        # Optional: Preprocessing für Inline-Sprecherwechsel
        if preprocess:
            text = cls.preprocess_inline_speakers(text)
        
        # Sprecher-Erkennung (generisch)
        detected_labels = cls._detect_speakers_generic(text)
        
        if detected_labels:
            # Klassifiziere wer Interviewer und wer Befragter ist
            if speaker_mapping is None:
                speaker_mapping = cls._classify_speakers(text, detected_labels, interviewer_label)
            
            doc.turns = cls._parse_dialog(text, detected_labels, speaker_mapping, sentence_tokenizer)
            doc.metadata['detected_speakers'] = list(detected_labels)
        else:
            doc.turns = cls._parse_monolog(text, sentence_tokenizer)
            doc.metadata['detected_speakers'] = []
        
        doc.metadata['parse_mode'] = 'dialog' if detected_labels else 'monolog'
        doc.metadata['speaker_mapping'] = speaker_mapping or {}
        doc.metadata['hash'] = hashlib.md5(text.encode()).hexdigest()[:12]
        
        return doc
    
    @staticmethod
    def _detect_speakers_generic(text):
        """
        Erkennt automatisch ALLE Sprecher-Labels im Text.
        
        Findet jedes Muster, das wie ein Sprecher-Label aussieht:
            - Name: (Großbuchstabe am Anfang)
            - I:, B:, A1:, etc.
            - Interviewer:, Amara:, Dr. Müller:, etc.
        
        Returns:
            Set von gefundenen Labels oder None
        
        WICHTIG: Gibt nur zurück wenn mindestens 2 VERSCHIEDENE Sprecher erkannt werden!
        """
        # Generisches Pattern: Wort(e) gefolgt von Doppelpunkt am Zeilenanfang
        # Erlaubt: "Interviewer:", "Amara:", "Dr. Smith:", "Speaker A:", "I:", "B1:"
        pattern = r'^([A-ZÄÖÜ][A-Za-zäöüßÄÖÜ\.\s]{0,30}?):\s'
        
        matches = re.findall(pattern, text, re.MULTILINE)
        
        if matches:
            # Bereinigen: Whitespace trimmen
            labels = set(m.strip() for m in matches)
            
            # FIX: Mindestens 2 VERSCHIEDENE Sprecher (nicht nur 2 Turns)
            if len(labels) >= 2:
                return labels
        
        return None  # Kein Dialog erkannt → Monolog
    
    @staticmethod
    def _classify_speakers(text, detected_labels, explicit_interviewer=None):
        """
        Klassifiziert die erkannten Sprecher als Interviewer oder Befragter.
        
        Heuristiken:
            1. Explizite Interviewer-Labels: "Interviewer", "I", "Interviewerin", "Int"
            2. Wer stellt mehr Fragen? (Fragezeichen-Häufigkeit)
            3. Wer hat kürzere Turns? (Interviewer sind meist kürzer)
            4. Wer spricht zuerst? (oft Interviewer)
        
        Returns:
            Dict {original_label: "Interviewer"/"Befragter"}
        """
        # Bekannte Interviewer-Labels
        interviewer_keywords = {
            'interviewer', 'interviewerin', 'int', 'i', 
            'moderator', 'moderatorin', 'mod',
            'forscher', 'forscherin', 'researcher',
            'fragender', 'fragende'
        }
        
        # Bekannte Befragten-Labels
        befragter_keywords = {
            'befragter', 'befragte', 'b', 'respondent', 'interviewee',
            'teilnehmer', 'teilnehmerin', 'participant', 'p',
            'erzähler', 'erzählerin', 'narrator'
        }
        
        mapping = {}
        
        # Schritt 1: Explizite Labels erkennen
        for label in detected_labels:
            label_lower = label.lower().strip()
            
            if explicit_interviewer and label_lower == explicit_interviewer.lower():
                mapping[label] = "Interviewer"
            elif label_lower in interviewer_keywords:
                mapping[label] = "Interviewer"
            elif label_lower in befragter_keywords:
                mapping[label] = "Befragter"
        
        # Schritt 2: Falls noch nicht alle klassifiziert → Heuristiken
        unclassified = [l for l in detected_labels if l not in mapping]
        
        if unclassified:
            # Analysiere Turn-Eigenschaften
            turn_stats = {}
            
            for label in detected_labels:
                # Finde alle Turns dieses Sprechers
                escaped_label = re.escape(label)
                other_labels = [re.escape(l) for l in detected_labels if l != label]
                if other_labels:
                    end_pattern = '|'.join(other_labels)
                    pattern = rf'^{escaped_label}:\s*(.+?)(?=^(?:{end_pattern}):\s|\Z)'
                else:
                    pattern = rf'^{escaped_label}:\s*(.+?)(?=\Z)'
                
                turns = re.findall(pattern, text, re.MULTILINE | re.DOTALL)
                
                if turns:
                    total_text = ' '.join(turns)
                    avg_length = len(total_text) / len(turns)
                    question_ratio = total_text.count('?') / max(len(turns), 1)
                    
                    turn_stats[label] = {
                        'n_turns': len(turns),
                        'avg_length': avg_length,
                        'question_ratio': question_ratio,
                    }
            
            # Interviewer: mehr Fragen, kürzere Turns
            for label in unclassified:
                if label in turn_stats:
                    stats = turn_stats[label]
                    
                    # Vergleiche mit anderen Sprechern
                    other_stats = [s for l, s in turn_stats.items() if l != label]
                    
                    if other_stats:
                        avg_other_length = sum(s['avg_length'] for s in other_stats) / len(other_stats)
                        avg_other_questions = sum(s['question_ratio'] for s in other_stats) / len(other_stats)
                        
                        # Interviewer-Score: kurze Turns + viele Fragen
                        is_interviewer = (
                            stats['avg_length'] < avg_other_length * 0.5 or  # Deutlich kürzer
                            stats['question_ratio'] > avg_other_questions * 2 or  # Deutlich mehr Fragen
                            stats['question_ratio'] > 0.8  # Fast jeder Turn hat Frage
                        )
                        
                        mapping[label] = "Interviewer" if is_interviewer else "Befragter"
                    else:
                        # Nur ein Sprecher übrig → Befragter (wenn schon Interviewer da)
                        if "Interviewer" in mapping.values():
                            mapping[label] = "Befragter"
                        else:
                            mapping[label] = "Interviewer"
        
        # Fallback: Falls immer noch unklassifiziert
        for label in detected_labels:
            if label not in mapping:
                # Wenn schon ein Interviewer existiert → dieser ist Befragter
                if "Interviewer" in mapping.values():
                    mapping[label] = "Befragter"
                else:
                    mapping[label] = "Interviewer"
        
        return mapping
    
    @staticmethod
    def _parse_dialog(text, detected_labels, speaker_mapping, sent_tokenizer):
        """Parst einen Dialog mit Sprecher-Labels."""
        # Regex aus den Labels bauen (sortiert nach Länge, längste zuerst)
        sorted_labels = sorted(detected_labels, key=len, reverse=True)
        label_pattern = '|'.join(re.escape(k) for k in sorted_labels)
        pattern = rf'^({label_pattern}):\s*(.+?)(?=^(?:{label_pattern}):\s|\Z)'
        
        matches = re.findall(pattern, text, re.MULTILINE | re.DOTALL)
        turns = []
        
        for i, (sprecher_raw, inhalt) in enumerate(matches):
            inhalt_bereinigt = ' '.join(inhalt.split())
            
            # Generisches Label zuweisen
            sprecher_generisch = speaker_mapping.get(sprecher_raw, "Befragter")
            
            saetze = sent_tokenizer(inhalt_bereinigt)
            
            turns.append(Turn(
                turn_id=i + 1,
                sprecher=sprecher_generisch,
                sprecher_original=sprecher_raw,
                text=inhalt_bereinigt,
                saetze=saetze,
            ))
        
        return turns
    
    @staticmethod
    def _parse_monolog(text, sent_tokenizer):
        """Parst einen Text ohne Sprecher-Labels als Monolog."""
        # Absätze als Turns verwenden
        absaetze = [a.strip() for a in text.split('\n\n') if a.strip()]
        
        if not absaetze:
            absaetze = [text.strip()]
        
        turns = []
        for i, absatz in enumerate(absaetze):
            bereinigt = ' '.join(absatz.split())
            saetze = sent_tokenizer(bereinigt)
            turns.append(Turn(
                turn_id=i + 1,
                sprecher='Sprecher',
                sprecher_original='Sprecher',
                text=bereinigt,
                saetze=saetze,
            ))
        
        return turns
    
    @staticmethod
    def _default_sentence_tokenizer(language):
        """Gibt einen Satz-Tokenizer für die Sprache zurück."""
        lang_map = {
            'de': 'german', 'en': 'english', 'fr': 'french',
            'es': 'spanish', 'it': 'italian', 'pt': 'portuguese',
            'nl': 'dutch', 'tr': 'turkish',
        }
        lang = lang_map.get(language, 'english')

        def regex_splitter(t: str):
            return [s.strip() for s in re.split(r'(?<=[.!?])\s+', t) if s.strip()]

        try:
            from nltk.tokenize import sent_tokenize

            def tok(t: str):
                try:
                    return sent_tokenize(t, language=lang)
                except LookupError:
                    return regex_splitter(t)

            return tok
        except ImportError:
            return regex_splitter
    
    # ---- Zugriff ----
    
    def get_turns(self, sprecher=None):
        """Gibt Turns zurück, optional gefiltert nach Sprecher."""
        if sprecher is None:
            return self.turns
        return [t for t in self.turns if t.sprecher == sprecher]
    
    def get_befragte_turns(self):
        """
        Gibt nur die Turns der befragten Person zurück (nicht Interviewer).
        
        FIX: Nutzt != "Interviewer" statt == "Befragter" für Robustheit.
        """
        return [t for t in self.turns if t.sprecher != "Interviewer"]
    
    def get_interviewer_turns(self):
        """Gibt nur die Turns des Interviewers zurück."""
        return [t for t in self.turns if t.sprecher == "Interviewer"]
    
    def get_annotations(self, modul=None, kategorie=None, turn_id=None):
        """Filtert Annotations."""
        result = self.annotations
        if modul:
            result = [a for a in result if a.modul == modul]
        if kategorie:
            result = [a for a in result if a.kategorie == kategorie]
        if turn_id:
            result = [a for a in result if a.turn_id == turn_id]
        return result
    
    def add_annotation(self, annotation):
        """Fügt eine Annotation hinzu."""
        self.annotations.append(annotation)
    
    # ---- Export ----
    
    def annotations_to_jsonl(self, filepath):
        """Exportiert alle Annotations als JSONL."""
        with open(filepath, 'w', encoding='utf-8') as f:
            for a in self.annotations:
                d = a.to_dict()
                d['doc_id'] = self.doc_id
                f.write(json.dumps(d, ensure_ascii=False) + '\n')
    
    def summary(self):
        """Gibt eine Zusammenfassung des Dokuments zurück."""
        n_turns = len(self.turns)
        n_befragte = len(self.get_befragte_turns())
        n_interviewer = len(self.get_interviewer_turns())
        n_saetze = sum(t.n_saetze for t in self.turns)
        n_woerter = sum(t.n_woerter for t in self.turns)
        n_annotations = len(self.annotations)
        
        module_counts = {}
        for a in self.annotations:
            module_counts[a.modul] = module_counts.get(a.modul, 0) + 1
        
        return {
            'doc_id': self.doc_id,
            'language': self.language,
            'n_turns': n_turns,
            'n_interviewer_turns': n_interviewer,
            'n_befragte_turns': n_befragte,
            'n_saetze': n_saetze,
            'n_woerter': n_woerter,
            'n_annotations': n_annotations,
            'annotations_per_module': module_counts,
            'parse_mode': self.metadata.get('parse_mode', 'unknown'),
            'detected_speakers': self.metadata.get('detected_speakers', []),
            'speaker_mapping': self.metadata.get('speaker_mapping', {}),
        }
    
    def print_turn_overview(self, max_text_length=80):
        """Druckt eine Übersicht aller Turns."""
        print(f"=== {self.doc_id}: {len(self.turns)} Turns ===")
        print(f"Erkannte Sprecher: {self.metadata.get('detected_speakers', [])}")
        print(f"Mapping: {self.metadata.get('speaker_mapping', {})}")
        print("-" * 60)
        for t in self.turns:
            text_preview = t.text[:max_text_length] + "..." if len(t.text) > max_text_length else t.text
            orig = f" ({t.sprecher_original})" if t.sprecher_original != t.sprecher else ""
            print(f"[{t.turn_id}] {t.sprecher}{orig}: {text_preview}")
        print("-" * 60)
        print(f"Interviewer-Turns: {len(self.get_interviewer_turns())}")
        print(f"Befragten-Turns: {len(self.get_befragte_turns())}")


# ============================================================
# CORPUS — Sammlung von Interviews
# ============================================================

@dataclass
class Corpus:
    """
    Sammlung von Interviews. Ermöglicht Batch-Analyse und Vergleich.
    """
    name: str = "corpus"
    documents: list = field(default_factory=list)
    
    def add(self, doc):
        """Fügt ein Document hinzu."""
        self.documents.append(doc)
    
    def get(self, doc_id):
        """Findet ein Document nach ID."""
        for doc in self.documents:
            if doc.doc_id == doc_id:
                return doc
        return None
    
    def all_annotations(self, modul=None):
        """Alle Annotations über alle Dokumente, optional gefiltert."""
        result = []
        for doc in self.documents:
            anns = doc.get_annotations(modul=modul)
            for a in anns:
                d = a.to_dict()
                d['doc_id'] = doc.doc_id
                result.append(d)
        return result
    
    def summary_table(self):
        """Vergleichstabelle über alle Dokumente."""
        import pandas as pd
        rows = [doc.summary() for doc in self.documents]
        return pd.DataFrame(rows)
    
    def export_all_annotations(self, filepath):
        """Exportiert alle Annotations aller Dokumente als JSONL."""
        with open(filepath, 'w', encoding='utf-8') as f:
            for doc in self.documents:
                for a in doc.annotations:
                    d = a.to_dict()
                    d['doc_id'] = doc.doc_id
                    f.write(json.dumps(d, ensure_ascii=False) + '\n')
    
    def __len__(self):
        return len(self.documents)
    
    def __repr__(self):
        return f"Corpus('{self.name}', {len(self.documents)} documents)"
