'use client';

import { useEffect, useRef, useState } from 'react';

interface AvatarVideoProps {
  idleVideoSrc?: string;      // Vídeo quando NÃO está falando (ouvindo)
  talkingVideoSrc?: string;   // Vídeo quando está falando
  isAgentSpeaking?: boolean;  // Se o agente está falando
  isUserSpeaking?: boolean;   // Se o usuário está falando
}

export default function AvatarVideo({
  idleVideoSrc = '/videos/agrinho_idle.mp4',
  talkingVideoSrc = '/videos/agrinho_talking.mp4',
  isAgentSpeaking = false,
  isUserSpeaking = false
}: AvatarVideoProps) {
  const idleVideoRef = useRef<HTMLVideoElement>(null);
  const talkingVideoRef = useRef<HTMLVideoElement>(null);
  const pendingVideoRef = useRef<'idle' | 'talking' | null>(null);
  const [idleReady, setIdleReady] = useState(false);
  const [talkingReady, setTalkingReady] = useState(false);
  const [activeVideo, setActiveVideo] = useState<'idle' | 'talking'>('idle');

  const playVideoSafe = (video: HTMLVideoElement | null, label: string) => {
    if (!video) return;
    const playPromise = video.play();
    if (playPromise && typeof playPromise.then === 'function') {
      playPromise.catch(() => {
        console.log(`⚠️ Autoplay bloqueado para vídeo ${label}. Interação necessária.`);
      });
    }
  };

  const switchToVideo = (target: 'idle' | 'talking') => {
    const targetRef = target === 'idle' ? idleVideoRef : talkingVideoRef;
    const otherRef = target === 'idle' ? talkingVideoRef : idleVideoRef;

    if (targetRef.current) {
      targetRef.current.currentTime = 0;
      playVideoSafe(targetRef.current, target);
    }

    if (otherRef.current) {
      otherRef.current.pause();
    }

    setActiveVideo(target);
  };

  useEffect(() => {
    const idleVideo = idleVideoRef.current;
    const talkingVideo = talkingVideoRef.current;

    playVideoSafe(idleVideo, 'idle');
    playVideoSafe(talkingVideo, 'talking');
  }, [idleVideoSrc, talkingVideoSrc]);

  useEffect(() => {
    const targetVideo = isAgentSpeaking ? 'talking' : 'idle';
    const isReady = targetVideo === 'talking' ? talkingReady : idleReady;

    if (isReady) {
      switchToVideo(targetVideo);
      pendingVideoRef.current = null;
    } else {
      pendingVideoRef.current = targetVideo;
      const ref = targetVideo === 'talking' ? talkingVideoRef.current : idleVideoRef.current;
      ref?.load();
    }

    console.log('🎬 Alternando vídeo:', {
      isAgentSpeaking,
      isUserSpeaking,
      videoAtual: targetVideo.toUpperCase(),
      pronto: isReady
    });
  }, [isAgentSpeaking, idleReady, talkingReady, isUserSpeaking]);

  useEffect(() => {
    // Garantir que o vídeo ativo continua tocando (ex.: após retorno do foco)
    if (activeVideo === 'idle') {
      playVideoSafe(idleVideoRef.current, 'idle');
    } else {
      playVideoSafe(talkingVideoRef.current, 'talking');
    }
  }, [activeVideo]);

  const handleIdleLoaded = () => {
    setIdleReady(true);

    if (pendingVideoRef.current === 'idle') {
      switchToVideo('idle');
      pendingVideoRef.current = null;
    }
  };

  const handleTalkingLoaded = () => {
    setTalkingReady(true);

    if (pendingVideoRef.current === 'talking') {
      switchToVideo('talking');
      pendingVideoRef.current = null;
    }
  };

  return (
    <div className="relative w-full h-full bg-gradient-to-br from-green-900 to-green-700 flex items-center justify-center overflow-hidden">
      {/* Vídeos do Avatar */}
      <div className="relative w-full h-full flex items-center justify-center">
        <video
          ref={idleVideoRef}
          src={idleVideoSrc}
          loop
          muted
          playsInline
          preload="auto"
          className={`
            absolute inset-0 w-full h-full object-contain
            scale-100 brightness-100 pointer-events-none
            ${activeVideo === 'idle' ? 'opacity-100 visible z-10' : 'opacity-0 invisible z-0'}
          `}
          onLoadedData={handleIdleLoaded}
          onError={(e) => {
            console.error('❌ Erro ao carregar vídeo idle:', e);
          }}
        />
        <video
          ref={talkingVideoRef}
          src={talkingVideoSrc}
          loop
          muted
          playsInline
          preload="auto"
          className={`
            absolute inset-0 w-full h-full object-contain
            scale-100 brightness-100 pointer-events-none
            ${activeVideo === 'talking' ? 'opacity-100 visible z-10 drop-shadow-2xl' : 'opacity-0 invisible z-0'}
          `}
          onLoadedData={handleTalkingLoaded}
          onError={(e) => {
            console.error('❌ Erro ao carregar vídeo talking:', e);
          }}
        />
      </div>

      {/* Indicador de estado */}
      {(isAgentSpeaking || isUserSpeaking) && (
        <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2">
          <div className={`flex items-center gap-2 px-4 py-2 backdrop-blur-sm rounded-full ${
            isAgentSpeaking ? 'bg-green-500/80' : 'bg-blue-500/80'
          }`}>
            <div className="flex gap-1">
              <div className="w-1 h-4 bg-white rounded-full animate-pulse" style={{ animationDelay: '0ms' }} />
              <div className="w-1 h-6 bg-white rounded-full animate-pulse" style={{ animationDelay: '150ms' }} />
              <div className="w-1 h-4 bg-white rounded-full animate-pulse" style={{ animationDelay: '300ms' }} />
            </div>
            <span className="text-white font-semibold text-sm">
              {isAgentSpeaking ? 'Falando...' : 'Ouvindo...'}
            </span>
          </div>
        </div>
      )}

      {/* Nome do Avatar */}
      <div className="absolute top-8 left-8">
        <div className="px-4 py-2 bg-white/10 backdrop-blur-md rounded-lg border border-white/20">
          <h2 className="text-white font-bold text-xl">🌾 Agrinho</h2>
          <p className="text-green-200 text-sm">Assistente do Campo</p>
        </div>
      </div>
    </div>
  );
}
