# settings.py
import os
import sys
import logging
from dataclasses import dataclass
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env.local
load_dotenv(".env.local")

def setup_logging():
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(
        level=level,
        format="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.info("LOG_LEVEL=%s", level_name)

@dataclass
class Env:
    openai_api_key: str | None
    livekit_api_key: str | None
    livekit_api_secret: str | None
    livekit_url: str | None

    assistant_prompt: str | None
    voice: str | None
    allow_interruptions: bool
    greeting: str | None

    @classmethod
    def load(cls) -> "Env":
        def _bool(name: str, default: bool) -> bool:
            val = os.getenv(name)
            if val is None:
                return default
            return val.strip().lower() in {"1", "true", "yes", "y"}

        return cls(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            livekit_api_key=os.getenv("LIVEKIT_API_KEY"),
            livekit_api_secret=os.getenv("LIVEKIT_API_SECRET"),
            livekit_url=os.getenv("LIVEKIT_URL"),
            assistant_prompt=os.getenv("ASSISTANT_PROMPT", "ASSISTANT"),
            voice=os.getenv("VOICE", "coral"),
            allow_interruptions=_bool("ALLOW_INTERRUPTIONS", True),
            greeting=os.getenv("GREETING", "Olá! Eu já estou te ouvindo. Como posso te ajudar agora?"),
        )

    def validate(self, *, require_openai: bool = True, require_livekit: bool = True) -> None:
        missing: list[str] = []
        if require_openai and not self.openai_api_key:
            missing.append("OPENAI_API_KEY")
        if require_livekit:
            if not self.livekit_api_key:
                missing.append("LIVEKIT_API_KEY")
            if not self.livekit_api_secret:
                missing.append("LIVEKIT_API_SECRET")
            if not self.livekit_url:
                missing.append("LIVEKIT_URL")
        if missing:
            msg = f"Variáveis de ambiente ausentes: {', '.join(missing)}"
            logging.error(msg)
            print(msg)
            sys.exit(1)
