# Contributing to Mechanics Roster Optimization

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Development Setup

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/yourusername/mechanics-roster-optimization.git
   cd mechanics-roster-optimization
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

## Code Style

This project uses:
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting

Before committing, run:
```bash
black src/ tests/
isort src/ tests/
flake8 src/ tests/
```

## Testing

- Write tests for all new features
- Ensure all tests pass: `pytest`
- Maintain or improve test coverage
- Run tests with coverage: `pytest --cov=src/mechanics_roster --cov-report=html`

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes
3. Add/update tests
4. Ensure all tests pass
5. Run linting checks
6. Update documentation if needed
7. Submit a pull request with a clear description

## Commit Messages

Use clear, descriptive commit messages:
- `feat: Add new feature`
- `fix: Fix bug in optimizer`
- `docs: Update README`
- `test: Add tests for data loader`
- `refactor: Restructure code`

## Questions?

Feel free to open an issue for questions or discussions!
