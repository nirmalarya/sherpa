# Git Hooks Documentation - SHERPA V1

## Overview

SHERPA V1 uses pre-commit hooks to automatically run code quality checks before allowing commits. This ensures that only code that passes linting, formatting, and security checks can be committed to the repository.

## Quick Start

### Installation

```bash
# One-time setup
./setup_hooks.sh
```

This script will:
1. Install pre-commit framework
2. Install detect-secrets for security scanning
3. Configure git hooks
4. Install hook dependencies
5. Test the hooks on all files

### Manual Installation

```bash
# Activate virtual environment
source venv-312/bin/activate  # or venv/bin/activate

# Install pre-commit
pip install pre-commit detect-secrets

# Install hooks
pre-commit install

# Install hook dependencies
pre-commit install-hooks
```

## Configured Hooks

### Frontend Checks

**ESLint** - JavaScript/JSX Linting
- Runs: `npm run lint` in sherpa/frontend/
- Checks: Code style, React best practices, unused variables
- Files: `*.js`, `*.jsx`

### Backend Checks

**flake8** - Python Linting
- Runs: `flake8 sherpa/`
- Checks: PEP 8 compliance, code complexity
- Config: `.flake8`

**black** - Python Formatting
- Runs: `black sherpa/ --check`
- Checks: Code formatting consistency
- Config: `pyproject.toml`

**mypy** - Type Checking
- Runs: `mypy sherpa/`
- Checks: Type annotations and type safety
- Config: `pyproject.toml`
- Note: Non-blocking (uses `|| true`)

### General Checks

**Trailing Whitespace** - Remove trailing spaces
- Auto-fixes trailing whitespace
- Excludes: `*.md` files

**End of File Fixer** - Ensure single newline at EOF
- Auto-fixes end of file formatting
- Excludes: `*.md` files

**YAML Validation** - Check YAML syntax
- Validates: `.yaml`, `.yml` files

**JSON Validation** - Check JSON syntax
- Validates: `.json` files

**Large File Detection** - Prevent large commits
- Max size: 1000 KB
- Prevents accidentally committing large files

**Merge Conflict Detection** - Catch merge markers
- Prevents committing files with conflict markers

**Private Key Detection** - Security check
- Prevents committing SSH private keys

**Mixed Line Endings** - Ensure consistent line endings
- Fixes: Convert to LF (Unix-style)

### Security Checks

**detect-secrets** - Secret Detection
- Scans for: API keys, passwords, tokens
- Uses baseline: `.secrets.baseline`
- Excludes: `package-lock.json`

## Usage

### Normal Commits

```bash
# Make changes
git add .

# Commit (hooks run automatically)
git commit -m "Your commit message"

# Hooks will run and either:
# ✅ Allow commit if all checks pass
# ❌ Block commit if any check fails
```

### Running Hooks Manually

```bash
# Run all hooks on all files
pre-commit run --all-files

# Run specific hook
pre-commit run eslint --all-files
pre-commit run flake8 --all-files

# Run on specific files
pre-commit run --files sherpa/api/main.py
```

### Skipping Hooks (Not Recommended)

```bash
# Skip hooks for emergency commits only
git commit --no-verify -m "Emergency fix"

# Better approach: Fix the issues!
```

### Updating Hooks

```bash
# Update to latest hook versions
pre-commit autoupdate

# Re-install after updating
pre-commit install-hooks
```

## Hook Configuration

### .pre-commit-config.yaml

The main configuration file defines all hooks:

```yaml
repos:
  - repo: local
    hooks:
      - id: eslint
        name: ESLint (Frontend)
        entry: bash -c 'cd sherpa/frontend && npm run lint'
        language: system
        files: \.jsx?$

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
```

### .secrets.baseline

Baseline file for detect-secrets:
- Records known false positives
- Prevents re-alerting on same issues
- Can be updated with new baseline

## Troubleshooting

### Hook Failed: ESLint

**Error:** `ESLint found errors`

**Solution:**
```bash
cd sherpa/frontend
npm run lint -- --fix
```

### Hook Failed: flake8

**Error:** `flake8 found style violations`

**Solution:**
```bash
# Auto-fix many issues with black
venv-312/bin/black sherpa/

# Check remaining issues
venv-312/bin/flake8 sherpa/
```

### Hook Failed: black

**Error:** `Files would be reformatted`

**Solution:**
```bash
# Reformat files
venv-312/bin/black sherpa/

# Add and commit again
git add .
git commit -m "Your message"
```

### Hook Failed: detect-secrets

**Error:** `Potential secrets detected`

**Solution:**
```bash
# Review the flagged content
# If false positive, update baseline:
detect-secrets scan --baseline .secrets.baseline

# If real secret, remove it and use environment variables
```

### Hooks Not Running

**Problem:** Hooks don't run on commit

**Solutions:**
1. Check installation:
   ```bash
   ls -la .git/hooks/pre-commit
   ```

2. Reinstall hooks:
   ```bash
   pre-commit install
   ```

3. Verify config file:
   ```bash
   pre-commit validate-config
   ```

### Pre-commit Not Found

**Problem:** `pre-commit: command not found`

**Solution:**
```bash
# Activate virtual environment
source venv-312/bin/activate

# Install pre-commit
pip install pre-commit

# Or run setup script
./setup_hooks.sh
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Pre-commit Checks

on: [push, pull_request]

jobs:
  pre-commit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install pre-commit
          pre-commit install-hooks

      - name: Run pre-commit
        run: pre-commit run --all-files
```

## Best Practices

### Do's ✅

1. **Run hooks before pushing**
   ```bash
   pre-commit run --all-files
   git push
   ```

2. **Fix issues immediately**
   - Don't accumulate hook failures
   - Fix at commit time, not later

3. **Update hooks regularly**
   ```bash
   pre-commit autoupdate
   ```

4. **Test on all files after major changes**
   ```bash
   pre-commit run --all-files
   ```

5. **Keep .secrets.baseline updated**
   - Review and update when needed
   - Don't ignore real secrets

### Don'ts ❌

1. **Don't skip hooks habitually**
   - `--no-verify` should be rare
   - Fix issues instead of skipping

2. **Don't commit secrets**
   - Use environment variables
   - Use secret management tools

3. **Don't ignore hook failures**
   - Address issues promptly
   - Don't defer to "fix later"

4. **Don't disable useful hooks**
   - If a hook is annoying, fix the root cause
   - Don't remove hooks to avoid fixing code

## Hook Customization

### Adding New Hooks

Edit `.pre-commit-config.yaml`:

```yaml
  - repo: local
    hooks:
      - id: custom-hook
        name: My Custom Check
        entry: ./scripts/my-check.sh
        language: system
        pass_filenames: false
```

### Modifying Existing Hooks

```yaml
  - repo: local
    hooks:
      - id: flake8
        name: flake8 (Backend)
        entry: flake8 sherpa/
        language: system
        types: [python]
        args: ['--max-line-length=120']  # Custom args
```

### Disabling Specific Hooks

```yaml
# Temporarily disable a hook
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
        exclude: '^path/to/exclude/'
```

## Performance Tips

### Speed Up Hooks

1. **Use file filtering**
   ```yaml
   files: '^sherpa/.*\.py$'  # Only Python files in sherpa/
   ```

2. **Run hooks in parallel**
   - Pre-commit runs hooks in parallel by default
   - Keep hooks independent for best performance

3. **Use `pass_filenames: false` sparingly**
   - This forces hook to run on all files
   - Use `pass_filenames: true` when possible

### Debugging Slow Hooks

```bash
# Show hook execution times
pre-commit run --all-files --verbose

# Profile specific hook
time pre-commit run flake8 --all-files
```

## Resources

- [Pre-commit Documentation](https://pre-commit.com/)
- [Pre-commit Hooks Catalog](https://pre-commit.com/hooks.html)
- [detect-secrets Documentation](https://github.com/Yelp/detect-secrets)
- [Git Hooks Documentation](https://git-scm.com/docs/githooks)

## Summary

Git hooks are now configured for SHERPA V1:

✅ **Frontend:** ESLint linting
✅ **Backend:** flake8 linting, black formatting, mypy type checking
✅ **General:** Whitespace, file formatting, YAML/JSON validation
✅ **Security:** Secret detection, private key detection
✅ **Setup:** Automated setup script (`setup_hooks.sh`)
✅ **Documentation:** Comprehensive guide

Run `./setup_hooks.sh` to get started!

---

**Git Hooks Status:** ✅ CONFIGURED AND READY

🤖 Generated with Claude Code 🏔️
