# Contributing to the Cardiology Care Optimization System

First off, thank you for considering contributing! Your help is appreciated and will make this project better.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Pull Requests](#pull-requests)
- [Development Setup](#development-setup)
- [Styleguides](#styleguides)
  - [Git Commit Messages](#git-commit-messages)
  - [Python Styleguide](#python-styleguide)
  - [Documentation Styleguide](#documentation-styleguide)
- [Testing](#testing)
- [Releasing](#releasing)

## Code of Conduct

This project and everyone participating in it is governed by the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/code_of_conduct.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

- **Ensure the bug was not already reported** by searching on GitHub under [Issues](https://github.com/yourusername/ca-cardiology-optimizer/issues).
- If you're unable to find an open issue addressing the problem, [open a new one](https://github.com/yourusername/ca-cardiology-optimizer/issues/new). Be sure to include a **title and clear description**, as much relevant information as possible, and a **code sample** or an **executable test case** demonstrating the expected behavior that is not occurring.

### Suggesting Enhancements

- Open an issue and provide as much detail as possible about the enhancement, including the use case and why it would be beneficial.

### Pull Requests

1.  Fork the repo and create your branch from `develop`.
2.  If you've added code that should be tested, add tests.
3.  If you've changed APIs, update the documentation.
4.  Ensure the test suite passes (`make test`).
5.  Make sure your code lints (`make lint`).
6.  Issue that pull request!

## Development Setup

You can set up your local development environment by following the instructions in the [README.md](README.md) or by running the automated setup script:

```bash
bash scripts/setup_env.sh
```

Remember to activate your virtual environment before you start developing:
```bash
source venv/bin/activate
```

## Styleguides

### Git Commit Messages

- Use the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification.
- Message format: `<type>(<scope>): <subject>`
  - `feat`: A new feature
  - `fix`: A bug fix
  - `docs`: Documentation only changes
  - `style`: Changes that do not affect the meaning of the code (white-space, formatting, etc)
  - `refactor`: A code change that neither fixes a bug nor adds a feature
  - `perf`: A code change that improves performance
  - `test`: Adding missing tests or correcting existing tests
  - `chore`: Changes to the build process or auxiliary tools and libraries such as documentation generation

### Python Styleguide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/).
- Use `black` for code formatting and `isort` for import sorting.
- Our `pre-commit` hooks will enforce this automatically.

### Documentation Styleguide

- Use Markdown for all documentation.
- Docstrings should follow the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings).

## Testing

- All new features should be accompanied by tests.
- We use `pytest` for testing. You can run the full test suite with `make test`.
- Aim for a high level of test coverage.

## Releasing

- The `main` branch is for stable releases.
- The `develop` branch is for ongoing development.
- Releases are tagged using semantic versioning (e.g., `v1.2.3`).
- A new release is created by a project maintainer by merging `develop` into `main` and creating a new tag.

Thank you for your contribution!
