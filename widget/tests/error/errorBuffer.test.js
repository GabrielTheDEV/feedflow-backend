// errorBuffer.test.js
import { describe, it, expect, beforeEach } from 'vitest';
import { instrumentGlobalErrors } from '../../src/errorBuffer.js';
import { getConsoleBuffer, resetConsoleBuffer } from '../../src/consoleBuffer.js';
describe('errorBuffer', () => {
  beforeEach(() => { resetConsoleBuffer(); });
  it('captura window.onerror', () => {
    instrumentGlobalErrors();
    window.onerror && window.onerror('erro de teste', 'file.js', 1, 2, {});
    const buf = getConsoleBuffer();
    expect(buf[buf.length-1].source).toBe('window.onerror');
    expect(buf[buf.length-1].message).toContain('erro de teste');
  });
  it('captura unhandledrejection', () => {
    instrumentGlobalErrors();
    window.onunhandledrejection && window.onunhandledrejection({ reason: 'promessa rejeitada' });
    const buf = getConsoleBuffer();
    expect(buf[buf.length-1].source).toBe('unhandledrejection');
    expect(buf[buf.length-1].message).toContain('promessa rejeitada');
  });
  it('é idempotente', () => {
    instrumentGlobalErrors();
    instrumentGlobalErrors();
    window.onerror && window.onerror('erro idempotente', 'file.js', 1, 2, {});
    const buf = getConsoleBuffer();
    expect(buf[buf.length-1].message).toContain('erro idempotente');
  });
});
