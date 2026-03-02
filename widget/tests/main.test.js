import { describe, it, expect, beforeEach, vi } from 'vitest';

vi.mock('../src/screenshot', () => ({
  captureScreenshot: vi.fn(async () => new Blob(['img'], { type: 'image/png' })),
}));

describe('main widget integration', () => {
  beforeEach(() => {
    vi.resetModules();
    document.head.innerHTML = '';
    document.body.innerHTML = '';

    const script = document.createElement('script');
    script.setAttribute('data-api-token', 'token-123');
    script.setAttribute('data-api-url', 'http://localhost:8000/api/v1');
    script.setAttribute('data-button-text', 'Reportar Problema');

    Object.defineProperty(document, 'currentScript', {
      value: script,
      configurable: true,
    });

    global.fetch = vi.fn(async () => ({
      ok: true,
      json: async () => ({ ok: true }),
    }));
  });

  it('auto-init cria botão e modal no DOM', async () => {
    await import('../src/main');

    expect(window.FeedFlowWidget).toBeTruthy();
    expect(document.getElementById('feedflow-trigger-btn')).toBeTruthy();
    expect(document.getElementById('feedflow-modal')).toBeTruthy();
  });

  it('abre e fecha modal via API pública', async () => {
    await import('../src/main');

    const modal = document.getElementById('feedflow-modal');

    window.FeedFlowWidget.open();
    expect(modal.style.display).toBe('flex');

    window.FeedFlowWidget.close();
    expect(modal.style.display).toBe('none');
  });

  it('abre modal ao clicar no botão', async () => {
    await import('../src/main');

    const button = document.getElementById('feedflow-trigger-btn');
    const modal = document.getElementById('feedflow-modal');

    button.click();
    expect(modal.style.display).toBe('flex');
  });
});
