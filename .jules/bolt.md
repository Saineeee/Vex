## 2024-05-24 - Database queries in high-frequency events
**Learning:** High-frequency events like `on_voice_state_update` trigger on every voice action (mute, deafen, etc.), and querying the database for settings on each event creates a massive performance bottleneck.
**Action:** Implement in-memory caches with negative caching for high-frequency event listeners to prevent redundant database queries.
