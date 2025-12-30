import { NextRequest, NextResponse } from 'next/server';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic'; // Garante que não use cache

// Função helper para encaminhar a resposta (JSON ou texto)
async function forwardResponse(url: string, init: RequestInit) {
  console.log(`[Vercel Proxy] Tentando chamar: ${init.method} ${url}`);
  const res = await fetch(url, init);
  console.log(`[Vercel Proxy] Resposta recebida de ${url}: Status ${res.status}`);
  const contentType = res.headers.get('content-type') || '';
  const status = res.status;

  if (contentType.includes('application/json')) {
    const json = await res.json();
    return NextResponse.json(json, { status });
  } else {
    const text = await res.text();
    return new NextResponse(text, {
      status,
      headers: { 'content-type': contentType || 'text/plain' },
    });
  }
}

export async function POST(_req: Request) {
  console.log('\n--- [Vercel Proxy] Chamada recebida: /api/agent/stop ---'); // Log atualizado
  const base = process.env.AGRINHO_V3_BACKEND_URL;

  if (!base) {
    console.error('[Vercel Proxy] ERRO: AGRINHO_V3_BACKEND_URL não configurada!');
    return NextResponse.json(
      { ok: false, error: 'Configuração do servidor proxy incompleta (AGRINHO_V3_BACKEND_URL ausente)' },
      { status: 500 }
    );
  }

  // Usa o novo caminho /close
  const targetUrl = new URL('/close', base).toString();
  console.log(`[Vercel Proxy] Encaminhando chamada para ${targetUrl}`);

  try {
    return await forwardResponse(targetUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      signal: AbortSignal.timeout(15000), // Adiciona timeout
      // A chamada /stop geralmente não precisa de corpo
    });
  } catch (err: any) {
    console.error(`[Vercel Proxy] Falha ao contatar ${targetUrl}:`, err);
    return NextResponse.json(
      {
        ok: false,
        error: 'Proxy falhou ao se comunicar com o servidor do agente (verifique AGRINHO_V3_BACKEND_URL)',
        details: String(err?.message || err),
      },
      { status: 502 } // Bad Gateway
    );
  }
}

// Suporte a GET para teste rápido via navegador
export async function GET(request: NextRequest) {
  return POST(request as unknown as Request);
}