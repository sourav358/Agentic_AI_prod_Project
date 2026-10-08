from langchain_mcp_adapters.client import MultiServerMCPClient 
from My_claude.mcp.My_claude_mcp_config import load_My_claude_mcp_configs 
from My_claude.observability.logger import get_logger 
 
logger = get_logger(__name__) 
 
async def get_My_claude_mcp_tools() -> list: 
  """Connect to all configured MCP servers and return their tools.""" 
  configs = load_My_claude_mcp_configs() 
  logger.info(f"Connecting to MCP servers: {list(configs.keys())}") 
  client = MultiServerMCPClient(configs) 
  tools = await client.get_tools() 
  logger.info(f"Loaded {len(tools)} tools from MCP servers") 
  return tools