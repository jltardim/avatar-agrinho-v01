#!/bin/bash
# Script para iniciar o backend do Agrinho

echo "🚀 Iniciando Backend Agrinho..."
echo ""

# Navegar para a pasta do backend
cd "$(dirname "$0")/voice_agent"

# Verificar se .env.local existe
if [ ! -f ".env.local" ]; then
    echo "❌ Erro: Arquivo .env.local não encontrado!"
    echo "Por favor, configure suas credenciais em voice_agent/.env.local"
    exit 1
fi

# Verificar se OPENAI_API_KEY está configurada
if grep -q "sua_chave_openai_aqui" .env.local; then
    echo "⚠️  ATENÇÃO: Você precisa configurar sua chave OpenAI!"
    echo ""
    echo "Edite o arquivo: voice_agent/.env.local"
    echo "Substitua 'sua_chave_openai_aqui' pela sua chave real da OpenAI"
    echo ""
    exit 1
fi

# Ativar ambiente virtual
echo "📦 Ativando ambiente virtual..."
source .venv/bin/activate

# Iniciar o agente
echo "🎙️  Iniciando agente de voz..."
echo ""
python3 agent.py dev
