## 2024-05-24 - Database queries in High-Frequency Listeners
**Learning:** Performing database queries directly inside high-frequency event listeners like `on_voice_state_update` creates massive bottlenecks. This is exacerbated when many events are emitted rapidly.
**Action:** Implement in-memory dictionaries for settings lookup and only hit the database if the key is missing. Ensure command-based changes update both the database and the cache.
