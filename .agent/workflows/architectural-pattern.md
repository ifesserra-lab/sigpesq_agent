---
description: Architectural Pattern for Libs and Enterprise Apps
---

# Strictly Layered Architectural Pattern

This document defines the reference architectural pattern for this library and its derivatives. It emphasizes separation of concerns, strict dependency rules, and high testability through generic abstraction.

## 1. High-Level Structure

The architecture is composed of four primary layers, following the **Domain-Driven Design (DDD)** tactical patterns and **Clean Architecture** principles.

| Layer | Component | Responsibility |
|-------|-----------|----------------|
| **Presentation** | **Controllers** | Public API (Facade). Handles input, delegates to Services. |
| **Business Logic**| **Services** | Encapsulates business rules. Orchestrates Repositories. |
| **Data Access**   | **Repositories** | Abstract interface for data operations (Generic CRUD+L). |
| **Domain**        | **Unified Models**| Independent Core. Entities are also ORM Models (DRY). |

## 2. Strict Dependency Rule

> [!IMPORTANT]
> Dependencies must only point **inward**. Outer layers depend on inner layers.
> `Controller -> Service -> Repository -> Domain`

- The **Domain** layer is the center and MUST NOT depend on any other layer.
- **Infrastructure** (Concrete Repositories) implements interfaces defined in the Service/Domain layer.

## 3. Key Design Patterns

### 3.1 Generic Component Pattern (via `libbase`)
Every major component should inherit from a generic base class to ensure consistency and minimize boilerplate:
- `GenericController[T]`
- `GenericService[T]`
- `GenericRepository[T]`

### 3.2 Strategy Pattern (Storage)
Concrete implementations of repositories (Postgres, JSON, In-Memory) are selected at runtime via configuration. This allows switching storage without changing business logic.

### 3.3 Factory Pattern (Dependency Injection)
A `ServiceFactory` is responsible for:
1. Reading configuration (`.env`).
2. Selecting the appropriate Repository Strategy.
3. Instantiating Services with injected Repositories.
4. Wiring Controllers with the correct Services.

## 4. Standard Component Templates

### 4.1 Domain Model
Use SQLAlchemy Declarative for a unified model:
```python
class MyEntity(Base):
    __tablename__ = "my_entities"
    id: Mapped[int] = mapped_column(primary_key=True)
    # ... attributes ...
```

### 4.2 Service
Extend `GenericService`:
```python
class MyService(GenericService[MyEntity]):
    def __init__(self, repo: MyRepository):
        super().__init__(repo)
```

### 4.3 Controller
Extend `GenericController`:
```python
class MyController(GenericController[MyEntity]):
    def __init__(self):
        self._service = ServiceFactory.get_my_service()
```

## 5. Verification Standards (TDD)
- **100% Coverage** on the Service Layer.
- **Integration Tests** for Repository Strategies.
- **Demo Script** (`tests/demo.py`) to verify the full flow from Controller to Database.
