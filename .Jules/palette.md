## 2026-04-26 - [Missing Form Associations and Live Regions]
**Learning:** This app heavily relies on vanilla HTML forms lacking programmatic associations between labels and inputs, as well as missing live regions for dynamic alerts/toasts, severely impacting screen reader users.
**Action:** Always ensure `for` attributes match input `id`s when styling heading tags as labels, and add `aria-live="polite"` to toast/loading elements to announce status changes without shifting focus.
