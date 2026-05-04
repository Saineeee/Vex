## 2024-05-18 - Avoid Database Queries in High-Frequency Listeners
**Learning:** Making raw database queries (like `find_one`) inside high-frequency Discord event listeners (such as `on_voice_state_update`) creates massive bottlenecks, especially for servers without the feature enabled where it repeatedly queries for nothing.
**Action:** Always implement an in-memory dictionary cache (`self._settings_cache = {}`) inside the cog. Use negative caching (storing `{}`) if a database query returns no result, and ensure any commands that modify the settings also synchronize the local cache.
