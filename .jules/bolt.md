## 2026-04-27 - [Parallelize Discord API calls in verify_login]
**Learning:** Independent network requests to external APIs (like fetching a user profile and their servers) can and should be parallelized using asyncio.gather to significantly reduce latency.
**Action:** Use asyncio.gather when making multiple independent awaitable calls in async functions to execute them concurrently instead of sequentially.
