## 2024-04-28 - Missing Semantic Form Labels
**Learning:** This application has a pattern of using `<h3>` heading tags to describe input fields instead of semantic `<label>` elements. This breaks the link between the descriptive text and the form input, significantly impacting accessibility for screen reader users and preventing users from clicking the text to focus the input field.
**Action:** Always check form structures in this application to ensure `<label>` elements are used with matching `for` and `id` attributes rather than heading or generic div tags for input descriptions.
