"""
core/language.py – Language Gate

Zentraler Mechanismus für Mehrsprachigkeit.
Jedes Modul fragt hier an: "Habe ich Ressourcen für diese Sprache?"
Und bekommt zurück: "Ja (vollständig / light)" oder "Nein".

Prinzip:
    - Regex-Muster: funktionieren immer (wenn im Framebook definiert)
    - Spacy-Modelle: nur wenn installiert → graceful degradation
    - Stoppwörter: NLTK wenn verfügbar, sonst Minimal-Liste
"""

import warnings


# Spacy-Modelle pro Sprache
SPACY_MODELS = {
    'de': 'de_core_news_sm',
    'en': 'en_core_web_sm',
    'fr': 'fr_core_news_sm',
    'es': 'es_core_news_sm',
    'it': 'it_core_news_sm',
    'pt': 'pt_core_news_sm',
    'nl': 'nl_core_news_sm',
}

# NLTK Sprachcodes
NLTK_LANGUAGES = {
    'de': 'german', 'en': 'english', 'fr': 'french',
    'es': 'spanish', 'it': 'italian', 'pt': 'portuguese',
    'nl': 'dutch', 'tr': 'turkish', 'pl': 'polish',
}

# Minimale Stoppwörter als Fallback
MINIMAL_STOPWORDS = {
    'de': {'der', 'die', 'das', 'ein', 'eine', 'und', 'oder', 'aber', 'ist',
           'sind', 'war', 'hat', 'haben', 'ich', 'du', 'er', 'sie', 'es',
           'wir', 'ihr', 'in', 'an', 'auf', 'mit', 'für', 'von', 'zu',
           'nicht', 'auch', 'noch', 'dann', 'wenn', 'als', 'nach', 'bei'},
    'en': {'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'has',
           'have', 'I', 'you', 'he', 'she', 'it', 'we', 'they', 'in', 'on',
           'at', 'with', 'for', 'from', 'to', 'not', 'also', 'then', 'if'},
    'fr': {'le', 'la', 'les', 'un', 'une', 'et', 'ou', 'mais', 'est', 'sont',
           'je', 'tu', 'il', 'elle', 'nous', 'vous', 'ils', 'dans', 'sur',
           'avec', 'pour', 'de', 'ne', 'pas', 'aussi', 'puis', 'si'},
}


class LanguageGate:
    """
    Prüft und stellt sprachspezifische Ressourcen bereit.
    
    Verwendung:
        gate = LanguageGate("de")
        if gate.has_spacy:
            nlp = gate.get_spacy()
            doc = nlp(text)
        # Regex-Muster funktionieren immer
        patterns = gate.get_patterns(framebook_entry)
    """
    
    def __init__(self, language="de"):
        self.language = language
        self._spacy_nlp = None
        self._check_resources()
    
    def _check_resources(self):
        """Prüft, welche Ressourcen verfügbar sind."""
        self.has_spacy = False
        self.has_nltk_stopwords = False
        self.has_nltk_tokenizer = False
        
        # Spacy prüfen
        try:
            import spacy
            model_name = SPACY_MODELS.get(self.language)
            if model_name:
                try:
                    self._spacy_nlp = spacy.load(model_name)
                    self.has_spacy = True
                except OSError:
                    pass
        except ImportError:
            pass
        
        # NLTK prüfen
        try:
            from nltk.corpus import stopwords
            nltk_lang = NLTK_LANGUAGES.get(self.language)
            if nltk_lang:
                try:
                    stopwords.words(nltk_lang)
                    self.has_nltk_stopwords = True
                except LookupError:
                    pass
            
            from nltk.tokenize import sent_tokenize
            try:
                sent_tokenize("Test.", language=nltk_lang or 'english')
                self.has_nltk_tokenizer = True
            except LookupError:
                pass
        except ImportError:
            pass
    
    @property
    def capability_level(self):
        """
        Gibt das Fähigkeitslevel zurück:
            'full': Spacy + NLTK verfügbar
            'light': Nur Regex-basiert
        """
        if self.has_spacy:
            return 'full'
        return 'light'
    
    def get_spacy(self):
        """Gibt das Spacy-Modell zurück oder None."""
        return self._spacy_nlp
    
    def get_stopwords(self):
        """Gibt Stoppwörter zurück (NLTK oder Fallback)."""
        if self.has_nltk_stopwords:
            from nltk.corpus import stopwords
            nltk_lang = NLTK_LANGUAGES[self.language]
            return set(stopwords.words(nltk_lang))
        return MINIMAL_STOPWORDS.get(self.language, set())
    
    def get_patterns(self, framebook_entry):
        """
        Holt die Regex-Muster für die aktuelle Sprache aus einem Framebook-Eintrag.
        
        Args:
            framebook_entry: Dict mit 'indikatoren' → {'de': [...], 'en': [...]}
        
        Returns:
            Liste von Regex-Patterns, oder leere Liste wenn Sprache nicht definiert.
        """
        indikatoren = framebook_entry.get('indikatoren', {})
        patterns = indikatoren.get(self.language, [])
        
        if not patterns:
            # Warnung, aber kein Fehler
            warnings.warn(
                f"Keine Muster für Sprache '{self.language}' in dieser Kategorie. "
                f"Verfügbar: {list(indikatoren.keys())}",
                UserWarning
            )
        
        return patterns
    
    def status_report(self):
        """Gibt einen Statusbericht über verfügbare Ressourcen."""
        report = {
            'language': self.language,
            'capability_level': self.capability_level,
            'spacy': '✅' if self.has_spacy else '❌',
            'nltk_stopwords': '✅' if self.has_nltk_stopwords else '❌',
            'nltk_tokenizer': '✅' if self.has_nltk_tokenizer else '❌',
        }
        return report
    
    def __repr__(self):
        return f"LanguageGate('{self.language}', level='{self.capability_level}')"
