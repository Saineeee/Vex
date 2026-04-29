## 2026-04-29 - In-Memory Caching for High-Frequency Listeners
**Learning:** High-frequency event listeners (like voice state updates) that query the database create severe bottlenecks. The temp_voice settings are safe to cache indefinitely because its configuration keys do not overlap with the mutable fields in the FastAPI dashboard.
**Action:** Implemented a guild-level in-memory cache in the TempVoice cog to eliminate redundant database queries on every voice state event.
