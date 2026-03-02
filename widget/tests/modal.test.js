import { describe, it, expect, vi, beforeEach } from 'vitest';
import { createModal, setupModalEvents, setupModalDrag } from '../src/modal';

describe('modal', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
  });

  it('createModal renderiza estrutura principal no DOM', () => {
    const modal = createModal({
      primaryColor: '#4F46E5',
    });

    expect(modal).toBeTruthy();
    expect(document.getElementById('feedflow-modal')).toBeTruthy();
    expect(document.getElementById('feedflow-form')).toBeTruthy();
    expect(document.getElementById('feedflow-camera-btn')).toBeTruthy();
    expect(document.getElementById('feedflow-submit-btn')).toBeTruthy();
  });

  it('setupModalEvents conecta handlers principais', () => {
    const modal = createModal({
      primaryColor: '#4F46E5',
    });

    const onClose = vi.fn();
    const onSubmit = vi.fn((e) => e.preventDefault());

    setupModalEvents(modal, {
      onClose,
      onSubmit,
      onMessageInput: vi.fn(),
      onEmailInput: vi.fn(),
      onMessageKeydown: vi.fn(),
      onPreviewClick: vi.fn(),
      onRemoveScreenshot: vi.fn(),
    });

    const closeBtn = document.getElementById('feedflow-close-btn');
    closeBtn.click();
    expect(onClose).toHaveBeenCalledOnce();

    const form = document.getElementById('feedflow-form');
    form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
    expect(onSubmit).toHaveBeenCalledOnce();
  });

  it('setupModalDrag inicializa listeners de drag sem erro', () => {
    const modal = createModal({
      primaryColor: '#4F46E5',
    });

    const content = modal.querySelector('#feedflow-modal-content');
    vi.spyOn(content, 'getBoundingClientRect').mockReturnValue({
      width: 300,
      height: 300,
      left: 10,
      top: 10,
      right: 310,
      bottom: 310,
      x: 10,
      y: 10,
      toJSON: () => ({}),
    });

    setupModalDrag(modal);

    const handle = modal.querySelector('#feedflow-drag-handle');
    handle.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, clientX: 30, clientY: 30 }));
    document.dispatchEvent(new MouseEvent('mousemove', { bubbles: true, clientX: 50, clientY: 60 }));

    expect(content.style.left).not.toBe('');
    expect(content.style.top).not.toBe('');
  });
});
