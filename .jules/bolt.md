## 2024-05-03 - [Optimize DB Lookups in High-Frequency Listeners]
**Learning:** High-frequency Discord listeners (like `on_voice_state_update`) will query the database heavily on every event if caching isn't used.
**Action:** Implemented negative caching (`{}`) inside an in-memory dictionary `_settings_cache` to ensure even failed DB lookups aren't repeated, mitigating performance bottlenecks.
