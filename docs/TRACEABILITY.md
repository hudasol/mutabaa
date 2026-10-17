# Traceability: claim → test

Format: `| claim | test file :: test name |`. `scripts/check_traceability.py` fails CI if a listed test does not exist.

| Claim | Test |
|---|---|
| A changed extraction note is detected | tests/test_real_data.py :: test_hash_tamper_is_caught |
| The committed payload equals a rebuild | tests/test_real_data.py :: test_site_payload_is_up_to_date |
| Evidence older than 180 days is flagged stale | tests/test_real_data.py :: test_staleness_flag_boundary |
| Every failed check yields a question | tests/test_real_data.py :: test_questions_cover_every_missing_check |
| Search coverage is reported per commitment | tests/test_real_data.py :: test_every_commitment_has_search_coverage_or_is_flagged |
| Unreachable sources are warned about and never counted as verified | tests/test_real_data.py :: test_unreachable_is_a_warning_not_an_error |
| Payload diffs report status, target and verification changes | tests/test_diff.py :: test_detects_status_target_and_verification_changes |
| The Python and TypeScript sensitivity sweeps agree | site/src/engine.test.ts :: matches the golden file on every definition |
| CSV export neutralises spreadsheet formulas | site/src/engine.test.ts :: neutralises formulas |
| URL state round-trips | site/src/route.test.ts :: round |
| English and Arabic have the same keys | site/src/i18n.test.ts :: has the same keys |
| No page makes a third-party request | site/e2e/app.spec.ts :: without console errors or third-party requests |
| No serious accessibility violations, EN/AR, light/dark | site/e2e/app.spec.ts :: no serious or critical axe violations |
| The offline file opens from file:// | site/e2e/app.spec.ts :: the single-file build opens from file:// |
| Inline script injection is blocked by the CSP | site/e2e/app.spec.ts :: CSP meta is present |
| Robustness, calibration and agreement results equal a fresh run | tests/test_analysis.py :: test_robustness_matches_committed_file |
| Axis definitions in the config match the code | tests/test_analysis.py :: test_axes_config_matches_code |
| Statistics helpers are correct and deterministic | tests/test_analysis.py :: test_kappa_known_values |
| The CSV size cap truncates and says so | site/src/engine.test.ts :: flags truncation and keeps only the cap |
| Portfolio ranks entities and shares ties | site/src/engine.test.ts :: shares ties rather than ordering arbitrarily |
| An uploaded CSV is kept across pages and shown in the portfolio | site/e2e/app.spec.ts :: an uploaded CSV is kept when moving between pages |
| Numbers in documents equal the files the code produces | tests/test_docs_agree.py :: test_marked_numbers_match_facts |
| The facts file equals a fresh computation | tests/test_docs_agree.py :: test_facts_file_is_up_to_date |
| Prose follows the public voice rules | tests/test_voice.py :: test_prose_follows_voice_rules |
| The exploratory analyses are labelled as not preregistered (EN/AR) | site/e2e/app.spec.ts :: the assurance page labels its analyses as exploratory |
| The TypeScript score equals Python on every public commitment | site/src/commitments.test.ts :: scores every public commitment exactly as Python does |
| The TypeScript questions equal Python on every public commitment | site/src/commitments.test.ts :: asks exactly the same questions as Python |
| Golden score and question files equal a fresh run | tests/test_real_data.py :: test_golden_score_and_question_files_are_up_to_date |
| A user's commitments are scored in the browser with questions and a persistent banner, no request leaves the page | site/e2e/app.spec.ts :: a user file is scored in the browser |
| Exported questions neutralise spreadsheet formulas | site/e2e/app.spec.ts :: a user file is scored in the browser |
| My commitments works in Arabic, right to left | site/e2e/app.spec.ts :: Arabic questions and right to left layout |
| A malformed user file shows an error | site/e2e/app.spec.ts :: a malformed file shows an error |
| My commitments with results has no serious accessibility violations, EN/AR, light/dark | site/e2e/app.spec.ts :: with results: no serious or critical axe violations |
| Preregistered results equal a fresh run | tests/test_evaluate.py :: test_committed_results_equal_a_fresh_run |
| The Python layers import only downward | tests/test_layers.py :: test_no_lower_layer_imports_a_higher_one |
| Generated JSON Schema files are current and match the TypeScript types | tests/test_schema.py :: test_typescript_types_match_schema_fields |
