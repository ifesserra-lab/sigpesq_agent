# Project Backlog

## Epics

### [EPIC-1] Project Refactoring & Standards Alignment
*Goal: Align project structure, documentation, and configuration with "The Band Project" standards and actual code usage.*

#### User Stories
- [ ] **US-1**: Cleanup Documentation & Dependencies
    - *As a maintainer, I want to remove unused dependency documentation and standardize exports so that the project configuration is accurate.*
    - **Tasks**:
        - [ ] Remove SQLAlchemy/libbase refs from config.
        - [ ] Configure `__init__.py` exports.

## Releases
### [v0.1.1] Refactor Dependencies
- **PR**: [#2](https://github.com/ifesserra-lab/sigpesq_agent/pull/2)
- **Description**: Removed unused documentation references (SQLAlchemy, libbase) and standardized `__init__.py` exports.
- **Commit**: `refactor: remove unused deps docs and standardize exports (closes #1)`

### Bugs
- [x] Fix agent execution error (DevTools/ChromeDriver) - [PR #5](https://github.com/ifesserra-lab/sigpesq_agent/pull/5)
- [x] Fix agent execution error (DevTools/ChromeDriver) - [PR #5](https://github.com/ifesserra-lab/sigpesq_agent/pull/5)

### [v0.3.1] Doc Update (ADR)
- **PR**: [#24](https://github.com/ifesserra-lab/sigpesq_agent/pull/24)
- **Description**: Added Architecture Decision Record (ADR 0001) for Playwright migration.
- **Commit**: `docs: Add ADR 0001 regarding Playwright migration (#23)`

### [v0.3.0] Playwright Migration
- **PR**: [#20](https://github.com/ifesserra-lab/sigpesq_agent/pull/20)
- **Description**: Migrated from Selenium to Playwright. Implemented new strategies and CLI.
- **Commit**: `release: v0.2.0 - Playwright Migration (closes #19, #16)`

### [v0.2.0] Refactor Strategies & Implement Downloads
- **PR**: [#8](https://github.com/ifesserra-lab/sigpesq_agent/pull/8)
- **Description**: Implemented real download strategies for Research Groups, Projects, and Advisorships. Refactored common logic into `BaseSeleniumStrategy`.
- **Commit**: `refactor: abstract common download logic into BaseSeleniumStrategy (closes #7)`
