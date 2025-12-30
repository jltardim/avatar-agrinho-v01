#!/bin/bash
# Script para iniciar o agente Agrinho

echo "🤖 Iniciando Agente Agrinho..."
echo ""

# Navegar para a pasta do agente
cd "$(dirname "$0")/voice_agent"

# Verificar se Python 3 está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Erro: Python 3 não encontrado!"
    echo "Por favor, instale Python 3.10 ou superior"
    exit 1
fi

# Verificar se .env.local existe
if [ ! -f ".env.local" ]; then
    echo "❌ Erro: Arquivo .env.local não encontrado!"
    echo "Por favor, configure suas credenciais em voice_agent/.env.local"
    exit 1
fi

# Criar virtual environment se não existir
if [ ! -d ".venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv .venv
fi

# Ativar virtual environment
source .venv/bin/activate

# Instalar dependências
echo "📚 Instalando dependências..."
pip install -q -r requirements.txt

# Executar o agente
echo ""
echo "🚀 Iniciando agente em modo direto..."
echo ""
python3 agent_direct.py
