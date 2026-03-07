import { getConfig } from './config';
import { createFloatingButton } from './button';
import { createModal, setupModalDrag, setupModalEvents } from './modal';
import { createFullscreenViewer, openFullscreenViewer } from './fullscreen';
import { captureScreenshot } from './screenshot';
import {
  showStatus,
  hideStatus,
  collectMetadata,
  isValidEmail,
  updateCharCounter,
} from './utils';

(function(window) {
  'use strict';

  const defaultConfig = {
    apiToken: null,
    apiUrl: null,
    buttonText: 'Reportar Problema',
    buttonPosition: 'bottom-right',
    primaryColor: '#4F46E5',
    language: 'pt-BR',
  };

  const state = {
    isOpen: false,
    isCapturing: false,
    screenshotBlob: null,
    screenshotPreviewUrl: null,
    hasPreview: false,
  };

  const instance = {
    initialized: false,
    config: { ...defaultConfig },
    button: null,
    modal: null,
    fullscreenViewer: null,
  };

  function openModal() {
    if (!instance.modal) return;
    instance.modal.style.display = 'flex';
    state.isOpen = true;
    validateForm();
    updateCameraButtonState();
  }

  function closeModal() {
    if (!instance.modal) return;
    instance.modal.style.display = 'none';
    state.isOpen = false;
    resetForm();
  }

  function updateCameraButtonState() {
    const cameraBtn = document.getElementById('feedflow-camera-btn');
    if (!cameraBtn) return;
    const isDisabled = state.isCapturing || state.hasPreview;
    cameraBtn.disabled = isDisabled;
    cameraBtn.style.opacity = isDisabled ? '0.5' : '1';
    cameraBtn.style.cursor = isDisabled ? 'not-allowed' : 'pointer';
  }

  function clearScreenshotPreview() {
    const previewBox = document.getElementById('feedflow-screenshot-preview');
    const previewImg = document.getElementById('feedflow-screenshot-img');
    if (state.screenshotPreviewUrl) {
      URL.revokeObjectURL(state.screenshotPreviewUrl);
    }
    state.screenshotBlob = null;
    state.screenshotPreviewUrl = null;
    state.hasPreview = false;
    if (previewImg) previewImg.src = '';
    if (previewBox) previewBox.style.display = 'none';
    updateCameraButtonState();
  }

  function setScreenshotPreview(blob) {
    const previewBox = document.getElementById('feedflow-screenshot-preview');
    const previewImg = document.getElementById('feedflow-screenshot-img');
    if (!previewBox || !previewImg) return;

    if (state.screenshotPreviewUrl) {
      URL.revokeObjectURL(state.screenshotPreviewUrl);
    }

    const previewUrl = URL.createObjectURL(blob);
    state.screenshotBlob = blob;
    state.screenshotPreviewUrl = previewUrl;
    state.hasPreview = true;
    previewImg.src = previewUrl;
    previewBox.style.display = 'block';
    updateCameraButtonState();
  }

  function validateForm() {
    const emailInput = document.getElementById('feedflow-email');
    const messageInput = document.getElementById('feedflow-message');
    const submitBtn = document.getElementById('feedflow-submit-btn');
    if (!emailInput || !messageInput || !submitBtn) return;

    const email = emailInput.value.trim();
    const message = messageInput.value.trim();
    const isEmailValid = email.length > 0 && isValidEmail(email);
    const isMessageValid = message.length > 0 && message.length <= 550;
    const isValid = isEmailValid && isMessageValid;

    submitBtn.disabled = !isValid;
    submitBtn.style.opacity = isValid ? '1' : '0.5';
    submitBtn.style.cursor = isValid ? 'pointer' : 'not-allowed';

    emailInput.style.borderColor = email.length === 0 ? '#D1D5DB' : (isEmailValid ? '#10B981' : '#EF4444');
    messageInput.style.borderColor = message.length === 0 ? '#D1D5DB' : (isMessageValid ? '#10B981' : '#EF4444');
  }

  function resetForm() {
    const emailInput = document.getElementById('feedflow-email');
    const messageInput = document.getElementById('feedflow-message');
    const charCount = document.getElementById('feedflow-char-count');
    if (emailInput) emailInput.value = '';
    if (messageInput) messageInput.value = '';
    updateCharCounter(charCount, 0);
    if (emailInput) emailInput.style.borderColor = '#D1D5DB';
    if (messageInput) messageInput.style.borderColor = '#D1D5DB';
    clearScreenshotPreview();
    hideStatus();
    validateForm();
  }

  async function sendReport(screenshot, email, message, metadata) {
    const payload = {
      title: 'Widget report',
      message,
      email,
      page: window.location.href,
      metadata,
      has_screenshot: Boolean(screenshot),
    };

    const response = await fetch(`${instance.config.apiUrl}/reports?api_key=${encodeURIComponent(instance.config.apiToken)}`, {
      method: 'POST',
      body: JSON.stringify(payload),
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json();
      let errorMessage = error.error || error.detail || 'Erro ao enviar feedback';
      errorMessage = typeof errorMessage === 'string' ? errorMessage : JSON.stringify(errorMessage);
      if (errorMessage.toLowerCase().includes('slack')) {
        errorMessage += '\n\n👉 Conecte seu Slack para enviar feedbacks. Clique em "Conectar Slack" nas configurações.';
      }
      throw new Error(errorMessage);
    }

    if (response.status === 204) {
      return null;
    }

    return response.json();
  }

  async function handleCapture() {
    if (state.isCapturing || state.hasPreview) return;
    state.isCapturing = true;
    updateCameraButtonState();
    showStatus('Capturando screenshot...', 'info');

    try {
      if (instance.modal) instance.modal.style.display = 'none';
      await new Promise((resolve) => setTimeout(resolve, 100));
      const screenshot = await captureScreenshot();
      setScreenshotPreview(screenshot);
      showStatus('✓ Screenshot capturado!', 'success');
    } catch (error) {
      console.error('[FeedFlow] Erro ao capturar screenshot:', error);
      showStatus('✗ Erro ao capturar screenshot.', 'error');
    } finally {
      if (instance.modal) instance.modal.style.display = 'flex';
      state.isCapturing = false;
      updateCameraButtonState();
    }
  }

  async function handleSubmit(event) {
    event.preventDefault();
    if (state.isCapturing) return;

    const emailInput = document.getElementById('feedflow-email');
    const messageInput = document.getElementById('feedflow-message');
    if (!emailInput || !messageInput) return;

    const email = emailInput.value.trim();
    const message = messageInput.value.trim();

    if (!email || !isValidEmail(email)) {
      showStatus('✗ Por favor, forneça um e-mail válido.', 'error');
      return;
    }

    if (!message || message.length > 550) {
      showStatus('✗ Por favor, descreva o problema (1-550 caracteres).', 'error');
      return;
    }

    showStatus('Enviando feedback...', 'info');
    state.isCapturing = true;
    updateCameraButtonState();

    try {
      const metadata = collectMetadata();
      await sendReport(state.screenshotBlob, email, message, metadata);
      showStatus('✓ Feedback enviado com sucesso! Obrigado.', 'success');
      setTimeout(() => {
        closeModal();
      }, 2000);
    } catch (error) {
      console.error('[FeedFlow] Erro:', error);
      showStatus(error.message || '✗ Erro ao enviar feedback. Tente novamente.', 'error');
    } finally {
      state.isCapturing = false;
      updateCameraButtonState();
    }
  }

  function wireEvents() {
    const cameraBtn = document.getElementById('feedflow-camera-btn');
    const emailInput = document.getElementById('feedflow-email');
    const messageInput = document.getElementById('feedflow-message');
    const charCount = document.getElementById('feedflow-char-count');
    const previewImg = document.getElementById('feedflow-screenshot-img');

    if (instance.button) {
      instance.button.onclick = openModal;
    }

    setupModalEvents(instance.modal, {
      onClose: closeModal,
      onSubmit: handleSubmit,
      onMessageInput: (e) => {
        updateCharCounter(charCount, e.target.value.length);
        validateForm();
      },
      onEmailInput: () => {
        validateForm();
      },
      onMessageKeydown: (e) => {
        if (e.target.value.length >= 550 && e.key !== 'Backspace' && e.key !== 'Delete') {
          e.preventDefault();
        }
      },
      onPreviewClick: () => {
        if (previewImg && previewImg.src) {
          openFullscreenViewer(instance.fullscreenViewer, previewImg.src);
        }
      },
      onRemoveScreenshot: () => {
        clearScreenshotPreview();
      },
    });

    if (cameraBtn) cameraBtn.addEventListener('click', handleCapture);
    if (emailInput) emailInput.addEventListener('input', validateForm);
    if (messageInput) messageInput.addEventListener('input', validateForm);
  }

  function mountWidget(config) {
    if (instance.initialized) return;

    instance.button = createFloatingButton(config);
    instance.modal = createModal(config);
    instance.fullscreenViewer = createFullscreenViewer();

    setupModalDrag(instance.modal);
    wireEvents();
    validateForm();
    updateCameraButtonState();

    instance.initialized = true;
    console.log('[FeedFlow] Widget inicializado com sucesso');
  }

  function init(options = {}) {
    instance.config = { ...defaultConfig, ...options };

    if (!instance.config.apiToken) {
      console.error('[FeedFlow] API Token é obrigatório');
      return;
    }
    if (!instance.config.apiUrl) {
      console.error('[FeedFlow] API URL é obrigatória');
      return;
    }

    const doMount = () => mountWidget(instance.config);
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', doMount, { once: true });
    } else {
      doMount();
    }
  }

  window.FeedFlowWidget = {
    get config() {
      return instance.config;
    },
    init,
    open: openModal,
    close: closeModal,
  };

  const autoConfig = getConfig();
  if (autoConfig.apiToken) {
    window.FeedFlowWidget.init(autoConfig);
  }
})(window);
