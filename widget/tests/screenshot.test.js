import { describe, it, expect, vi, beforeEach } from 'vitest';
import html2canvas from 'html2canvas';
import { captureScreenshot } from '../src/screenshot';

vi.mock('html2canvas', () => ({
  default: vi.fn(),
}));

describe('captureScreenshot', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('retorna blob quando toBlob é bem-sucedido', async () => {
    const blob = new Blob(['img'], { type: 'image/png' });
    const canvasMock = {
      toBlob: (cb) => cb(blob),
    };

    html2canvas.mockResolvedValue(canvasMock);

    const result = await captureScreenshot();

    expect(html2canvas).toHaveBeenCalledOnce();
    expect(result).toBe(blob);
  });

  it('lança erro quando toBlob retorna null', async () => {
    const canvasMock = {
      toBlob: (cb) => cb(null),
    };

    html2canvas.mockResolvedValue(canvasMock);

    await expect(captureScreenshot()).rejects.toThrow('Falha ao converter canvas para blob');
  });
});
