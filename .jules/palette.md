## 2024-04-27 - Utility-First UI Accessibility

**Learning:** Developers building quick UIs with utility frameworks (like Tailwind) often rely on visual styling (e.g., generic `<h3>` or `<p>` tags acting as headers/labels) rather than semantic HTML (`<label for="...">`). Similarly, dynamic elements like toast notifications or loading text styled to appear and disappear are frequently missing `aria-live` regions, leaving screen reader users unaware of status changes.

**Action:** When auditing utility-first frontends, explicitly check that inputs are programmatically associated with semantic labels, and ensure any dynamically rendered or toggled text content has `aria-live="polite"` and `role="status"` to announce updates properly.
