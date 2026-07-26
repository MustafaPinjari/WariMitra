# Development & Engineering Guidelines - WariMitra

## 1. Development Principles
- **Clean Architecture & SOLID Principles**
- **Offline-First:** Always assume the user has poor or no internet connectivity.
- **Security-by-Design:** Enforce RBAC and encryption at every layer.
- **API-First Development:** Document APIs via Swagger/OpenAPI before implementation.

## 2. Coding Standards
- **Python (Backend):** Use `black` for formatting, `isort` for imports, `flake8` for linting, and `mypy` for static typing.
- **TypeScript (Frontend):** Use `ESLint` and `Prettier`.
- **Dart (Flutter):** Use `dart format` and `flutter analyze`.

## 3. Git Workflow & Branching
- `main`: Production-ready code.
- `develop`: Integration branch.
- `feature/*`: New features (e.g., `feature/sos-integration`).
- `bugfix/*`: Non-critical bug fixes.
- `hotfix/*`: Emergency production fixes.
- **Commit Convention:** Use conventional commits (e.g., `feat(auth): implement JWT login`).

## 4. Testing Strategy
- **Unit Testing:** Minimum 90% code coverage. Use `pytest` for Django, `Jest` for React, and `flutter test`.
- **Integration Testing:** Verify API contracts using Postman/Newman.
- **E2E Testing:** Automated user journeys using Cypress or Playwright.
- **Performance Testing:** Load testing via JMeter or k6 to ensure stability under heavy pilgrim traffic.

## 5. CI/CD Pipeline
Every pull request triggers:
1. Linting & Formatting Checks
2. Unit & Integration Tests
3. Security Scanning (SAST/DAST using tools like Snyk or Trivy)
4. Docker Image Build
5. Deployment to Staging Environment (upon approval)
