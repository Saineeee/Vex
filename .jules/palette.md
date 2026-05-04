## 2024-05-04 - [Accessibility] Semantic Form Labels
**Learning:** The dashboard UI exhibited an accessibility anti-pattern by using `<h3>` heading tags to label form inputs. Headings do not provide programmable association for screen readers, breaking accessibility.
**Action:** Always use semantic `<label>` elements for form inputs. Ensure each `<label>` has a `for` attribute that exactly matches the `id` of its corresponding input element. Use utility classes like `block` to preserve layout when converting block-level headings to inline `<label>` elements.
