# Evaluation: blind second extraction

## What was done
A second extractor (a smaller model, Claude Haiku) was given only the twelve extraction notes in `data/real/extracts/`. It was not shown the ledger, the schemas or the plan. It was asked to list every AI-related commitment and every figure that appears only in media notes. Its raw output is in `data/real/blind_extraction.json`. The comparison below was made by hand.

## Results
| Check | Result |
| --- | --- |
| Commitments in the ledger that the blind pass also found | 22 of 24 (the two it missed: C09 "first for proactive legislation"; C16 AiNative 20,000, which it listed only as a media figure) |
| Measurable targets the blind pass found that the ledger lacked | 1: the 60% low-digital-skill workforce target (S12). Added as C25. |
| Blind-pass numeric items left out on purpose | GDP doubling and the cybersecurity index rank (not AI commitments), the 11 million daily interactions (a design capacity), the Security Operations Centre user count (a current figure) |
| Media-only figures in the ledger's claims that the blind pass also flagged | 5 of 5 |
| Kind labels | The blind pass called nearly everything a "deliverable" or "measurable target" and had no category for assessments or inputs, so kind agreement is not reported as a number. |

The blind pass produced 46 items against 24 because it counted reported achievements (for example TAMM results) as commitments. The ledger treats achievements as evidence, not as commitments.

## What this does and does not show
- It shows that a second reader working from the same notes finds almost the same commitments, and that the one missed target was findable.
- It does not show that the notes are faithful to the web pages. Both passes read the same notes. Faithfulness to the pages is checked only by anchors and hashes, and by the human spot-check in `docs/REVIEW_CHECKLIST.md`.
- n is small (24 and 5). Treat the agreement figures as a sanity check, not a measured accuracy.
- The second extractor is a model. This is not human validation.
