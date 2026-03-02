import { describe, it, expect, beforeEach } from 'vitest';
import {
  showStatus,
  hideStatus,
  collectMetadata,
  isValidEmail,
  updateCharCounter,
} from '../src/utils';

describe('utils', () => {
  beforeEach(() => {
    document.body.innerHTML = '<div id="feedflow-status" style="display:none"></div>';
  });

  it('showStatus exibe mensagem com cores por tipo', () => {
    showStatus('ok', 'success');
    const el = document.getElementById('feedflow-status');

    expect(el.textContent).toBe('ok');
    expect(el.style.display).toBe('block');
    expect(el.style.background).toBe('rgb(209, 250, 229)');
  });

  it('hideStatus oculta elemento de status', () => {
    showStatus('erro', 'error');
    hideStatus();
    const el = document.getElementById('feedflow-status');
    expect(el.style.display).toBe('none');
  });

  it('isValidEmail valida formatos básicos', () => {
    expect(isValidEmail('teste@email.com')).toBe(true);
    expect(isValidEmail('invalido@')).toBe(false);
    expect(isValidEmail('sem-arroba.com')).toBe(false);
  });

  it('updateCharCounter atualiza texto e cor', () => {
    const counter = document.createElement('span');

    updateCharCounter(counter, 0);
    expect(counter.textContent).toBe('0 / 550');

    updateCharCounter(counter, 520);
    expect(counter.textContent).toBe('520 / 550');
    expect(counter.style.color).toBe('rgb(239, 68, 68)');
  });

  it('collectMetadata retorna campos obrigatórios', () => {
    const metadata = collectMetadata();

    expect(metadata).toHaveProperty('page_url');
    expect(metadata).toHaveProperty('user_agent');
    expect(metadata).toHaveProperty('viewport_width');
    expect(metadata).toHaveProperty('screen_width');
    expect(metadata).toHaveProperty('timestamp');
  });
});
