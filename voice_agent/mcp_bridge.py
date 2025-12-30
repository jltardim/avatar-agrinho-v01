# mcp_bridge.py (substitua o arquivo por esta versão mais resiliente)
import os
import logging
from typing import Any, Callable
from livekit.agents import FunctionTool, function_tool

# SDK MCP (cliente)
from mcp import ClientSession, types
from mcp.client.streamable_http import streamablehttp_client
from mcp.client.stdio import stdio_client, StdioServerParameters

log = logging.getLogger("mcp-bridge")

class MCPClient:
    def __init__(self, server_url: str | None = None, stdio_cmd: list[str] | None = None, bearer: str | None = None):
        self.server_url = server_url
        self.stdio_cmd = stdio_cmd
        self.bearer = bearer

    async def _open(self):
        if self.stdio_cmd:
            params = StdioServerParameters(command=self.stdio_cmd[0], args=self.stdio_cmd[1:])
            return stdio_client(params)
        if not self.server_url:
            raise RuntimeError("MCP não configurado.")
        auth = {"Authorization": f"Bearer {self.bearer}"} if self.bearer else None
        return streamablehttp_client(self.server_url, headers=auth)

    async def list_tools(self) -> list[types.Tool]:
        async with (await self._open()) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                return tools.tools

    async def call_tool(self, name: str, args: dict[str, Any]) -> str:
        async with (await self._open()) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(name, args)
                texts = []
                for c in result.content:
                    if isinstance(c, types.TextContent):
                        texts.append(c.text)
                    elif isinstance(c, types.JsonContent):
                        texts.append(str(c.json))
                return "\n".join(texts) if texts else "(sem conteúdo)"

def _mk_tool_wrapper(mcp_client: MCPClient, tool_name: str):
    async def _tool(**kwargs) -> str:
        return await mcp_client.call_tool(tool_name, kwargs)
    return _tool

async def build_livekit_tools_from_mcp() -> list[FunctionTool]:
    server_url = os.getenv("MCP_SERVER_URL")
    bearer = os.getenv("MCP_BEARER")
    stdio_raw = os.getenv("MCP_STDIO_CMD")  # ex.: "python my_server.py stdio"
    stdio_cmd = stdio_raw.split(" ") if stdio_raw else None

    # Se nada configurado, não falhe — apenas retorne lista vazia.
    if not server_url and not stdio_cmd:
        log.info("MCP desabilitado (nenhum MCP_SERVER_URL/MCP_STDIO_CMD). Prosseguindo sem MCP.")
        return []

    try:
        mcp = MCPClient(server_url=server_url, stdio_cmd=stdio_cmd, bearer=bearer)
        tools = await mcp.list_tools()
    except Exception as e:
        log.error("Falha ao conectar/listar MCP: %s", e)
        # Siga sem MCP para não derrubar o agente
        return []

    allow = None
    if os.getenv("MCP_ALLOW_TOOLS"):
        allow = {t.strip() for t in os.getenv("MCP_ALLOW_TOOLS").split(",") if t.strip()}

    livekit_tools: list[FunctionTool] = []
    for t in tools:
        name = t.name
        if allow and name not in allow:
            continue
        fn = _mk_tool_wrapper(mcp, name)
        livekit_tools.append(function_tool(fn, name=name, description=t.description or f"MCP tool: {name}"))
        log.info("Registrada MCP tool: %s", name)

    return livekit_tools
