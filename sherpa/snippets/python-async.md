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
    result1 = await fetch_data("https://api.example.com/1")
    result2 = await fetch_data("https://api.example.com/2")

    # Concurrent execution
    results = await asyncio.gather(
        fetch_data("https://api.example.com/1"),
        fetch_data("https://api.example.com/2"),
        fetch_data("https://api.example.com/3")
    )

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Async Context Managers

```python
import aiosqlite

class DatabaseConnection:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None

    async def __aenter__(self):
        self.connection = await aiosqlite.connect(self.db_path)
        return self.connection

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            await self.connection.close()

# Usage
async def query_database():
    async with DatabaseConnection("app.db") as conn:
        cursor = await conn.execute("SELECT * FROM users")
        rows = await cursor.fetchall()
        return rows
```

### 3. Async Generators

```python
from typing import AsyncGenerator

async def paginated_fetch(total_pages: int) -> AsyncGenerator[dict, None]:
    """Async generator for pagination"""
    for page in range(1, total_pages + 1):
        # Simulate fetching page
        await asyncio.sleep(0.5)
        yield {
            "page": page,
            "data": [f"item_{i}" for i in range(10)]
        }

# Usage
async def process_all_pages():
    async for page_data in paginated_fetch(total_pages=5):
        print(f"Processing page {page_data['page']}")
        # Process page data
```

### 4. Task Management and Cancellation

```python
async def long_running_task(task_id: str):
    try:
        for i in range(10):
            print(f"Task {task_id}: Step {i}")
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        print(f"Task {task_id} was cancelled")
        # Cleanup code here
        raise

async def task_manager():
    # Create tasks
    task1 = asyncio.create_task(long_running_task("1"))
    task2 = asyncio.create_task(long_running_task("2"))

    # Wait a bit then cancel
    await asyncio.sleep(3)
    task1.cancel()

    # Wait for tasks to complete or be cancelled
    results = await asyncio.gather(task1, task2, return_exceptions=True)
    print(f"Results: {results}")
```

### 5. Async Queue for Producer-Consumer

```python
import asyncio
from asyncio import Queue

async def producer(queue: Queue, producer_id: int):
    """Produce items and put in queue"""
    for i in range(5):
        item = f"Producer-{producer_id}-Item-{i}"
        await queue.put(item)
        print(f"Produced: {item}")
        await asyncio.sleep(0.5)

async def consumer(queue: Queue, consumer_id: int):
    """Consume items from queue"""
    while True:
        try:
            item = await asyncio.wait_for(queue.get(), timeout=3.0)
            print(f"Consumer-{consumer_id} processing: {item}")
            await asyncio.sleep(1)
            queue.task_done()
        except asyncio.TimeoutError:
            print(f"Consumer-{consumer_id} timed out")
            break

async def producer_consumer_pattern():
    queue = Queue(maxsize=10)

    # Start producers and consumers
    producers = [asyncio.create_task(producer(queue, i)) for i in range(2)]
    consumers = [asyncio.create_task(consumer(queue, i)) for i in range(3)]

    # Wait for producers to finish
    await asyncio.gather(*producers)

    # Wait for queue to be processed
    await queue.join()

    # Cancel consumers
    for c in consumers:
        c.cancel()
```

### 6. Async Locking and Synchronization

```python
import asyncio

class SharedResource:
    def __init__(self):
        self.value = 0
        self.lock = asyncio.Lock()

    async def increment(self, worker_id: int):
        """Thread-safe increment"""
        async with self.lock:
            current = self.value
            await asyncio.sleep(0.1)  # Simulate work
            self.value = current + 1
            print(f"Worker {worker_id}: {self.value}")

async def concurrent_increments():
    resource = SharedResource()
    tasks = [
        asyncio.create_task(resource.increment(i))
        for i in range(10)
    ]
    await asyncio.gather(*tasks)
    print(f"Final value: {resource.value}")
```

### 7. FastAPI with Async Database Operations

```python
from fastapi import FastAPI, HTTPException
import aiosqlite
from typing import List, Optional

app = FastAPI()

# Database connection pool
class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._connection: Optional[aiosqlite.Connection] = None

    async def connect(self):
        if self._connection is None:
            self._connection = await aiosqlite.connect(self.db_path)
            self._connection.row_factory = aiosqlite.Row
        return self._connection

    async def close(self):
        if self._connection:
            await self._connection.close()
            self._connection = None

db = Database("app.db")

@app.on_event("startup")
async def startup():
    await db.connect()

@app.on_event("shutdown")
async def shutdown():
    await db.close()

@app.get("/users")
async def get_users() -> List[dict]:
    conn = await db.connect()
    cursor = await conn.execute("SELECT * FROM users")
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]

@app.post("/users")
async def create_user(name: str, email: str):
    conn = await db.connect()
    try:
        await conn.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            (name, email)
        )
        await conn.commit()
        return {"status": "created"}
    except Exception as e:
        await conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
```

### 8. Concurrent API Calls with Timeout

```python
import httpx
import asyncio
from typing import List, Dict

async def fetch_with_timeout(
    client: httpx.AsyncClient,
    url: str,
    timeout: float = 5.0
) -> Dict:
    """Fetch URL with timeout"""
    try:
        response = await asyncio.wait_for(
            client.get(url),
            timeout=timeout
        )
        return {"url": url, "status": response.status_code, "data": response.json()}
    except asyncio.TimeoutError:
        return {"url": url, "status": "timeout", "data": None}
    except Exception as e:
        return {"url": url, "status": "error", "data": str(e)}

async def fetch_multiple_apis(urls: List[str]):
    """Fetch multiple APIs concurrently"""
    async with httpx.AsyncClient() as client:
        tasks = [fetch_with_timeout(client, url) for url in urls]
        results = await asyncio.gather(*tasks)
        return results

# Usage
urls = [
    "https://api.example.com/endpoint1",
    "https://api.example.com/endpoint2",
    "https://api.example.com/endpoint3"
]
results = asyncio.run(fetch_multiple_apis(urls))
```

### 9. Async Semaphore for Rate Limiting

```python
import asyncio

class RateLimiter:
    def __init__(self, max_concurrent: int = 5, delay: float = 0.1):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.delay = delay

    async def execute(self, coro):
        """Execute coroutine with rate limiting"""
        async with self.semaphore:
            result = await coro
            await asyncio.sleep(self.delay)
            return result

async def api_call(item_id: int):
    """Simulated API call"""
    await asyncio.sleep(0.5)
    return f"Result for item {item_id}"

async def process_items_with_rate_limit():
    limiter = RateLimiter(max_concurrent=3, delay=0.2)

    tasks = [
        limiter.execute(api_call(i))
        for i in range(20)
    ]

    results = await asyncio.gather(*tasks)
    return results
```

## Async Best Practices Checklist

- ✅ Use `async`/`await` for I/O-bound operations
- ✅ Don't use `asyncio.sleep()` in production (use for testing)
- ✅ Use `asyncio.gather()` for concurrent operations
- ✅ Implement proper error handling in async code
- ✅ Use async context managers for resources
- ✅ Cancel tasks properly to avoid resource leaks
- ✅ Use semaphores for rate limiting
- ✅ Avoid blocking operations in async code
- ✅ Use `asyncio.create_task()` for background tasks
- ✅ Test async code thoroughly
