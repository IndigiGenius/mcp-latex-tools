#!/usr/bin/env python3
"""Test simple tool registration."""

import asyncio
from mcp.server import Server
from mcp.types import Tool, ListToolsResult

server = Server("test-simple")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List tools."""
    print("handle_list_tools called")
    return [
            Tool(
                name="test_tool",
                description="A test tool",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "message": {"type": "string"}
                    }
                }
            )
        ]

async def main():
    # Check registered handlers
    print(f"Handlers: {list(server.request_handlers.keys())}")
    
    # Get the handler
    from mcp.types import ListToolsRequest
    handler = server.request_handlers.get(ListToolsRequest)
    if handler:
        print("Found handler")
        request = ListToolsRequest(method="tools/list", params={})
        try:
            result = await handler(request)
            print(f"Result: {result}")
            if hasattr(result, 'root') and hasattr(result.root, 'tools'):
                print(f"Tools: {result.root.tools}")
                print(f"Number of tools: {len(result.root.tools)}")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())