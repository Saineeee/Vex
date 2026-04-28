## 2024-05-01 - Sentinel initialized

## 2024-05-01 - Missing Authorization in Dashboard Settings Update
**Vulnerability:** The `/api/settings/update` endpoint lacked authentication and authorization checks, allowing arbitrary settings changes via unauthorized POST requests.
**Learning:** The frontend dashboard required login, but the backend endpoint did not validate the user's session or permissions, exposing a critical missing authorization vulnerability.
**Prevention:** Always enforce authorization at the API level (e.g., verifying Discord tokens and permissions) rather than relying solely on frontend UI restrictions.
