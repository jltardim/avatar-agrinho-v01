import os
import signal
import sys
import subprocess
import threading
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="Agrinho Voice Agent Backend - Robusto")

_process_lock = threading.Lock()
_agent_proc: subprocess.Popen | None = None

BASE_DIR = Path(__file__).parent.resolve()

# Garante que use o executável Python do ambiente atual (importante no Docker)
PYTHON_EXE = sys.executable or "python"

# Executa o agent_direct.py!
AGENT_SCRIPT = str(BASE_DIR / "agent_direct.py")


def _is_process_alive() -> bool:
    global _agent_proc
    try:
        if _agent_proc is None:
            return False
        return _agent_proc.poll() is None
    except Exception:
        return False


def _start_agent() -> tuple[bool, str, int | None]:
    global _agent_proc
    with _process_lock:
        if _is_process_alive():
            return True, "already_running", _agent_proc.pid if _agent_proc else None
        try:
            print(f"[Server.py Robusto] Tentando iniciar: {PYTHON_EXE} -u {AGENT_SCRIPT}")
            # Inicia em nova sessão/grupo para facilitar encerramento em cascata
            creationflags = 0
            preexec_fn = None
            start_new_session = False
            if os.name == "nt":
                creationflags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
            else:
                # POSIX: criar nova sessão
                start_new_session = True

            _agent_proc = subprocess.Popen(
                [PYTHON_EXE, "-u", AGENT_SCRIPT],
                cwd=str(BASE_DIR),
                stdout=None,
                stderr=None,
                creationflags=creationflags,
                start_new_session=start_new_session,
                preexec_fn=preexec_fn,
            )
            print(f"[Server.py Robusto] Processo iniciado com PID: {_agent_proc.pid}")
            return True, "started", _agent_proc.pid
        except Exception as e:
            print(f"[Server.py Robusto] ERRO ao iniciar processo: {e}")
            _agent_proc = None
            return False, f"error:{e}", None


def _kill_agent() -> tuple[bool, str]:
    global _agent_proc
    with _process_lock:
        if not _is_process_alive() or _agent_proc is None:
            print("[Server.py Robusto] Agente já não estava rodando.")
            _agent_proc = None
            return True, "not_running"
        pid_to_kill = _agent_proc.pid
        print(f"[Server.py Robusto] Tentando encerrar processo com PID: {pid_to_kill}")
        try:
            if os.name == "nt":
                print("[Server.py Robusto] Windows: tentando CTRL_BREAK_EVENT...")
                try:
                    _agent_proc.send_signal(getattr(signal, "CTRL_BREAK_EVENT", signal.SIGTERM))
                except Exception:
                    print("[Server.py Robusto] CTRL_BREAK_EVENT indisponível. Usando terminate().")
                    _agent_proc.terminate()
                try:
                    _agent_proc.wait(timeout=5)
                    print("[Server.py Robusto] Processo encerrou no Windows.")
                except subprocess.TimeoutExpired:
                    print("[Server.py Robusto] Timeout no Windows. Forçando kill().")
                    _agent_proc.kill()
                    _agent_proc.wait(timeout=5)
                    print("[Server.py Robusto] Processo encerrado via kill().")
            else:
                pgid = os.getpgid(pid_to_kill)
                print(f"[Server.py Robusto] Encontrado PGID: {pgid}. Enviando SIGTERM...")
                os.killpg(pgid, signal.SIGTERM)
                try:
                    _agent_proc.wait(timeout=5)
                    print("[Server.py Robusto] Processo encerrou com SIGTERM.")
                except subprocess.TimeoutExpired:
                    print("[Server.py Robusto] Timeout com SIGTERM. Enviando SIGKILL...")
                    os.killpg(pgid, signal.SIGKILL)
                    try:
                        _agent_proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        print("[Server.py Robusto] Ainda vivo após SIGKILL. Chamando kill() direto no processo.")
                        _agent_proc.kill()
                        _agent_proc.wait(timeout=5)
                    print("[Server.py Robusto] Processo encerrou com SIGKILL/kill().")
            _agent_proc = None
            return True, f"killed:{pid_to_kill}"
        except Exception as e:
            print(f"[Server.py Robusto] ERRO ao encerrar processo: {e}")
            try:
                if _agent_proc:
                    _agent_proc.kill()
            except Exception:
                pass
            _agent_proc = None
            return False, f"error:{e}"


# --- Rotas da API ---
@app.post("/start")
async def start() -> JSONResponse:
    print("[Server.py Robusto] Recebida requisição POST /start")
    ok, status, pid = _start_agent()
    return JSONResponse({"ok": ok, "status": status, "pid": pid})


@app.post("/close")
async def close() -> JSONResponse:
    print("[Server.py Robusto] Recebida requisição POST /close")
    ok, status = _kill_agent()
    return JSONResponse({"ok": ok, "status": status})


@app.get("/")
async def root() -> JSONResponse:
    print("[Server.py Robusto] Recebida requisição GET /")
    return JSONResponse({"ok": True, "status": "running"})
