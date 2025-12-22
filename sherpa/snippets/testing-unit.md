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
    return price * (1 - discount_percent / 100)

# Tests
def test_calculate_discount_valid():
    assert calculate_discount(100, 10) == 90
    assert calculate_discount(50, 20) == 40

def test_calculate_discount_zero():
    assert calculate_discount(100, 0) == 100

def test_calculate_discount_invalid():
    with pytest.raises(ValueError):
        calculate_discount(100, -10)
    with pytest.raises(ValueError):
        calculate_discount(100, 150)

# Parametrized tests
@pytest.mark.parametrize("price,discount,expected", [
    (100, 10, 90),
    (50, 20, 40),
    (200, 50, 100),
])
def test_calculate_discount_parametrized(price, discount, expected):
    assert calculate_discount(price, discount) == expected
```

### 2. Testing Async Functions (Python)

```python
import pytest
import asyncio

async def fetch_user(user_id: str) -> dict:
    await asyncio.sleep(0.1)  # Simulate async operation
    return {"id": user_id, "name": "Test User"}

@pytest.mark.asyncio
async def test_fetch_user():
    result = await fetch_user("123")
    assert result["id"] == "123"
    assert result["name"] == "Test User"

@pytest.mark.asyncio
async def test_fetch_user_concurrent():
    results = await asyncio.gather(
        fetch_user("1"),
        fetch_user("2"),
        fetch_user("3")
    )
    assert len(results) == 3
    assert all(r["name"] == "Test User" for r in results)
```

### 3. Fixtures and Mocking (Python)

```python
import pytest
from unittest.mock import Mock, patch, AsyncMock

# Fixtures
@pytest.fixture
def sample_user():
    return {"id": "123", "name": "Test User", "email": "test@example.com"}

@pytest.fixture
async def db_connection():
    # Setup
    conn = await create_connection()
    yield conn
    # Teardown
    await conn.close()

# Using fixtures
def test_user_creation(sample_user):
    assert sample_user["name"] == "Test User"

# Mocking
def test_api_call_with_mock():
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = {"status": "ok"}
        mock_get.return_value.status_code = 200

        response = make_api_call()
        assert response["status"] == "ok"
        mock_get.assert_called_once()

# Async mocking
@pytest.mark.asyncio
async def test_async_api_call():
    with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value.json.return_value = {"data": "test"}

        result = await fetch_api_data()
        assert result["data"] == "test"
```

### 4. JavaScript/TypeScript Tests with Jest

```typescript
// Function to test
function add(a: number, b: number): number {
  return a + b;
}

function fetchUser(id: string): Promise<User> {
  return fetch(`/api/users/${id}`).then(res => res.json());
}

// Basic tests
describe('add function', () => {
  test('adds two positive numbers', () => {
    expect(add(2, 3)).toBe(5);
  });

  test('adds negative numbers', () => {
    expect(add(-2, -3)).toBe(-5);
  });

  test('adds zero', () => {
    expect(add(0, 5)).toBe(5);
  });
});

// Testing arrays and objects
describe('User operations', () => {
  test('user object has required fields', () => {
    const user = { id: '1', name: 'John', email: 'john@example.com' };
    expect(user).toHaveProperty('id');
    expect(user).toHaveProperty('name');
    expect(user).toMatchObject({
      id: '1',
      name: 'John'
    });
  });

  test('array contains user', () => {
    const users = [
      { id: '1', name: 'John' },
      { id: '2', name: 'Jane' }
    ];
    expect(users).toContainEqual({ id: '1', name: 'John' });
    expect(users).toHaveLength(2);
  });
});
```

### 5. Testing Async Code (Jest)

```typescript
// Async function to test
async function fetchData(): Promise<string> {
  return new Promise((resolve) => {
    setTimeout(() => resolve('data'), 100);
  });
}

describe('Async tests', () => {
  test('fetches data successfully', async () => {
    const data = await fetchData();
    expect(data).toBe('data');
  });

  test('handles promise rejection', async () => {
    const failingFetch = () => Promise.reject(new Error('Failed'));
    await expect(failingFetch()).rejects.toThrow('Failed');
  });
});
```

### 6. Mocking in Jest

```typescript
import { fetchUser } from './api';

// Mock the module
jest.mock('./api');

describe('User fetching', () => {
  test('mocks fetch user', async () => {
    const mockUser = { id: '1', name: 'John' };
    (fetchUser as jest.Mock).mockResolvedValue(mockUser);

    const user = await fetchUser('1');
    expect(user).toEqual(mockUser);
    expect(fetchUser).toHaveBeenCalledWith('1');
  });

  test('mocks multiple calls with different values', async () => {
    (fetchUser as jest.Mock)
      .mockResolvedValueOnce({ id: '1', name: 'John' })
      .mockResolvedValueOnce({ id: '2', name: 'Jane' });

    const user1 = await fetchUser('1');
    const user2 = await fetchUser('2');

    expect(user1.name).toBe('John');
    expect(user2.name).toBe('Jane');
  });
});

// Spy on methods
describe('Spying', () => {
  test('spies on console.log', () => {
    const consoleSpy = jest.spyOn(console, 'log');

    console.log('test message');

    expect(consoleSpy).toHaveBeenCalledWith('test message');
    consoleSpy.mockRestore();
  });
});
```

### 7. React Component Testing

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Counter from './Counter';

describe('Counter Component', () => {
  test('renders initial count', () => {
    render(<Counter />);
    expect(screen.getByText(/count: 0/i)).toBeInTheDocument();
  });

  test('increments count on button click', () => {
    render(<Counter />);
    const button = screen.getByRole('button', { name: /increment/i });

    fireEvent.click(button);
    expect(screen.getByText(/count: 1/i)).toBeInTheDocument();
  });

  test('user interaction with userEvent', async () => {
    render(<Counter />);
    const button = screen.getByRole('button', { name: /increment/i });

    await userEvent.click(button);
    await userEvent.click(button);

    expect(screen.getByText(/count: 2/i)).toBeInTheDocument();
  });
});

// Testing async components
describe('UserProfile Component', () => {
  test('loads and displays user data', async () => {
    const mockUser = { name: 'John Doe', email: 'john@example.com' };

    global.fetch = jest.fn(() =>
      Promise.resolve({
        json: () => Promise.resolve(mockUser),
      })
    ) as jest.Mock;

    render(<UserProfile userId="123" />);

    // Initially shows loading
    expect(screen.getByText(/loading/i)).toBeInTheDocument();

    // Wait for user data to load
    await waitFor(() => {
      expect(screen.getByText(mockUser.name)).toBeInTheDocument();
    });

    expect(global.fetch).toHaveBeenCalledWith('/api/users/123');
  });
});
```

### 8. Testing with Fixtures and Setup/Teardown

```python
import pytest

class TestDatabase:
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        # Setup before each test
        self.db = create_test_database()
        yield
        # Teardown after each test
        self.db.cleanup()

    def test_insert_user(self):
        user_id = self.db.insert_user("test@example.com")
        assert user_id is not None

    def test_query_user(self):
        self.db.insert_user("test@example.com")
        user = self.db.get_user_by_email("test@example.com")
        assert user["email"] == "test@example.com"

# Module-level fixtures
@pytest.fixture(scope="module")
def database():
    db = create_database()
    db.migrate()
    yield db
    db.drop_all_tables()

def test_with_module_fixture(database):
    assert database.is_connected()
```

### 9. Code Coverage

```bash
# Python with pytest
pytest --cov=myapp --cov-report=html tests/

# JavaScript with Jest
jest --coverage

# TypeScript with Jest
jest --coverage --collectCoverageFrom='src/**/*.{ts,tsx}'
```

```python
# .coveragerc configuration
[run]
source = myapp
omit =
    */tests/*
    */migrations/*
    */__init__.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
```

## Testing Checklist

- ✅ Write tests before or alongside code (TDD)
- ✅ Test one thing per test
- ✅ Use descriptive test names
- ✅ Follow AAA pattern: Arrange, Act, Assert
- ✅ Mock external dependencies
- ✅ Test edge cases and error conditions
- ✅ Aim for high code coverage (80%+)
- ✅ Keep tests fast and independent
- ✅ Use fixtures for common setup
- ✅ Run tests in CI/CD pipeline
