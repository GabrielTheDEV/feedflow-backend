#!/bin/bash

echo "🛑 Parando FeedFlow..."
docker-compose down

echo ""
echo "✅ Containers parados!"
echo ""
echo "💡 Para remover volumes também, use: docker-compose down -v"
