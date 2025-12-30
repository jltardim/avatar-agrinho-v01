# vad_config.py - Configuração de Voice Activity Detection (VAD)
# Detecta fala do usuário sem ser afetado por barulho de fundo

import logging

async def get_vad_for_noisy_environment():
    """
    Retorna um VAD otimizado para ambientes ruidosos (eventos, multidões).

    Prioriza carregar Silero via plugin (`livekit.plugins.silero`).
    Caso indisponível, tenta fallback e, se não houver VAD, retorna None.
    """
    try:
        from livekit.plugins import silero
    except Exception as import_err:
        logging.warning(f"⚠️ Plugin Silero não disponível: {import_err}")
        # Fallback: tentar agentes.vad.SileroVAD se existir
        try:
            from livekit.agents import vad as agents_vad
            vad_instance = agents_vad.SileroVAD()  # pode não existir em algumas versões
            logging.info("🎤 VAD (Silero) carregado via livekit.agents.vad")
            return vad_instance
        except Exception as e2:
            logging.warning(f"⚠️ Falha ao carregar VAD via agentes: {e2}")
            logging.info("📢 Continuando sem VAD customizado...")
            return None

    try:
        vad_instance = silero.VAD.load(force_cpu=True)
        logging.info("🎤 VAD (Silero) carregado com sucesso (via plugin)")
        return vad_instance
    except Exception as e:
        logging.warning(f"⚠️ Falha ao carregar Silero VAD via plugin: {e}")
        logging.info("📢 Continuando sem VAD customizado...")
        return None


class VADConfig:
    """Configurações de VAD para diferentes ambientes"""

    # Ambiente silencioso (escritório, estúdio)
    QUIET_ENVIRONMENT = {
        "min_endpointing_delay": 0.3,  # Detectar fala mais rapidamente
        "max_endpointing_delay": 2.0,
        "min_interruption_duration": 0.2,
        "min_interruption_words": 1,
    }

    # Ambiente moderado (café, café internet)
    MODERATE_ENVIRONMENT = {
        "min_endpointing_delay": 0.5,
        "max_endpointing_delay": 3.0,
        "min_interruption_duration": 0.5,
        "min_interruption_words": 2,
    }

    # Ambiente ruidoso (evento, festival, multidão)
    NOISY_ENVIRONMENT = {
        "min_endpointing_delay": 0.8,   # Detectar fala rapidamente mas com margem
        "max_endpointing_delay": 5.0,   # Aguardar até 5s para confirmar término
        "min_interruption_duration": 0.5,  # Permitir interrupções mais rápidas
        "min_interruption_words": 2,    # Requer pelo menos 2 palavras
    }

    @staticmethod
    def get_config(environment: str = "noisy") -> dict:
        """
        Retorna configuração de VAD para o ambiente especificado.

        Args:
            environment: "quiet", "moderate", ou "noisy" (padrão)

        Returns:
            Dicionário com configurações VAD
        """
        configs = {
            "quiet": VADConfig.QUIET_ENVIRONMENT,
            "moderate": VADConfig.MODERATE_ENVIRONMENT,
            "noisy": VADConfig.NOISY_ENVIRONMENT,
        }

        config = configs.get(environment.lower(), VADConfig.NOISY_ENVIRONMENT)
        logging.info(f"🎯 VAD configurado para ambiente: {environment.upper()}")
        logging.debug(f"   Configurações: {config}")
        return config


# Exemplo de uso em agent_direct.py:
# from vad_config import get_vad_for_noisy_environment, VADConfig
#
# # Carregar VAD otimizado
# vad_instance = await get_vad_for_noisy_environment()
# vad_config = VADConfig.get_config("noisy")
#
# # Usar na sessão
# session = AgentSession(
#     llm=openai.realtime.RealtimeModel(
#         voice=env.voice,
#         turn_detection=None,  # Desabilitar detecção de turnos no servidor
#     ),
#     vad=vad_instance,
#     turn_detection="vad",  # Usar VAD local
#     **vad_config  # Aplicar configurações customizadas
# )
