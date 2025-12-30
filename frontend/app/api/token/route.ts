import { AccessToken } from 'livekit-server-sdk';
import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const room = request.nextUrl.searchParams.get('room') || 'agrinho-demo';
    const username = request.nextUrl.searchParams.get('username') || 'Usuario';

    if (!process.env.LIVEKIT_API_KEY || !process.env.LIVEKIT_API_SECRET) {
      throw new Error('❌ Credenciais do LiveKit não configuradas!');
    }

    console.log('🔑 Gerando token para:', { room, username });

    const at = new AccessToken(
      process.env.LIVEKIT_API_KEY,
      process.env.LIVEKIT_API_SECRET,
      {
        identity: username,
        ttl: '10h',
      }
    );

    at.addGrant({
      room,
      roomJoin: true,
      canPublish: true,
      canPublishData: true,
      canSubscribe: true,
    });

    const token = await at.toJwt();

    console.log('✅ Token gerado com sucesso!');

    return NextResponse.json({
      token,
      url: process.env.NEXT_PUBLIC_LIVEKIT_URL
    });

  } catch (error) {
    console.error('❌ Erro ao gerar token:', error);
    return NextResponse.json(
      { error: 'Falha ao gerar token' },
      { status: 500 }
    );
  }
}
