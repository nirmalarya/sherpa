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

  // Object state update
  const updateUser = (name: string, email: string) => {
    setUser({ name, email });
  };

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={increment}>Increment</button>
    </div>
  );
}
```

### 2. useEffect Hook

```typescript
import { useState, useEffect } from 'react';

function UserProfile({ userId }: { userId: string }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    const fetchUser = async () => {
      try {
        setLoading(true);
        const response = await fetch(`/api/users/${userId}`);
        const data = await response.json();

        if (!cancelled) {
          setUser(data);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    fetchUser();

    // Cleanup function
    return () => {
      cancelled = true;
    };
  }, [userId]); // Dependency array

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  return <div>User: {user?.name}</div>;
}
```

### 3. Custom Hooks

```typescript
import { useState, useEffect } from 'react';

// Custom hook for API fetching
function useFetch<T>(url: string) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await fetch(url);
        if (!response.ok) throw new Error('Network response was not ok');
        const json = await response.json();
        setData(json);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [url]);

  return { data, loading, error };
}

// Usage
function UserList() {
  const { data: users, loading, error } = useFetch<User[]>('/api/users');

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  return (
    <ul>
      {users?.map(user => <li key={user.id}>{user.name}</li>)}
    </ul>
  );
}
```

### 4. useContext for State Management

```typescript
import { createContext, useContext, useState, ReactNode } from 'react';

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  const login = async (email: string, password: string) => {
    const response = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await response.json();
    setUser(data.user);
  };

  const logout = () => {
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

// Usage in component
function LoginButton() {
  const { user, login, logout } = useAuth();

  if (user) {
    return <button onClick={logout}>Logout</button>;
  }

  return <button onClick={() => login('user@example.com', 'password')}>Login</button>;
}
```

### 5. useReducer for Complex State

```typescript
import { useReducer } from 'react';

interface State {
  count: number;
  error: string | null;
  loading: boolean;
}

type Action =
  | { type: 'increment' }
  | { type: 'decrement' }
  | { type: 'reset' }
  | { type: 'setError'; payload: string }
  | { type: 'setLoading'; payload: boolean };

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'increment':
      return { ...state, count: state.count + 1, error: null };
    case 'decrement':
      return { ...state, count: state.count - 1, error: null };
    case 'reset':
      return { ...state, count: 0, error: null };
    case 'setError':
      return { ...state, error: action.payload };
    case 'setLoading':
      return { ...state, loading: action.payload };
    default:
      return state;
  }
}

function Counter() {
  const [state, dispatch] = useReducer(reducer, {
    count: 0,
    error: null,
    loading: false
  });

  return (
    <div>
      <p>Count: {state.count}</p>
      {state.error && <p>Error: {state.error}</p>}
      <button onClick={() => dispatch({ type: 'increment' })}>+</button>
      <button onClick={() => dispatch({ type: 'decrement' })}>-</button>
      <button onClick={() => dispatch({ type: 'reset' })}>Reset</button>
    </div>
  );
}
```

### 6. useCallback and useMemo

```typescript
import { useState, useCallback, useMemo } from 'react';

function ExpensiveComponent() {
  const [count, setCount] = useState(0);
  const [items, setItems] = useState([1, 2, 3, 4, 5]);

  // Memoize expensive computation
  const sum = useMemo(() => {
    console.log('Computing sum...');
    return items.reduce((acc, item) => acc + item, 0);
  }, [items]); // Only recompute when items change

  // Memoize callback
  const handleClick = useCallback(() => {
    setCount(prev => prev + 1);
  }, []); // Never changes

  return (
    <div>
      <p>Sum: {sum}</p>
      <p>Count: {count}</p>
      <button onClick={handleClick}>Increment</button>
    </div>
  );
}
```

### 7. useRef for DOM and Mutable Values

```typescript
import { useRef, useEffect } from 'react';

function InputFocus() {
  const inputRef = useRef<HTMLInputElement>(null);
  const renderCount = useRef(0);

  useEffect(() => {
    // Focus input on mount
    inputRef.current?.focus();

    // Track render count
    renderCount.current++;
  });

  return (
    <div>
      <input ref={inputRef} type="text" />
      <p>Render count: {renderCount.current}</p>
    </div>
  );
}

// Timer example
function Timer() {
  const [seconds, setSeconds] = useState(0);
  const intervalRef = useRef<number | null>(null);

  const start = () => {
    if (intervalRef.current !== null) return;
    intervalRef.current = window.setInterval(() => {
      setSeconds(prev => prev + 1);
    }, 1000);
  };

  const stop = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  };

  const reset = () => {
    stop();
    setSeconds(0);
  };

  useEffect(() => {
    return () => stop(); // Cleanup on unmount
  }, []);

  return (
    <div>
      <p>Seconds: {seconds}</p>
      <button onClick={start}>Start</button>
      <button onClick={stop}>Stop</button>
      <button onClick={reset}>Reset</button>
    </div>
  );
}
```

### 8. Custom Hook for localStorage

```typescript
import { useState, useEffect } from 'react';

function useLocalStorage<T>(key: string, initialValue: T) {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(error);
      return initialValue;
    }
  });

  const setValue = (value: T | ((val: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(error);
    }
  };

  return [storedValue, setValue] as const;
}

// Usage
function Preferences() {
  const [theme, setTheme] = useLocalStorage('theme', 'light');

  return (
    <div>
      <p>Current theme: {theme}</p>
      <button onClick={() => setTheme('dark')}>Dark Mode</button>
      <button onClick={() => setTheme('light')}>Light Mode</button>
    </div>
  );
}
```

### 9. Custom Hook for Debouncing

```typescript
import { useState, useEffect } from 'react';

function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

// Usage
function SearchComponent() {
  const [searchTerm, setSearchTerm] = useState('');
  const debouncedSearchTerm = useDebounce(searchTerm, 500);

  useEffect(() => {
    if (debouncedSearchTerm) {
      // Perform search API call
      console.log('Searching for:', debouncedSearchTerm);
    }
  }, [debouncedSearchTerm]);

  return (
    <input
      type="text"
      value={searchTerm}
      onChange={(e) => setSearchTerm(e.target.value)}
      placeholder="Search..."
    />
  );
}
```

## React Hooks Checklist

- ✅ Only call hooks at the top level (not in loops or conditions)
- ✅ Only call hooks from React functions
- ✅ Always include all dependencies in useEffect dependency array
- ✅ Use useCallback for functions passed to child components
- ✅ Use useMemo for expensive computations
- ✅ Clean up side effects in useEffect return function
- ✅ Use custom hooks to extract and reuse logic
- ✅ Keep components small and focused
- ✅ Use TypeScript for better type safety
- ✅ Test hooks with React Testing Library
