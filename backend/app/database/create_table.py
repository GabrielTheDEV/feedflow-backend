from app.database.config import init_db

# Script para criar as tabelas no banco de dados -- Executar apenas uma vez 

if __name__ == "__main__":
    init_db()
    print("Tabelas criadas com sucesso!")
