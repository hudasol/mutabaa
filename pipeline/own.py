"""Read an office's own commitments file (CSV or JSON) so that it can be scored.

The TypeScript port in site/src/commitments.ts follows the same rules, and the shared test files
data/golden/own_inputs.json and data/golden/own_outputs.json keep both identical. The rules, in short:

* CSV: UTF-8, a byte order mark is ignored, the delimiter is a comma, a semicolon or a tab (the one used
  most in the header line outside quotes), quoted cells may hold delimiters and line breaks.
* JSON: an array of objects, or an object with a `commitments` array. A list value is joined with `; `.
* Columns are matched by name or by a small set of synonyms. `id`, `title` and `kind` are required.
* A deadline counts as dated when it is a calendar date, a month, a quarter or a year (see
  `deadline_precision`); any other text is relative.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

MAX_ROWS = 200_000

COLUMNS = (
    "id", "title", "owner", "metric", "unit", "target_number", "deadline", "measurement_source",
    "undefined_terms", "kind",
)
REQUIRED = ("id", "title", "kind")
KINDS = ("target", "milestone", "deliverable", "input", "projection", "assessment", "vision")

SYNONYMS: dict[str, tuple[str, ...]] = {
    "id": ("id", "code", "ref", "reference", "commitmentid"),
    "title": ("title", "name", "commitment", "target", "statement"),
    "owner": ("owner", "entity", "responsible", "accountable", "lead"),
    "metric": ("metric", "measure", "indicator", "kpi"),
    "unit": ("unit", "units", "unitofmeasure"),
    "target_number": ("targetnumber", "targetvalue", "value", "number"),
    "deadline": ("deadline", "due", "duedate", "date", "by"),
    "measurement_source": ("measurementsource", "source", "datasource", "measuredby"),
    "undefined_terms": ("undefinedterms", "terms", "undefined", "openterms"),
    "kind": ("kind", "type", "category"),
}

TEMPLATE = (
    ",".join(COLUMNS)
    + '\nX01,Move half of services to the new platform,Example Office,services moved,services,50,'
    '2027-12-31,Annual service report,"agentic; service",target\n'
)

_MONTHS = (
    "jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|"
    "sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?"
)
_I = re.IGNORECASE
_ISO_DAY = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
_NUM_DAY = re.compile(r"^(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})$")
_YMD_SLASH = re.compile(r"^(\d{4})[/.](\d{1,2})[/.](\d{1,2})$")
_DAY_MONTH_NAME = re.compile(rf"^\d{{1,2}}\s+(?:{_MONTHS})\.?,?\s+\d{{4}}$", _I)
_MONTH_NAME_DAY = re.compile(rf"^(?:{_MONTHS})\.?\s+\d{{1,2}},?\s+\d{{4}}$", _I)
_ISO_MONTH = re.compile(r"^(\d{4})-(\d{2})$")
_NUM_MONTH = re.compile(r"^(\d{1,2})[/-](\d{4})$")
_MONTH_NAME_YEAR = re.compile(rf"^(?:{_MONTHS})\.?\s+\d{{4}}$", _I)
_QUARTER = re.compile(r"^(?:q[1-4]\s*[-/ ]?\s*\d{4}|\d{4}\s*[-/ ]?\s*q[1-4])$", _I)
_YEAR = re.compile(r"^(?:(?:by|before|until)\s+)?(?:(?:the\s+)?end\s+of\s+)?\d{4}$", _I)


def _valid_day(a: int, b: int) -> bool:
    return (1 <= a <= 31 and 1 <= b <= 12) or (1 <= a <= 12 and 1 <= b <= 31)


def deadline_precision(value: str) -> str:
    """day, month, year, relative or none. Dates are read as written; no calendar arithmetic."""
    s = " ".join(value.split())
    if not s:
        return "none"
    if (m := _ISO_DAY.match(s)) is not None:
        return "day" if 1 <= int(m[2]) <= 12 and 1 <= int(m[3]) <= 31 else "relative"
    if (m := _NUM_DAY.match(s)) is not None:
        return "day" if _valid_day(int(m[1]), int(m[2])) else "relative"
    if (m := _YMD_SLASH.match(s)) is not None:
        return "day" if _valid_day(int(m[2]), int(m[3])) and int(m[2]) <= 12 else "relative"
    if _DAY_MONTH_NAME.match(s) or _MONTH_NAME_DAY.match(s):
        return "day"
    if (m := _ISO_MONTH.match(s)) is not None:
        return "month" if 1 <= int(m[2]) <= 12 else "relative"
    if (m := _NUM_MONTH.match(s)) is not None:
        return "month" if 1 <= int(m[1]) <= 12 else "relative"
    if _MONTH_NAME_YEAR.match(s) or _QUARTER.match(s):
        return "month"
    if _YEAR.match(s):
        return "year"
    return "relative"


# ------------------------------------------------------------------ reading CSV


def _first_line(text: str) -> str:
    out, quoted = [], False
    for ch in text:
        if ch == '"':
            quoted = not quoted
        if ch in "\r\n" and not quoted:
            break
        out.append(ch)
    return "".join(out)


def detect_delimiter(text: str) -> str:
    head = _first_line(text)
    counts = {d: 0 for d in (",", ";", "\t")}
    quoted = False
    for ch in head:
        if ch == '"':
            quoted = not quoted
        elif not quoted and ch in counts:
            counts[ch] += 1
    best = max(counts, key=lambda d: (counts[d], d == ","))
    return best if counts[best] > 0 else ","


def parse_csv(text: str) -> list[list[str]]:
    """Records of trimmed cells. Quotes may hold delimiters and line breaks; empty records are dropped."""
    text = text.removeprefix("﻿")
    delim = detect_delimiter(text)
    records: list[list[str]] = []
    row: list[str] = []
    cur: list[str] = []
    quoted = False
    i, n = 0, len(text)
    while i < n:
        ch = text[i]
        if quoted:
            if ch == '"' and text[i + 1 : i + 2] == '"':
                cur.append('"')
                i += 1
            elif ch == '"':
                quoted = False
            else:
                cur.append(ch)
        elif ch == '"' and not "".join(cur).strip():
            quoted = True
            cur = []
        elif ch == delim:
            row.append("".join(cur).strip())
            cur = []
        elif ch in "\r\n":
            if ch == "\r" and text[i + 1 : i + 2] == "\n":
                i += 1
            row.append("".join(cur).strip())
            cur = []
            records.append(row)
            row = []
        else:
            cur.append(ch)
        i += 1
    row.append("".join(cur).strip())
    records.append(row)
    return [r for r in records if any(c != "" for c in r)]


def read_file(name: str, text: str) -> tuple[list[str], list[list[str]], bool]:
    """Headers, rows and whether the row cap cut the file. Raises ValueError with a readable message."""
    looks_json = name.lower().endswith(".json") or re.match(r"^\s*[\[{]", text) is not None
    if not looks_json:
        records = parse_csv(text)
        if not records:
            return [], [], False
        return records[0], records[1 : MAX_ROWS + 1], len(records) - 1 > MAX_ROWS
    try:
        parsed = json.loads(text.removeprefix("﻿"))
    except json.JSONDecodeError as exc:
        raise ValueError("The file is not valid JSON.") from exc
    items = parsed.get("commitments") if isinstance(parsed, dict) else parsed
    if not isinstance(items, list):
        raise ValueError("JSON must be an array of commitments, or an object with a commitments array.")
    headers: list[str] = []
    for o in items:
        if isinstance(o, dict):
            headers += [k for k in o if k not in headers]

    def cell(v: object) -> str:
        if v is None:
            return ""
        if isinstance(v, list):
            return "; ".join(str(x) for x in v)
        if isinstance(v, bool):
            return "true" if v else "false"
        return str(v)

    rows = [[cell(o.get(h)) if isinstance(o, dict) else "" for h in headers] for o in items]
    return headers, rows, False


# ------------------------------------------------------------------ mapping and conversion


def _squash(h: str) -> str:
    return re.sub(r"[^a-z]", "", h.lower())


def map_columns(headers: list[str]) -> dict[str, int]:
    m: dict[str, int] = {}
    used: set[int] = set()
    for col in COLUMNS:
        idx = next((i for i, h in enumerate(headers) if i not in used and h.lower().strip() == col), -1)
        if idx < 0:
            idx = next(
                (i for i, h in enumerate(headers) if i not in used and _squash(h) in SYNONYMS[col]), -1
            )
        if idx >= 0:
            m[col] = idx
            used.add(idx)
    return m


@dataclass(frozen=True)
class OwnCommitment:
    id: str
    title: str
    kind: str
    owner: str | None
    metric: str | None
    unit: str | None
    target_number: float | None
    deadline: str | None
    deadline_precision: str
    measurement_source: str | None
    undefined_terms: list[str]
    row: int

    @property
    def title_ar(self) -> str:
        return self.title


@dataclass
class OwnResult:
    items: list[OwnCommitment] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    rows: int = 0
    rejected: int = 0
    duplicates: int = 0
    unmapped: list[str] = field(default_factory=list)
    truncated: bool = False

    @property
    def accepted(self) -> int:
        return len(self.items)


_ARABIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
_NUMBER = re.compile(r"^[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?$")


def parse_number(raw: str) -> float | None:
    """A plain number. Thousands commas, spaces and a trailing percent sign are ignored."""
    s = raw.translate(_ARABIC_DIGITS).strip().replace(",", "").replace(" ", "")
    s = s.removesuffix("%")
    if s == "":
        return None
    if not _NUMBER.match(s):
        raise ValueError(raw)
    return float(s)


def _or_none(s: str) -> str | None:
    s = s.strip()
    return s or None


def convert_rows(
    headers: list[str], rows: list[list[str]], mapping: dict[str, int], truncated: bool = False
) -> OwnResult:
    res = OwnResult(rows=len(rows), unmapped=[c for c in COLUMNS if c not in mapping], truncated=truncated)
    if not rows:
        res.errors.append("The file needs at least one commitment.")
        return res
    missing = [c for c in REQUIRED if c not in mapping]
    if missing:
        res.errors.append(f"Missing columns: {', '.join(missing)}.")
        return res
    seen: set[str] = set()
    for n, f in enumerate(rows):
        row = n + 2

        def get(c: str, f: list[str] = f) -> str:
            return f[mapping[c]] if c in mapping and mapping[c] < len(f) else ""

        bad: list[str] = []
        ident, kind = get("id").strip(), get("kind").strip().lower()
        if not ident:
            bad.append("id is empty")
        if ident in seen:
            bad.append("duplicate id")
            res.duplicates += 1
        if not get("title").strip():
            bad.append("title is empty")
        if kind not in KINDS:
            bad.append(f"kind must be one of {', '.join(KINDS)}")
        number: float | None = None
        try:
            number = parse_number(get("target_number"))
        except ValueError:
            bad.append("target_number must be a number or empty")
        if bad:
            res.errors.append(f"Row {row}: {'; '.join(bad)}.")
            continue
        seen.add(ident)
        terms = [t.strip() for t in re.split(r"[;|]", get("undefined_terms")) if t.strip()]
        res.items.append(
            OwnCommitment(
                id=ident,
                title=get("title").strip(),
                kind=kind,
                owner=_or_none(get("owner")),
                metric=_or_none(get("metric")),
                unit=_or_none(get("unit")),
                target_number=number,
                deadline=_or_none(get("deadline")),
                deadline_precision=deadline_precision(get("deadline")),
                measurement_source=_or_none(get("measurement_source")),
                undefined_terms=terms,
                row=row,
            )
        )
    res.rejected = len(rows) - len(res.items)
    return res


def load(name: str, text: str) -> OwnResult:
    """Read, map and convert in one step."""
    headers, rows, truncated = read_file(name, text)
    return convert_rows(headers, rows, map_columns(headers), truncated)


def csv_cell(v: object) -> str:
    """Quote a value for CSV and neutralise spreadsheet formula injection (leading = + - @ tab or CR)."""
    s = "" if v is None else str(v)
    if s[:1] in ("=", "+", "-", "@", "\t", "\r"):
        s = "'" + s
    return '"' + s.replace('"', '""') + '"'

