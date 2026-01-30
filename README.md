
# Avatar Agrinho — Avatar de Voz em Tempo Real com LiveKit

Este repositório entrega a experiência completa do **Avatar Agrinho**, um **avatar conversacional por voz em tempo real**, capaz de ouvir, interpretar e responder usuários com áudio sintetizado, mantendo estados visuais sincronizados (ouvindo/falando).

O projeto foi construído com foco em:

* **Baixa latência**
* **Experiência natural de conversação**
* **Arquitetura desacoplada**
* **Facilidade de customização de persona**

---

## 🎯 Objetivo do Projeto

Criar uma experiência de **conversa por voz em tempo real** que una:

* Interface visual amigável (avatar animado)
* Processamento de fala e linguagem natural
* Resposta imediata com áudio
* Possibilidade de expansão com **tools externas (MCP)**

O Avatar Agrinho pode ser utilizado em:

* Educação
* Atendimento automatizado
* Demonstrações interativas
* Experiências institucionais ou eventos

---

## 🧠 Decisões Técnicas (e por quê)

### 🎥 Por que LiveKit?

O **LiveKit** foi escolhido como base de comunicação porque:

* Oferece **WebRTC de baixa latência**
* É ideal para **áudio em tempo real**
* Possui SDKs maduros para frontend e backend
* Facilita sincronização de estados entre participantes

Isso é essencial para uma experiência de voz **fluida e natural**, sem delays perceptíveis.

---

### 🖥️ Por que Next.js no frontend?

O frontend foi construído em **Next.js** por:

* Excelente integração com React
* Suporte nativo a APIs (`app/api`)
* Ótima experiência de desenvolvimento
* Facilidade de deploy (Vercel ou similar)

Além disso, o Next.js permite:

* Separar claramente UI, estado do avatar e geração de tokens
* Renderizar animações e vídeos de forma performática

---

### 🐍 Por que um agente Python separado?

O **voice_agent** roda como um processo Python independente porque:

* Facilita o uso de bibliotecas de áudio, VAD e IA
* Permite controle fino do loop de escuta → processamento → resposta
* Evita acoplamento com o frontend
* Torna o backend reutilizável (CLI, worker, serviço)

Essa separação segue o princípio de **responsabilidade única**.

---

### 🧠 Por que OpenAI Realtime API?

A **OpenAI Realtime API** foi utilizada para:

* Processar fala e linguagem natural em tempo real
* Reduzir latência em comparação a chamadas tradicionais
* Permitir respostas contínuas e interrupções

Com isso, o agente consegue:

* Ouvir o usuário enquanto responde
* Interromper a fala se necessário
* Manter uma conversa mais natural

---

### 🧩 Por que suporte a MCP (opcional)?

O suporte a **MCP (Model Context Protocol)** foi incluído para:

* Integrar tools externas sem acoplamento forte
* Permitir expansão do agente (ex: clima, agenda, sistemas internos)
* Tornar o avatar extensível para casos reais de negócio

---

## 🧱 Arquitetura do Projeto

O projeto é composto por **dois módulos independentes**, mas integrados via LiveKit:

* `frontend/`: Interface web e avatar
* `voice_agent/`: Agente de voz e inteligência

```text
.
|-- frontend/              # Next.js + UI do avatar
|-- voice_agent/           # Agente de voz em Python
|-- start-frontend.sh      # Script para subir o frontend
|-- start-backend.sh       # Script para subir o backend
|-- start-agent.sh         # Agente em sala fixa
|-- start-all.sh           # Frontend + agente
`-- README.md
```

### Por que essa organização?

* 📦 Separação clara entre **UI** e **lógica de voz**
* 🔄 Possibilidade de escalar cada parte separadamente
* 🧪 Facilita testes e debug
* 🔧 Permite trocar frontend ou backend sem refatorar tudo

---

## 🧰 Recursos do Projeto

* Conversação por voz em tempo real
* Avatar com estados sincronizados (falando / ouvindo)
* Personas configuráveis via prompt
* VAD local (Silero) quando disponível
* Cancelamento de ruído (BVC)
* Integração opcional com tools via MCP
* Scripts para execução rápida

---

## 🧑‍🎤 Personas do Agente

O comportamento do avatar é controlado pela variável:

```env
ASSISTANT_PROMPT=ASSISTANT
```

Valores disponíveis:

* `ASSISTANT`
* `PROMPT_AGRINHO`
* `VENDEDOR_GENTIL`

📌 Para criar novas personas:

* Edite `voice_agent/prompts.py`
* Defina o tom, vocabulário e comportamento desejado

---

## ⚙️ Configuração de Ambiente (ESSENCIAL)

> ⚠️ As mesmas credenciais do LiveKit devem ser usadas **no frontend e no backend**

### Frontend — `frontend/.env.local`

```dotenv
NEXT_PUBLIC_LIVEKIT_URL=wss://SEU-PROJETO.livekit.cloud
LIVEKIT_API_KEY=APIxxxxxxxx
LIVEKIT_API_SECRET=seu_api_secret_aqui
```

---

### Backend — `voice_agent/.env.local`

```dotenv
LIVEKIT_URL=wss://SEU-PROJETO.livekit.cloud
LIVEKIT_API_KEY=APIxxxxxxxx
LIVEKIT_API_SECRET=seu_api_secret_aqui

OPENAI_API_KEY=sk-...

ASSISTANT_PROMPT=ASSISTANT
VOICE=coral
ALLOW_INTERRUPTIONS=true
GREETING=Ola! Eu ja estou te ouvindo. Como posso ajudar?

LOG_LEVEL=INFO
```

📌 **Por que variáveis de ambiente?**

* Evitam hardcode de segredos
* Facilitam deploy
* Permitem múltiplos ambientes

---

## 📦 Instalação

### Frontend

```bash
cd frontend
npm install
```

### Backend

```bash
cd voice_agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## ▶️ Executar Localmente

### 1️⃣ Agente de voz

```bash
cd voice_agent
source .venv/bin/activate
python3 agent.py start
```

### 2️⃣ Frontend

```bash
cd frontend
npm run dev
```

Acesse:
👉 `http://localhost:3000`
Permita o uso do microfone no navegador.

---

## 🚀 Execução via Scripts

* `./start-frontend.sh`
* `./start-backend.sh`
* `./start-agent.sh`
* `./start-all.sh`

Esses scripts facilitam o uso em ambientes de demonstração e desenvolvimento.

---

## 🎨 Personalização

* **Vídeos do avatar:** `frontend/public/videos/`
* **Voz:** `VOICE=alloy|verse|sage|coral|amber|onyx`
* **Persona:** `ASSISTANT_PROMPT`
* **Tools:** `voice_agent/tools.py`
* **MCP:** variáveis `MCP_*`

---

## 🧪 Troubleshooting

* **401 Invalid response status**
  Verifique se as credenciais do LiveKit são idênticas no frontend e backend.

* **Sem áudio**
  Confirme `OPENAI_API_KEY` e permissão do microfone.

* **Avatar não muda de estado**
  Valide os vídeos e o console do navegador.

---

## 🚢 Deploy (Visão Geral)

* **Frontend:** Vercel ou similar
* **Backend:** servidor Python com HTTPS e WebRTC liberado
* **Requisitos:** firewall liberado para WebRTC

---

## ✅ Checklist Rápido

* [ ] Criar projeto no LiveKit Cloud
* [ ] Configurar `.env.local` no frontend
* [ ] Configurar `.env.local` no backend
* [ ] Instalar dependências
* [ ] Rodar agente e frontend
* [ ] Testar microfone e áudio

---

## 🏁 Conclusão

Este projeto demonstra:

* Uso avançado de WebRTC
* Arquitetura desacoplada frontend/backend
* Integração com IA em tempo real
* Design focado em experiência do usuário
* Código extensível e profissional

É uma base sólida para **produtos conversacionais modernos**, tanto educacionais quanto comerciais.
