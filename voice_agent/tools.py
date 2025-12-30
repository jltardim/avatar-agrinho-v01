# tools.py
# Exemplo de tools (funções) que o LLM pode chamar via function-calling.

from datetime import datetime
from livekit.agents import function_tool

@function_tool
def get_weather(city: str, unit: str = "C") -> str:
    """
    Retorna um "clima" fictício só para demonstração.
    """
    fake_temp_c = 26
    if unit.upper() == "F":
        temp = round(fake_temp_c * 9/5 + 32)
        return f"Em {city}, agora está {temp}°F, céu parcialmente nublado."
    else:
        return f"Em {city}, agora está {fake_temp_c}°C, céu parcialmente nublado."

@function_tool
def get_time(timezone: str | None = None) -> str:
    """Retorna o horário atual (simples, sem fuso)."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"Horário local aproximado: {now}"
