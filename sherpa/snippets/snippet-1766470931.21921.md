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
interface User {
    id: string;
    name: string;
    email: string;
}

async function getUser(id: string): Promise<User> {
    try {
        const response = await fetch(`/api/users/${id}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Failed to fetch user:', error);
        throw error;
    }
}
```

## Resources
- TypeScript Handbook: https://www.typescriptlang.org/docs/
- Effective TypeScript: https://effectivetypescript.com/
