// Lê configurações da tag <script>
export function getConfig() {
  const currentScript = document.currentScript || (function() {
    const scripts = document.getElementsByTagName('script');
    return scripts[scripts.length - 1];
  })();
  return {
    apiToken: currentScript.getAttribute('data-api-token'),
    apiUrl: currentScript.getAttribute('data-api-url'),
    buttonText: currentScript.getAttribute('data-button-text') || 'Reportar Problema',
    buttonPosition: currentScript.getAttribute('data-button-position') || 'bottom-right',
    primaryColor: currentScript.getAttribute('data-primary-color') || '#4F46E5',
    language: currentScript.getAttribute('data-language') || 'pt-BR',
    domain: currentScript.getAttribute('data-domain') || undefined
  };
}
