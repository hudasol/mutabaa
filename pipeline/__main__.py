"""Command line: `mutabaa --help` (or `python -m pipeline --help`) lists every command."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import asdict
from pathlib import Path

from . import __version__, agreement, calibration, evaluate, facts, own, robustness, schema_export
from .diff import diff as payload_diff
from .diff import load_at, load_current
from .io import REAL, ROOT, load_real
from .own_report import as_csv, as_json, as_text, assess
from .questions import questions
from .render import refresh, render
from .schemas import Registry
from .score import score
from .sensitivity import summary, sweep
from .status import status
from .synth import generate
from .validate import file_hash, validate
from .verify_live import dumps as dump_report
from .verify_live import run as run_verify
from .verify_live import summarise


def cmd_validate() -> int:
    errors, warnings = validate()
    for w in warnings:
        print(f"warn  {w}")
    for e in errors:
        print(f"ERROR {e}")
    print(f"{len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


def cmd_rehash() -> int:
    p = REAL / "sources.json"
    rows = json.loads(p.read_text(encoding="utf-8"))
    for r in rows:
        r["content_hash"] = file_hash(r["extract_file"])
    p.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"rehashed {len(rows)} sources")
    return 0


SYNTH = ROOT / "data" / "synthetic"
GOLDEN = ROOT / "data" / "golden"


def cmd_synth() -> int:
    """Regenerate the synthetic registry and the golden sensitivity file."""
    reg = generate()
    SYNTH.mkdir(parents=True, exist_ok=True)
    GOLDEN.mkdir(parents=True, exist_ok=True)
    (SYNTH / "registry.json").write_text(
        json.dumps(reg.model_dump(mode="json"), indent=1) + "\n", encoding="utf-8", newline="\n"
    )
    rows = sweep(reg)
    (GOLDEN / "sensitivity.json").write_text(
        json.dumps(rows, indent=1) + "\n", encoding="utf-8", newline="\n"
    )
    print(f"registry: {len(reg.entities)} entities, {len(reg.items)} items; {summary(rows)}")
    return 0


def cmd_verify_live(args: list[str]) -> int:
    """Fetch each source page and check the figures the notes rely on. Needs network access."""
    only = None
    if "--only" in args:
        only = set(args[args.index("--only") + 1].split(","))
    d = load_real()
    rep = run_verify(d.sources, only=only)
    print(summarise(rep))
    if "--write" in args:
        path = REAL / "verification.json"
        old = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"results": {}}
        old["results"].update(rep["results"])
        old.update({k: v for k, v in rep.items() if k != "results"})
        path.write_text(dump_report(old), encoding="utf-8", newline="\n")
        print(f"wrote {path}")
    failed = [k for k, v in rep["results"].items() if v["result"] == "failed"]
    return 1 if failed else 0


ANALYSIS = ROOT / "data" / "analysis"


def compute_analysis(d) -> dict:
    return {
        "robustness": robustness.run(),
        "calibration": calibration.run(d.commitments),
        "agreement": agreement.run(d.commitments),
    }


def cmd_analyse() -> int:
    """Recompute robustness, calibration and agreement results and store them under data/analysis/."""
    ANALYSIS.mkdir(parents=True, exist_ok=True)
    for k, v in compute_analysis(load_real()).items():
        (ANALYSIS / f"{k}.json").write_text(
            json.dumps(v, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
        )
        print(f"wrote data/analysis/{k}.json")
    return 0


def cmd_facts() -> int:
    """Write results/facts.json: every number the documents are allowed to cite."""
    path = facts.write()
    print(f"wrote {path}")
    return 0


TEMPLATES = ROOT / "pipeline" / "templates"
REPORTS = {"EVALUATION.md": ROOT / "docs" / "EVALUATION.md"}


def render_reports() -> dict:
    fx = facts.compute()
    return {out: render((TEMPLATES / name).read_text(encoding="utf-8"), fx) for name, out in REPORTS.items()}


def cmd_report() -> int:
    """Refresh results/facts.json, then render docs/EVALUATION.md from its template and the facts."""
    facts.write()
    for out, text in render_reports().items():
        out.write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {out}")
    return 0


def cmd_sync_docs() -> int:
    """Rewrite the marked numbers in README.md and docs/*.md so that they match results/facts.json."""
    fx = facts.compute()
    changed = 0
    for path in [ROOT / "README.md", *sorted((ROOT / "docs").rglob("*.md"))]:
        old = path.read_text(encoding="utf-8")
        new = refresh(old, fx)
        if new != old:
            path.write_text(new, encoding="utf-8", newline="\n")
            print(f"updated {path.relative_to(ROOT).as_posix()}")
            changed += 1
    print(f"{changed} document(s) updated")
    return 0


def cmd_schema() -> int:
    """Write JSON Schema files for the shared models to schema/."""
    for p in schema_export.write(ROOT / "schema"):
        print(f"wrote {p.relative_to(ROOT).as_posix()}")
    return 0


def cmd_evaluate() -> int:
    """Run the preregistered experiments in PREREGISTRATION.md and write results/*.json, facts and reports."""
    import time

    facts.RESULTS.mkdir(parents=True, exist_ok=True)
    for name, run in evaluate.EXPERIMENTS.items():
        t = time.time()
        res = run()
        path = facts.RESULTS / f"{name}.json"
        path.write_text(json.dumps(res, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
        marks = ", ".join(f"{k} {v['result']}" for k, v in res["predictions"].items())
        print(f"wrote {path.name} in {time.time() - t:.0f}s: {marks}")
    return cmd_report()


def golden_files() -> dict[str, str]:
    """Score and questions for every public commitment: the TypeScript port must reproduce both exactly."""
    d = load_real()
    scores = [score(c) for c in d.commitments]
    sc = [s.model_dump(mode="json") for s in scores]
    qs = {c.id: questions(c, s) for c, s in zip(d.commitments, scores, strict=True)}
    dump = lambda x: json.dumps(x, ensure_ascii=False, indent=1, sort_keys=True) + "\n"  # noqa: E731
    reg = Registry.model_validate(json.loads((SYNTH / "registry.json").read_text(encoding="utf-8")))
    pf = evaluate.portfolio_table(reg)
    return {
        "score.json": dump(sc),
        "questions.json": dump(qs),
        "portfolio.json": dump(pf),
        "own_outputs.json": dump(own_outputs()),
    }


def own_outputs() -> list[dict]:
    """The file reader's result for every case in data/golden/own_inputs.json (the browser must match)."""
    cases = json.loads((GOLDEN / "own_inputs.json").read_text(encoding="utf-8"))
    out = []
    for c in cases:
        try:
            r = own.load(c["name"], c["text"])
        except ValueError as exc:
            out.append({"name": c["name"], "fatal": str(exc)})
            continue
        items = [
            asdict(i) for i in r.items
        ]
        out.append({
            "name": c["name"], "items": items, "errors": r.errors, "rows": r.rows, "rejected": r.rejected,
            "duplicates": r.duplicates, "unmapped": r.unmapped, "truncated": r.truncated,
        })
    return out


def cmd_golden() -> int:
    GOLDEN.mkdir(parents=True, exist_ok=True)
    for name, text in golden_files().items():
        (GOLDEN / name).write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote data/golden/{name}")
    return 0


def cmd_diff(args: list[str]) -> int:
    """python -m pipeline diff [REF]: commitment, status, band and verification changes since REF."""
    ref = args[0] if args else "HEAD~1"
    lines = payload_diff(load_at(ref), load_current())
    print("\n".join(lines) if lines else f"no differences against {ref}")
    return 0


def data_as_of(d):
    return max(s.retrieved for s in d.sources)


def derive():
    d = load_real()
    src = {s.id: s for s in d.sources}
    asof = data_as_of(d)
    scores = [score(c) for c in d.commitments]
    statuses = [status(c, d.evidence, src, asof) for c in d.commitments]
    return d, scores, statuses


def coverage(d) -> list[dict]:
    """For each commitment: how many searches touched it, when last, and what they found."""
    rows = []
    for c in d.commitments:
        qs = [q for q in d.searches if c.id in q.commitment_ids]
        rows.append(
            {
                "commitment_id": c.id,
                "searches": len(qs),
                "last_searched": max((q.searched_on.isoformat() for q in qs), default=None),
                "found_sources": sorted({sid for q in qs for sid in q.found_source_ids}),
                "outcomes": sorted({q.outcome for q in qs}),
            }
        )
    return rows


def evaluation_summary() -> dict:
    """The preregistered results that the site text states: E3 on Portfolio, E4 to E6 on Assurance."""
    res = facts.RESULTS

    def load(name: str) -> dict:
        return json.loads((res / f"{name}.json").read_text(encoding="utf-8"))

    e3, e4, e5, e6 = load("e3")["primary"], load("e4")["rates"], load("e5"), load("e6")
    f5 = e5["facts"]
    keep = ("flagged_share", "recall", "recall_numeric", "recall_other", "precision")
    return {
        "e3": {k: e3[k] for k in ("entities", "moved_3_or_more", "exceed_noise", "noise_only_mean")},
        "e4": {"bootstrap_coverage_at_095": e4["0.95"]["bootstrap"]["coverage"],
               "wilson_coverage_at_095": e4["0.95"]["wilson"]["coverage"]},
        "e5": {
            "units": f5["units"]["value"],
            "located": f5["located"]["value"],
            "blind_recall": f5["blind.recall"]["value"],
            "rules": {k: {m: e5["extractors"][k][m] for m in keep} for k in ("x1", "x2", "x3", "x4")},
        },
        "e6": {"violations": e6["facts"]["violations"]["value"], "killed": e6["facts"]["killed"]["value"],
               "mutants": e6["facts"]["mutants"]["value"]},
    }


def cmd_build() -> int:
    if cmd_validate():
        return 1
    d, scores, statuses = derive()
    out = ROOT / "site" / "src" / "data"
    out.mkdir(parents=True, exist_ok=True)
    qs = {c.id: questions(c, sc) for c, sc in zip(d.commitments, scores, strict=True)}
    payload = {
        "sources": [s.model_dump(mode="json") for s in d.sources],
        "commitments": [c.model_dump(mode="json") for c in d.commitments],
        "evidence": [e.model_dump(mode="json") for e in d.evidence],
        "claims": [k.model_dump(mode="json") for k in d.claims],
        "scores": [s.model_dump(mode="json") for s in scores],
        "statuses": [s.model_dump(mode="json") for s in statuses],
        "questions": qs,
        "coverage": coverage(d),
        "searches": [q.model_dump(mode="json") for q in d.searches],
        "verification": d.verification,
        "analysis": {
            k: json.loads((ANALYSIS / f"{k}.json").read_text(encoding="utf-8"))
            for k in ("robustness", "calibration", "agreement")
        },
        "evaluation": evaluation_summary(),
        "synthetic": json.loads((SYNTH / "registry.json").read_text(encoding="utf-8")),
        "sweep": json.loads((GOLDEN / "sensitivity.json").read_text(encoding="utf-8")),
    }
    body = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=1)
    payload["build"] = {
        "data_as_of": data_as_of(d).isoformat(),
        "payload_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
        "schema": 2,
    }
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=1) + "\n"
    (out / "real.json").write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {out / 'real.json'}")
    return 0


def cmd_own(args: argparse.Namespace) -> int:
    """Score the commitments in the file given on the command line. Exit 1 when a gate is not met."""
    path = Path(args.file)
    try:
        res = own.load(path.name, own.decode(path.read_bytes()))
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        print(f"mutabaa: {path}: {exc}", file=sys.stderr)
        return 2
    rows = assess(res)
    with_q = args.command == "questions" or args.questions
    if args.format == "json":
        out = as_json(res, rows, with_q)
    elif args.format == "csv":
        out = as_csv(rows)
    else:
        out = as_text(res, rows, args.lang, with_q)
    sys.stdout.write(out)
    if res.errors and not rows:
        return 2
    if args.strict and res.errors:
        return 1
    if args.min_ratio is not None and any(r["ratio"] < args.min_ratio for r in rows):
        return 1
    return 0


def cmd_template() -> int:
    sys.stdout.write(own.TEMPLATE)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="mutabaa",
        description="Mutabaa checks whether public commitments can be verified from public information.",
        epilog="Exit codes: 0 success, 1 a gate was not met, 2 the input could not be read.",
    )
    p.add_argument("--version", action="version", version=f"mutabaa {__version__}")
    sub = p.add_subparsers(dest="command", metavar="COMMAND")
    for name, help_ in (
        ("score", "score the commitments in a CSV or JSON file"),
        ("questions", "score a file and list the questions that would close each gap"),
    ):
        q = sub.add_parser(name, help=help_)
        q.add_argument("file", help="a CSV or JSON file; run `mutabaa template` for the columns")
        q.add_argument("--format", choices=("text", "json", "csv"), default="text")
        q.add_argument("--lang", choices=("en", "ar", "both"), default="en", help="question language")
        if name == "score":
            q.add_argument("--questions", action="store_true", help="also list the questions")
        else:
            q.set_defaults(questions=True)
        q.add_argument("--strict", action="store_true", help="exit 1 if any row is rejected")
        q.add_argument("--min-ratio", type=float, metavar="R", help="exit 1 if any score is below R (0 to 1)")
    sub.add_parser("template", help="print a CSV template with the expected columns")
    for name, help_ in (
        ("validate", "integrity checks on the real data"),
        ("rehash", "refresh the source note hashes"),
        ("synth", "regenerate the synthetic registry"),
        ("build", "regenerate site/src/data/real.json"),
        ("analyse", "recompute the exploratory analyses"),
        ("facts", "write results/facts.json"),
        ("report", "render the generated reports"),
        ("sync-docs", "rewrite stale fact markers in the documents"),
        ("schema", "write the JSON Schema files"),
        ("evaluate", "run the preregistered experiments"),
        ("golden", "write the golden files for the TypeScript port"),
    ):
        sub.add_parser(name, help=help_)
    d = sub.add_parser("diff", help="payload changes since a git ref")
    d.add_argument("ref", nargs="?", default="HEAD~1")
    v = sub.add_parser("verify-live", help="check source pages for the expected figures (needs network)")
    v.add_argument("--write", action="store_true")
    v.add_argument("--only", metavar="IDS", help="comma separated source ids")
    return p


def main(argv: list[str] | None = None) -> int:
    cmds = {
        "validate": cmd_validate, "rehash": cmd_rehash, "synth": cmd_synth,
        "build": cmd_build, "analyse": cmd_analyse, "facts": cmd_facts, "report": cmd_report,
        "sync-docs": cmd_sync_docs, "schema": cmd_schema, "evaluate": cmd_evaluate, "golden": cmd_golden,
        "template": cmd_template,
    }
    parser = build_parser()
    args = parser.parse_args(sys.argv[1:] if argv is None else argv[1:])
    if args.command is None:
        parser.print_help()
        return 2
    if args.command in ("score", "questions"):
        return cmd_own(args)
    if args.command == "diff":
        return cmd_diff([args.ref])
    if args.command == "verify-live":
        flags = (["--write"] if args.write else []) + (["--only", args.only] if args.only else [])
        return cmd_verify_live(flags)
    return cmds[args.command]()


def run() -> None:
    """Console script entry point."""
    sys.exit(main())


if __name__ == "__main__":
    sys.exit(main())
