#!/usr/bin/env python3
"""Direct test of the MCP server without subprocess."""

import asyncio
import logging
from mcp.server import Server
from mcp.types import (
    ListToolsRequest,
    CallToolRequest,
    Tool,
    ListToolsResult,
    CallToolResult,
    TextContent,
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_direct():
    """Test the server directly."""
    # Import our server
    from mcp_latex_tools.server import server
    
    # Test list_tools
    logger.info("Testing list_tools...")
    
    # Get the handler for ListToolsRequest
    handler = server.request_handlers.get(ListToolsRequest)
    if handler:
        logger.info("Found list_tools handler")
        # The handler expects a request object
        request = ListToolsRequest(method="tools/list", params={})
        result = await handler(request)
        logger.info(f"Result type: {type(result)}")
        logger.info(f"Result: {result}")
        if hasattr(result, 'tools'):
            logger.info(f"Number of tools: {len(result.tools)}")
            for tool in result.tools:
                logger.info(f"Tool: {tool.name} - {tool.description}")
    else:
        logger.error("No handler found for ListToolsRequest")
    
    # Test compile_latex
    logger.info("\nTesting compile_latex...")
    
    # Create a test LaTeX file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False) as tmp:
        tmp.write(r"""
\documentclass{article}
\begin{document}
Hello, World!
\end{document}
""")
        tmp.flush()
        tex_path = tmp.name
    
    # Get the handler for CallToolRequest
    handler = server.request_handlers.get(CallToolRequest)
    if handler:
        logger.info("Found call_tool handler")
        # Create a CallToolRequest
        request = CallToolRequest(
            method="tools/call",
            params={
                "name": "compile_latex",
                "arguments": {
                    "tex_path": tex_path
                }
            }
        )
        result = await handler(request.params.name, request.params.arguments)
        logger.info(f"Result type: {type(result)}")
        logger.info(f"Result: {result}")
    else:
        logger.error("No handler found for CallToolRequest")

if __name__ == "__main__":
    asyncio.run(test_direct())