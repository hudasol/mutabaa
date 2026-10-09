# Team service (Profile C): design only

Not built. The static site stays the client; the service only adds persistence and sharing.

## Components
- **API** (`docs/design/openapi.yaml`): workspaces, registries (uploaded exports), saved definitions, review notes, export bundles.
- **Auth**: the host organisation's identity provider (OIDC). No passwords stored by Mutabaa.
- **Storage**: one encrypted database per tenant; object store for uploaded exports; no cross-tenant queries.
- **Audit log**: append-only record of who read, changed, or exported what and when. Retained per the host's policy.
- **Compute**: the same deterministic engines (Python reference, TypeScript client). No model calls.

## Roles
| Role | Can |
|---|---|
| Viewer | Read workspaces they are added to |
| Analyst | Upload registries, save definitions, add review notes |
| Reviewer | Approve a saved definition and a published brief |
| Admin | Manage members and retention |

## Non-goals
Performance scoring of entities, automatic emails to entities, any use of personal data.

## Open questions
Where it is hosted; which identity provider; retention period; who is the data controller.
