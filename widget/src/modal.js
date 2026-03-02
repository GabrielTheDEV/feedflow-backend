export function createModal(config) {
  const modal = document.createElement('div');
  modal.id = 'feedflow-modal';
  modal.style.cssText = `
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.5);
    z-index: 999999;
    justify-content: center;
    align-items: center;
    backdrop-filter: blur(4px);
  `;
  modal.innerHTML = `
    <div id="feedflow-modal-content" style="
      background: white;
      border-radius: 16px;
      padding: 16px;
      max-width: 360px;
      width: 90%;
      max-height: 55vh;
      overflow-y: auto;
      box-shadow: 0 20px 60px rgba(0,0,0,0.3);
      position: fixed;
      bottom: 100px;
      right: 20px;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    ">
      <button id="feedflow-close-btn" style="
        position: absolute;
        top: 16px;
        right: 16px;
        background: transparent;
        border: none;
        font-size: 24px;
        cursor: pointer;
        color: #6B7280;
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 8px;
        transition: background 0.2s;
      ">&times;</button>
      <div id="feedflow-drag-handle" style="
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 6px;
        margin: -16px 0 12px 0;
        padding: 8px 0;
        cursor: move;
        user-select: none;
      ">
        <div style="
          width: 48px;
          height: 6px;
          border-radius: 999px;
          background: #E5E7EB;
        "></div>
        <span style="font-size: 12px; color: #9CA3AF;">Arraste</span>
      </div>

      <h2 style="margin: 0 0 8px 0; font-size: 24px; color: #111827;">
        Reportar Problema
      </h2>
      <p style="margin: 0 0 24px 0; color: #6B7280; font-size: 14px;">
        Capture uma imagem da tela e nos conte o que aconteceu
      </p>
      <form id="feedflow-form">
        <div style="margin-bottom: 16px;">
          <label style="display: block; margin-bottom: 8px; font-size: 14px; font-weight: 600; color: #374151;">
            Seu E-mail <span style="color: #EF4444;">*</span>
          </label>
          <input 
            type="email" 
            id="feedflow-email" 
            placeholder="seu@email.com"
            required
            style="
              width: 100%;
              padding: 12px;
              border: 2px solid #D1D5DB;
              border-radius: 8px;
              font-size: 14px;
              box-sizing: border-box;
              transition: border-color 0.2s;
            "
          />
        </div>
        <div style="margin-bottom: 20px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <label style="font-size: 14px; font-weight: 600; color: #374151;">
              Descreva o problema
            </label>
            <span id="feedflow-char-count" style="font-size: 12px; color: #9CA3AF;">
              0 / 550
            </span>
          </div>
          <textarea 
            id="feedflow-message" 
            rows="3"
            maxlength="550"
            placeholder="O que aconteceu? O que você esperava que acontecesse?"
            style="
              width: 100%;
              padding: 12px;
              border: 2px solid #D1D5DB;
              border-radius: 8px;
              font-size: 14px;
              resize: vertical;
              font-family: inherit;
              box-sizing: border-box;
              transition: border-color 0.2s;
            "
          ></textarea>
        </div>

        <div id="feedflow-screenshot-preview" style="
          display: none;
          position: relative;
          margin-bottom: 12px;
          padding: 8px;
          border: 1px solid #E5E7EB;
          border-radius: 10px;
          background: #F9FAFB;
          box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        ">
          <button id="feedflow-remove-screenshot" type="button" style="
            position: absolute;
            top: 6px;
            right: 6px;
            background: white;
            border: 1px solid #E5E7EB;
            color: #6B7280;
            width: 24px;
            height: 24px;
            border-radius: 999px;
            cursor: pointer;
            font-size: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 2px 6px rgba(0,0,0,0.08);
          ">×</button>
          <img id="feedflow-screenshot-img" alt="Preview do screenshot" style="
            width: 100%;
            max-height: 120px;
            object-fit: cover;
            border-radius: 8px;
            display: block;
            cursor: pointer;
          " />
        </div>
        <div style="display: flex; gap: 10px; align-items: center;">
          <button
            type="button"
            id="feedflow-camera-btn"
            aria-label="Capturar screenshot"
            style="
              width: 46px;
              height: 46px;
              border-radius: 10px;
              border: 1px solid #E5E7EB;
              background: white;
              cursor: pointer;
              font-size: 20px;
              display: flex;
              align-items: center;
              justify-content: center;
              transition: all 0.2s;
              box-shadow: 0 4px 10px rgba(0,0,0,0.08);
            "
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#374151" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h4l2-2h6l2 2h4a2 2 0 0 1 2 2z"></path>
              <circle cx="12" cy="13" r="4"></circle>
            </svg>
          </button>
          <button 
            type="submit" 
            id="feedflow-submit-btn"
            disabled
            style="
              flex: 1;
              padding: 14px;
              background: ${config.primaryColor};
              color: white;
              border: none;
              border-radius: 8px;
              font-size: 16px;
              font-weight: 600;
              cursor: pointer;
              transition: all 0.2s;
              opacity: 0.5;
            "
          >Enviar Feedback</button>
        </div>
      </form>
      <div id="feedflow-status" style="
        margin-top: 16px;
        padding: 12px;
        border-radius: 8px;
        font-size: 14px;
        display: none;
      "></div>
    </div>
  `;
  document.body.appendChild(modal);

  return modal;
}

export function setupModalDrag(modal) {
  const modalContent = modal.querySelector('#feedflow-modal-content');
  const handle = modal.querySelector('#feedflow-drag-handle');
  if (!modalContent || !handle) return;

  let isDragging = false;
  let startX = 0;
  let startY = 0;
  let startLeft = 0;
  let startTop = 0;
  let contentWidth = 0;
  let contentHeight = 0;

  const onMouseMove = (e) => {
    if (!isDragging) return;
    const dx = e.clientX - startX;
    const dy = e.clientY - startY;
    const newLeft = Math.min(Math.max(startLeft + dx, 0), window.innerWidth - contentWidth);
    const newTop = Math.min(Math.max(startTop + dy, 0), window.innerHeight - contentHeight);
    modalContent.style.left = `${newLeft}px`;
    modalContent.style.top = `${newTop}px`;
  };

  const onTouchMove = (e) => {
    if (!isDragging || !e.touches || !e.touches.length) return;
    const t = e.touches[0];
    const dx = t.clientX - startX;
    const dy = t.clientY - startY;
    const newLeft = Math.min(Math.max(startLeft + dx, 0), window.innerWidth - contentWidth);
    const newTop = Math.min(Math.max(startTop + dy, 0), window.innerHeight - contentHeight);
    modalContent.style.left = `${newLeft}px`;
    modalContent.style.top = `${newTop}px`;
  };

  const onMouseUp = () => {
    isDragging = false;
    document.removeEventListener('mousemove', onMouseMove);
    document.removeEventListener('mouseup', onMouseUp);
    document.removeEventListener('touchmove', onTouchMove);
  };

  const startDrag = (clientX, clientY) => {
    const rect = modalContent.getBoundingClientRect();
    contentWidth = rect.width;
    contentHeight = rect.height;
    startX = clientX;
    startY = clientY;
    startLeft = rect.left;
    startTop = rect.top;
    modalContent.style.transform = 'none';
    modalContent.style.left = `${rect.left}px`;
    modalContent.style.top = `${rect.top}px`;
    isDragging = true;
    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);
    document.addEventListener('touchmove', onTouchMove, { passive: true });
  };

  handle.addEventListener('mousedown', (e) => {
    e.preventDefault();
    startDrag(e.clientX, e.clientY);
  });

  handle.addEventListener('touchstart', (e) => {
    if (!e.touches || !e.touches.length) return;
    const t = e.touches[0];
    startDrag(t.clientX, t.clientY);
  }, { passive: true });

  document.addEventListener('touchend', () => {
    if (!isDragging) return;
    isDragging = false;
  });
}

export function setupModalEvents(modal, handlers) {
  if (!modal) return;
  const closeBtn = modal.querySelector('#feedflow-close-btn');
  const form = modal.querySelector('#feedflow-form');
  const textarea = modal.querySelector('#feedflow-message');
  const emailInput = modal.querySelector('#feedflow-email');
  const previewImg = modal.querySelector('#feedflow-screenshot-img');
  const removeScreenshotBtn = modal.querySelector('#feedflow-remove-screenshot');

  closeBtn.onclick = handlers.onClose;
  closeBtn.onmouseover = () => { closeBtn.style.background = '#F3F4F6'; };
  closeBtn.onmouseout = () => { closeBtn.style.background = 'transparent'; };

  form.onsubmit = handlers.onSubmit;

  modal.onclick = (e) => {
    if (e.target === modal) handlers.onClose();
  };

  textarea.addEventListener('input', handlers.onMessageInput);
  emailInput.addEventListener('input', handlers.onEmailInput);
  textarea.addEventListener('keydown', handlers.onMessageKeydown);

  if (previewImg) {
    previewImg.addEventListener('click', handlers.onPreviewClick);
  }
  if (removeScreenshotBtn) {
    removeScreenshotBtn.addEventListener('click', handlers.onRemoveScreenshot);
  }
}
