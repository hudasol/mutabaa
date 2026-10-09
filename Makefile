.PHONY: reproduce test site offline sbom
# One command: validate data, run all tests, rebuild the payload, and fail if it differs from what is committed.
reproduce:
	python -m pipeline validate
	ruff check .
	python -m pytest -q
	python -m pipeline build
	git diff --exit-code -- site/src/data/real.json
	cd site && npm ci && npx tsc --noEmit && npx vitest run && npm run build && npm run build:offline

test:
	python -m pytest -q && cd site && npx vitest run

offline:
	cd site && npm run build:offline

sbom:
	cd site && npm run sbom
	python -m cyclonedx_py requirements requirements.lock -o sbom/python.cdx.json --of JSON
