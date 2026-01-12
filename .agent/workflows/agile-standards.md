---
description: Enforce Agile & Project Management Standards for tasks
---

Follow this workflow ensuring all work adheres to "The Band Project" standards.

## 1. Branching Strategy (GitFlow)
- **main**: Stable production branch. Restricted.
- **developing**: Integration branch for new work. Branched from `main`.
- **features**: Feature/Bugfix branches. Fork/Branch from `developing`.
    - Format: `feat/<name>`, `bugfix/issue-<id>`, `fix/<name>`.

## 2. Iteration Cadence
- **Frequency**: 2 weeks.
- **Cadence**: 2 interactions per month.
    - **First Interaction**: Starts on the 1st day of the month.
    - **Second Interaction**: Starts on the 15th day of the month (Mean).

## 3. Definition of Ready (DoR) Check
Before moving a task to "In Progress":
- [ ] **Documentation First**:
    - [ ] Update `docs/*.md` (e.g., `requirements.md`, `sdd.md`) before creating the issue.
    - [ ] **Reference**: Description MUST link to docs (e.g., "Implement Req 1.1 as detailed in `docs/requirements.md`").
- [ ] **Hierarchy Check**: Confirm strict hierarchy: `Epic -> User Story -> Task`.
- [ ] **Governance**: Ensure work is associated with "The Band Project" ecosystem.
- [ ] **readiness**:
    - [ ] Clear Objective defined?
    - [ ] Acceptance Criteria defined?
    - [ ] Technical Plan ready?
- [ ] **GitHub Issue**:
    - [ ] **Draft**: Provide technical proposal/text to the user.
    - [ ] **Approval**: Mandatory user approval before proceeding.
    - [ ] **Create**: Create the issue on GitHub ONLY after approval.
        - [ ] **Fields Requirement (MANDATORY AND NON-NEGOTIABLE)**:
            - [ ] **Label**: Must be set (epic, us, task).
            - [ ] **Type**: Must be set (feature, bug, task).
            - [ ] **Milestone**: Must be set.
            - [ ] **Project**: Must be set to "The Band Project".
            - [ ] **Assignee**: Must be set to the logged-in user.
    - [ ] **Start**: Begin programming ONLY after issue creation. **MANDATORY AND NON-NEGOTIABLE**.

## 4. Artifact Maintenance
Maintain the following artifacts throughout the lifecycle:
- [ ] `task.md`: For detailed task tracking.
- [ ] `implementation_plan.md`: For technical planning and review.
    - [ ] **Test Plan**: MUST list all test cases based on requirements. **MANDATORY AND NON-NEGOTIABLE**.
- [ ] `docs/backlog.md`: Must include **Releases** section with:
    - PR Number & Link
    - Description
    - Commit SHA & Link

## 5. Implementation Standards
- [ ] **TDD**: Implement the test cases defined in the plan BEFORE the implementation code. **MANDATORY AND NON-NEGOTIABLE**.
- [ ] **Style**: Code must pass `black`, `flake8`, `isort`.
- [ ] **Business Logic**: All business rules requirements must be satisfied and verified.

## 6. Pull Request Standards
- [ ] **Process**:
    - [ ] Create PR from feature branch targeting `developing`.
    - [ ] **Template**: Use `.github/pull_request_template.md`.
- [ ] **Content Requirements**:
    - [ ] **Related Issues**: List linked issues (e.g., `Closes #1`).
    - [ ] **Modifications**: Detailed list of technical changes.
    - [ ] **How to Test**: Clear steps for verification.


## 7. Release Strategy (CD)
- [ ] **Promotion**: `developing` -> `main`.
- [ ] **Trigger**: All tests passed on `developing`.
- [ ] **Process**:
    - [ ] Open Pull Request from `developing` to `main`.
    - [ ] Title Format: `release: <description>`.
    - [ ] No direct commits to `main` allowed.
        - [ ] **Versioning (MANDATORY)**:
            - [ ] **MUST** create a new version (git tag) whenever `developing` is merged to `main`.
            - [ ] **DO NOT** run `bump_version.py` locally (CI/CD handles this).
            - [ ] **Create Tag**: `git tag vX.Y.Z` (at end of each feature/fix/release).
            - [ ] **Update Latest**: `git tag -f latest` and `git push origin -f latest` (at end of each feature/fix/bug).
            - [ ] **Push Tag**: `git push origin vX.Y.Z`.
            - [ ] **CI/CD**: GitHub Action handles version bump & publish.

## 8. Merge Standards
- [ ] **Conflict Free**: PR can be merged if there are no conflicts.
- [ ] **Automation**: If the CI pipeline (`.github/workflows/ci.yml`) passes, the PR MUST be merged and related issues closed automatically. **MANDATORY AND NON-NEGOTIABLE**.
- [ ] **Cleanup**: 
    - [ ] **Remote**: Delete the feature/bugfix branch from GitHub immediately after the PR is merged.
    - [ ] **Local**: Delete the local branch to keep the workspace clean.
    - [ ] **Sync**: Run `git remote prune origin` to synchronize remote branch tracking.

## 9. Definition of Done (DoD)
- [ ] **Verification**:
    - [ ] Test suite passing. **MANDATORY AND NON-NEGOTIABLE**.
    - [ ] Linting checks passing.
- [ ] **Documentation**:
    - [ ] Update Google-style docstrings.
    - [ ] Update relevant `docs/*.md` files.
    - [ ] Update/Create `walkthrough.md`.
- [ ] **Closure**:
    - [ ] Close related GitHub Issues.
    - [ ] Update hierarchical status in `docs/backlog.md`.
    - [ ] **Cleanup**: Confirm that all related feature/fix/bug branches (remote and local) have been deleted.
    - [ ] **Versioning**: Tag the release and update `latest` tag (see Section 7) after Feature/Fix/Bug closure.

## 10. Tooling Standards
- [ ] **GitHub Interaction**:
    - [ ] **MUST USE** GitHub MCP Tools (`github-mcp-server`) for:
        - Creating/Merging Pull Requests.
        - Creating/Updating Issues.
        - Managing Branches (Remote).
        - Releases.
    - [ ] **AVOID** `git` CLI commands where MCP alternatives exist.
## 11. Senior CI/CD/QA Role
- **Responsibility**: Monitor GitHub Actions for all branches, especially `developing` and `main`.
- **Process**:
    - [ ] If a GitHub Action failure is detected:
        - [ ] Create a new GitHub Issue with the label `bug` and type `bugfix`.
        - [ ] Reference the failed Run ID and Branch in the issue.
        - [ ] Assign the issue to the current agent.
        - [ ] Switch to a `fix/` branch to resolve the issue.
        - [ ] Verify the fix locally and push to trigger a new CI Run.
        - [ ] Once passed, close the issue and merge the PR.
