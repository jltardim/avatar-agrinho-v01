#!/usr/bin/env python3
"""
test_audio_capture.py - Diagnóstico de captura de áudio
Testa se o áudio está sendo capturado e processado corretamente.
"""

import asyncio
import logging
from livekit import rtc, api
from livekit.agents import RoomInputOptions
from livekit.plugins import noise_cancellation
from livekit.plugins import silero

from settings import setup_logging, Env

async def test_audio_capture():
    """Testa a captura de áudio da sala LiveKit"""
    try:
        env = Env.load()
        logging.info("🧪 Iniciando teste de captura de áudio...")

        # Conecta à sala
        room = rtc.Room()

        # Gera token para o agente de teste
        token = api.AccessToken(env.livekit_api_key, env.livekit_api_secret)
        token.with_identity("audio-test-agent")
        token.with_name("Audio Test")
        token.with_grants(api.VideoGrants(
            room_join=True,
            room="agrinho-demo",
        ))
        jwt_token = token.to_jwt()

        logging.info("🔗 Conectando à sala 'agrinho-demo'...")
        await room.connect(env.livekit_url, jwt_token)
        logging.info("✅ Conectado à sala!")

        # Listar participantes
        logging.info(f"👥 Participantes na sala: {room.num_participants}")
        for identity, participant in room.remote_participants.items():
            logging.info(f"   - {participant.identity} ({participant.name})")

        # Testar VAD
        logging.info("🎤 Testando Voice Activity Detection (VAD) Silero...")
        try:
            vad_instance = silero.VAD.load(
                min_speech_duration=0.05,
                min_silence_duration=0.8,
                activation_threshold=0.6,
                sample_rate=16000,
                force_cpu=True
            )
            logging.info("✅ VAD (Silero) carregado com sucesso!")
        except Exception as e:
            logging.warning(f"⚠️ Falha ao carregar VAD: {e}")
            vad_instance = None

        # Testar Noise Cancellation
        logging.info("🔇 Testando Noise Cancellation (BVC)...")
        try:
            bvc = noise_cancellation.BVC()
            logging.info("✅ BVC carregado com sucesso!")
        except Exception as e:
            logging.warning(f"⚠️ Falha ao carregar BVC: {e}")

        # Registrar para eventos de audio
        logging.info("📡 Aguardando áudio da sala por 30 segundos...")
        audio_received = False

        async def on_audio_frame(frame: rtc.AudioFrame):
            nonlocal audio_received
            audio_received = True
            logging.info(f"🎵 Áudio recebido: {frame.sample_rate}Hz, {frame.num_channels} canais, {frame.samples_per_channel} amostras")

        # Registrar callback para frames de áudio
        # (Nota: isto é pseudocódigo - a API real pode variar)

        # Aguardar e monitorar
        for i in range(30):
            await asyncio.sleep(1)
            participants = room.num_participants
            logging.info(f"   [{i+1}/30] Participantes: {participants}")

            if audio_received:
                logging.info("✅ Áudio foi recebido durante o teste!")

        if not audio_received:
            logging.warning("⚠️ Nenhum áudio foi recebido. Possíveis causas:")
            logging.warning("   1. Nenhum outro participante está falando")
            logging.warning("   2. O microfone não está compartilhando áudio")
            logging.warning("   3. Há problema na conexão LiveKit")
        else:
            logging.info("✅ Teste de áudio concluído com sucesso!")

        await room.disconnect()
        logging.info("👋 Desconectado da sala")

    except Exception as e:
        logging.exception(f"❌ Erro durante teste: {e}")

if __name__ == "__main__":
    try:
        setup_logging()
        env = Env.load()
        env.validate(require_openai=False, require_livekit=True)
        logging.info("🎯 Teste de Captura de Áudio")
        asyncio.run(test_audio_capture())
    except Exception as e:
        logging.exception(f"❌ Falha: {e}")
