// Question templates copied from pipeline/questions.py. data/golden/questions.json keeps them identical.
export const MAX_TERM_QUESTIONS = 3;
export const QUESTION_TEMPLATES: Record<string, [string, string]> = {
  numeric_target: ["What number defines success for “{title}”, and is it a minimum, an exact value or a ceiling?", "ما الرقم الذي يُعرّف النجاح في «{title}»، وهل هو حد أدنى أم قيمة محددة أم سقف؟"],
  unit_defined: ["What exactly is counted for “{title}”? Name the unit and the denominator it is measured against.", "ما الذي يُعدّ تحديداً في «{title}»؟ حدّدوا الوحدة والمقام الذي تُقاس به."],
  dated_deadline: ["By what calendar date must “{title}” be met, and from what start date is it counted?", "في أي تاريخ ميلادي يجب تحقيق «{title}»، ومن أي تاريخ بدء يُحتسب؟"],
  owner_named: ["Which entity is accountable for delivering “{title}”?", "ما الجهة المسؤولة عن تنفيذ «{title}»؟"],
  measurement_source: ["Which dataset or report will be used to measure “{title}”, and who publishes it, how often?", "ما مجموعة البيانات أو التقرير الذي سيُستخدم لقياس «{title}»، ومن ينشره وبأي دورية؟"],
};
export const TERM_TEMPLATE: [string, string] = ["For “{title}”, how is “{term}” defined?", "في «{title}»، كيف يُعرَّف «{term}»؟"];
