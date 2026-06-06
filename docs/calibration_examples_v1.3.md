# RJA v1.3 — Calibration: worked boundary examples for relation_type

These are the three turns where the human coder (Achim) diverged from both LLM coders.
On inspection, two of the three are not irreducible disagreement but **mis-keyings of the
decision rule** that a worked example fixes; one is a genuine ambiguity that needs a rule
clarification. Use these in coder training.

> Honest note on adjudication: the "ruling" below applies the manual's own decision rule.
> Because the LLMs were prompted with that rule, their agreement with the ruling is partly
> built in. The point is not "the LLM was right" but "the rule has a determinate answer here
> that a human can be trained to reach."

---

## Boundary 1 — T3: recurring "soft no". gatekeeping vs anticipatory_gatekeeping
> M: "… Wenn ich gesagt habe, ich möchte eine Ausbildung machen, kam: 'Sind Sie sicher, dass Sie das schaffen?' … Es war nie direkt ein Nein. Es war eher ein weiches Nein."

- **Human read:** anticipatory_gatekeeping + voice_asymmetry (primary: voice, dignity)
- **LLM read:** gatekeeping + justification_asymmetry (primary: justification, recognition)
- **Genuinely ambiguous?** Partly. The turn reports the institution's *responses to stated wishes* (Ausbildung/arbeiten/studieren) — these are real, if softly negated, access decisions. That is gatekeeping (decisions reported), not anticipatory (self-regulation before evaluation).
- **RULING → gatekeeping.** Asymmetry: she names having to *justify wishes* ("schon für Wünsche") → **justification_asymmetry** (ranks above voice_asymmetry in the tie-break; her wishes are not merely unheeded, they must be defended).
- **RULE CLARIFICATION (add to manual):** *A recurring pattern of soft refusals to stated requests is `gatekeeping`, not `anticipatory_gatekeeping`. Anticipatory_gatekeeping requires the absence of a reported decision — only the speaker's self-management in advance of one.*

## Boundary 2 — T4: managing affect ("die richtige Temperatur"). The clearest mis-keying
> M: "… Wenn man laut wird, dann heißt es: schwierig … Also versucht man, genau die richtige Temperatur zu haben."

- **Human read:** multi_institutional_configuration + primary: representation
- **LLM read:** anticipatory_gatekeeping + definitional_power
- **Assessment:** T4 describes *self-regulation of affect in anticipation of evaluation* — the textbook case of **anticipatory_gatekeeping**. There is no *contradiction between two named institutions* here, so `multi_institutional_configuration` is mis-applied (that pattern belongs to T7/T8). This is a training error, not a real ambiguity.
- **RULING → anticipatory_gatekeeping.** Teaching point: `multi_institutional_configuration` requires *two or more explicitly named, contradictory* institutional demands in the turn. Affect-management for a single anticipated evaluator is anticipatory_gatekeeping.

## Boundary 3 — T5: rehearsing before appointments. Same mis-keying as T4
> M: "Ich habe manchmal vor Terminen geübt, wie ich spreche … danach war ich völlig erschöpft. Nicht wegen des Inhalts, sondern wegen dieser Rolle."

- **Human read:** gatekeeping + resource_asymmetry (primary: dignity, access)
- **LLM read:** anticipatory_gatekeeping + definitional_power/recognition
- **Assessment:** "vor Terminen geübt" = preparation *before* an encounter; no decision is made *in* the turn → **anticipatory_gatekeeping**, not gatekeeping. `resource_asymmetry` does not fit (no material resource is at issue); the operative mechanism is the institution's power to define acceptable self-presentation → **definitional_power**.
- **RULING → anticipatory_gatekeeping + definitional_power.** Teaching point: rehearsal/preparation language ("vor … geübt", "ich habe mir gesagt") is a reliable cue for anticipatory_gatekeeping.

---

## What this implies
Of the three relation_type divergences, **two (T4, T5) are correctable mis-keyings** and **one (T3)
needs a one-line rule clarification**. So the human–LLM gap on relation_type is substantially
*trainable* — it is not evidence that the category is hopeless, but that the manual needs these
three worked examples plus the T3 clarification. The genuinely interpretive residue (which two
dimensions are *primary*, fine asymmetry distinctions) is smaller than the raw kappa suggested.

**Next test:** after adding these examples to the manual, re-code with a human and check whether
relation_type agreement rises. That isolates "trainable" from "irreducible" divergence.
