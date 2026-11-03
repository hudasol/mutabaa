"""Regression freeze. Existing outputs at v1.6.0 must not change when new work is added.

The file tests/frozen/v1_6_0.json was written before the v1.7.0 to v1.9.0 work began. The first 25
public commitments keep the same checks, scores and questions, and the synthetic experiments E1 to E4,
the sweep, the portfolio ranking and the own file golden cases keep the same bytes of meaning.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FROZEN = json.loads((ROOT / "tests" / "frozen" / "v1_6_0.json").read_text(encoding="utf-8"))


def _digest(path: str) -> str:
    data = json.loads((ROOT / path).read_text(encoding="utf-8"))
    text = json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def test_frozen_hashes_of_synthetic_results_and_goldens():
    for path, want in FROZEN["sha256"].items():
        assert _digest(path) == want, f"{path} changed after the v1.6.0 freeze"


def test_first_public_commitments_keep_their_scores():
    rows = json.loads((ROOT / "data/golden/score.json").read_text(encoding="utf-8"))
    now = {r["commitment_id"]: r for r in rows}
    for row in FROZEN["score_rows"]:
        assert now[row["commitment_id"]] == row, row["commitment_id"]


def test_first_public_commitments_keep_their_questions():
    now = json.loads((ROOT / "data/golden/questions.json").read_text(encoding="utf-8"))
    for cid, row in FROZEN["question_rows"].items():
        assert now[cid] == row, cid
