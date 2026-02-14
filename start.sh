#!/bin/bash

echo "🚀 Iniciando FeedFlow..."
echo "========================"

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando. Por favor, inicie o Docker primeiro."
    exit 1
fi

# Subir containers
echo ""
echo "📦 Subindo containers..."
docker-compose up -d

# Aguardar backend estar pronto
echo ""
echo "⏳ Aguardando backend inicializar..."
sleep 10

# Verificar se está rodando
if curl -s http://localhost:8000/health > /dev/null; then
    echo ""
    echo "✅ FeedFlow está rodando!"
    echo ""
    echo "📊 Serviços disponíveis:"
    echo "   - API: http://localhost:8000"
    echo "   - Docs: http://localhost:8000/docs"
    echo "   - PostgreSQL: localhost:5432"
    echo ""
    echo "📝 Próximos passos:"
    echo "   1. Criar merchant: docker-compose exec backend python create_merchant.py"
    echo "   2. Abrir demo: widget/demo.html no navegador"
    echo ""
    echo "📋 Comandos úteis:"
    echo "   - Ver logs: docker-compose logs -f backend"
    echo "   - Parar: docker-compose down"
    echo "   - Reiniciar: docker-compose restart"
    echo ""
else
    echo ""
    echo "⚠️  Backend pode estar ainda inicializando..."
    echo "   Verifique os logs: docker-compose logs backend"
fi
