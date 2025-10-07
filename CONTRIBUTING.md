# Contributing to OpenGov-EarlyMathematics

We welcome contributions from the community! This document outlines the process for contributing to the OpenGov-EarlyMathematics project.

## Getting Started

### Prerequisites

- Python 3.9 or higher
- uv package manager (recommended)
- Git
- A code editor (VS Code, PyCharm, etc.)

### Development Setup

1. **Fork the repository** on GitHub

2. **Clone your fork**:
   ```bash
   git clone https://github.com/your-username/earlymathematics.git
   cd earlymathematics
   ```

3. **Set up development environment**:
   ```bash
   # Install uv
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Install dependencies
   uv sync --dev

   # Set up pre-commit hooks
   uv run pre-commit install
   ```

4. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### Code Quality Standards

- **Formatting**: Use `black` and `isort` for consistent code formatting
- **Linting**: Use `ruff` for fast Python linting
- **Type Checking**: Use `mypy` for static type checking
- **Security**: Use `bandit` for security vulnerability scanning

Run all quality checks:
```bash
uv run hatch run quality
```

### Testing Requirements

All new features must include comprehensive tests:

- **Unit tests**: Test individual functions and methods
- **Integration tests**: Test component interactions
- **Property-based tests**: Use `hypothesis` for edge cases
- **End-to-end tests**: Test complete user workflows

Run the full test suite:
```bash
uv run pytest -q
```

### Documentation

- Update docstrings for new functions/classes
- Add examples for complex features
- Update README.md for user-facing changes
- Update API documentation for endpoint changes

## Submitting Contributions

### Pull Request Process

1. **Ensure all tests pass**:
   ```bash
   uv run hatch run all
   ```

2. **Update documentation** as needed

3. **Push your branch**:
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create a Pull Request** on GitHub

5. **Address review feedback** and update your PR

### Pull Request Checklist

- [ ] Code follows project style guidelines
- [ ] Tests added/updated for new functionality
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Type hints added for new functions
- [ ] Security considerations addressed
- [ ] Performance impact assessed

## Code Style Guidelines

### Python Conventions

- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Use descriptive variable names
- Keep functions small and focused
- Add docstrings to all public functions

### Commit Messages

Use conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Maintenance tasks

### File Organization

```
src/opengov_earlymathematics/
├── core/           # Core business logic
├── api/            # API endpoints and routes
├── ui/             # User interface components
├── agents/         # AI agents and integrations
├── utils/          # Utility functions
├── tui/            # Terminal user interface
└── ml/             # Machine learning components

tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
├── e2e/           # End-to-end tests
└── property/       # Property-based tests
```

## Reporting Issues

### Bug Reports

When reporting bugs, please include:

- **Description**: Clear description of the issue
- **Steps to reproduce**: Detailed steps to reproduce the problem
- **Expected behavior**: What you expected to happen
- **Actual behavior**: What actually happened
- **Environment**: Python version, OS, relevant dependencies
- **Error messages**: Full error traceback if applicable

### Feature Requests

For feature requests, please include:

- **Use case**: Description of the problem you're trying to solve
- **Proposed solution**: How you think it should work
- **Alternatives considered**: Other solutions you've considered
- **Additional context**: Any other relevant information

## Community Guidelines

### Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

### Getting Help

- Check the [troubleshooting guide](../README.md#troubleshooting) in README.md
- Search existing [issues](https://github.com/opengov/earlymathematics/issues) for similar problems
- Ask questions in [discussions](https://github.com/opengov/earlymathematics/discussions)

## Recognition

Contributors will be recognized in the project README and changelog. Significant contributions may also be acknowledged in release notes and blog posts.

## License

By contributing to this project, you agree that your contributions will be licensed under the same MIT License that covers the project.