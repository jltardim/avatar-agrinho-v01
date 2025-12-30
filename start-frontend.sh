#!/bin/bash
# Script para iniciar o frontend do Agrinho

echo "🌐 Iniciando Frontend Agrinho..."
echo ""

# Navegar para a pasta do frontend
cd "$(dirname "$0")/frontend"

# Liberar binários nativos do Gatekeeper para evitar falhas de carregamento
if command -v xattr >/dev/null 2>&1; then
    for binary in \
        "node_modules/@next/swc-darwin-arm64/next-swc.darwin-arm64.node" \
        "node_modules/lightningcss-darwin-arm64/lightningcss.darwin-arm64.node" \
        "node_modules/@tailwindcss/oxide-darwin-arm64/tailwindcss-oxide.darwin-arm64.node"; do
        if [ -f "$binary" ]; then
            xattr -dr com.apple.quarantine "$binary" >/dev/null 2>&1
        fi
    done
fi

# Garante que o pacote base do lightningcss tenha o binário ARM64 disponível
if [ -f "node_modules/lightningcss-darwin-arm64/lightningcss.darwin-arm64.node" ] \
   && [ ! -f "node_modules/lightningcss/lightningcss.darwin-arm64.node" ]; then
    cp "node_modules/lightningcss-darwin-arm64/lightningcss.darwin-arm64.node" \
       "node_modules/lightningcss/lightningcss.darwin-arm64.node"
fi

# Verificar se .env.local existe
if [ ! -f ".env.local" ]; then
    echo "❌ Erro: Arquivo .env.local não encontrado!"
    echo "Por favor, configure suas credenciais em frontend/.env.local"
    exit 1
fi

# Iniciar servidor Next.js
echo "🎬 Iniciando servidor de desenvolvimento..."
echo ""
npm run dev
