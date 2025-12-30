# Avatar Agrinho - Voz em Tempo Real com LiveKit

Este repositorio entrega a experiencia completa do **Avatar Agrinho** conversando em tempo real com usuarios via **LiveKit**. Ele e composto por dois modulos:

- `frontend/`: app Next.js que renderiza o avatar, controla estados (ouvindo/falando) e conecta ao LiveKit.
- `voice_agent/`: agente Python que escuta, interpreta (OpenAI Realtime) e responde com audio, incluindo suporte opcional a tools e MCP.

## Recursos

- Conversacao por voz em tempo real com resposta sintetizada
- Avatar com estados de fala/escuta sincronizados
- Personas configuraveis via `ASSISTANT_PROMPT`
- VAD local (Silero) e cancelamento de ruido (BVC) quando disponiveis
- Integracao opcional com MCP para tools externas
- Scripts para subir frontend, backend e ambos juntos

## Stack

- **Frontend:** Next.js 15, React 19, LiveKit Components
- **Backend:** LiveKit Agents + OpenAI Realtime API
- **Infra local:** Node 18+, Python 3.10/3.11

## Estrutura do Projeto

```
.
|-- frontend/              # Next.js + UI do avatar
|-- voice_agent/           # Agente de voz em Python
|-- start-frontend.sh      # Sobe o frontend (macOS friendly)
|-- start-backend.sh       # Sobe o backend (modo dev)
|-- start-agent.sh         # Agente em modo direto (sala fixa)
|-- start-all.sh           # Sobe frontend + agente
`-- README.md
```

## Requisitos

- Node.js 18+ (recomendado 20 LTS)
- Python 3.10 ou 3.11
- Conta no LiveKit Cloud
- Chave da OpenAI com acesso ao Realtime API
- Navegador moderno com WebRTC
- Microfone disponivel

## Credenciais LiveKit (passo rapido)

1. Acesse `https://cloud.livekit.io/` e crie uma conta.
2. Crie um projeto no dashboard.
3. Copie **WebSocket URL**, **API Key** e **API Secret**.
4. Use as mesmas credenciais no frontend e no backend.

## Configuracao de ambiente

Crie dois arquivos `.env.local` com as mesmas credenciais do LiveKit.

`frontend/.env.local`

```dotenv
NEXT_PUBLIC_LIVEKIT_URL=wss://SEU-PROJETO.livekit.cloud
LIVEKIT_API_KEY=APIxxxxxxxx
LIVEKIT_API_SECRET=seu_api_secret_aqui
```

`voice_agent/.env.local`

```dotenv
LIVEKIT_URL=wss://SEU-PROJETO.livekit.cloud
LIVEKIT_API_KEY=APIxxxxxxxx
LIVEKIT_API_SECRET=seu_api_secret_aqui

# OpenAI Realtime
OPENAI_API_KEY=sk-...

# Comportamento do agente
ASSISTANT_PROMPT=ASSISTANT
VOICE=coral
ALLOW_INTERRUPTIONS=true
GREETING=Ola! Eu ja estou te ouvindo. Como posso ajudar?

# Logs
LOG_LEVEL=INFO

# MCP (opcional)
# MCP_SERVER_URL=https://seu-mcp-server.com/mcp
# MCP_BEARER=seu_token
# MCP_ALLOW_TOOLS=get_weather,calendar_next
# MCP_STDIO_CMD=python meu_mcp_server.py stdio
```

Valores aceitos em `ASSISTANT_PROMPT` (padrao: `ASSISTANT`):

- `ASSISTANT`
- `PROMPT_AGRINHO`
- `VENDEDOR_GENTIL`

Para criar novas personas, edite `voice_agent/prompts.py`.

## Instalacao

### Frontend

```bash
cd frontend
npm install
```

### Backend

```bash
cd voice_agent
python3 -m venv .venv
source .venv/bin/activate      # macOS / Linux
# .venv\Scripts\activate       # Windows PowerShell
pip install -r requirements.txt
```

## Executar localmente

Em dois terminais:

### 1) Agente de voz

```bash
cd voice_agent
source .venv/bin/activate
python3 agent.py start
```

### 2) Frontend

```bash
cd frontend
npm run dev
```

Abra `http://localhost:3000` e permita o uso do microfone.

### Alternativas por script

- `./start-frontend.sh` (inclui ajustes para Gatekeeper no macOS)
- `./start-backend.sh` (modo dev via `agent.py dev`)
- `./start-agent.sh` (modo direto via `agent_direct.py`, sala fixa `agrinho-demo`)
- `./start-all.sh` (frontend + agente)

## Personalizacao

- **Videos do avatar:** substitua arquivos em `frontend/public/videos/` mantendo a resolucao.
- **Voz do agente:** `VOICE=alloy|verse|sage|coral|amber|onyx`.
- **Persona:** ajuste `ASSISTANT_PROMPT` e edite `voice_agent/prompts.py`.
- **Tools:** adicione funcoes em `voice_agent/tools.py`.
- **MCP:** configure as variaveis `MCP_*` para registrar tools externas.

## Troubleshooting

- **401 Invalid response status**
  Confirme se URL/API Key/API Secret sao identicos no frontend e no backend.

- **Sem audio / avatar parado**
  Verifique `OPENAI_API_KEY` e se o navegador liberou o microfone.

- **Erro com interrupcoes**
  Se `ALLOW_INTERRUPTIONS=false`, o VAD local precisa estar disponivel; reinstale deps do backend.

- **Avatar nao muda de estado**
  Verifique os videos em `frontend/public/videos/` e o console do navegador.

## Deploy (visao geral)

- **Frontend:** Vercel ou similar.
- **Backend:** servidor Python com acesso a WebRTC e variaveis de ambiente seguras.
- Garanta HTTPS e firewall liberado para WebRTC.

## Checklist rapido

- [ ] Criar projeto no LiveKit Cloud
- [ ] Preencher `frontend/.env.local` e `voice_agent/.env.local`
- [ ] `npm install` em `frontend/`
- [ ] `pip install -r requirements.txt` em `voice_agent/`
- [ ] Rodar `python3 agent.py start` e `npm run dev`
- [ ] Acessar `http://localhost:3000`
