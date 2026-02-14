"""
core/export.py – Standardisierte Export-Formate.
"""

import json
import os
import pandas as pd
from datetime import datetime


def export_annotations_jsonl(corpus, filepath):
    """Exportiert alle Annotations als JSONL."""
    with open(filepath, 'w', encoding='utf-8') as f:
        for doc in corpus.documents:
            for ann in doc.annotations:
                row = ann.to_dict()
                row['doc_id'] = doc.doc_id
                row['language'] = doc.language
                f.write(json.dumps(row, ensure_ascii=False) + '\n')
    total = sum(len(doc.annotations) for doc in corpus.documents)
    print(f"  {total} Annotations → {filepath}")


def export_turn_summary(corpus, modules_dict, filepath):
    """Exportiert Turn-Level-Zusammenfassung als CSV."""
    rows = []
    for doc in corpus.documents:
        for turn in doc.get_befragte_turns():
            row = {
                'doc_id': doc.doc_id, 'turn_id': turn.turn_id,
                'sprecher': turn.sprecher, 'n_woerter': turn.n_woerter,
                'n_saetze': turn.n_saetze, 'text_vorschau': turn.text[:150],
            }
            for mname, modul in modules_dict.items():
                anns = doc.get_annotations(modul=modul.modul_id, turn_id=turn.turn_id)
                row[f'{mname}_n'] = len(anns)
                row[f'{mname}_kat'] = '; '.join(sorted(set(a.kategorie for a in anns)))
            total = len(doc.get_annotations(turn_id=turn.turn_id))
            row['total_n'] = total
            row['total_dichte'] = round((total / max(turn.n_woerter, 1)) * 100, 1)
            rows.append(row)
    pd.DataFrame(rows).to_csv(filepath, index=False, encoding='utf-8')
    print(f"  {len(rows)} Turns → {filepath}")


def export_doc_summary(corpus, filepath):
    """Exportiert Interview-Level-Kennwerte als CSV."""
    pd.DataFrame([doc.summary() for doc in corpus.documents]).to_csv(
        filepath, index=False, encoding='utf-8')
    print(f"  {len(corpus)} Dokumente → {filepath}")


def export_excel(corpus, modules_dict, filepath):
    """Exportiert alles als Excel mit mehreren Sheets."""
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        # Sheet 1: Dokument-Übersicht
        pd.DataFrame([doc.summary() for doc in corpus.documents]).to_excel(
            writer, sheet_name='Dokumente', index=False)
        
        # Sheet 2: Turn-Summary
        rows = []
        for doc in corpus.documents:
            for turn in doc.get_befragte_turns():
                row = {'doc_id': doc.doc_id, 'turn_id': turn.turn_id,
                       'n_woerter': turn.n_woerter}
                for mname, modul in modules_dict.items():
                    anns = doc.get_annotations(modul=modul.modul_id, turn_id=turn.turn_id)
                    row[f'{mname}_n'] = len(anns)
                rows.append(row)
        pd.DataFrame(rows).to_excel(writer, sheet_name='Turns', index=False)
        
        # Sheet 3: Alle Annotations
        ann_rows = []
        for doc in corpus.documents:
            for a in doc.annotations:
                d = a.to_dict()
                d['doc_id'] = doc.doc_id
                ann_rows.append(d)
        if ann_rows:
            pd.DataFrame(ann_rows).to_excel(writer, sheet_name='Annotations', index=False)
    
    print(f"  Excel → {filepath}")


def export_all(corpus, modules_dict, output_dir):
    """Exportiert alle Formate auf einmal."""
    os.makedirs(output_dir, exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M')
    
    print(f"=== Export ({ts}) ===")
    export_annotations_jsonl(corpus, os.path.join(output_dir, f'annotations_{ts}.jsonl'))
    export_turn_summary(corpus, modules_dict, os.path.join(output_dir, f'turn_summary_{ts}.csv'))
    export_doc_summary(corpus, os.path.join(output_dir, f'doc_summary_{ts}.csv'))
    export_excel(corpus, modules_dict, os.path.join(output_dir, f'analyse_{ts}.xlsx'))
    print("✅ Export abgeschlossen.")
