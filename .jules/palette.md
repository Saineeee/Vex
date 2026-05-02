## 2024-10-24 - Semantic HTML & ARIA Attributes for Dashboard

**Learning:** The application's dashboard historically contains an anti-pattern of using `<h3>` heading tags instead of semantic `<label>` elements for form inputs. This causes screen readers to misinterpret form structure and fail to associate labels with inputs. Additionally, dynamic content updates (like toast notifications) lacked `aria-live` regions, and images (like user avatars) lacked `alt` text.

**Action:** Always ensure form structures use proper `<label>` elements with matching `for` and `id` attributes (while retaining visual styling by applying appropriate classes like `block text-lg font-bold`). Add `aria-live="polite"` (or `assertive`) to dynamic text/toasts so they are announced to screen reader users, and always include `alt` text for images.
