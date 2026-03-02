/**
 * FeedFlow Widget - Captura Visual de Feedback
 * 
 * Widget em Vanilla JavaScript para capturar screenshots e enviar feedbacks
 * Pode ser injetado em qualquer site (especialmente lojas Shopify)
 * 
 * Uso:
 * <script src="https://seu-dominio.com/widget.js"></script>
 * <script>
 *   FeedFlowWidget.init({
 *     apiToken: 'seu-token-aqui',
 *     apiUrl: 'https://api.feedflow.com'
 *   });
 * </script>
 */

(function(window) {
    'use strict';

    // Namespace global
    const FeedFlowWidget = {
        config: {
            apiToken: null,
            apiUrl: null,
            buttonText: 'Reportar Problema',
            buttonPosition: 'bottom-right', // bottom-right, bottom-left, top-right, top-left
            primaryColor: '#4F46E5',
            language: 'pt-BR'
        },
        state: {
            isOpen: false,
            isCapturing: false,
            screenshotBlob: null,
            screenshotPreviewUrl: null,
            hasPreview: false
        },
        elements: {},

        /**
         * Inicializa o widget com configurações personalizadas
         * @param {Object} options - Configurações do widget
         */
        init(options = {}) {
            // Validar configurações obrigatórias
            if (!options.apiToken) {
                console.error('[FeedFlow] API Token é obrigatório');
                return;
            }
            if (!options.apiUrl) {
                console.error('[FeedFlow] API URL é obrigatória');
                return;
            }

            // Merge configurações
            this.config = { ...this.config, ...options };

            // Aguardar DOM estar pronto
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => this.render());
            } else {
                this.render();
            }
        },

        /**
         * Renderiza o botão flutuante e modal
         */
        render() {
            // Criar botão flutuante
            this.createFloatingButton();
            
            // Criar modal
            this.createModal();

            // Criar fullscreen viewer
            this.createFullscreenViewer();

            console.log('[FeedFlow] Widget inicializado com sucesso');
        },

        /**
         * Cria o botão flutuante na tela
         */
        createFloatingButton() {
            const button = document.createElement('button');
            button.id = 'feedflow-trigger-btn';
            button.innerHTML = `
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                </svg>
                <span>${this.config.buttonText}</span>
            `;

            // Estilos do botão
            const positions = {
                'bottom-right': 'bottom: 20px; right: 20px;',
                'bottom-left': 'bottom: 20px; left: 20px;',
                'top-right': 'top: 20px; right: 20px;',
                'top-left': 'top: 20px; left: 20px;'
            };

            button.style.cssText = `
                position: fixed;
                ${positions[this.config.buttonPosition]}
                background: ${this.config.primaryColor};
                color: white;
                border: none;
                border-radius: 50px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                z-index: 999998;
                display: flex;
                align-items: center;
                gap: 8px;
                transition: all 0.3s ease;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            `;

            button.onmouseover = () => {
                button.style.transform = 'scale(1.05)';
                button.style.boxShadow = '0 6px 16px rgba(0,0,0,0.2)';
            };
            button.onmouseout = () => {
                button.style.transform = 'scale(1)';
                button.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
            };

            button.onclick = () => this.openModal();

            document.body.appendChild(button);
            this.elements.button = button;
        },

        /**
         * Cria o modal de feedback
         */
        createModal() {
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
                            " />
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
                                    background: ${this.config.primaryColor};
                                    color: white;
                                    border: none;
                                    border-radius: 8px;
                                    font-size: 16px;
                                    font-weight: 600;
                                    cursor: pointer;
                                    transition: all 0.2s;
                                    opacity: 0.5;
                                "
                            >
                                Enviar Feedback
                            </button>
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
            this.elements.modal = modal;
            this.elements.modalContent = modal.querySelector('#feedflow-modal-content');
            this.elements.dragHandle = modal.querySelector('#feedflow-drag-handle');

            // Event listeners
            modal.querySelector('#feedflow-close-btn').onclick = () => this.closeModal();
            modal.querySelector('#feedflow-form').onsubmit = (e) => this.handleSubmit(e);
            modal.onclick = (e) => {
                if (e.target === modal) this.closeModal();
            };

            // Textarea validation listeners
            const textarea = modal.querySelector('#feedflow-message');
            const emailInput = modal.querySelector('#feedflow-email');
            const charCount = modal.querySelector('#feedflow-char-count');
            const submitBtn = modal.querySelector('#feedflow-submit-btn');
            const cameraBtn = modal.querySelector('#feedflow-camera-btn');
            const previewBox = modal.querySelector('#feedflow-screenshot-preview');
            const previewImg = modal.querySelector('#feedflow-screenshot-img');
            const removeScreenshotBtn = modal.querySelector('#feedflow-remove-screenshot');

            textarea.addEventListener('input', (e) => {
                const length = e.target.value.length;
                charCount.textContent = `${length} / 550`;
                
                // Atualizar cor do contador
                if (length === 0) {
                    charCount.style.color = '#9CA3AF';
                } else if (length > 500) {
                    charCount.style.color = '#EF4444';
                } else {
                    charCount.style.color = '#6B7280';
                }
                
                // Validar e atualizar estado do botão
                this.validateFeedbackForm(modal);
            });

            // Email validation listener
            emailInput.addEventListener('input', (e) => {
                this.validateFeedbackForm(modal);
            });

            cameraBtn.addEventListener('click', async () => {
                if (this.state.isCapturing || this.state.hasPreview) return;
                this.state.isCapturing = true;
                this.updateCameraButtonState(modal);
                this.showStatus('Capturando screenshot...', 'info');

                try {
                    const screenshot = await this.captureScreenshot();
                    this.setScreenshotPreview(screenshot, modal);
                    this.showStatus('✓ Screenshot capturado!', 'success');
                } catch (error) {
                    console.error('[FeedFlow] Erro ao capturar screenshot:', error);
                    this.showStatus('✗ Erro ao capturar screenshot.', 'error');
                } finally {
                    this.state.isCapturing = false;
                    this.updateCameraButtonState(modal);
                }
            });

            removeScreenshotBtn.addEventListener('click', () => {
                this.clearScreenshotPreview(modal);
            });

            // Adicionar evento de clique na imagem para abrir fullscreen
            previewImg.addEventListener('click', () => {
                this.openFullscreenViewer();
            });
            previewImg.style.cursor = 'pointer';

            textarea.addEventListener('keydown', (e) => {
                // Impedir digitação acima do limite
                if (e.target.value.length >= 550 && e.key !== 'Backspace' && e.key !== 'Delete') {
                    e.preventDefault();
                }
            });

            // Estado inicial do botão de câmera
            this.updateCameraButtonState(modal);

            // Drag handlers
            this.setupDragHandlers();

            // Hover effect no botão fechar
            const closeBtn = modal.querySelector('#feedflow-close-btn');
            closeBtn.onmouseover = () => closeBtn.style.background = '#F3F4F6';
            closeBtn.onmouseout = () => closeBtn.style.background = 'transparent';
        },

        /**
         * Configura os eventos para arrastar o modal
         */
        setupDragHandlers() {
            const handle = this.elements.dragHandle;
            const modalContent = this.elements.modalContent;
            if (!handle || !modalContent) return;

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
                const newLeft = Math.min(
                    Math.max(startLeft + dx, 0),
                    window.innerWidth - contentWidth
                );
                const newTop = Math.min(
                    Math.max(startTop + dy, 0),
                    window.innerHeight - contentHeight
                );
                modalContent.style.left = `${newLeft}px`;
                modalContent.style.top = `${newTop}px`;
            };

            const onMouseUp = () => {
                if (!isDragging) return;
                isDragging = false;
                document.removeEventListener('mousemove', onMouseMove);
                document.removeEventListener('mouseup', onMouseUp);
            };

            const startDrag = (clientX, clientY) => {
                const rect = modalContent.getBoundingClientRect();
                contentWidth = rect.width;
                contentHeight = rect.height;
                startX = clientX;
                startY = clientY;
                startLeft = rect.left;
                startTop = rect.top;

                // Remove transform para permitir posicionamento absoluto
                modalContent.style.transform = 'none';
                modalContent.style.left = `${rect.left}px`;
                modalContent.style.top = `${rect.top}px`;

                isDragging = true;
                document.addEventListener('mousemove', onMouseMove);
                document.addEventListener('mouseup', onMouseUp);
            };

            handle.addEventListener('mousedown', (e) => {
                e.preventDefault();
                startDrag(e.clientX, e.clientY);
            });

            handle.addEventListener('touchstart', (e) => {
                if (!e.touches || e.touches.length === 0) return;
                const touch = e.touches[0];
                startDrag(touch.clientX, touch.clientY);
            }, { passive: true });

            document.addEventListener('touchmove', (e) => {
                if (!isDragging || !e.touches || e.touches.length === 0) return;
                const touch = e.touches[0];
                const dx = touch.clientX - startX;
                const dy = touch.clientY - startY;
                const newLeft = Math.min(
                    Math.max(startLeft + dx, 0),
                    window.innerWidth - contentWidth
                );
                const newTop = Math.min(
                    Math.max(startTop + dy, 0),
                    window.innerHeight - contentHeight
                );
                modalContent.style.left = `${newLeft}px`;
                modalContent.style.top = `${newTop}px`;
            }, { passive: true });

            document.addEventListener('touchend', () => {
                if (!isDragging) return;
                isDragging = false;
            });
        },

        /**
         * Cria o modal fullscreen para visualizar imagens
         */
        createFullscreenViewer() {
            const viewer = document.createElement('div');
            viewer.id = 'feedflow-fullscreen-viewer';
            viewer.style.cssText = `
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.7);
                z-index: 999999;
                justify-content: center;
                align-items: center;
                cursor: pointer;
            `;

            viewer.innerHTML = `
                <img id="feedflow-fullscreen-img" src="" alt="Screenshot fullscreen" style="
                    max-width: 90%;
                    max-height: 90%;
                    object-fit: contain;
                    cursor: auto;
                    border-radius: 8px;
                " />
            `;

            document.body.appendChild(viewer);
            this.elements.fullscreenViewer = viewer;

            // Event listeners
            viewer.addEventListener('click', (e) => {
                if (e.target === viewer) this.closeFullscreenViewer();
            });

            // Fechar com ESC
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') this.closeFullscreenViewer();
            });
        },

        /**
         * Abre o fullscreen viewer
         */
        openFullscreenViewer() {
            const viewer = this.elements.fullscreenViewer;
            const img = viewer.querySelector('#feedflow-fullscreen-img');
            const previewImg = this.elements.modal.querySelector('#feedflow-screenshot-img');
            
            if (previewImg.src) {
                img.src = previewImg.src;
                viewer.style.display = 'flex';
            }
        },

        /**
         * Fecha o fullscreen viewer
         */
        closeFullscreenViewer() {
            const viewer = this.elements.fullscreenViewer;
            if (viewer) {
                viewer.style.display = 'none';
            }
        },

        /**
         * Abre o modal
         */
        openModal() {
            this.elements.modal.style.display = 'flex';
            this.state.isOpen = true;
            // Validar formulário ao abrir
            this.validateFeedbackForm();
            this.updateCameraButtonState();
        },

        /**
         * Fecha o modal
         */
        closeModal() {
            this.elements.modal.style.display = 'none';
            this.state.isOpen = false;
            this.resetForm();
        },

        /**
         * Reseta o formulário
         */
        resetForm() {
            document.getElementById('feedflow-email').value = '';
            document.getElementById('feedflow-message').value = '';
            document.getElementById('feedflow-char-count').textContent = '0 / 550';
            document.getElementById('feedflow-char-count').style.color = '#9CA3AF';
            const email = document.getElementById('feedflow-email');
            const textarea = document.getElementById('feedflow-message');
            email.style.borderColor = '#D1D5DB';
            textarea.style.borderColor = '#D1D5DB';
            this.hideStatus();
            this.clearScreenshotPreview();
            this.validateFeedbackForm();
        },

        /**
         * Valida o formulário de feedback e atualiza estado do botão
         */
        validateFeedbackForm(modal = null) {
            if (!modal) {
                modal = this.elements.modal;
                if (!modal) return;
            }

            const email = modal.querySelector('#feedflow-email');
            const textarea = modal.querySelector('#feedflow-message');
            const submitBtn = modal.querySelector('#feedflow-submit-btn');
            const emailValue = email.value.trim();
            const message = textarea.value.trim();
            
            // Validar email (formato básico)
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            const isEmailValid = emailValue.length > 0 && emailRegex.test(emailValue);
            const isMessageValid = message.length > 0 && message.length <= 550;
            
            const isValid = isEmailValid && isMessageValid;
            
            // Atualizar estado do botão
            submitBtn.disabled = !isValid;
            submitBtn.style.opacity = isValid ? '1' : '0.5';
            submitBtn.style.cursor = isValid ? 'pointer' : 'not-allowed';
            
            // Atualizar borda do email
            if (emailValue.length === 0) {
                email.style.borderColor = '#D1D5DB';
            } else if (!isEmailValid) {
                email.style.borderColor = '#EF4444';
            } else {
                email.style.borderColor = '#10B981';
            }
            
            // Atualizar borda do textarea
            if (message.length === 0) {
                textarea.style.borderColor = '#D1D5DB';
            } else if (message.length > 550) {
                textarea.style.borderColor = '#EF4444';
            } else if (message.length <= 550) {
                textarea.style.borderColor = '#10B981';
            }
        },

        /**
         * Atualiza o estado do botão de câmera
         */
        updateCameraButtonState(modal = null) {
            if (!modal) {
                modal = this.elements.modal;
                if (!modal) return;
            }

            const cameraBtn = modal.querySelector('#feedflow-camera-btn');
            if (!cameraBtn) return;

            const isDisabled = this.state.isCapturing || this.state.hasPreview;
            cameraBtn.disabled = isDisabled;
            cameraBtn.style.opacity = isDisabled ? '0.5' : '1';
            cameraBtn.style.cursor = isDisabled ? 'not-allowed' : 'pointer';
        },

        /**
         * Define o preview do screenshot
         */
        setScreenshotPreview(blob, modal = null) {
            if (!modal) {
                modal = this.elements.modal;
                if (!modal) return;
            }

            const previewBox = modal.querySelector('#feedflow-screenshot-preview');
            const previewImg = modal.querySelector('#feedflow-screenshot-img');
            if (!previewBox || !previewImg) return;

            if (this.state.screenshotPreviewUrl) {
                URL.revokeObjectURL(this.state.screenshotPreviewUrl);
            }

            const previewUrl = URL.createObjectURL(blob);
            this.state.screenshotBlob = blob;
            this.state.screenshotPreviewUrl = previewUrl;
            this.state.hasPreview = true;

            previewImg.src = previewUrl;
            previewBox.style.display = 'block';
            this.updateCameraButtonState(modal);
        },

        /**
         * Remove o preview do screenshot
         */
        clearScreenshotPreview(modal = null) {
            if (!modal) {
                modal = this.elements.modal;
                if (!modal) return;
            }

            const previewBox = modal.querySelector('#feedflow-screenshot-preview');
            const previewImg = modal.querySelector('#feedflow-screenshot-img');
            if (!previewBox || !previewImg) return;

            if (this.state.screenshotPreviewUrl) {
                URL.revokeObjectURL(this.state.screenshotPreviewUrl);
            }

            this.state.screenshotBlob = null;
            this.state.screenshotPreviewUrl = null;
            this.state.hasPreview = false;

            previewImg.src = '';
            previewBox.style.display = 'none';
            this.updateCameraButtonState(modal);
        },

        /**
         * Manipula o submit do formulário
         */
        async handleSubmit(event) {
            event.preventDefault();

            if (this.state.isCapturing) return;

            const email = document.getElementById('feedflow-email').value.trim();
            const message = document.getElementById('feedflow-message').value.trim();

            // Validação adicional - garantir email e texto
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!email || !emailRegex.test(email)) {
                this.showStatus('✗ Por favor, forneça um e-mail válido.', 'error');
                return;
            }

            if (!message || message.length === 0 || message.length > 550) {
                this.showStatus('✗ Por favor, descreva o problema (1-550 caracteres).', 'error');
                return;
            }

            this.showStatus('Enviando feedback...', 'info');
            this.state.isCapturing = true;
            this.updateCameraButtonState();

            try {
                // Coletar metadados
                const metadata = this.collectMetadata();

                // Enviar para API
                await this.sendFeedback(this.state.screenshotBlob, email, message, metadata);

                this.showStatus('✓ Feedback enviado com sucesso! Obrigado.', 'success');
                
                setTimeout(() => {
                    this.closeModal();
                }, 2000);

            } catch (error) {
                console.error('[FeedFlow] Erro:', error);
                this.showStatus('✗ Erro ao enviar feedback. Tente novamente.', 'error');
            } finally {
                this.state.isCapturing = false;
                this.updateCameraButtonState();
            }
        },

        /**
         * Captura screenshot da página usando html2canvas
         */
        async captureScreenshot() {
            // Ocultar modal temporariamente
            this.elements.modal.style.display = 'none';

            // Aguardar um pouco para o DOM atualizar
            await new Promise(resolve => setTimeout(resolve, 100));

            return new Promise((resolve, reject) => {
                // Carregar html2canvas dinamicamente
                if (!window.html2canvas) {
                    const script = document.createElement('script');
                    script.src = 'https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js';
                    script.onload = () => this.performCapture(resolve, reject);
                    script.onerror = () => reject(new Error('Falha ao carregar html2canvas'));
                    document.head.appendChild(script);
                } else {
                    this.performCapture(resolve, reject);
                }
            }).finally(() => {
                // Reexibir modal
                this.elements.modal.style.display = 'flex';
            });
        },

        /**
         * Executa a captura usando html2canvas
         */
        performCapture(resolve, reject) {
            window.html2canvas(document.body, {
                allowTaint: true,
                useCORS: true,
                logging: false,
                scale: window.devicePixelRatio || 1
            }).then(canvas => {
                canvas.toBlob(blob => {
                    if (blob) {
                        resolve(blob);
                    } else {
                        reject(new Error('Falha ao converter canvas para blob'));
                    }
                }, 'image/png');
            }).catch(reject);
        },

        /**
         * Coleta metadados técnicos da página
         */
        collectMetadata() {
            return {
                page_url: window.location.href,
                user_agent: navigator.userAgent,
                viewport_width: window.innerWidth,
                viewport_height: window.innerHeight,
                screen_width: window.screen.width,
                screen_height: window.screen.height,
                timestamp: new Date().toISOString(),
                browser_language: navigator.language,
                referrer: document.referrer || null
            };
        },

        /**
         * Envia o feedback para a API
         */
        async sendFeedback(screenshot, email, message, metadata) {
            const formData = new FormData();
            
            // Adicionar arquivo (opcional)
            if (screenshot) {
                formData.append('screenshot', screenshot, 'screenshot.png');
            }
            
            // Adicionar token
            formData.append('api_token', this.config.apiToken);
            
            // Adicionar dados opcionais
            if (email) formData.append('customer_email', email);
            if (message) formData.append('customer_message', message);
            formData.append('metadata', JSON.stringify(metadata));

            const response = await fetch(`${this.config.apiUrl}/submit-feedback`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-API-Token': this.config.apiToken
                }
            });

            if (!response.ok) {
                const error = await response.json();
                let errorMessage = error.error || error.detail || 'Erro ao enviar feedback';
                
                // Se for erro de Slack não conectado, adiciona instruções
                if (errorMessage.toLowerCase().includes('slack')) {
                    errorMessage += '\n\n👉 Conecte seu Slack para enviar feedbacks. Clique em "Conectar Slack" nas configurações.';
                }
                
                throw new Error(errorMessage);
            }

            return await response.json();
        },

        /**
         * Exibe mensagem de status
         */
        showStatus(message, type) {
            const statusEl = document.getElementById('feedflow-status');
            const colors = {
                info: { bg: '#DBEAFE', text: '#1E40AF' },
                success: { bg: '#D1FAE5', text: '#065F46' },
                error: { bg: '#FEE2E2', text: '#991B1B' }
            };

            statusEl.textContent = message;
            statusEl.style.background = colors[type].bg;
            statusEl.style.color = colors[type].text;
            statusEl.style.display = 'block';
        },

        /**
         * Oculta mensagem de status
         */
        hideStatus() {
            const statusEl = document.getElementById('feedflow-status');
            statusEl.style.display = 'none';
        }
    };


    // Expor no escopo global
    window.FeedFlowWidget = FeedFlowWidget;

    // Auto-init: busca configurações no <script> que carregou o widget
    (function() {
        const currentScript = document.currentScript || (function() {
            const scripts = document.getElementsByTagName('script');
            return scripts[scripts.length - 1];
        })();

        if (currentScript) {
            const apiToken = currentScript.getAttribute('data-api-token');
            const apiUrl = currentScript.getAttribute('data-api-url');
            const domain = currentScript.getAttribute('data-domain');
            if (apiToken) {
                window.FeedFlowWidget.init({
                    apiToken: apiToken,
                    apiUrl: apiUrl || undefined,
                    buttonText: currentScript.getAttribute('data-button-text') || '',
                    buttonPosition: currentScript.getAttribute('data-button-position') || undefined,
                    primaryColor: currentScript.getAttribute('data-primary-color') || undefined,
                    domain: domain || undefined
                });
            }
        }
    })();

})(window);
