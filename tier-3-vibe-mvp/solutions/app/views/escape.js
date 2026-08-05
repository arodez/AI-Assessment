'use strict';

// Manual HTML escaping — required because this app has no templating engine
// (no EJS, since npm install wasn't available in the build environment).
// EVERY piece of user-supplied data rendered into HTML must go through this.
function escapeHtml(value) {
  if (value === null || value === undefined) return '';
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

module.exports = { escapeHtml };
