import { describe, it, expect, beforeEach } from 'vitest';
import { getConfig } from '../src/config';

describe('getConfig', () => {
  beforeEach(() => {
    document.head.innerHTML = '';
    Object.defineProperty(document, 'currentScript', {
      value: null,
      configurable: true,
    });
  });

  it('lê atributos data-* da currentScript', () => {
    const script = document.createElement('script');
    script.setAttribute('data-api-token', 'token-123');
    script.setAttribute('data-api-url', 'http://localhost:8000/api/v1');
    script.setAttribute('data-button-text', 'Enviar');
    script.setAttribute('data-button-position', 'top-left');
    script.setAttribute('data-primary-color', '#111111');
    script.setAttribute('data-language', 'en-US');
    script.setAttribute('data-domain', 'example.com');

    Object.defineProperty(document, 'currentScript', {
      value: script,
      configurable: true,
    });

    const config = getConfig();

    expect(config.apiToken).toBe('token-123');
    expect(config.apiUrl).toBe('http://localhost:8000/api/v1');
    expect(config.buttonText).toBe('Enviar');
    expect(config.buttonPosition).toBe('top-left');
    expect(config.primaryColor).toBe('#111111');
    expect(config.language).toBe('en-US');
    expect(config.domain).toBe('example.com');
  });

  it('usa defaults quando atributos opcionais não existem', () => {
    const script = document.createElement('script');
    script.setAttribute('data-api-token', 'token-abc');
    script.setAttribute('data-api-url', 'https://api.feedflow.com/api/v1');

    Object.defineProperty(document, 'currentScript', {
      value: script,
      configurable: true,
    });

    const config = getConfig();

    expect(config.buttonText).toBe('Reportar Problema');
    expect(config.buttonPosition).toBe('bottom-right');
    expect(config.primaryColor).toBe('#4F46E5');
    expect(config.language).toBe('pt-BR');
    expect(config.domain).toBeUndefined();
  });
});
