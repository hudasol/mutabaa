"""Turn what a commitment lacks into questions an analyst can put to the owning entity."""

from __future__ import annotations

from .schemas import Commitment, VerifiabilityResult

MAX_TERM_QUESTIONS = 3

_T = {
    "numeric_target": (
        "What number defines success for “{title}”, and is it a minimum, an exact value or a ceiling?",
        "ما الرقم الذي يُعرّف النجاح في «{title}»، وهل هو حد أدنى أم قيمة محددة أم سقف؟",
    ),
    "unit_defined": (
        "What exactly is counted for “{title}”? Name the unit and the denominator it is measured against.",
        "ما الذي يُعدّ تحديداً في «{title}»؟ حدّدوا الوحدة والمقام الذي تُقاس به.",
    ),
    "dated_deadline": (
        "By what calendar date must “{title}” be met, and from what start date is it counted?",
        "في أي تاريخ ميلادي يجب تحقيق «{title}»، ومن أي تاريخ بدء يُحتسب؟",
    ),
    "owner_named": (
        "Which entity is accountable for delivering “{title}”?",
        "ما الجهة المسؤولة عن تنفيذ «{title}»؟",
    ),
    "measurement_source": (
        "Which dataset or report will be used to measure “{title}”, and who publishes it, how often?",
        "ما مجموعة البيانات أو التقرير الذي سيُستخدم لقياس «{title}»، ومن ينشره وبأي دورية؟",
    ),
}
_TERM = (
    "For “{title}”, how is “{term}” defined?",
    "في «{title}»، كيف يُعرَّف «{term}»؟",
)


def questions(c: Commitment, s: VerifiabilityResult) -> list[dict]:
    out: list[dict] = []
    for check in s.missing:
        if check in _T:
            en, ar = _T[check]
            out.append(
                {
                    "check": check,
                    "en": en.format(title=c.title),
                    "ar": ar.format(title=c.title_ar),
                }
            )
    if "terms_defined" in s.missing:
        for term in c.undefined_terms[:MAX_TERM_QUESTIONS]:
            out.append(
                {
                    "check": "terms_defined",
                    "en": _TERM[0].format(title=c.title, term=term),
                    "ar": _TERM[1].format(title=c.title_ar, term=term),
                }
            )
    return out
