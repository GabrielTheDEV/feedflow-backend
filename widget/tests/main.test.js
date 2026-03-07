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
      status: 204,
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

  it('envia report para /reports com api_key e payload JSON', async () => {
    await import('../src/main');

    const button = document.getElementById('feedflow-trigger-btn');
    button.click();

    const emailInput = document.getElementById('feedflow-email');
    const messageInput = document.getElementById('feedflow-message');
    const form = document.getElementById('feedflow-form');

    emailInput.value = 'qa@feedflow.dev';
    messageInput.value = 'Erro ao finalizar checkout';

    emailInput.dispatchEvent(new Event('input', { bubbles: true }));
    messageInput.dispatchEvent(new Event('input', { bubbles: true }));

    form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
    await new Promise((resolve) => setTimeout(resolve, 0));

    expect(global.fetch).toHaveBeenCalledTimes(1);

    const [url, options] = global.fetch.mock.calls[0];

    expect(url).toBe('http://localhost:8000/api/v1/reports?api_key=token-123');
    expect(options.method).toBe('POST');
    expect(options.headers['Content-Type']).toBe('application/json');

    const payload = JSON.parse(options.body);
    expect(payload).toMatchObject({
      title: 'Widget report',
      message: 'Erro ao finalizar checkout',
      email: 'qa@feedflow.dev',
      has_screenshot: false,
    });
    expect(payload).toHaveProperty('metadata');
    expect(payload).toHaveProperty('page');
  });
});
