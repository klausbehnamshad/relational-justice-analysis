# RJA v1.3 — Instructions for human coders

Goal: produce independent human codings of the 10 RJA-I turns so we can measure
human reliability (human-vs-human and human-vs-LLM). This is the validity gate the
LLM-LLM pilots cannot provide.

## What to read first (in order)
1. `quick_reference_v1.3.md` — the rules, one page. Now includes the relation_type **boundary cues**.
2. `calibration_examples_v1.3.md` — three worked examples (T3, T4, T5) showing how the
   relation_type decision rule resolves the cases where coders previously diverged. Read these
   before you start; they are the most common mistakes.

## What to do
1. Open `human_coding_worksheet_v1.3.md`. For **all 10 turns**, fill the JSON skeleton.
2. Code each turn **independently** — do not look at anyone else's coding (LLM or human) first.
3. Replace every placeholder (`a|b|c` strings) with ONE chosen value. List a justice dimension
   only if its salience is medium or high. Set `vulnerability` to `null` if no exposure is present.
4. Put your own id in every `coder_id` (e.g. `H1` for the first human, `H2` for the second).
5. Save your 10 objects as a JSON array.

## Where to save
- First human (e.g. Achim), all 10 turns → `coderH1.json`
- Second human → `coderH2.json`

## ⚠️ The answer file must be VALID JSON — this broke both previous submissions
Your saved file must contain **only a JSON array**, nothing else. It must start with `[` and end with `]`.
Concretely, do NOT:
- put a filename or title line at the top (e.g. `5. coderH1.json`) — the file must begin with `[`;
- write `//` comments (e.g. `// hier fehlt das Komma`) — JSON has no comments;
- leave trailing commas before `}` or `]`;
- paste the worksheet prose, the quick-reference, or the calibration examples into the answer file —
  copy out ONLY the filled `{ … }` objects;
- leave placeholder pipes (`"acute | chronic | latent"`) — replace each with ONE chosen value.

If you want to leave a note, put it inside a field value, e.g. in `audit.rationale`.
Quick self-check before sending: paste the file into any JSON validator (or run
`python -c "import json;json.load(open('coderH1.json'))"`) — it must load without error.

## ⚠️ Use the text-locked template — keep the turn numbering fixed
Edit **`coderH_TEMPLATE_with_text.json`** directly. Each object already contains the correct
`turn_id` AND the verbatim turn in `_text_DO_NOT_EDIT`. **Do not change `turn_id`, do not renumber,
do not re-segment the turns, do not add or remove turns.** Fill exactly these 10 objects, all 10 of
them. (Previous submissions used a different numbering from the full transcript, which made them
impossible to compare — the locked text prevents that.) The `_`-prefixed fields are ignored by the
scorer, so you may leave them as-is.

## Then (automated)
The reliability report runs in seconds:
```
python v1.3/tools/reliability.py v1.3/pilot/coderH1.json v1.3/pilot/coderH2.json --label "v1.3 human-vs-human" --md v1.3/pilot/report_H1_vs_H2.md
python v1.3/tools/reliability.py v1.3/pilot/coderH1.json v1.3/pilot/coderA.json   --label "v1.3 human-vs-LLM"   --md v1.3/pilot/report_H1_vs_A.md
```

## Note for Achim
You coded T1–T5 against v1.2 (saved as `v1.2/pilot/coderH.json`, migrated to
`v1.3/pilot/coderH_migrated.json`). For the clean v1.3 gate, please (a) finish **T6–T10** and
(b) re-check T3–T5 against the new boundary cues — these were the three turns where your reading
and the LLM's diverged, and the calibration examples explain the intended resolution.
