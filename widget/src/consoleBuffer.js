// consoleBuffer.js
// Intercepta e bufferiza console.log/warn/error/info de forma idempotente, leve e segura

const MAX_ENTRIES = 50;
const MAX_MSG_LEN = 1000;
let buffer = [];
let orig = {};
let wrapped = false;

function pushEntry(level, message, source) {
  buffer.push({
    level,
    message: String(message).slice(0, MAX_MSG_LEN),
    timestamp: Date.now(),
    source
  });
  if (buffer.length > MAX_ENTRIES) buffer.shift();
}

export function getConsoleBuffer() {
  return buffer.slice();
}

export function instrumentConsole() {
  if (wrapped) return;
  ['log', 'warn', 'error', 'info'].forEach(level => {
    if (!orig[level]) orig[level] = console[level];
    console[level] = function(...args) {
      try {
        pushEntry(level, args.map(a => (typeof a === 'string' ? a : JSON.stringify(a))).join(' '), 'console');
      } catch {}
      orig[level].apply(console, args);
    };
  });
  wrapped = true;
}

export function resetConsoleBuffer() {
  buffer = [];
}
