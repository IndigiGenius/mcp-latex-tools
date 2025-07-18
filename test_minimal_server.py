#!/usr/bin/env python3
"""Minimal MCP server to test basic functionality."""

import asyncio
import logging
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent, ListToolsResult, CallToolResult

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create server
server = Server("minimal-test")

@server.list_tools()
async def list_tools() -> ListToolsResult:
    """List available tools."""
    return ListToolsResult(
        tools=[
            Tool(
                name="test_tool",
                description="A simple test tool",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "message": {"type": "string"}
                    },
                    "required": ["message"]
                }
            )
        ]
    )

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> CallToolResult:
    """Handle tool calls."""
    if name == "test_tool":
        message = arguments.get("message", "No message")
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Test tool received: {message}"
                )
            ]
        )
    else:
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Unknown tool: {name}"
                )
            ]
        )

async def main():
    """Run the minimal server."""
    logger.info("Starting minimal MCP server")
    
    try:
        async with stdio_server() as (read_stream, write_stream):
            logger.info("Got stdio streams")
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="minimal-test",
                    server_version="0.1.0",
                ),
            )
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())