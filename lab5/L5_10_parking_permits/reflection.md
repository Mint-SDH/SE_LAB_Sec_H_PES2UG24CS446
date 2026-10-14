# Lab 5: Reflection on Static Code Analysis

### 1. Purpose and Scope of Static Code Analysis
Static code analysis evaluates source code without executing it. It allows developers to systematically detect security vulnerabilities, logical bugs, anti-patterns, and style inconsistencies early in the development lifecycle before code enters production.

### 2. Role of the Tools Used
- **Bandit**: Acts as a security scanner focused on Python vulnerabilities, such as hardcoded credentials, insecure pseudo-random generators (`B311`), and dangerous suppression patterns like `try...except...pass` (`B110`).
- **Flake8**: Enforces syntax consistency and PEP 8 styling conventions, identifying whitespace violations, missing blank lines between declarations, and overly broad exception handling.
- **Pylint**: Serves as a deep static analysis engine, evaluating structural design, code smells (e.g. mutable default arguments), docstrings, naming standards, and resource management.

### 3. Impact of Static Analysis on Software Maintainability
Static analysis automates code reviews and establishes consistency across collaborative engineering teams. Addressing issues like mutable default arguments (`W0102`) prevents subtle bugs in stateful applications, while adopting context managers ensures that file descriptors and OS resources are safely managed.

### 4. Conclusion and Best Practices
Incorporating static analysis into automated CI/CD pipelines (such as GitHub Actions or pre-commit hooks) ensures that code quality, security posture, and coding standards are rigorously enforced before pull requests are merged.
