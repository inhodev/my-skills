---
name: git-organize-history
description: Analyze a repository with many accumulated uncommitted changes, divide the diff into coherent feature-level commits, write self-contained detailed Korean commit messages with real line breaks, validate each group, and push the completed history to the current branch's safe GitHub upstream in one uninterrupted run. Use when the user says changes have piled up, asks to organize or split commits by feature, requests detailed Korean commit messages, or wants accumulated work safely committed and pushed. Do not use for a single routine commit or read-only Git history questions.
---

# Git Organize History

Turn a large dirty worktree into an understandable sequence of reversible, feature-level commits. Preserve user work and finish every explicitly authorized commit-and-push run without pausing for redundant approval.

## Classify the Request

Choose one mode from the user's wording:

- `PREVIEW`: inspect and propose commit groups without staging, committing, or pushing.
- `COMMIT`: inspect, group, validate, and create local commits without pushing.
- `COMMIT_AND_PUSH`: create the commits and push only to the explicitly requested remote and branch.

Treat "정리해서 커밋해" as `COMMIT`. Treat "푸시해", "깃허브까지 올려", or an equivalent explicit instruction as `COMMIT_AND_PUSH`.

In `COMMIT_AND_PUSH`, show the plan as a progress update and continue in the same run through staging, committing, validation, push, and remote verification. Do not end the response after the plan and do not ask for a second confirmation. Stop only for a real safety blocker: an unknown or mismatched repository owner, no safe destination branch, remote commits not contained locally, detected secrets, failing required validation, destructive history rewriting, or another decision only the user can make.

Never infer permission to force-push, rewrite published history, create a repository, open a pull request, merge into another branch, or deploy.

## Inspect Ground Truth

Read repository-local instructions first. Then inspect the live repository state and the complete diffs, not only filenames:

```bash
git status --short --branch
git branch --show-current
git remote -v
git diff --stat
git diff
git diff --staged --stat
git diff --staged
git log -15 --pretty=format:'%h %s'
git rev-parse --show-toplevel
```

Also inspect untracked files by type and size before grouping them. Read relevant source files when a diff lacks enough context to identify behavior. Check the repository's ignore rules, contribution instructions, test commands, and default branch. Preserve pre-existing staged selections unless the user explicitly included them in this reorganization; do not silently unstage or absorb them.

For a requested GitHub push, verify the active account and remote owner when `gh` is available. Resolve the destination before the first commit:

- If the current branch has an upstream, push to that exact upstream.
- If it has no upstream, use the same branch name on `origin` and establish tracking only when the remote owner and branch name are safe and unambiguous.
- Push to `origin/main` only when the checked-out reviewed branch is local `main`, unless the user separately and explicitly authorized integration into `main`.
- Never redirect a feature branch to remote `main`, merge it into `main`, or switch branches merely because a generic prompt mentions GitHub.

Fetch the exact destination branch when network access is available, then determine ahead/behind state. Do not print credentials or token-bearing remote URLs.

## Build Atomic Feature Groups

Group changes by behavior and independent revertability. A good group leaves the repository internally coherent and can be explained with one purpose.

Keep together:

- one feature's implementation, direct tests, migrations, generated outputs required by that implementation, and focused documentation;
- a bug fix and the regression test that proves it;
- a source change and lockfile changes directly caused by its dependency update.

Usually split:

- unrelated features or modules;
- refactoring from behavior changes when each stands alone;
- infrastructure, documentation, formatting, and test-only work from product features;
- generated, cache, local-environment, or large binary files unless they are required tracked artifacts.

If one file contains multiple concerns, use patch-level staging and re-check the resulting staged and unstaged versions. Do not split a hunk when doing so would create a broken intermediate commit. Never manufacture a neat history by editing or discarding user code, and never amend, squash, rebase, reset, or force-push existing commits unless separately and explicitly requested.

Order groups by dependency: foundation or schema first, then domain logic, user-facing behavior, integrations, and finally independent documentation or maintenance. Prefer the smallest number of commits that still makes each purpose independently understandable; do not create one commit per file.

Apply a large-group challenge before accepting a commit that spans multiple subsystems or roughly 20 or more files. Attempt to split it by user-visible behavior, data/storage behavior, analytics/compliance, or infrastructure. Keep it combined only when shared hunks or dependencies make each smaller intermediate commit fail to build, test, or preserve coherent behavior. Record that concrete reason in the progress update; size alone is not a reason to split or combine.

## Present the Commit Plan

Before changing the index, show a compact numbered plan containing for every proposed commit:

1. Korean title.
2. Purpose and observable behavior change.
3. Files or partial hunks included.
4. Verification to run.

Also list excluded or suspicious files and the intended remote branch. In `PREVIEW` mode, stop after this plan. In `COMMIT` and `COMMIT_AND_PUSH`, the user's invocation already authorizes the named operations: present the plan as a progress update and continue immediately without waiting for another reply.

Revise the plan if staging reveals that a group is not independent. Report the changed grouping and concrete dependency reason as a progress update, then continue unless the change expands beyond the user's authorization. The final report must reconcile proposed and actual commit groups.

## Write Detailed Korean Commit Messages

Write every new commit message in natural Korean unless repository policy explicitly requires another format. Follow a mandatory repository convention such as a ticket prefix, but do not adopt Conventional Commits merely by habit.

Use this structure:

```text
<무엇이 달라졌는지 드러나는 한국어 제목>

- 변경 전 문제 또는 이번 작업의 목적
- 구현한 핵심 동작과 중요한 설계 선택
- 사용자나 시스템 관점에서 달라진 결과
- 검증, 마이그레이션 또는 호환성 관련 사항
```

Make the body self-contained. State what changed, why it was needed, and what behavior now results. Include only facts proven by the staged diff and validation. Use as many body lines as needed, but avoid repeating filenames or narrating mechanical edits that add no understanding. Keep the title concise and specific; do not use vague subjects such as "수정", "업데이트", "작업 내용 반영", or "기타 변경".

Example:

```text
프로필 편집 과정에 입력 검증과 실패 복구 추가

- 이름과 소개 문구를 한 화면에서 수정할 수 있도록 편집 흐름 구성
- 빈 이름과 글자 수 초과 입력은 서버 요청 전에 차단하도록 검증 추가
- 저장 실패 시 작성 중인 내용을 유지하고 원인을 안내하도록 오류 상태 처리
- 저장 성공 후 최신 사용자 정보를 다시 불러와 화면과 서버 상태를 동기화
```

Do not claim that a test passed, a bug was fixed, or compatibility was preserved unless that result was actually verified.

Create multiline messages with actual newline characters. Prefer a temporary message file passed to `git commit -F <file>` or separate `-m` arguments. Never embed the two literal characters `\n` as line separators. Keep temporary message files outside the repository and remove them after use.

## Stage and Commit One Group at a Time

For each approved group:

1. Stage exact paths or hunks; never use broad staging such as `git add .` or `git add -A` for a mixed worktree.
2. Inspect `git diff --staged --stat`, `git diff --staged --name-status`, and the full staged diff.
3. Confirm no unrelated hunk, secret, credential, local configuration, cache, build output, or unintended large file is staged. Report secret findings by location and category without printing the value.
4. Run the cheapest meaningful syntax, formatting, or focused test check for that group when available.
5. Commit with the planned Korean title and body.
6. Verify the new commit with `git show --stat --oneline --decorate HEAD`, inspect `git log -1 --format=%B`, and ensure the remaining worktree still contains every uncommitted user change.
7. Reject a message that contains literal `\n`, lacks the planned body, or differs factually from the staged diff. If the new commit is still local and unpushed, correct that just-created commit before continuing.

If a check fails, do not hide the failure inside the commit or push. Diagnose whether it is caused by the proposed group. Fix only when the user's request includes implementation; otherwise stop with the staged state described clearly. Never delete or weaken tests to obtain a green result.

## Validate the Complete Sequence

After all commits, inspect the range and run the repository's relevant test, lint, typecheck, or build commands in proportion to the accumulated changes. A successful commit command is not behavioral verification.

Confirm:

- commit order and messages match the plan;
- each commit is understandable and independently revertible;
- every detailed body renders as real separate lines and contains no literal `\n` separators;
- remaining dirty files are intentional and reported;
- no secrets, oversized accidental assets, caches, or build products entered the new commits;
- applicable checks pass, or pre-existing/unavailable checks are named precisely.

Do not rewrite newly created commits merely for cosmetic perfection after validation. A literal `\n`, missing body, factual error, or invalid grouping is a correctness defect and must be corrected before push while the affected commits remain local.

## Push Safely

Push only in `COMMIT_AND_PUSH` mode.

Immediately before pushing:

1. Verify the current branch, requested destination, remote URL, active GitHub account, and remote owner.
2. Fetch the destination branch and recompute ahead/behind state.
3. If the remote has commits not contained locally, stop. Do not automatically pull, merge, rebase, or force-push.
4. Reconfirm the destination rule: current branch upstream first; otherwise same branch name on `origin`; `origin/main` only from reviewed local `main` without separate integration authority.
5. Use a normal push, never `--force` or `--force-with-lease` under this skill.

After pushing, verify the remote ref directly and confirm local/remote divergence is zero, for example with `git ls-remote` and `git rev-list --left-right --count`. Do not describe an upload as successful until this remote verification passes.

## Report the Result

Return:

- each commit's short hash, Korean title, and one-line purpose;
- validation commands and their actual results;
- pushed remote and branch, plus remote verification evidence;
- any difference between the initial plan and actual commits, with the dependency reason;
- all intentionally uncommitted or excluded files;
- any blocked or unverified item and the exact reason.

Keep unrelated user changes untouched and make that boundary explicit.
