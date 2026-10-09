import copy

from pipeline.diff import diff, load_current


def test_no_change_is_empty():
    p = load_current()
    assert diff(p, copy.deepcopy(p)) == []


def test_detects_status_target_and_verification_changes():
    old = load_current()
    new = copy.deepcopy(old)
    cid = new["commitments"][0]["id"]
    new["commitments"][0]["target"] = 99
    st = next(s for s in new["statuses"] if s["commitment_id"] == cid)
    st["status"] = "milestone-reported"
    sid = next(iter(new["verification"]["results"]))
    new["verification"]["results"][sid]["result"] = "failed"
    out = "\n".join(diff(old, new))
    assert f"{cid} target" in out and f"{cid} status" in out and f"source {sid} verification" in out
