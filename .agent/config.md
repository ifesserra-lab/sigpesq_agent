# Agent Configuration -eo_lib

## 🏗 Technical Stack
- **Language**: Python 3.12+
- **Build System**: Hatchling (see `pyproject.toml`)
- **Main Dependencies**: SQLAlchemy 2.0+
- **Test Framework**: Pytest
- **Linting Tools**: Black, Flake8, isort

## 📂 Project Structure Map
- `src/eo_lib/domain/`: `BaseEntity` and core abstractions.
- `src/eo_lib/infrastructure/`: Repository strategies (SQL, JSON, Memory).
- `src/eo_lib/services/`: `GenericService`.
- `src/eo_lib/controllers/`: `GenericController`.
- `tests/`: TDD suite mimicking the `src/` structure.
- `docs/`: Full project documentation (SRS, SDD, Backlog, Milestones).

## ⚙️ Environment Commands
- **Install Dev**: `pip install -e ".[dev]"`
- **Test**: `pytest`
- **Lint**: `flake8 src tests`
- **Format**: `black src tests && isort src tests`
- **Pre-commit**: `lefthook run pre-commit`
- **Bump Version**: `python scripts/bump_version.py [major|minor|patch]`

## 📦 Distribution Standards
- Adhere to SemVer 2.0.0.
- Minimal external dependencies.
- Unified Domain/ORM models (DRY).

## 📝 Governance Templates
Use these patterns for all new issues:
- **Epic**: [.agent/templates/epic.md](.agent/templates/epic.md)
- **User Story**: [.agent/templates/user_story.md](.agent/templates/user_story.md)
- **Task**: [.agent/templates/task.md](.agent/templates/task.md)
