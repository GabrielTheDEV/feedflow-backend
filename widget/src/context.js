// context.js
// Captura contexto de navegação de forma síncrona, leve e segura

export function getNavigationContext() {
  try {
    return {
      url: window.location.href || '',
      path: window.location.pathname || ''
    };
  } catch (e) {
    return { url: '', path: '' };
  }
}
