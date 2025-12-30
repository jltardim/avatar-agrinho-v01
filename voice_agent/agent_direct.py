# agent_direct.py - Conecta DIRETAMENTE à sala sem esperar dispatch
import asyncio
import logging
from livekit import agents, rtc
from livekit.agents import Agent, AgentSession, RoomInputOptions, FunctionTool
from livekit.plugins import openai, noise_cancellation

from settings import setup_logging, Env
from prompts import get_prompt
import tools as agent_tools
from mcp_bridge import build_livekit_tools_from_mcp
from vad_config import get_vad_for_noisy_environment, VADConfig

class Assistant(Agent):
    def __init__(self, instructions: str, tools: list[FunctionTool] | None = None) -> None:
        super().__init__(instructions=instructions, tools=tools or [])

async def run_agent():
    """Conecta o agente diretamente à sala 'agrinho-demo'"""
    try:
        env = Env.load()
        logging.info("🚀 Iniciando agente Agrinho (MODO DIRETO)...")

        # Carrega tools do MCP
        mcp_tools = await build_livekit_tools_from_mcp()
        logging.info("🔧 MCP tools carregadas: %d", len(mcp_tools))

        # Conecta à sala usando RTC
        room = rtc.Room()

        # Gera token para o agente
        from livekit import api
        token = api.AccessToken(env.livekit_api_key, env.livekit_api_secret)
        token.with_identity("agrinho-agent")
        token.with_name("Agrinho")
        token.with_grants(api.VideoGrants(
            room_join=True,
            room="agrinho-demo",
        ))
        jwt_token = token.to_jwt()

        logging.info("🔗 Conectando à sala 'agrinho-demo'...")
        await room.connect(env.livekit_url, jwt_token)
        logging.info("✅ Conectado à sala!")

        # Carregar VAD otimizado para ambientes ruidosos
        logging.info("🎤 Carregando VAD (Voice Activity Detection) para detecção robusta de fala...")
        vad_instance = await get_vad_for_noisy_environment()
        if vad_instance:
            logging.info("✅ VAD carregado com sucesso - pronto para detectar fala em ambiente ruidoso")
        else:
            logging.warning("⚠️ VAD não foi carregado - usando configuração padrão do OpenAI")

        vad_config = VADConfig.get_config("noisy")

        # Se ALLOW_INTERRUPTIONS=false e não há VAD local, falhar explicitamente
        if not env.allow_interruptions and not vad_instance:
            raise RuntimeError(
                "ALLOW_INTERRUPTIONS=false requer VAD local; Silero VAD não disponível"
            )

        # Cria sessão do agente com VAD local e desabilita turn detection no servidor
        session = AgentSession(
            llm=openai.realtime.RealtimeModel(
                voice=env.voice,
                turn_detection=None,  # Desabilitar detecção de turnos no servidor
            ),
            vad=vad_instance,                    # Usar VAD local (Silero)
            allow_interruptions=env.allow_interruptions,  # Respeitar configuração
            turn_detection="vad" if vad_instance else "server",  # Preferir VAD local
            **vad_config                         # Aplicar configurações customizadas para ambiente ruidoso
        )

        logging.info("🎬 Iniciando sessão do agente...")
        await session.start(
            room=room,
            agent=Assistant(get_prompt(env.assistant_prompt), tools=mcp_tools),
            room_input_options=RoomInputOptions(
                noise_cancellation=noise_cancellation.BVC(),  # Cancelamento de ruído BVC
                close_on_disconnect=False,                    # Não fechar quando participante desconectar
            ),
        )

        logging.info("👋 Enviando saudação: %s", env.greeting)
        await session.generate_reply(instructions=env.greeting)
        logging.info("✅ Agente pronto e aguardando interação em ambiente ruidoso!")
        logging.info("📢 Configurações ativas:")
        logging.info("   - Cancelamento de ruído (BVC): Ativado")
        logging.info("   - VAD (Silero) para detecção robusta: %s", "Ativado" if vad_instance else "Desativado")
        if vad_instance:
            logging.info("   - Threshold de ativação: 0.6 (robusto contra ruído)")
            logging.info("   - Duração mínima de silêncio: 0.8s (aguarda confirmação)")
        logging.info("   - Ambiente: RUIDOSO")

        # Mantém o agente rodando
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        logging.info("⚠️  Interrompido pelo usuário")
    except Exception as e:
        logging.exception("❌ Falha ao executar agente: %s", e)
        raise

if __name__ == "__main__":
    try:
        setup_logging()
        env = Env.load()
        env.validate(require_openai=True, require_livekit=True)
        logging.info("🎯 Modo DIRETO - Conectando à sala...")
        asyncio.run(run_agent())
    except SystemExit:
        raise
    except KeyboardInterrupt:
        logging.info("👋 Encerrando...")
    except Exception as e:
        logging.exception("❌ Falha fatal: %s", e)
        raise
