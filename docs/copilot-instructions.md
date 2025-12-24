# GitHub Copilot Instructions

This file provides context and instructions for GitHub Copilot.

## Project Guidelines

This project uses SHERPA for knowledge management and follows organizational best practices.

## Code Patterns

Please follow these organizational patterns when suggesting code:

### Git Commits

Category: git/commits

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
# perf...

[See full snippet in .cursor/rules/00-sherpa-knowledge.md]

### Api Rest

Category: api/rest

# REST API Design Patterns

## Category: api/rest
## Language: python, javascript, typescript
## Tags: rest-api, http, fastapi, express, api-design

## Best Practices for REST API Design

### 1. RESTful Endpoint Structure

```
# Resource-based URLs
GET    /api/users              # List all users
GET    /api/users/:id          # Get specific user
POST   /api/users              # Create new user
PUT    /api/users/:id          # Update user (full replacement)
PATCH  /api/users/:id          # Update...

[See full snippet in .cursor/rules/00-sherpa-knowledge.md]

### React Hooks

Category: react/hooks

# React Hooks Patterns

## Category: react/hooks
## Language: javascript, typescript
## Tags: react, hooks, state-management, useEffect, useState

## Best Practices for React Hooks

### 1. useState Hook

```typescript
import { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);
  const [user, setUser] = useState<{ name: string; email: string } | null>(null);

  // Functional update pattern
  const increment = () => setCount(prev => prev + 1);

  // Object stat...

[See full snippet in .cursor/rules/00-sherpa-knowledge.md]

### Security Auth

Category: security/auth

# Security & Authentication Patterns

## Category: security/auth
## Language: python, javascript
## Tags: authentication, authorization, security, jwt, oauth

## Best Practices for Authentication

### 1. Password Hashing (Python)

```python
import bcrypt
from passlib.hash import bcrypt

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against a hash""...

[See full snippet in .cursor/rules/00-sherpa-knowledge.md]

### Python Error Handling

Category: python/error-handling

# Python Error Handling Patterns

## Category: python/error-handling
## Language: python
## Tags: error-handling, exceptions, logging, debugging

## Best Practices for Error Handling

### 1. Custom Exception Classes

```python
class AppException(Exception):
    """Base exception for application"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class ValidationError(AppExcept...

[See full snippet in .cursor/rules/00-sherpa-knowledge.md]

### Python Async

Category: python/async

# Python Async/Await Patterns

## Category: python/async
## Language: python
## Tags: async, await, asyncio, concurrency, performance

## Best Practices for Async Programming

### 1. Basic Async/Await Pattern

```python
import asyncio
from typing import List

async def fetch_data(url: str) -> dict:
    """Async function to fetch data"""
    # Simulate async I/O operation
    await asyncio.sleep(1)
    return {"url": url, "data": "some data"}

async def main():
    # Sequential execution
    resu...

[See full snippet in .cursor/rules/00-sherpa-knowledge.md]

### Testing Unit

Category: testing/unit

# Unit Testing Patterns

## Category: testing/unit
## Language: python, javascript, typescript
## Tags: testing, pytest, jest, unit-tests, tdd

## Best Practices for Unit Testing

### 1. Python Unit Tests with pytest

```python
import pytest
from datetime import datetime

# Function to test
def calculate_discount(price: float, discount_percent: float) -> float:
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("Discount must be between 0 and 100")
    return price *...

[See full snippet in .cursor/rules/00-sherpa-knowledge.md]

### None

Category: general

# TypeScript Best Practices

## Overview
This snippet contains best practices for writing TypeScript code.

## Key Principles

1. **Use Strict Mode**
   - Always enable strict mode in tsconfig.json
   - Catches common errors at compile time

2. **Proper Type Annotations**
   - Avoid using 'any' type
   - Use interfaces for object shapes
   - Use type aliases for unions

3. **Error Handling**
   - Use custom error types
   - Handle async errors with try/catch

## Example Code

```typescript
inter...

[See full snippet in .cursor/rules/00-sherpa-knowledge.md]


## Instructions

- Follow organizational coding standards
- Use patterns from the knowledge base above
- Maintain consistency with existing code
- Prioritize security and best practices

---

*Generated by SHERPA V1*
