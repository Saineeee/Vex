## 2026-05-05 - Replacing non-semantic headings with semantic form labels
**Learning:** The application's dashboard historically contains an anti-pattern of using `<h3>` heading tags instead of semantic `<label>` elements for form inputs. This makes the forms less accessible to screen readers.
**Action:** Always ensure form structures use proper `<label>` elements with matching `for` and `id` attributes. When replacing headings with labels, utilize `class="block"` to preserve the expected visual layout of the dashboard without needing custom CSS.
