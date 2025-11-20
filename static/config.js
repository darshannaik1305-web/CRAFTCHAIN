// Central API base URL for all frontend pages.
// This file auto-detects whether the frontend is served by the backend
// (same-origin) or served statically from a different port. When the
// frontend is served by the backend (e.g. Flask on port 5002), API
// requests should use relative paths like '/api/...'. When served
// statically (e.g. python -m http.server on port 8000), this defaults
// to the backend at http://127.0.0.1:5002 so the frontend can reach APIs.
const API_BASE = (function () {
	const defaultBase = 'http://127.0.0.1:5002';
	try {
		const loc = window.location;
		// If the page is being served from the backend (same origin),
		// return empty string so fetch('/api/...') works.
		if (loc.hostname === '127.0.0.1' || loc.hostname === 'localhost') {
			if (loc.port === '5002' || loc.port === '') {
				return '';
			}
		}
	} catch (e) {
		// ignore and fall back to default
	}
	return defaultBase;
})();
