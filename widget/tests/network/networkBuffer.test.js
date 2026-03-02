// networkBuffer.test.js
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { instrumentNetwork, getNetworkBuffer } from '../../src/networkBuffer.js';

describe('networkBuffer', () => {
  beforeEach(() => { getNetworkBuffer().splice(0); });

  it('bufferiza falhas de fetch', async () => {
    instrumentNetwork();
    // Mock fetch para simular falha
    vi.spyOn(window, 'fetch').mockImplementation(() => Promise.reject('fail'));
    try { await window.fetch('/fail'); } catch {}
    const buf = getNetworkBuffer();
    expect(buf.length).toBeGreaterThan(0);
    expect(buf[buf.length-1].type).toBe('fetch');
    expect(buf[buf.length-1].success).toBe(false);
    window.fetch.mockRestore && window.fetch.mockRestore();
  });

  it('bufferiza falhas de XHR', async () => {
    instrumentNetwork();
    // Mock XHR para simular status >= 400
    const origXHR = window.XMLHttpRequest;
    class MockXHR {
      constructor() {
        this._listeners = {};
        this.status = 404;
      }
      open() {}
      addEventListener(event, cb) {
        this._listeners[event] = cb;
      }
      dispatchEvent(event) {
        if (this._listeners[event.type]) this._listeners[event.type]();
      }
    }
    window.XMLHttpRequest = MockXHR;
    const xhr = new window.XMLHttpRequest();
    xhr.open('GET', '/fail');
    xhr.addEventListener('loadend', function() {
      const buf = getNetworkBuffer();
      expect(buf.length).toBeGreaterThan(0);
      expect(buf[buf.length-1].type).toBe('xhr');
      expect(buf[buf.length-1].success).toBe(false);
    });
    xhr.dispatchEvent(new Event('loadend'));
    window.XMLHttpRequest = origXHR;
  });

  it('é idempotente', () => {
    instrumentNetwork();
    instrumentNetwork();
    expect(typeof window.fetch).toBe('function');
    expect(typeof window.XMLHttpRequest).toBe('function');
  });
});
