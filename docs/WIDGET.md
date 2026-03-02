# FeedFlow Widget - Documentação de Uso

## O que é?
O FeedFlow Widget permite que qualquer site colete feedback visual dos usuários, incluindo captura de tela e envio direto para sua API.

## Como instalar
Basta adicionar a seguinte tag ao HTML do seu site, substituindo os valores conforme necessário:

```html
<script 
  src="https://seu-dominio.com/widget.js"
  data-api-token="SEU_TOKEN_AQUI"
  data-api-url="https://api.feedflow.com"
  data-button-text="Reportar Problema"
  data-button-position="bottom-right"
  data-primary-color="#4F46E5"
  data-domain="seudominio.com"
></script>
```

### Produção
```html
<script 
  src="https://seu-dominio.com/widget.js"
  data-api-token="SEU_TOKEN_AQUI"
  data-api-url="https://api.feedflow.com"
  data-button-text="Reportar Problema"
  data-button-position="bottom-right"
  data-primary-color="#4F46E5"
  data-domain="seudominio.com"
></script>
```

### Desenvolvimento (local)
```html
<script 
  src="http://localhost:8000/static/widget.js"
  data-api-token="SEU_TOKEN_AQUI"
  data-api-url="http://localhost:8000/api/v1"
  data-button-text="Reportar Problema"
  data-button-position="bottom-right"
  data-primary-color="#4F46E5"
></script>
```

## Parâmetros disponíveis

## Funcionamento
Ao carregar a página, o widget será ativado automaticamente, exibindo um botão flutuante. O usuário pode clicar para abrir o modal de feedback, capturar a tela e enviar o feedback.

## Exemplo completo
```html
<script 
  src="https://seu-dominio.com/widget.js"
  data-api-token="123456"
  data-api-url="https://api.feedflow.com"
  data-button-text="Enviar Feedback"
  data-button-position="bottom-right"
  data-primary-color="#4F46E5"
  data-domain="meusite.com"
></script>
```
```html
<script 
  src="http://localhost:8000/static/widget.js"
  data-api-token="123456"
  data-api-url="http://localhost:8000/api/v1"
  data-button-text="Enviar Feedback"
  data-button-position="bottom-right"
  data-primary-color="#4F46E5"
></script>
```
```

## Observações
- Não é necessário nenhuma chamada JavaScript adicional.
- O widget funciona em qualquer site que permita inserir tags `<script>`.
- Para personalizações avançadas, consulte o desenvolvedor do widget.

---
Dúvidas? Fale com o suporte FeedFlow.