export function showStatus(message, type) {
  const statusEl = document.getElementById('feedflow-status');
  if (!statusEl) return;
  const colors = {
    info: { bg: '#DBEAFE', text: '#1E40AF' },
    success: { bg: '#D1FAE5', text: '#065F46' },
    error: { bg: '#FEE2E2', text: '#991B1B' }
  };
  statusEl.textContent = message;
  statusEl.style.background = colors[type].bg;
  statusEl.style.color = colors[type].text;
  statusEl.style.display = 'block';
}

export function hideStatus() {
  const statusEl = document.getElementById('feedflow-status');
  if (!statusEl) return;
  statusEl.style.display = 'none';
}

export function collectMetadata() {
  return {
    page_url: window.location.href,
    user_agent: navigator.userAgent,
    viewport_width: window.innerWidth,
    viewport_height: window.innerHeight,
    screen_width: window.screen.width,
    screen_height: window.screen.height,
    timestamp: new Date().toISOString(),
    browser_language: navigator.language,
    referrer: document.referrer || null,
  };
}

export function isValidEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

export function updateCharCounter(counterElement, length) {
  if (!counterElement) return;
  counterElement.textContent = `${length} / 550`;
  if (length === 0) {
    counterElement.style.color = '#9CA3AF';
  } else if (length > 500) {
    counterElement.style.color = '#EF4444';
  } else {
    counterElement.style.color = '#6B7280';
  }
}
