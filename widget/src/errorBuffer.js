// errorBuffer.js
// Intercepta window.onerror e window.onunhandledrejection, envia para o mesmo buffer do console
import { getConsoleBuffer, instrumentConsole } from './consoleBuffer.js';

let errorWrapped = false;

function pushErrorEntry(level, message, source) {
  try {
    // Reutiliza pushEntry do consoleBuffer indiretamente
    instrumentConsole(); // Garante que buffer existe
    // Usa console[level] para garantir pushEntry
    console[level](message); // Isso já insere no buffer com source 'console'
    // Corrige source para erro global
    const buf = getConsoleBuffer();
    if (buf.length) buf[buf.length - 1].source = source;
  } catch {}
}

export function instrumentGlobalErrors() {
  if (errorWrapped) return;
  window.onerror = function(msg, url, line, col, err) {
    pushErrorEntry('error', `[window.onerror] ${msg} @${url}:${line}:${col}`, 'window.onerror');
  };
  window.onunhandledrejection = function(ev) {
    let reason = ev && ev.reason ? ev.reason : ev;
    pushErrorEntry('error', `[unhandledrejection] ${reason}`, 'unhandledrejection');
  };
  errorWrapped = true;
}
