import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const baseUrl = process.env.AGRINHO_V3_BACKEND_URL;
    if (!baseUrl) {
      return NextResponse.json(
        { error: 'AGRINHO_V3_BACKEND_URL não configurada no ambiente do Vercel/Next.js' },
        { status: 500 }
      );
    }

    const targetUrl = new URL('/start', baseUrl).toString();

    let body: string | undefined = undefined;
    try {
      const raw = await request.text();
      body = raw && raw.trim().length > 0 ? raw : undefined;
    } catch {}

    const resp = await fetch(targetUrl, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body,
      // Timeout de 15s para evitar travas
      signal: AbortSignal.timeout(15000),
    });

    const contentType = resp.headers.get('content-type') || '';
    let payload: any;
    if (contentType.includes('application/json')) {
      payload = await resp.json();
    } else {
      payload = await resp.text();
    }

    if (!resp.ok) {
      return NextResponse.json(
        { error: 'Falha ao iniciar backend (verifique AGRINHO_V3_BACKEND_URL)', status: resp.status, data: payload },
        { status: 502 }
      );
    }

    return NextResponse.json({ ok: true, data: payload });
  } catch (error: any) {
    return NextResponse.json(
      { error: error?.message || 'Erro ao acionar backend via proxy' },
      { status: 500 }
    );
  }
}

// Suporte a GET para teste rápido via navegador
export async function GET(request: NextRequest) {
  return POST(request);
}