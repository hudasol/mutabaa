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
