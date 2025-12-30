#!/bin/bash
# Script para iniciar Frontend + Agente simultaneamente

echo "🚀 Iniciando Agrinho (Frontend + Agente)..."
echo ""

# Obter diretório do script
DIR="$(cd "$(dirname "$0")" && pwd)"

# Iniciar Frontend em background
echo "🌐 Iniciando Frontend..."
(cd "$DIR" && ./start-frontend.sh) &
FRONTEND_PID=$!

# Aguardar um pouco para o frontend iniciar
sleep 3

# Iniciar Agente em background
echo "🤖 Iniciando Agente..."
(cd "$DIR" && ./start-agent.sh) &
AGENT_PID=$!

echo ""
echo "✅ Frontend (PID: $FRONTEND_PID) rodando em http://localhost:3000"
echo "✅ Agente (PID: $AGENT_PID) conectado ao LiveKit"
echo ""
echo "Para parar tudo: Ctrl+C ou kill $FRONTEND_PID $AGENT_PID"
echo ""

# Manter o script rodando
wait
