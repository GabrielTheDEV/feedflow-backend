"""
Script auxiliar para testar o endpoint de submit-feedback
Execute: python test_api.py
"""
import pytest
import requests
import json
from pathlib import Path

pytestmark = pytest.mark.skip(reason="Teste manual, fora da suíte automatizada")


def create_test_image():
    """Cria uma imagem de teste simples"""
    from PIL import Image
    
    # Criar imagem simples 100x100 azul
    img = Image.new('RGB', (100, 100), color=(73, 109, 137))
    img.save('test_screenshot.png')
    print("✅ Imagem de teste criada: test_screenshot.png")


def test_submit_feedback(api_token: str, api_url: str = "http://localhost:8000"):
    """
    Testa o endpoint de submit-feedback
    
    Args:
        api_token: Token de API do merchant
        api_url: URL da API (padrão: http://localhost:8000)
    """
    
    print("\n" + "="*60)
    print("🧪 Testando API do FeedFlow")
    print("="*60)
    
    # Verifica se a imagem de teste existe
    if not Path('test_screenshot.png').exists():
        print("\n📸 Criando imagem de teste...")
        try:
            create_test_image()
        except ImportError:
            print("❌ Pillow não instalado. Instale com: pip install Pillow")
            print("   Ou use uma imagem existente como 'test_screenshot.png'")
            return
    
    # Preparar dados
    url = f"{api_url}/api/v1/submit-feedback"
    headers = {
        "X-API-Token": api_token
    }
    
    # Metadados
    metadata = {
        "page_url": "https://minhaloja.com/produto-teste",
        "user_agent": "Test Agent",
        "viewport_width": 1920,
        "viewport_height": 1080,
        "screen_width": 1920,
        "screen_height": 1080,
        "timestamp": "2026-02-13T10:30:00Z",
        "browser_language": "pt-BR",
        "referrer": "https://google.com"
    }
    
    # Preparar multipart
    files = {
        'screenshot': ('test_screenshot.png', open('test_screenshot.png', 'rb'), 'image/png')
    }
    
    data = {
        'customer_email': 'teste@email.com',
        'customer_message': 'Este é um feedback de teste. O botão de compra não está funcionando!',
        'metadata': json.dumps(metadata)
    }
    
    print(f"\n📡 Enviando requisição para: {url}")
    print(f"🔑 Token: {api_token[:10]}...")
    
    try:
        # Fazer requisição
        response = requests.post(url, headers=headers, files=files, data=data)
        
        print(f"\n📊 Status Code: {response.status_code}")
        
        # Processar resposta
        if response.status_code == 201:
            result = response.json()
            print("\n✅ Sucesso! Feedback enviado.")
            print(f"   Mensagem: {result.get('message')}")
            if 'data' in result:
                print(f"   Feedback ID: {result['data'].get('feedback_id')}")
                print(f"   Status: {result['data'].get('status')}")
                print(f"   Criado em: {result['data'].get('created_at')}")
        else:
            print("\n❌ Erro na requisição")
            print(f"   Resposta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Erro de conexão!")
        print("   Verifique se o servidor está rodando em", api_url)
    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")
    finally:
        files['screenshot'][1].close()
    
    print("\n" + "="*60)


def main():
    """Função principal"""
    print("="*60)
    print("🚀 FeedFlow - Teste de API")
    print("="*60)
    
    # Solicitar configurações
    api_token = input("\nDigite o API Token: ").strip()
    api_url = input("Digite a API URL [http://localhost:8000]: ").strip()
    
    if not api_url:
        api_url = "http://localhost:8000"
    
    if not api_token:
        print("❌ Token não pode estar vazio!")
        return
    
    # Executar teste
    test_submit_feedback(api_token, api_url)
    
    print("\n✨ Teste concluído!")


if __name__ == "__main__":
    main()
