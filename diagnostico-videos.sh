#!/bin/bash

echo "🔍 DIAGNÓSTICO - Sistema de Vídeos do Avatar"
echo "=============================================="
echo ""

echo "1️⃣ Verificando vídeos na pasta public/videos/:"
echo "-----------------------------------------------"
ls -lh frontend/public/videos/
echo ""

echo "2️⃣ Verificando se vídeos são válidos (podem ser reproduzidos):"
echo "---------------------------------------------------------------"
if command -v ffprobe &> /dev/null; then
    echo "📹 idle.mp4:"
    ffprobe -v error -show_entries format=duration,size,bit_rate -show_entries stream=codec_name,width,height frontend/public/videos/idle.mp4 2>&1 | grep -E "(codec_name|width|height|duration)"
    echo ""
    echo "📹 agrinho_talking.mp4:"
    ffprobe -v error -show_entries format=duration,size,bit_rate -show_entries stream=codec_name,width,height frontend/public/videos/agrinho_talking.mp4 2>&1 | grep -E "(codec_name|width|height|duration)"
else
    echo "⚠️  ffprobe não encontrado. Pulando validação de vídeo."
fi
echo ""

echo "3️⃣ Verificando se o agente está rodando:"
echo "-----------------------------------------"
if pgrep -f "agent.py" > /dev/null; then
    echo "✅ Processo do agente encontrado:"
    ps aux | grep "agent.py" | grep -v grep
else
    echo "❌ Nenhum processo do agente encontrado!"
    echo "   Execute: cd voice_agent && source .venv/bin/activate && python agent.py dev"
fi
echo ""

echo "4️⃣ Verificando servidor frontend:"
echo "----------------------------------"
if pgrep -f "next" > /dev/null; then
    echo "✅ Next.js rodando"
    lsof -i :3000 2>/dev/null || echo "   Porta 3000 não está aberta"
else
    echo "❌ Next.js não está rodando!"
    echo "   Execute: cd frontend && npm run dev"
fi
echo ""

echo "📋 INSTRUÇÕES PARA TESTAR:"
echo "=========================="
echo "1. Abra o navegador em http://localhost:3000"
echo "2. Abra o Console do Navegador (F12 → Console)"
echo "3. Procure por estas mensagens:"
echo "   - '👥 Participantes na sala:' → Ver se agente entrou"
echo "   - '🤖 Agente encontrado:' → Confirmar detecção do agente"
echo "   - '🔊 Agente falando:' → Ver se detecta quando agente fala"
echo "   - '🎬 Alternando vídeo:' → Ver se troca de vídeo"
echo ""
echo "4. Fale algo e veja se aparece:"
echo "   - '🎤 Usuário falando: true'"
echo ""
echo "Se NÃO aparecer '🤖 Agente encontrado:', o problema é que"
echo "o agente não está entrando na sala!"
