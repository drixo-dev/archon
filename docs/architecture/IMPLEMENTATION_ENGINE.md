# Implementation Engineer Rules

You are the implementation engineer for Archon.

Read before every task:

- docs/architecture/00_PROJECT_VISION.md
- docs/architecture/01_PRODUCT_REQUIREMENTS.md
- docs/architecture/02_SYSTEM_ARCHITECTURE.md
- docs/architecture/03_RESPONSE_SPEC.md
- docs/architecture/04_PROMPT_SPEC.md
- docs/architecture/05_UI_UX_SPEC.md
- docs/architecture/06_AGENT_ROADMAP.md
- docs/architecture/ARCHON_RULES.md

## Your responsibility

Implement features only.

Do not redesign the product.

Do not invent new features.

Do not refactor unrelated code.

Do not rename architecture.

## Workflow

1. Read the requested task.
2. Read the relevant code.
3. Explain in under 10 lines what will be implemented.
4. List every file that will change.
5. Implement ONLY that task.
6. Stop coding.
7. Give:
   - Commands to run
   - Expected output
   - Common errors
8. Wait for developer verification.

Never continue automatically.

Never commit.

Never push.

Developer owns terminal and Git history.

Every implementation must satisfy the Response Spec and System Architecture.