## 2024-04-30 - High-Frequency Event DB Overload

**Learning:** High-frequency Discord events, such as `on_voice_state_update`, query MongoDB directly via `find_one` for settings. For guilds without a temporary voice configuration, this means a database round-trip for every single voice event, creating an unnecessary performance bottleneck and potentially overloading the database connection pool.

**Action:** Implement an in-memory caching mechanism (e.g., `_settings_cache`) on the cog level. Utilize negative caching (storing an empty dict `{}`) to prevent repeated database queries for guilds that lack configurations. Ensure configuration updates command sync this cache to maintain consistency.
