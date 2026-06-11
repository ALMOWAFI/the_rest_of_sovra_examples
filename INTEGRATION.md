# Sovra AI — Demo Modules Integration Guide

4 standalone demo modules. Each is a single self-contained HTML file.
No server, no dependencies, no build step — just open in a browser.

---

## Modules

| Module | File | Input | Description |
|---|---|---|---|
| Automotive Assistant | `automotive/index.html` | Text | Car Q&A — warning lights, sounds, maintenance |
| Enterprise Knowledge | `enterprise/index.html` | Text | Company policy & HR Q&A |
| Document Intelligence | `document/index.html` | File upload + Text | Upload PDF/doc, then chat about it |
| Smart Manufacturing | `manufacturing/index.html` | Image upload + Text | Upload production image, get defect analysis |

---

## How to embed in the main website

Each module is designed to run inside an `<iframe>` on the main site:

```html
<!-- On your main website, inside each demo card: -->
<iframe
  src="/demos/automotive/index.html"
  width="100%"
  height="600px"
  frameborder="0"
  style="border-radius: 16px;"
></iframe>
```

Or link to them directly as separate pages:
```
yoursite.com/demos/automotive
yoursite.com/demos/enterprise
yoursite.com/demos/document
yoursite.com/demos/manufacturing
```

---

## Folder structure to add to main project

```
your-main-project/
└── public/
    └── demos/
        ├── automotive/
        │   └── index.html
        ├── enterprise/
        │   └── index.html
        ├── document/
        │   └── index.html
        └── manufacturing/
            └── index.html
```

---

## Swapping mock responses for real AI (when ready)

Each module has a `send()` function. To connect to a real backend, replace the `setTimeout` block:

**Current (mock):**
```javascript
setTimeout(() => {
  t.remove();
  appendMsg('bot', renderBot(match(q)));
}, 900);
```

**Replace with (real API):**
```javascript
const res = await fetch('/api/ask', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ question: q, module: 'automotive' })
});
const data = await res.json();
t.remove();
appendMsg('bot', data.answer);
```

---

## Customization

- **Colors:** Each module has a primary accent color. Change the CSS variable at the top of each file.
  - Automotive: `#818cf8` (indigo)
  - Enterprise: `#10b981` (green)
  - Document: `#f59e0b` (amber)
  - Manufacturing: `#e879f9` (purple)

- **Knowledge base:** Each module has a `const KB = [...]` array at the top of the script.
  Add or edit entries to customize the hardcoded responses.

- **Suggestion chips:** Edit the `.chip` elements in the HTML to change the quick-action buttons.
