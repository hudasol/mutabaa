"""Typed schemas for every record in the repository.

Real records (commitments, evidence, sources) are grounded in public sources.
Synthetic records (registry) always carry ``is_synthetic: true``; the schema refuses anything else.
"""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# --------------------------------------------------------------------------- vocab

Jurisdiction = Literal["federal", "abu-dhabi", "national"]

SourceKind = Literal[
    "official-statement",  # a government announcement of a policy, target or decision
    "official-self-report",  # a government entity reporting its own progress
    "secondary-media",  # news or trade reporting
    "third-party",  # independent assessment
]

CommitmentKind = Literal[
    "target",  # a measurable outcome to be reached
    "milestone",  # an intermediate step with a measure
    "deliverable",  # a thing to be delivered (yes/no)
    "input",  # money, people or capacity committed
    "projection",  # an expected benefit, not a commitment to deliver it
    "assessment",  # how people or entities will be judged
    "vision",  # a direction with no measure
]

DeadlinePrecision = Literal["day", "month", "year", "relative", "none"]

EvidenceKind = Literal["activity", "quantified-progress", "target-met-claim"]

Corroboration = Literal[
    "official-confirmed",  # found in an official source
    "single-source",  # one non-official source only
    "not-in-official-statement",  # in media, absent from the official statement checked
]

UNITS = (
    "services",
    "sectors",
    "operations",
    "solutions",
    "use-cases",
    "agents",
    "employees",
    "processes",
    "entities",
    "aed",
    "jobs",
    "percent-time",
    "rank",
)

MaturityLevel = Literal[0, 1, 2, 3, 4]

_STRICT = ConfigDict(extra="forbid", frozen=False)


# --------------------------------------------------------------------------- real data


class Source(BaseModel):
    """A public source. The repository stores metadata and a hash of the extraction notes only."""

    model_config = _STRICT

    id: str = Field(pattern=r"^S\d{2}$")
    title: str
    publisher: str
    url: str = Field(pattern=r"^https://")
    kind: SourceKind
    published: date | None = None
    published_note: str | None = None
    retrieved: date
    extract_file: str
    content_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    ai_assisted: bool = False
    notes: str = ""
    # Checked against the raw page by `python -m pipeline verify-live`.
    # Each entry may list alternatives separated by "|" (formats differ between pages).
    expect_present: list[str] = Field(default_factory=list)
    # Things the notes say the page does NOT contain (for example media figures missing from
    # the official statement). Checked the same way.
    expect_absent: list[str] = Field(default_factory=list)


class Anchor(BaseModel):
    """A short phrase (under 15 words) that must appear in the source's extraction notes."""

    model_config = _STRICT

    source_id: str = Field(pattern=r"^S\d{2}$")
    text: str

    @field_validator("text")
    @classmethod
    def _short(cls, v: str) -> str:
        if len(v.split()) >= 15:
            raise ValueError("anchor must be under 15 words")
        if not v.strip():
            raise ValueError("anchor must not be empty")
        return v


class Commitment(BaseModel):
    model_config = _STRICT

    id: str = Field(pattern=r"^C\d{2}$")
    title: str
    title_ar: str
    statement: str = Field(max_length=400)
    statement_ar: str = Field(max_length=500)
    jurisdiction: Jurisdiction
    kind: CommitmentKind
    owner: str | None = None
    metric: str | None = None
    unit: str | None = None
    baseline: str | None = None
    target_value: str | None = None
    target_number: float | None = None
    target_comparator: Literal["=", ">=", "up-to"] | None = None
    deadline: date | None = None
    deadline_text: str | None = None
    deadline_precision: DeadlinePrecision = "none"
    measurement_source: str | None = None
    undefined_terms: list[str] = Field(default_factory=list)
    announced: date | None = None
    tags: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(min_length=1)
    anchors: list[Anchor] = Field(min_length=1)
    notes: str = ""

    @field_validator("unit")
    @classmethod
    def _unit_known(cls, v: str | None) -> str | None:
        if v is not None and v not in UNITS:
            raise ValueError(f"unknown unit {v!r}")
        return v

    @model_validator(mode="after")
    def _consistent(self) -> Commitment:
        if self.deadline_precision in ("day", "month", "year") and self.deadline is None:
            raise ValueError("deadline_precision implies a deadline date")
        if self.deadline_precision == "none" and self.deadline is not None:
            raise ValueError("deadline given but precision is 'none'")
        if self.target_number is not None and self.target_value is None:
            raise ValueError("target_number requires target_value text")
        if self.target_number is not None and self.target_comparator is None:
            raise ValueError("target_number requires a comparator")
        return self


class Evidence(BaseModel):
    model_config = _STRICT

    id: str = Field(pattern=r"^E\d{2}$")
    commitment_ids: list[str] = Field(min_length=1)
    kind: EvidenceKind
    summary: str = Field(max_length=400)
    summary_ar: str = Field(max_length=500)
    as_of: date | None = None
    as_of_note: str | None = None
    value: float | None = None
    value_text: str | None = None
    unit: str | None = None
    source_id: str = Field(pattern=r"^S\d{2}$")
    anchor: str
    corroboration: Corroboration = "official-confirmed"
    note: str = ""

    @field_validator("unit")
    @classmethod
    def _unit_known(cls, v: str | None) -> str | None:
        if v is not None and v not in UNITS:
            raise ValueError(f"unknown unit {v!r}")
        return v

    @field_validator("anchor")
    @classmethod
    def _short(cls, v: str) -> str:
        if len(v.split()) >= 15 or not v.strip():
            raise ValueError("anchor must be 1-14 words")
        return v


class Claim(BaseModel):
    """A media-reported figure we checked against official statements and did not treat as fact."""

    model_config = _STRICT

    id: str = Field(pattern=r"^K\d{2}$")
    text: str = Field(max_length=300)
    text_ar: str = Field(max_length=400)
    source_id: str = Field(pattern=r"^S\d{2}$")
    anchor: str
    corroboration: Corroboration
    official_sources_checked: list[str] = Field(default_factory=list)
    commitment_ids: list[str] = Field(default_factory=list)
    note: str = ""

    @field_validator("anchor")
    @classmethod
    def _short(cls, v: str) -> str:
        if len(v.split()) >= 15 or not v.strip():
            raise ValueError("anchor must be 1-14 words")
        return v


SearchOutcome = Literal["progress-found", "target-restatement-only", "nothing-official-found"]


class SearchEntry(BaseModel):
    """One search we ran. Lets 'no public evidence' mean 'searched here, on this date, found nothing'."""

    model_config = _STRICT

    id: str = Field(pattern=r"^Q\d{2}$")
    searched_on: date
    tool: Literal["WebSearch", "WebFetch", "shell"]
    query: str
    commitment_ids: list[str] = Field(min_length=1)
    outcome: SearchOutcome
    found_source_ids: list[str] = Field(default_factory=list)
    note: str = ""


# --------------------------------------------------------------------------- derived


class VerifiabilityResult(BaseModel):
    commitment_id: str
    checks: dict[str, bool | None]  # None = not applicable
    applicable: int
    passed: int
    ratio: float
    band: Literal["checkable", "partly-checkable", "not-yet-checkable"]
    missing: list[str]


Status = Literal[
    "not-checkable",
    "no-public-evidence",
    "activity-reported",
    "milestone-reported",
    "target-claimed-met",
]


class StatusResult(BaseModel):
    commitment_id: str
    status: Status
    reasons: list[str]
    evidence_ids: list[str]
    excluded_evidence_ids: list[str]
    self_reported_only: bool
    unit_mismatch: bool
    progress_ratio: float | None = None
    progress_as_of: date | None = None
    latest_evidence_date: date | None = None
    evidence_age_days: int | None = None
    stale: bool = False


# --------------------------------------------------------------------------- synthetic


class SyntheticEntity(BaseModel):
    model_config = _STRICT

    id: str = Field(pattern=r"^SE\d{2}$")
    name: str
    sector: str
    advancement: float = Field(ge=0.0, le=1.0)
    is_synthetic: Literal[True] = True


class ServiceItem(BaseModel):
    model_config = _STRICT

    id: str
    entity_id: str
    sector: str
    kind: Literal["service", "operation"]
    audience: Literal["citizen", "business", "internal"]
    name: str
    annual_transactions: int = Field(ge=0)
    maturity: MaturityLevel
    oversight: bool
    audit_trail: bool
    uae_residency: bool
    fallback: bool
    is_synthetic: Literal[True] = True

    @model_validator(mode="after")
    def _kind_audience(self) -> ServiceItem:
        if self.kind == "operation" and self.audience != "internal":
            raise ValueError("operations are internal")
        if self.kind == "service" and self.audience == "internal":
            raise ValueError("services are citizen- or business-facing")
        return self


class RegistryMeta(BaseModel):
    model_config = _STRICT

    seed: int
    generator_version: str
    is_synthetic: Literal[True] = True
    disclaimer: str


class Registry(BaseModel):
    model_config = _STRICT

    meta: RegistryMeta
    entities: list[SyntheticEntity]
    items: list[ServiceItem]


# --------------------------------------------------------------------------- sensitivity

Unit = Literal["services", "transactions", "entities", "sectors"]
Scope = Literal["citizen-services", "all-services", "services-and-operations"]
Threshold = Literal[2, 3, 4]
Guardrails = Literal["none", "required"]


class Definition(BaseModel):
    model_config = ConfigDict(frozen=True)

    unit: Unit
    scope: Scope
    threshold: Threshold
    guardrails: Guardrails
