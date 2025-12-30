# agent.py - VERSÃO ATUALIZADA
import logging
from livekit import agents, rtc
from livekit.agents import Agent, AgentSession, RoomInputOptions, FunctionTool
from livekit.plugins import openai

try:
    from livekit.plugins import noise_cancellation
except ImportError:
    noise_cancellation = None  # type: ignore[assignment]

from settings import setup_logging, Env
from prompts import get_prompt
import tools as agent_tools
from mcp_bridge import build_livekit_tools_from_mcp
from vad_config import get_vad_for_noisy_environment, VADConfig

class Assistant(Agent):
    def __init__(self, instructions: str, tools: list[FunctionTool] | None = None) -> None:
        super().__init__(instructions=instructions, tools=tools or [])

async def entrypoint(ctx: agents.JobContext):
    try:
        env = Env.load()
        logging.info("🚀 Iniciando agente Agrinho...")
        logging.info("📝 Persona: %s | 🗣️ Voz: %s | 🎙️ Interrupções: %s",
                     env.assistant_prompt, env.voice, env.allow_interruptions)

        # Carrega tools do MCP
        mcp_tools = await build_livekit_tools_from_mcp()
        logging.info("🔧 MCP tools carregadas: %d", len(mcp_tools))

        # Carrega VAD otimizado para ambientes ruidosos
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

        # Cria sessão com VAD local e turn_detection desabilitado no servidor
        session = AgentSession(
            llm=openai.realtime.RealtimeModel(voice=env.voice, turn_detection=None),
            vad=vad_instance,
            allow_interruptions=env.allow_interruptions,
            turn_detection="vad" if vad_instance else "server",
            **vad_config,
        )

        # Configura áudio da sala (ativa BVC quando disponível)
        room_input_kwargs: dict[str, object] = {}
        if noise_cancellation:
            try:
                room_input_kwargs["noise_cancellation"] = noise_cancellation.BVC()
                logging.info("🔇 Noise cancellation (BVC) ativado.")
            except Exception as err:
                logging.warning("⚠️ Falha ao iniciar noise cancellation: %s", err)
        else:
            logging.info("ℹ️ Plugin 'livekit-plugins-noise-cancellation' não encontrado; seguindo sem BVC.")

        logging.info("🎬 Iniciando sessão...")
        await session.start(
            room=ctx.room,
            agent=Assistant(get_prompt(env.assistant_prompt), tools=mcp_tools),
            room_input_options=RoomInputOptions(**room_input_kwargs),
        )

        logging.info("👋 Enviando saudação: %s", env.greeting)
        await session.generate_reply(instructions=env.greeting)
        logging.info("✅ Agente pronto e aguardando interação...")

    except Exception as e:
        logging.exception("❌ Falha no entrypoint: %s", e)

if __name__ == "__main__":
    try:
        setup_logging()
        env = Env.load()
        env.validate(require_openai=True, require_livekit=True)
        logging.info("🎯 Iniciando worker LiveKit...")
        agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
    except SystemExit:
        raise
    except Exception as e:
        logging.exception("❌ Falha ao iniciar o agente: %s", e)
        raise
