"""
core/integration.py – Integrationsschicht

Das fehlende Stück: Module A–D produzieren Annotations und Claims
jeweils für sich. Diese Schicht führt sie zusammen und sucht nach
CROSS-MODULE-MUSTERN.

Erzeugt:
    - Triangulationsbefunde: Wo stimmen mehrere Module überein?
    - Spannungsfelder: Wo widersprechen sich die Signale?
    - Verdichtungsberichte: Welche Turns sind analytisch am ergiebigsten?
    - Hypothesen: Formulierte Prüffragen für die Feinanalyse

Jeder Output ist ein epistemischer Vorschlag, kein Befund.
"""


class Integrator:
    """
    Führt die Ergebnisse aller Module zusammen.
    
    Verwendung:
        integrator = Integrator(document, mod_a, mod_b, mod_c, mod_d)
        report = integrator.vollbericht()
    """
    
    def __init__(self, document, mod_a, mod_b, mod_c, mod_d):
        self.doc = document
        self.mod_a = mod_a
        self.mod_b = mod_b
        self.mod_c = mod_c
        self.mod_d = mod_d
    
    def vollbericht(self):
        """
        Erzeugt den integrierten Analysebericht.
        
        Returns:
            Dict mit:
                - turn_profile: Pro Turn alle Module zusammengeführt
                - verdichtungsstellen: Top-N analytisch dichteste Turns
                - triangulationen: Cross-Module-Übereinstimmungen
                - hypothesen: Formulierte Prüffragen
                - claims: Alle Claims aus allen Modulen
        """
        return {
            'turn_profile': self._turn_profile(),
            'verdichtungsstellen': self._verdichtungsstellen(),
            'triangulationen': self._triangulieren(),
            'hypothesen': self._hypothesen_generieren(),
            'claims': self._alle_claims(),
        }
    
    # ================================================================
    # TURN PROFILE – Alles auf einen Blick pro Turn
    # ================================================================
    
    def _turn_profile(self):
        """Integriertes Profil pro Turn mit allen Modulen."""
        profiles = []
        
        a_summary = {r['turn_id']: r for r in self.mod_a.zusammenfassung(self.doc)}
        b_summary = {r['turn_id']: r for r in self.mod_b.zusammenfassung(self.doc)}
        c_summary = {r['turn_id']: r for r in self.mod_c.zusammenfassung(self.doc)}
        d_summary = {r['turn_id']: r for r in self.mod_d.zusammenfassung(self.doc)}
        
        for turn in self.doc.get_befragte_turns():
            tid = turn.turn_id
            
            a = a_summary.get(tid, {})
            b = b_summary.get(tid, {})
            c = c_summary.get(tid, {})
            d = d_summary.get(tid, {})
            
            # Flags sammeln
            flags = []
            
            # Verlaufskurve erkannt?
            if 'VERLAUFSKURVE' in a.get('prozessstrukturen', ''):
                flags.append('VERLAUFSKURVE')
            if 'WANDLUNG' in a.get('prozessstrukturen', ''):
                flags.append('WANDLUNG')
            
            # Hohe affektive Intensität?
            if d.get('marker_dichte', 0) > 5:
                flags.append('AFFEKT_HOCH')
            
            # Erleidend/passiv?
            if b.get('dominant_agency') == 'ERLEIDEND_PASSIV':
                flags.append('PASSIV')
            
            # Mehrere Frames aktiv?
            if c.get('n_frames_aktiv', 0) >= 3:
                flags.append('MULTI_FRAME')
            
            # Textsorten-Wechsel?
            if a.get('n_transitions', 0) >= 2:
                flags.append('TEXTSORTEN_WECHSEL')
            
            profile = {
                'turn_id': tid,
                'n_woerter': turn.n_woerter,
                'text_vorschau': turn.text[:150],
                # Modul A
                'textsorten_sequenz': a.get('sequenz_kurz', ''),
                'prozessstrukturen': a.get('prozessstrukturen', '-'),
                'n_transitions': a.get('n_transitions', 0),
                # Modul B
                'dominant_agency': b.get('dominant_agency', '-'),
                'agency_dichte': b.get('agency_dichte', 0),
                'pronomen': b.get('pronomen', {}),
                # Modul C
                'dominant_frame': c.get('dominant_frame', '-'),
                'n_frames_aktiv': c.get('n_frames_aktiv', 0),
                'frames': c.get('frames', {}),
                # Modul D
                'affekt_dichte': d.get('marker_dichte', 0),
                'affekt_dimensionen': d.get('aktive_dimensionen', []),
                # Integration
                'flags': flags,
                'n_flags': len(flags),
                'total_annotations': len(self.doc.get_annotations(turn_id=tid)),
            }
            profiles.append(profile)
        
        return profiles
    
    # ================================================================
    # VERDICHTUNGSSTELLEN – Analytisch ergiebigste Turns
    # ================================================================
    
    def _verdichtungsstellen(self, n=5):
        """
        Identifiziert die Turns mit der höchsten analytischen Dichte.
        
        Kriterien (gewichtet):
            - Anzahl Flags (Cross-Module-Signale)
            - Affektive Intensität
            - Frame-Komplexität
            - Prozessstruktur-Überlagerung
            - Textsorten-Wechsel
        """
        profiles = self._turn_profile()
        
        for p in profiles:
            score = 0
            reasons = []
            
            # Flags (stärkstes Signal)
            score += p['n_flags'] * 3
            if p['flags']:
                reasons.append(f"Flags: {', '.join(p['flags'])}")
            
            # Affektive Intensität
            if p['affekt_dichte'] > 5:
                score += 3
                reasons.append(f"Hohe Affekt-Dichte: {p['affekt_dichte']}%")
            elif p['affekt_dichte'] > 2:
                score += 1
            
            # Frame-Komplexität
            if p['n_frames_aktiv'] >= 3:
                score += 2
                reasons.append(f"{p['n_frames_aktiv']} Frames aktiv")
            
            # Textsorten-Wechsel
            if p['n_transitions'] >= 2:
                score += 2
                reasons.append(f"{p['n_transitions']} Textsorten-Wechsel")
            
            # Prozessstruktur
            if p['prozessstrukturen'] != '-':
                score += 2
                reasons.append(f"Prozessstruktur: {p['prozessstrukturen']}")
            
            p['verdichtung_score'] = score
            p['verdichtung_reasons'] = reasons
        
        profiles.sort(key=lambda x: -x['verdichtung_score'])
        return profiles[:n]
    
    # ================================================================
    # TRIANGULATION – Wo stimmen Module überein?
    # ================================================================
    
    def _triangulieren(self):
        """
        Sucht nach Stellen, an denen mehrere Module auf dasselbe hindeuten.
        
        Das ist methodisch das stärkste Signal: Wenn Narration, Agency,
        Diskurs UND Affekt in dieselbe Richtung zeigen, ist das mehr
        als eine einzelne Annotation.
        """
        triangulationen = []
        profiles = self._turn_profile()
        
        for p in profiles:
            tid = p['turn_id']
            muster = []
            
            # Muster 1: KRISE
            # Verlaufskurve + passiv + hoher Affekt
            is_krise = (
                'VERLAUFSKURVE' in p['flags'] and
                ('PASSIV' in p['flags'] or p['dominant_agency'] == 'ERLEIDEND_PASSIV') and
                p['affekt_dichte'] > 2
            )
            if is_krise:
                muster.append({
                    'muster': 'KRISE',
                    'beschreibung': 'Narrative Verlaufskurve + passives Subjekt + hohe affektive Intensität',
                    'module': ['A (Verlaufskurve)', 'B (Erleidend)', 'D (Affekt)'],
                    'prueffrage': 'Handelt es sich um einen biografischen Wendepunkt? '
                                 'Wie wird die Krise narrativ verarbeitet?',
                })
            
            # Muster 2: WIDERSTAND
            # Systemkritik + aktive Agency + moralische Positionierung
            has_systemkritik = 'SYSTEMVERSAGEN' in p.get('frames', {})
            is_aktiv = p['dominant_agency'] == 'AKTIV_HANDELND' or p['dominant_agency'] == 'MORALISCH_REFLEKTIEREND'
            if has_systemkritik and is_aktiv:
                muster.append({
                    'muster': 'WIDERSTAND',
                    'beschreibung': 'Systemkritik + aktive/moralische Agency',
                    'module': ['B (Agency)', 'C (Systemversagen)'],
                    'prueffrage': 'Positioniert sich die Person als widerständiges Subjekt? '
                                 'Gegen wen/was richtet sich der Widerstand?',
                })
            
            # Muster 3: AMBIVALENTES FESTHALTEN
            # Berufung + Ökonomisierung + Ambivalenz-Affekt
            has_berufung = 'BERUFUNG' in p.get('frames', {})
            has_oeko = 'OEKONOMISIERUNG' in p.get('frames', {})
            has_ambivalenz = 'AMBIVALENZ' in p.get('affekt_dimensionen', [])
            if has_berufung and (has_oeko or has_ambivalenz):
                muster.append({
                    'muster': 'AMBIVALENTES_FESTHALTEN',
                    'beschreibung': 'Berufungs-Frame + ökonomischer Druck/Ambivalenz',
                    'module': ['C (Berufung + Ökonomisierung)', 'D (Ambivalenz)'],
                    'prueffrage': 'Wie verhandelt die Person den Widerspruch zwischen '
                                 'innerer Überzeugung und äußerem Druck?',
                })
            
            # Muster 4: NARRATIVE TRANSFORMATION
            # Wandlung + Frame-Wechsel + Textsorten-Wechsel
            has_wandlung = 'WANDLUNG' in p['flags']
            has_wechsel = p['n_transitions'] >= 1
            if has_wandlung and has_wechsel:
                muster.append({
                    'muster': 'NARRATIVE_TRANSFORMATION',
                    'beschreibung': 'Wandlung + Textsorten-Wechsel → mögliche Umorientierung',
                    'module': ['A (Wandlung)', 'A (Textsorten-Wechsel)'],
                    'prueffrage': 'Ist hier ein Übergang von der Erleidens- zur '
                                 'Handlungsperspektive erkennbar?',
                })
            
            # Muster 5: AFFEKTIVE VERDICHTUNG + KÖRPER
            has_koerper = 'KOERPERLICHER_VERWEIS' in p.get('affekt_dimensionen', [])
            if has_koerper and p['affekt_dichte'] > 3:
                muster.append({
                    'muster': 'VERKÖRPERTER_AFFEKT',
                    'beschreibung': 'Hohe Affekt-Dichte + körperliche Verweise',
                    'module': ['D (Intensität)', 'D (Körperlichkeit)'],
                    'prueffrage': 'Wird hier etwas ausgedrückt, das sprachlich nicht '
                                 'vollständig sagbar ist? Leibliche Dimension prüfen.',
                })
            
            if muster:
                triangulationen.append({
                    'turn_id': tid,
                    'muster': muster,
                    'n_muster': len(muster),
                    'text_vorschau': p['text_vorschau'],
                })
        
        # Nach Anzahl der Muster sortieren
        triangulationen.sort(key=lambda x: -x['n_muster'])
        return triangulationen
    
    # ================================================================
    # HYPOTHESEN – Formulierte Prüffragen
    # ================================================================
    
    def _hypothesen_generieren(self):
        """
        Generiert übergreifende Hypothesen aus dem Gesamtbild.
        
        NICHT: "Das Interview zeigt X."
        SONDERN: "Es gibt Hinweise auf X. Prüfe anhand von Y."
        """
        hypothesen = []
        profiles = self._turn_profile()
        
        if not profiles:
            return hypothesen
        
        # 1. Gesamtdynamik: Handeln → Erleiden oder umgekehrt?
        agency_verlauf = [p['dominant_agency'] for p in profiles]
        
        aktiv_indices = [i for i, a in enumerate(agency_verlauf) if a == 'AKTIV_HANDELND']
        passiv_indices = [i for i, a in enumerate(agency_verlauf) if a == 'ERLEIDEND_PASSIV']
        
        if aktiv_indices and passiv_indices:
            avg_aktiv = sum(aktiv_indices) / len(aktiv_indices)
            avg_passiv = sum(passiv_indices) / len(passiv_indices)
            
            if avg_aktiv < avg_passiv:
                hypothesen.append({
                    'hypothese': 'Das Interview zeigt eine mögliche Verlaufskurve: '
                                'Aktives Handeln zu Beginn weicht zunehmend einem Erleidensmodus.',
                    'evidenz': f"Aktive Agency dominant in frühen Turns, passive in späteren.",
                    'prueffrage': 'Handelt es sich um eine biografische Verlaufskurve '
                                 'im Sinne Schützes?',
                    'zu_pruefen': 'Originalstellen in den markierten Turns lesen.',
                })
            elif avg_passiv < avg_aktiv:
                hypothesen.append({
                    'hypothese': 'Das Interview zeigt eine mögliche Wandlungsdynamik: '
                                'Von passivem Erleiden zu aktiver Gestaltung.',
                    'evidenz': f"Passive Agency dominant in frühen Turns, aktive in späteren.",
                    'prueffrage': 'Handelt es sich um einen Wandlungsprozess im Sinne Schützes?',
                    'zu_pruefen': 'Wo genau kippt die Perspektive? Gibt es einen Auslöser?',
                })
        
        # 2. Frame-Dominanz und ihre Implikationen
        alle_frames = {}
        for p in profiles:
            for f, c in p.get('frames', {}).items():
                alle_frames[f] = alle_frames.get(f, 0) + c
        
        if alle_frames:
            dominant = max(alle_frames, key=alle_frames.get)
            total = sum(alle_frames.values())
            pct = alle_frames[dominant] / total * 100 if total > 0 else 0
            
            if pct > 35:
                hypothesen.append({
                    'hypothese': f"Der Frame '{dominant}' dominiert das Interview ({pct:.0f}%). "
                                f"Dies könnte der zentrale Deutungsrahmen der befragten Person sein.",
                    'evidenz': f"Frame-Verteilung: {alle_frames}",
                    'prueffrage': f"Ist '{dominant}' eine genuine Deutung der Person oder "
                                 f"ein Effekt der Interviewführung/Fragestellung?",
                    'zu_pruefen': 'Kommt der Frame in Antworten auf verschiedene Fragen vor?',
                })
        
        # 3. Affektive Gesamtdynamik
        affekt_werte = [p['affekt_dichte'] for p in profiles]
        if affekt_werte:
            max_idx = affekt_werte.index(max(affekt_werte))
            max_turn = profiles[max_idx]['turn_id']
            
            # Steigt oder fällt die Intensität?
            if len(affekt_werte) >= 3:
                erste_haelfte = sum(affekt_werte[:len(affekt_werte)//2])
                zweite_haelfte = sum(affekt_werte[len(affekt_werte)//2:])
                
                if zweite_haelfte > erste_haelfte * 1.5:
                    hypothesen.append({
                        'hypothese': 'Die affektive Intensität nimmt im Interviewverlauf zu. '
                                    'Das Gespräch bewegt sich möglicherweise in Richtung '
                                    'einer emotional aufgeladenen Kernproblematik.',
                        'evidenz': f"Erste Hälfte: {erste_haelfte:.1f}, Zweite Hälfte: {zweite_haelfte:.1f}",
                        'prueffrage': 'Führen die Interviewfragen gezielt dorthin, '
                                     'oder öffnet sich die Person sukzessive?',
                        'zu_pruefen': f'Schlüsselstelle: Turn {max_turn}',
                    })
        
        return hypothesen
    
    # ================================================================
    # ALLE CLAIMS SAMMELN
    # ================================================================
    
    def _alle_claims(self):
        """Sammelt Claims aus allen Modulen, die Claims erzeugen."""
        claims = []
        
        # Modul A: Wendepunkt-Kandidaten als Claims
        for wp in self.mod_a.wendepunkt_kandidaten(self.doc):
            claims.append({
                'modul': 'A_narrative',
                'typ': 'WENDEPUNKT',
                'beschreibung': f"Narrativer Wendepunkt-Kandidat in Turn {wp['turn_id']}",
                'evidenz': '; '.join(wp['reasons']),
                'turns': [wp['turn_id']],
                'staerke': wp['score'],
                'prueffrage': 'Markiert dieser Turn tatsächlich einen Wendepunkt '
                             'in der biografischen Erzählung?',
            })
        
        # Modul C: Claims
        if hasattr(self.mod_c, 'generate_claims'):
            for claim in self.mod_c.generate_claims(self.doc):
                claim['modul'] = 'C_diskurs'
                claims.append(claim)
        
        # Modul D: Verdichtungsstellen als Claims
        for stelle in self.mod_d.verdichtungsstellen(self.doc):
            claims.append({
                'modul': 'D_affekt',
                'typ': 'AFFEKTIVE_VERDICHTUNG',
                'beschreibung': f"Affektive Verdichtung in Turn {stelle['turn_id']}",
                'evidenz': '; '.join(stelle['reasons']),
                'turns': [stelle['turn_id']],
                'staerke': stelle['score'],
                'prueffrage': 'Korreliert die affektive Verdichtung mit einem narrativen '
                             'Wendepunkt oder Frame-Wechsel?',
            })
        
        # Nach Stärke sortieren
        claims.sort(key=lambda x: -x.get('staerke', 0))
        return claims
    
    # ================================================================
    # FORMATIERTE AUSGABE
    # ================================================================
    
    def print_bericht(self):
        """Druckt einen lesbaren Gesamtbericht."""
        report = self.vollbericht()
        
        print("=" * 72)
        print("   INTEGRIERTER ANALYSEBERICHT")
        print("   Epistemischer Status: Vorschläge zur Prüfung")
        print("=" * 72)
        
        # 1. Verdichtungsstellen
        print("\n📍 TOP VERDICHTUNGSSTELLEN")
        print("-" * 40)
        for v in report['verdichtungsstellen']:
            print(f"\n  Turn {v['turn_id']} (Score: {v['verdichtung_score']})")
            for r in v['verdichtung_reasons']:
                print(f"    → {r}")
            print(f"    Text: {v['text_vorschau'][:120]}...")
        
        # 2. Triangulationen
        if report['triangulationen']:
            print(f"\n\n🔺 TRIANGULATIONEN (Cross-Module-Muster)")
            print("-" * 40)
            for tri in report['triangulationen']:
                print(f"\n  Turn {tri['turn_id']}:")
                for m in tri['muster']:
                    print(f"    ⚡ {m['muster']}: {m['beschreibung']}")
                    print(f"       Module: {', '.join(m['module'])}")
                    print(f"       ❓ {m['prueffrage']}")
        
        # 3. Claims
        if report['claims']:
            print(f"\n\n📋 CLAIMS ({len(report['claims'])} gesamt)")
            print("-" * 40)
            for i, c in enumerate(report['claims'][:8]):
                modul = c.get('modul', '?')
                print(f"\n  [{i+1}] [{modul}] {c['typ']}")
                print(f"      {c['beschreibung']}")
                print(f"      Evidenz: {c['evidenz'][:120]}")
                print(f"      ❓ {c['prueffrage']}")
        
        # 4. Hypothesen
        if report['hypothesen']:
            print(f"\n\n🧠 HYPOTHESEN")
            print("-" * 40)
            for h in report['hypothesen']:
                print(f"\n  H: {h['hypothese']}")
                print(f"     Evidenz: {h['evidenz']}")
                print(f"     ❓ {h['prueffrage']}")
                print(f"     Zu prüfen: {h['zu_pruefen']}")
        
        print("\n" + "=" * 72)
        print("⚠️  Alle Befunde sind epistemische Vorschläge.")
        print("   Sie ersetzen nicht die qualitative Interpretation.")
        print("   Prüfe die markierten Stellen im Originaltranskript.")
        print("=" * 72)
