'use strict';

const { escapeHtml } = require('./escape');

const STYLE = `
  :root {
    --bg: #0f1115; --card: #171a21; --border: #2a2e38; --text: #e8e9ec;
    --muted: #9aa0ab; --accent: #6c8cff; --danger: #ff6b6b; --success: #52c98a;
  }
  * { box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: var(--bg); color: var(--text); margin: 0; padding: 0 0 4rem;
  }
  header {
    padding: 1.5rem 2rem; border-bottom: 1px solid var(--border);
    display: flex; justify-content: space-between; align-items: center;
  }
  header h1 { font-size: 1.25rem; margin: 0; }
  header nav a {
    color: var(--muted); text-decoration: none; margin-left: 1.25rem; font-size: 0.9rem;
  }
  header nav a:hover { color: var(--text); }
  main { max-width: 720px; margin: 0 auto; padding: 2rem; }
  .card {
    background: var(--card); border: 1px solid var(--border); border-radius: 10px;
    padding: 1.25rem 1.5rem; margin-bottom: 1rem;
  }
  .card h2 { margin-top: 0; font-size: 1.1rem; }
  .meta { color: var(--muted); font-size: 0.85rem; margin-bottom: 0.5rem; }
  .spots { font-size: 0.85rem; font-weight: 600; }
  .spots.low { color: var(--danger); }
  .spots.ok { color: var(--success); }
  form { display: flex; flex-direction: column; gap: 0.75rem; }
  label { font-size: 0.85rem; color: var(--muted); }
  input, textarea {
    background: #10131a; border: 1px solid var(--border); color: var(--text);
    padding: 0.6rem 0.75rem; border-radius: 6px; font-size: 0.95rem; font-family: inherit;
  }
  button {
    background: var(--accent); color: white; border: none; padding: 0.6rem 1rem;
    border-radius: 6px; font-size: 0.95rem; cursor: pointer; font-weight: 600;
  }
  button:hover { opacity: 0.9; }
  .alert { padding: 0.75rem 1rem; border-radius: 8px; font-size: 0.9rem; margin-bottom: 1rem; }
  .alert.error { background: rgba(255,107,107,0.12); color: var(--danger); border: 1px solid rgba(255,107,107,0.3); }
  .alert.success { background: rgba(82,201,138,0.12); color: var(--success); border: 1px solid rgba(82,201,138,0.3); }
  table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
  th, td { text-align: left; padding: 0.5rem 0.6rem; border-bottom: 1px solid var(--border); }
  th { color: var(--muted); font-weight: 600; }
  .empty { color: var(--muted); font-style: italic; padding: 1rem 0; }
  .btn-link { display: inline-block; margin-top: 0.75rem; color: var(--accent); text-decoration: none; font-size: 0.85rem; }
`;

function layout({ title, body, activeNav }) {
  const nav = (key, href, label) =>
    `<a href="${href}" style="${activeNav === key ? 'color:var(--text);font-weight:600;' : ''}">${escapeHtml(label)}</a>`;

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${escapeHtml(title)} — Community Events Hub</title>
  <style>${STYLE}</style>
</head>
<body>
  <header>
    <h1>Community Events Hub</h1>
    <nav>
      ${nav('events', '/', 'Events')}
      ${nav('create', '/events/new', 'Create Event')}
      ${nav('organizer', '/organizer', 'Organizer')}
    </nav>
  </header>
  <main>
    ${body}
  </main>
</body>
</html>`;
}

module.exports = { layout };
