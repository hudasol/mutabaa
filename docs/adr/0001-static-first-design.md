# ADR 0001: Static by design

## Status
Accepted.

## Context
Mutabaa is a student prototype and a proposal seed, not a deployment. It has to be readable by an analyst on an ordinary laptop, on a closed office network and from a USB stick, and it has to be checkable by a reviewer who has no access to any server we run. A tool that grades public commitments must also be able to show where every number came from, and it should not hold any data it does not need.

## Options considered
1. A web application with a server, a database and an API, serving the ledger and the Definition Lab on request.
2. A static site built from files in the repository, with the browser as the only runtime.
3. A static site that calls a hosted service for some features (for example search or saving a workspace).

## Decision
We chose option 2. The Python pipeline in `pipeline/` is the reference: it validates the data, computes scores and statuses, runs the sensitivity sweep and writes one payload JSON. The Vite and React app in `site/` reads that payload and nothing else. There is no runtime model, no runtime network call and no secret (`docs/ARCHITECTURE.md`, section 1). The parts of the method that the browser must recompute on a user's own CSV are mirrored in `site/src/engine.ts`, and `data/golden/sensitivity.json` holds both engines to the same results.

The same build serves deployment profile A (a public demo on a static host) and profile B (an office intranet with no outbound traffic). Profile C, a team service with identity, persistence and an audit log, is kept as a design only (`docs/design/`).

## Consequences
- Every number on screen can be recomputed from files in the repository, and a test checks that the committed payload equals a rebuild.
- The site makes no third party requests, and a browser test fails if any request leaves the origin (`docs/SECURITY.md`).
- A user's CSV is parsed in the browser and is never sent anywhere, because there is nowhere to send it.
- There is no shared state, no review workflow and no multi user editing. Data updates are reviewed commits, not live edits. These needs are deferred to profile C.
- Hosting is simple, but the security headers depend on the host. The meta Content-Security-Policy is a fallback and cannot set every directive.
