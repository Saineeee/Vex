## 2024-05-24 - [Semantic Form Accessibility]
**Learning:** The dashboard previously used `<h3>` headings to act as form labels, breaking screen reader associations for the adjacent text inputs.
**Action:** Replaced `<h3>` with proper `<label>` elements matching `for` to `id` while applying `block text-lg font-bold text-white mb-2` classes to preserve layout integrity. Always ensure semantic tags match intent.
