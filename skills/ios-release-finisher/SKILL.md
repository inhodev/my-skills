---
name: ios-release-finisher
description: Use when an iOS, iPadOS, Flutter iOS, React Native iOS, or Xcode app has been selected for serious App Store release preparation, including store metadata, privacy and legal documents, age rating, regional compliance, screenshots, code rejection blockers, pricing decisions, App Store Connect readiness, or a request to finish everything possible without stopping for deferrable owner inputs.
---

# iOS Release Finisher

Finish every safe release-preparation task that current evidence and authority allow. Do not turn missing emails, prices, policy contacts, rating approvals, or portal-only fields into early stopping points.

## Non-negotiable execution contract

1. Inspect the real project, repository instructions, Apple state, and prior release artifacts before drafting answers.
2. Work through all 14 release domains. Read [references/release-domain-checklist.md](references/release-domain-checklist.md) completely.
3. Classify every unknown as `DEFERRED_INPUT`, `EXTERNAL_BLOCK`, or `RELEASE_BLOCK`. Read [references/autonomy-and-approval.md](references/autonomy-and-approval.md) completely.
4. A block in one branch does not stop independent branches. Continue code audit, drafts, fixes, tests, image planning, and API dry-runs.
5. Ask no mid-work preference question when a reversible evidence-based default or placeholder lets work continue.
6. Collect owner-only facts in `FINAL_INPUT_REQUEST.md`; request them once after all safe work is exhausted.
7. Never invent personal data, legal identity, business facts, data practices, content rights, age-rating facts, credentials, or regulatory status.
8. Never accept agreements, publish privacy answers, choose Made for Kids, change public/private distribution, archive, upload, submit for review, or release without the authority required for that exact action.

The user saying “prepare,” “finish,” or invoking this skill authorizes read-only discovery, local release documents, and in-scope local fixes. It does not by itself authorize archive, upload, App Review submission, or public release.

## Start immediately

From the exact project root, run:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/ios-release-finisher/scripts/prepare_release_workspace.py" \
  --root .
```

This creates `.ios-release-finisher/` without overwriting existing Markdown drafts. Re-run with `--inspect` for JSON-only read-only discovery.

Then:

1. Read project `AGENTS.md` and obey its validation order.
2. Resolve exact app identity. Prefer Bundle ID over display name.
3. Read `.ios-release-finisher/RELEASE_STATE.json` and expand the generated packet with repository evidence.
4. Run the project’s headless analysis, unit/component tests, and Release compile checks before simulator or device work.
5. If simulator QA is necessary and authorized, use only the existing iPhone 17 Pro and never take it from another task.

## Work the packet, not a questionnaire

Maintain these artifacts:

| Artifact | Required result |
|---|---|
| `RELEASE_READINESS_REPORT.md` | 14-domain status, evidence, owners, next actions |
| `APP_STORE_METADATA_DRAFT.md` | localized, length-checked, fact-checked copy |
| `PRIVACY_AND_LEGAL_AUDIT.md` | code/SDK/server/store/policy consistency |
| `AGE_RATING_DRAFT.md` | evidence-backed candidate answers and approval fields |
| `SCREENSHOT_PLAN.md` | device, locale, real screen, message, capture status |
| `PORTAL_ACTIONS.md` | exact portal-only action and responsible role |
| `FINAL_INPUT_REQUEST.md` | one consolidated owner-input request |
| `RELEASE_STATE.json` | machine-readable workflow state |

Do not leave template `TODO` entries if the repository or a live authenticated Apple surface can resolve them. Label unverified claims; never silently convert them into facts.

## Execution order

### 1. Identity and live-state gate

- Detect framework, Xcode workspace/project, shared scheme, targets, Bundle IDs, versions, Team, entitlements, dependencies, and release configuration.
- Query existing App Store Connect state when authenticated read access exists.
- If no app record exists, record portal creation; the public API cannot create the initial record.
- If two plausible apps remain and choosing wrong would mutate the wrong product, ask one identity question. Otherwise continue.

### 2. Product, data, and feature inventory

- Trace user-visible flows, account model, backend, SDKs, permissions, tracking, payments, UGC, AI, health, children, location, gambling, streaming, and external hardware.
- Build a data-flow table with collection, purpose, linkage, tracking, retention, processors, and international transfer.
- Compare source, server/schema evidence, Privacy manifest, App Privacy candidate answers, and policy text.

### 3. Draft release materials

- Draft privacy policy, terms, community policy, support copy, age-rating candidates, review notes, metadata, localization, and screenshot plan as applicable.
- Read [references/copy-and-localization.md](references/copy-and-localization.md) before writing store copy.
- Missing contact or business values become named placeholders, not reasons to pause.

### 4. Remove release blockers

- Fix in-scope local defects that would block release: privacy manifest, usage descriptions, account deletion, login-policy gaps, UGC controls, broken links, placeholder UI, test endpoints, secret exposure, incorrect entitlements, version identity, signing configuration, or release-only crashes.
- Use the project’s implementation and test instructions. Do not broaden into optional redesign.
- Treat a legal document as incomplete if the actual product lacks the behavior it promises.

### 5. Verify the release surface

- Run static analysis and targeted tests first.
- Run Release compilation or archive preflight when authorized by project rules.
- Test the exact artifact on a real device or production-like surface only when requested or required and available.
- Keep build, archive, export, upload, processing, submission, approval, and live availability as separate states.

### 6. Prepare Apple changes

Read [references/app-store-connect-boundaries.md](references/app-store-connect-boundaries.md) before any Apple write.

- Use the latest official OpenAPI specification to confirm endpoint support.
- Generate a before/after change preview for API-writable metadata.
- Keep App Privacy Publish, agreements, tax, banking, DSA, Korean identity, and permits in portal actions.
- Apply production changes only when the current request authorizes them.

### 7. Ask once, late

Only after independent work is exhausted, consolidate the remaining owner inputs. Ask for exact values in a paste-ready form and explain where each value is used. Do not repeat facts already available in project files or Apple state.

If one missing fact becomes a true whole-work blocker before then, ask exactly one question and state the blocked branch. Resume from existing artifacts; never restart the release audit.

## Store-copy quality gate

- Lead with the user outcome and write one idea per sentence.
- Do not chain clauses with repeated commas.
- Remove generic AI phrasing and unsupported superlatives.
- Do not keyword-stuff prose or repeat app/company names in keywords.
- Match every promise to current functionality and screenshot evidence.
- Rewrite for each locale; do not ship literal machine translation.
- Enforce current Apple field byte and character limits before upload.

## Safety and credential handling

- Never print or copy `.p8` contents, API secrets, passwords, 2FA codes, sessions, certificate private keys, or demo credentials into reports.
- Report credential presence, role, key identifier redaction, and usability only.
- Do not delete caches, DerivedData, profiles, builds, store records, or tester state as routine cleanup.
- Do not change agreements, tax, banking, legal entity, territories, pricing, or release method by assumption.

## Completion contract

Set `workflow_state` to `PREPARATION_COMPLETE` only when:

- every safe local investigation, draft, in-scope fix, and headless verification is done;
- every unresolved item has status, evidence, owner, and exact next action;
- no unexplained `RELEASE_BLOCK` remains;
- all owner-only inputs are consolidated once;
- portal-only work is click/input specific;
- no upload, submission, or release state is claimed without matching live evidence.

Final reporting must separate:

- `완료`
- `자동 반영 가능`
- `사용자 최종 입력 필요`
- `App Store Connect 포털 작업 필요`
- `법률 검토 권장`
- `코드 수정 필요`
- `출시 차단`
- `선택 개선`

Stop at release-preparation completion unless the user explicitly requests the next external stage. Use `ios-testflight-publisher` only for an explicitly authorized TestFlight archive/upload workflow.

## Rationalization checks

| Temptation | Required response |
|---|---|
| “I need the email before I can draft the policy.” | Use a named placeholder, finish the factual document, request once at the end. |
| “The user has not chosen a price.” | Prepare the price decision table and continue every non-price branch. |
| “Age rating is a choice, so ask now.” | Audit features, draft evidence-backed answers, defer semantic approval. |
| “App Privacy has no write API, so stop.” | Prepare the full answer map and exact portal steps; continue. |
| “Archive succeeded, so release is ready.” | Verify each later state separately; never overclaim. |
| “A policy document should satisfy review.” | Verify the promised product and server behavior exists. |
