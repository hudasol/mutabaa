# Roadmap with decision points

| Stage | Goal | Work | Exit criteria (decision to continue) |
|---|---|---|---|
| 0. Prototype (done, v1.4.0) | Show the idea is real and honest | Ledger, live verifier, Definition Lab, Portfolio, Assurance, offline build, documentation | A reviewer can run it, read every rule, and find the limits on the page |
| 1. Review | Remove what a person must check | Human review of notes and Arabic; legal read of `SOURCES_POLICY.md` and `COMPLIANCE.md`; gold-labelled extraction set; practitioner review of definition axes | Disagreement with reviewers under 5%; written sign-off on sources policy |
| 2. Pilot (12 weeks) | Prove value on a real registry | `docs/PILOT.md` | Targets in the plan met; sponsor records a definition decision |
| 3. Team service (Profile C) | Persistence, roles, audit | `docs/design/SERVICE.md`: sign-in with the host's identity provider, role-based access, audit log, retention, signed export bundles | Security review passed; pilot office wants shared workspaces |
| 4. Programme | Many offices, many registries | Multi-tenant isolation, standard export formats, support model | Funded owner and a support team |

Nothing past stage 1 is built. Each stage ends with a go or stop decision by the sponsor, not by the maintainer.

## Buy, build or reuse
- Reuse: published frameworks for maturity levels where they exist, once reviewed.
- Build: the verifiability score, the status rules, the source log. They are small, deterministic and need to be readable by non-engineers.
- Do not build: a general dashboard product. Existing tools do that. Mutabaa's value is the evidence rules.
