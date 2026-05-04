## 2024-05-04 - Unauthenticated Settings Update
**Vulnerability:** The `/api/settings/update` endpoint allowed any unauthenticated user to update guild settings or lock channels by simply providing a valid `guild_id`.
**Learning:** Endpoints updating sensitive guild configurations must validate authorization by checking the user's Discord access token against the discord `/users/@me/guilds` API to ensure they possess Administrator (`0x8`) permissions for the targeted guild.
**Prevention:** Always require an `Authorization` Bearer token containing the Discord access token for endpoints that perform write operations, and actively verify permissions with the external auth provider before modifying state.
