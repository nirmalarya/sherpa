# Type Checking Documentation - SHERPA V1

## Overview

SHERPA V1 uses type checking for both frontend and backend code to catch errors early and improve code quality.

## Frontend Type Checking (TypeScript)

### Configuration

The frontend uses JavaScript with TypeScript for type checking through **jsconfig.json**:

```json
{
  "compilerOptions": {
    "checkJs": true,
    "jsx": "react-jsx",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "target": "ES2020",
    "lib": ["ES2020", "DOM", "DOM.Iterable"]
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "build"]
}
```

### Running Frontend Type Checking

```bash
# From project root
cd sherpa/frontend
npm run type-check

# Or use the convenience script
./run_type_check.sh
```

### TypeScript Configuration Files

1. **jsconfig.json** - Main configuration for JavaScript type checking
2. **tsconfig.json** - TypeScript compiler configuration (for future migration)
3. **tsconfig.node.json** - Configuration for Node.js tooling (Vite)

## Backend Type Checking (mypy)

### Configuration

The backend uses **mypy** configured in `pyproject.toml`:

```toml
[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false
ignore_missing_imports = true
exclude = [
    "venv",
    "venv-312",
    "node_modules",
    "dist",
    "build",
    "sherpa/frontend"
]
```

### Running Backend Type Checking

```bash
# From project root
venv-312/bin/mypy sherpa/

# Or use the convenience script
./run_type_check.sh
```

### Type Annotation Guidelines

1. **Function Signatures**
   ```python
   async def get_snippets(
       category: Optional[str] = None,
       limit: int = 10
   ) -> List[Dict[str, Any]]:
       pass
   ```

2. **Class Attributes**
   ```python
   from dataclasses import dataclass

   @dataclass
   class SessionConfig:
       session_id: str
       max_iterations: int = 100
       timeout: float = 300.0
   ```

3. **Return Types**
   ```python
   from typing import Dict, List, Optional, Union

   def process_data(data: Dict[str, Any]) -> Optional[str]:
       return data.get("value")
   ```

## Running All Type Checks

### Automated Script

Use the provided bash script to run both frontend and backend type checking:

```bash
chmod +x run_type_check.sh
./run_type_check.sh
```

The script will:
1. Check for and install dependencies if needed
2. Run TypeScript compiler on frontend
3. Run mypy on backend
4. Display a summary of results

### Manual Checks

**Frontend:**
```bash
cd sherpa/frontend
npm run type-check
```

**Backend:**
```bash
source venv-312/bin/activate  # or venv/bin/activate
mypy sherpa/
```

## Integration with Development Workflow

### IDE Integration

**VS Code:**
- Install "TypeScript" extension (built-in)
- Install "Pylance" extension for Python
- Type errors will be highlighted in the editor

**Cursor:**
- Type checking is automatically enabled
- Hover over variables to see inferred types

### Pre-commit Hooks

Type checking can be integrated into Git pre-commit hooks:

```bash
# In .git/hooks/pre-commit
#!/bin/bash

# Run type checking before allowing commit
./run_type_check.sh

if [ $? -ne 0 ]; then
    echo "Type checking failed. Please fix errors before committing."
    exit 1
fi
```

### CI/CD Integration

Add to GitHub Actions or other CI/CD pipelines:

```yaml
# .github/workflows/type-check.yml
name: Type Checking

on: [push, pull_request]

jobs:
  type-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      # Frontend
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install frontend dependencies
        run: |
          cd sherpa/frontend
          npm install

      - name: Type check frontend
        run: |
          cd sherpa/frontend
          npm run type-check

      # Backend
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install backend dependencies
        run: |
          python -m pip install -r requirements.txt

      - name: Type check backend
        run: mypy sherpa/
```

## Type Coverage

### Frontend

TypeScript can check JavaScript files with JSDoc comments:

```javascript
/**
 * Fetch user data from API
 * @param {string} userId - The user ID
 * @returns {Promise<Object>} User data
 */
async function fetchUser(userId) {
    const response = await fetch(`/api/users/${userId}`);
    return response.json();
}
```

### Backend

Aim for high type coverage:

```bash
# Check type coverage
mypy sherpa/ --html-report mypy-report

# View report
open mypy-report/index.html
```

## Common Type Errors and Fixes

### Frontend

**Error:** `Cannot find module 'react'`
```bash
# Fix: Install type definitions
npm install --save-dev @types/react @types/react-dom
```

**Error:** `Property 'foo' does not exist on type`
```javascript
// Fix: Add proper JSDoc or use type assertions
/** @type {{foo: string}} */
const obj = { foo: 'bar' };
```

### Backend

**Error:** `Missing type annotation for variable`
```python
# Before
data = {}

# After
data: Dict[str, Any] = {}
```

**Error:** `Incompatible return value type`
```python
# Before
def get_value() -> str:
    return None  # Error!

# After
def get_value() -> Optional[str]:
    return None  # OK
```

## Best Practices

### Frontend
1. ✅ Use TypeScript's `strict` mode for new files
2. ✅ Add JSDoc comments for complex functions
3. ✅ Use type imports: `import type { User } from './types'`
4. ✅ Leverage IDE autocomplete and type hints
5. ✅ Run type checking before commits

### Backend
1. ✅ Add type annotations to all public functions
2. ✅ Use dataclasses for structured data
3. ✅ Import from `typing` module: `List`, `Dict`, `Optional`
4. ✅ Use `Any` sparingly - be specific when possible
5. ✅ Run mypy regularly during development

## Troubleshooting

### TypeScript Not Found

```bash
cd sherpa/frontend
npm install typescript --save-dev
```

### mypy Not Found

```bash
pip install mypy
# or
source venv-312/bin/activate
pip install mypy
```

### Configuration Issues

1. **jsconfig.json not recognized**
   - Restart your IDE
   - Check that file is in `sherpa/frontend/` directory

2. **mypy ignoring files**
   - Check `exclude` patterns in `pyproject.toml`
   - Verify file paths are correct

## Resources

- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- [mypy Documentation](https://mypy.readthedocs.io/)
- [Python Type Hints (PEP 484)](https://peps.python.org/pep-0484/)
- [JSConfig Reference](https://code.visualstudio.com/docs/languages/jsconfig)

## Summary

Type checking is now configured for SHERPA V1:

✅ Frontend: TypeScript checking JavaScript files via jsconfig.json
✅ Backend: mypy checking Python files via pyproject.toml
✅ Automated script: `./run_type_check.sh`
✅ IDE integration ready
✅ CI/CD integration examples provided

Run `./run_type_check.sh` before commits to catch type errors early!
