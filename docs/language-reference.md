# Language Reference

Use the project-native command when available.

| Language/Framework | Test | Build | Review |
|---|---|---|---|
| Go | `/go-test` or `go test ./...` | `/go-build` or `go build ./...` | `/go-review` |
| Rust | `/rust-test` or `cargo test` | `/rust-build` or `cargo build` | `/rust-review` |
| C++ | `/cpp-test` or CTest | `/cpp-build` | `/cpp-review` |
| Flutter/Dart | `/flutter-test` | `/flutter-build` | `/flutter-review` |
| Kotlin | `/kotlin-test` | `/kotlin-build` | `/kotlin-review` |
| Python | `pytest` | project-specific | `/python-review` |
| Laravel | `/laravel-tdd` | project-specific | `/laravel-verification` |
| Django | `/django-tdd` | project-specific | `/django-verification` |
| Spring Boot | `/springboot-tdd` | Maven/Gradle build | `/springboot-verification` |
| TypeScript/JS | `bun test` / `npm test` | `bun run build` / `npm run build` | `/code-review` |

## Skill Routing Hints

- Frontend/UI: use `visual-engineering` plus frontend/UI skills only when visual implementation matters.
- Backend/API: prefer `backend-patterns` and `api-design` for API/service work.
- Full stack: use `fullstack-dev` and `tdd-workflow` when frontend-backend integration is part of the task.
- Data/DB: use `database-migrations` and `postgres-patterns` for schema or query changes.
- Keep skill loading narrow; broad skill sets are a token cost and should match actual task scope.
