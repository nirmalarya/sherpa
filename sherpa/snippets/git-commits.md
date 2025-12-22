# Git Commit Patterns

## Category: git/commits
## Language: bash, git
## Tags: git, version-control, commits, best-practices

## Best Practices for Git Commits

### 1. Commit Message Format

```bash
# Conventional Commits format
<type>(<scope>): <subject>

<body>

<footer>

# Types:
# feat: A new feature
# fix: A bug fix
# docs: Documentation only changes
# style: Changes that don't affect code meaning (formatting, etc.)
# refactor: Code change that neither fixes a bug nor adds a feature
# perf: Code change that improves performance
# test: Adding or updating tests
# chore: Changes to build process or auxiliary tools

# Examples:
git commit -m "feat(auth): add JWT authentication

Implement JWT-based authentication system with:
- Token generation and validation
- Refresh token mechanism
- Middleware for protected routes

Closes #123"

git commit -m "fix(api): resolve null pointer exception in user endpoint

The user endpoint was throwing NPE when email field was missing.
Added validation to check for required fields.

Fixes #456"

git commit -m "docs: update API documentation for v2.0"

git commit -m "refactor(database): optimize query performance

Replaced N+1 queries with join operations.
Performance improvement: 10x faster on large datasets."
```

### 2. Atomic Commits

```bash
# Bad: Multiple unrelated changes
git add .
git commit -m "Fix bugs and add features"

# Good: Separate commits for each logical change
git add auth.py
git commit -m "feat(auth): add password reset functionality"

git add tests/test_auth.py
git commit -m "test(auth): add tests for password reset"

git add docs/api.md
git commit -m "docs(auth): document password reset endpoint"
```

### 3. Interactive Staging

```bash
# Stage specific parts of files
git add -p file.py

# Interactive commit
git commit --verbose

# Amend last commit (only if not pushed!)
git commit --amend

# Amend without changing message
git commit --amend --no-edit

# Fix commit message
git commit --amend -m "New commit message"
```

### 4. Branch Management

```bash
# Create feature branch
git checkout -b feature/user-authentication

# Work on feature with multiple commits
git commit -m "feat(auth): add login endpoint"
git commit -m "feat(auth): add logout endpoint"
git commit -m "test(auth): add authentication tests"

# Squash commits before merging (interactive rebase)
git rebase -i main

# In editor, change 'pick' to 'squash' for commits to combine
# pick abc123 feat(auth): add login endpoint
# squash def456 feat(auth): add logout endpoint
# squash ghi789 test(auth): add authentication tests

# Push feature branch
git push origin feature/user-authentication

# Create pull request, then merge
# After merge, delete branch
git checkout main
git pull
git branch -d feature/user-authentication
git push origin --delete feature/user-authentication
```

### 5. Commit Hooks

```bash
# .git/hooks/pre-commit
#!/bin/bash

# Run linter
echo "Running linter..."
npm run lint || exit 1

# Run tests
echo "Running tests..."
npm test || exit 1

# Check for debugging code
if grep -r "console.log" src/; then
    echo "Error: console.log() found in source files"
    exit 1
fi

echo "Pre-commit checks passed!"
```

```bash
# .git/hooks/commit-msg
#!/bin/bash

# Validate commit message format
commit_msg=$(cat "$1")

# Check for conventional commit format
if ! echo "$commit_msg" | grep -qE "^(feat|fix|docs|style|refactor|perf|test|chore)(\(.+\))?: .{1,}"; then
    echo "Error: Commit message must follow conventional commits format"
    echo "Format: type(scope): subject"
    echo "Example: feat(auth): add login functionality"
    exit 1
fi

# Check subject line length
subject=$(echo "$commit_msg" | head -n 1)
if [ ${#subject} -gt 72 ]; then
    echo "Error: Subject line too long (max 72 characters)"
    exit 1
fi
```

### 6. Useful Git Commands

```bash
# View commit history
git log --oneline --graph --all
git log --author="John Doe" --since="2 weeks ago"
git log --grep="fix" --oneline

# Show changes in commit
git show abc123
git show HEAD~2

# View file history
git log --follow -- path/to/file.py
git blame path/to/file.py

# Undo commits (careful!)
git reset --soft HEAD~1  # Keep changes staged
git reset --mixed HEAD~1 # Keep changes unstaged (default)
git reset --hard HEAD~1  # Discard changes (dangerous!)

# Revert a commit (creates new commit)
git revert abc123

# Cherry-pick specific commit
git cherry-pick abc123

# Stash changes
git stash save "Work in progress"
git stash list
git stash pop
git stash apply stash@{0}

# Clean up
git clean -fd  # Remove untracked files and directories
git gc         # Garbage collection
```

### 7. Git Workflow Examples

```bash
# Feature Branch Workflow
git checkout main
git pull origin main
git checkout -b feature/new-feature
# ... work and commit ...
git push origin feature/new-feature
# Create PR, review, merge

# Gitflow Workflow
# Main branches: main, develop
# Supporting branches: feature/, release/, hotfix/

# Start feature
git checkout develop
git checkout -b feature/my-feature
# ... work ...
git checkout develop
git merge --no-ff feature/my-feature
git branch -d feature/my-feature

# Create release
git checkout develop
git checkout -b release/1.2.0
# ... version bump, bug fixes ...
git checkout main
git merge --no-ff release/1.2.0
git tag -a v1.2.0 -m "Release version 1.2.0"
git checkout develop
git merge --no-ff release/1.2.0
git branch -d release/1.2.0

# Hotfix
git checkout main
git checkout -b hotfix/critical-bug
# ... fix ...
git checkout main
git merge --no-ff hotfix/critical-bug
git tag -a v1.2.1 -m "Hotfix version 1.2.1"
git checkout develop
git merge --no-ff hotfix/critical-bug
git branch -d hotfix/critical-bug
```

### 8. Commit Signing

```bash
# Configure GPG signing
git config --global user.signingkey YOUR_GPG_KEY
git config --global commit.gpgSign true

# Sign commits
git commit -S -m "feat: add secure feature"

# Verify signed commits
git log --show-signature
git verify-commit abc123
```

### 9. Git Aliases

```bash
# Add to ~/.gitconfig or use git config --global

[alias]
    # Shortcuts
    co = checkout
    br = branch
    ci = commit
    st = status

    # Useful aliases
    unstage = reset HEAD --
    last = log -1 HEAD
    visual = log --oneline --graph --all --decorate

    # Amend staged changes to previous commit
    amend = commit --amend --no-edit

    # Show diff of staged changes
    staged = diff --staged

    # List all aliases
    aliases = config --get-regexp alias

    # Undo last commit but keep changes
    undo = reset --soft HEAD~1

    # Clean up merged branches
    cleanup = "!git branch --merged | grep -v '\\*\\|main\\|develop' | xargs -n 1 git branch -d"
```

### 10. Commit Message Templates

```bash
# Create template file: ~/.gitmessage
# <type>(<scope>): <subject>
#
# <body>
#
# <footer>
#
# Type: feat, fix, docs, style, refactor, perf, test, chore
# Scope: component or file name
# Subject: imperative, lowercase, no period at end
# Body: explain what and why (not how)
# Footer: reference issues, breaking changes

# Configure Git to use template
git config --global commit.template ~/.gitmessage
```

## Git Commit Checklist

- ✅ Write clear, descriptive commit messages
- ✅ Use conventional commit format
- ✅ Keep commits atomic (one logical change per commit)
- ✅ Don't commit commented-out code or debug statements
- ✅ Test code before committing
- ✅ Don't commit secrets or sensitive data
- ✅ Keep subject line under 72 characters
- ✅ Use imperative mood ("add feature" not "added feature")
- ✅ Reference issue numbers in commit messages
- ✅ Review changes before committing
- ✅ Use branches for features and fixes
- ✅ Squash commits before merging to main
- ✅ Sign important commits
- ✅ Pull before pushing
- ✅ Don't rewrite public history (pushed commits)
