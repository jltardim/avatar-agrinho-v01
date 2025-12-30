'use client';

import { LiveKitRoom, RoomAudioRenderer, useParticipants, useTracks } from '@livekit/components-react';
import '@livekit/components-styles';
import { useEffect, useState } from 'react';
import { Track } from 'livekit-client';
import AvatarVideo from './AvatarVideo';

function RoomContent() {
  const participants = useParticipants();
  const tracks = useTracks([Track.Source.Microphone]);
  const [isAgentSpeaking, setIsAgentSpeaking] = useState(false);
  const [isUserSpeaking, setIsUserSpeaking] = useState(false);

  useEffect(() => {
    // Filtrar apenas participantes "reais" (humanos + agentes)
    // Excluir bots internos do LiveKit
    const realParticipants = participants.filter(p =>
      !p.identity.includes('[bot]') &&
      !p.identity.includes('system')
    );

    console.log('👥 Participantes na sala:', realParticipants.map(p => ({
      identity: p.identity,
      isAgent: p.identity.includes('agent') || p.identity.includes('agrinho'),
      isLocal: p.isLocal
    })));

    // Detectar quando o AGENTE está falando
    const agentParticipant = realParticipants.find(p =>
      p.identity.includes('agent') || p.identity.includes('agrinho')
    );

    if (agentParticipant) {
      console.log('🤖 Agente encontrado:', agentParticipant.identity);

      // Listener para mudanças no estado de fala
      const handleIsSpeakingChanged = (speaking: boolean) => {
        console.log('🔊 Agente falando:', speaking);
        setIsAgentSpeaking(speaking);
      };

      // Adicionar listener para mudanças no estado de fala
      agentParticipant.on('isSpeakingChanged', handleIsSpeakingChanged);

      // Cleanup: remover listener quando componente desmontar ou participante mudar
      return () => {
        agentParticipant.off('isSpeakingChanged', handleIsSpeakingChanged);
      };
    } else {
      console.log('⏳ Aguardando agente entrar na sala...');
      setIsAgentSpeaking(false);
    }
  }, [participants]);

  useEffect(() => {
    // Detectar quando o USUÁRIO está falando (baseado nas tracks de microfone)
    const userIsSpeaking = tracks.length > 0 && tracks.some(track => track.participant.isLocal);
    console.log('🎤 Usuário falando:', userIsSpeaking);
    setIsUserSpeaking(userIsSpeaking);
  }, [tracks]);

  return (
    <div className="w-full h-screen relative">
      {/* Vídeo do Avatar */}
      <AvatarVideo
        idleVideoSrc="/videos/idle.mp4"
        talkingVideoSrc="/videos/agrinho_talking.mp4"
        isAgentSpeaking={isAgentSpeaking}
        isUserSpeaking={isUserSpeaking}
      />
    </div>
  );
}

export default function CustomVideoConference() {
  const [token, setToken] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isConversing, setIsConversing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleToggleConversation = async () => {
    // Log no console do navegador para indicar ação
    console.log(`[Frontend Local] Botão clicado. Tentando ${isConversing ? 'ENCERRAR' : 'INICIAR'} conversa.`);
    setIsLoading(true); // Desabilita o botão e mostra "Processando..."
    // Define qual API Route local chamar baseado no estado atual
    const apiUrl = isConversing ? '/api/agent/stop' : '/api/agent/start';
    const actionVerb = isConversing ? 'encerrar' : 'iniciar';
    try {
      console.log(`[Frontend Local] Chamando API Route local: ${apiUrl}...`);
      // Chama a API Route local (que por sua vez chamará o AGENT_BASE_URL)
      const response = await fetch(apiUrl, { method: 'POST' });
      const data = await response.json(); // Assume resposta JSON
      console.log(`[Frontend Local] Resposta recebida de ${apiUrl}:`, data);
      if (response.ok && data.ok) {
        // Sucesso: API local e backend externo responderam OK.
        // Alterna o estado do botão APÓS a confirmação.
        setIsConversing(!isConversing);
        console.log(`[Frontend Local] Conversa ${actionVerb === 'iniciar' ? 'INICIADA' : 'ENCERRADA'} com sucesso (via backend).`);
      } else {
        // Falha na API local ou no backend externo
        const errorMsg = data?.error || data?.details || 'Erro desconhecido vindo do proxy ou backend.';
        console.error(`[Frontend Local] Falha ao ${actionVerb} backend:`, errorMsg, data);
        alert(`Erro ao ${actionVerb} a conversa: ${errorMsg}`);
      }
    } catch (error) {
      // Falha grave de rede ao chamar a API local
      console.error(`[Frontend Local] Erro de rede ou fetch ao chamar ${apiUrl}:`, error);
      alert(`Erro de conexão ao tentar ${actionVerb} a conversa.`);
    } finally {
      setIsLoading(false); // Reabilita o botão independentemente do resultado
    }
  };

  useEffect(() => {
    async function getToken() {
      try {
        console.log('🔍 Solicitando token...');

        const response = await fetch('/api/token?room=agrinho-demo&username=Usuario');
        const data = await response.json();

        if (data.token) {
          console.log('✅ Token recebido!');
          setToken(data.token);
        } else {
          console.error('❌ Token não recebido:', data);
          setError('Não foi possível obter o token de acesso.');
        }
      } catch (error) {
        console.error('❌ Erro ao buscar token:', error);
        setError('Erro ao conectar com o servidor.');
      } finally {
        setLoading(false);
      }
    }

    getToken();
  }, []);

  // Estado: Carregando
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-screen bg-gradient-to-br from-green-900 to-green-700">
        <div className="text-white text-6xl mb-6 animate-bounce">🌾</div>
        <div className="text-white text-3xl font-bold mb-2">Conectando ao Agrinho...</div>
        <div className="text-green-200 text-lg">Preparando a conversa...</div>
      </div>
    );
  }

  // Estado: Erro
  if (error || !token) {
    return (
      <div className="flex flex-col items-center justify-center h-screen bg-gradient-to-br from-red-900 to-red-700">
        <div className="text-white text-6xl mb-6">❌</div>
        <div className="text-white text-3xl font-bold mb-2">Erro ao conectar!</div>
        <div className="text-red-200 text-lg mb-6">{error || 'Token não disponível'}</div>
        <button
          onClick={() => window.location.reload()}
          className="px-8 py-3 bg-white text-red-700 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
        >
          Tentar novamente
        </button>
      </div>
    );
  }

  const serverUrl = process.env.NEXT_PUBLIC_LIVEKIT_URL || '';

  // Estado: Conectado
  return (
    <LiveKitRoom
      video={false}  // Não usar vídeo do usuário (só áudio)
      audio={true}   // Habilitar áudio do usuário
      token={token}
      serverUrl={serverUrl}
      style={{ height: '100vh', width: '100vw' }}
      onConnected={() => {
        console.log('✅ Conectado ao LiveKit!');
        console.log('🎤 Aguardando Agrinho entrar na sala...');
      }}
      onDisconnected={() => {
        console.log('❌ Desconectado do LiveKit');
      }}
    >
      {/* Conteúdo da sala */}
      <RoomContent />

      {/* Renderizar áudio da sala */}
      <RoomAudioRenderer />

      {/* Botão principal de iniciar/encerrar conversa */}
      <div className="absolute bottom-4 right-4 z-50">
        <button
          onClick={handleToggleConversation}
          disabled={isLoading}
          className={`px-4 py-2 rounded-lg text-white font-semibold 
            ${isConversing ? 'bg-red-600 hover:bg-red-700' : 'bg-green-600 hover:bg-green-700'} 
            ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}
          `}
        >
          {isLoading
            ? 'Processando...'
            : (isConversing ? 'Encerrar Conversa' : 'Iniciar Conversa')
          }
        </button>
      </div>
    </LiveKitRoom>
  );
}
