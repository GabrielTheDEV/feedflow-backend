"""
Script para criar um novo Merchant e gerar seu API Token
Execute: python create_merchant.py
"""
import sys
import os

# Adiciona o diretório pai ao path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal, init_db
from app.models.models import Merchant
import secrets


def generate_api_token() -> str:
    """Gera um token seguro para API"""
    return secrets.token_urlsafe(32)


def create_merchant(shop_url: str) -> Merchant:
    """
    Cria um novo merchant no banco de dados
    
    Args:
        shop_url: URL da loja Shopify
        
    Returns:
        Merchant: Objeto do merchant criado
    """
    db: Session = SessionLocal()
    
    try:
        # Verifica se já existe
        existing = db.query(Merchant).filter(Merchant.shop_url == shop_url).first()
        if existing:
            print(f"❌ Merchant já existe para a loja: {shop_url}")
            print(f"   ID: {existing.id}")
            print(f"   Token: {existing.api_token}")
            return existing
        
        # Gera token
        api_token = generate_api_token()
        
        # Cria merchant
        merchant = Merchant(
            shop_url=shop_url,
            api_token=api_token,
            is_active=1
        )
        
        db.add(merchant)
        db.commit()
        db.refresh(merchant)
        
        print(f"✅ Merchant criado com sucesso!")
        print(f"   ID: {merchant.id}")
        print(f"   Loja: {merchant.shop_url}")
        print(f"   Token: {merchant.api_token}")
        print(f"\n📋 Use este token no widget:")
        print(f"   apiToken: '{merchant.api_token}'")
        
        return merchant
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao criar merchant: {str(e)}")
        raise
    finally:
        db.close()


def main():
    """Função principal"""
    print("=" * 60)
    print("🚀 FeedFlow - Criador de Merchant")
    print("=" * 60)
    
    # Inicializa banco
    print("\n📦 Inicializando banco de dados...")
    init_db()
    print("✅ Banco inicializado!")
    
    # Solicita URL da loja
    print("\n" + "=" * 60)
    shop_url = input("Digite a URL da loja Shopify: ").strip()
    
    if not shop_url:
        print("❌ URL não pode estar vazia!")
        return
    
    # Cria merchant
    print("\n📝 Criando merchant...")
    create_merchant(shop_url)
    
    print("\n" + "=" * 60)
    print("✨ Processo concluído!")
    print("=" * 60)


if __name__ == "__main__":
    main()
