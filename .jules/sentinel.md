## 2024-05-15 - [Authorization Bypass Fix]
**Vulnerability:** The `/api/settings/update` endpoint blindly accepted payload data without verifying if the requester was authenticated or authorized to make changes for that specific Discord server (IDOR).
**Learning:** The frontend fetched discord user auth via the server but did not correctly set headers to allow the server to re-verify the users credentials in subsequent protected api calls.
**Prevention:** Implement strict backend authorization checks to verify user permissions with an access token for protected API calls.
