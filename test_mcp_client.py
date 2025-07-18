#!/usr/bin/env python3
"""Test MCP server using the MCP client."""

import asyncio
import logging
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.types import InitializeRequest, InitializeRequestParams, Implementation, InitializedNotification, ClientCapabilities
import subprocess
import sys
from pathlib import Path

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

async def test_mcp_client():
    """Test the MCP server using the official MCP client."""
    
    print("🔍 Testing MCP Server with Official Client")
    print("=" * 50)
    
    # Start the server process
    server_path = Path(__file__).parent / "src" / "mcp_latex_tools" / "server.py"
    
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(server_path)],
        env=None,
        cwd=None,
        encoding="utf-8",
        encoding_error_handler="strict"
    )
    
    print(f"Starting server: {server_params.command} {' '.join(server_params.args)}")
    
    try:
        # Connect to the server using stdio client
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                
                # Test 1: Initialize the server
                print("\n📋 Test 1: Initialize server")
                init_result = await session.initialize()
                print(f"✅ Server initialized: {init_result.serverInfo.name}")
                
                # Test 2: Send initialized notification
                print("\n📋 Test 2: Send initialized notification")
                await session.send_notification(
                    InitializedNotification(
                        method="notifications/initialized",
                        params=None
                    )
                )
                print("✅ Initialized notification sent")
                
                # Test 3: List tools
                print("\n📋 Test 3: List tools")
                tools_result = await session.list_tools()
                print(f"✅ Found {len(tools_result.tools)} tools:")
                for tool in tools_result.tools:
                    print(f"   • {tool.name}: {tool.description}")
                
                # Test 4: Call a tool
                print("\n📋 Test 4: Call compile_latex tool")
                import tempfile
                
                # Create a test file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False) as tmp:
                    tmp.write(r"""
\documentclass{article}
\begin{document}
Hello, MCP!
\end{document}
""")
                    tmp.flush()
                    test_file = tmp.name
                
                call_result = await session.call_tool(
                    name="compile_latex",
                    arguments={"tex_path": test_file}
                )
                print(f"✅ Tool call result: {call_result.content[0].text[:100]}...")
                
                # Clean up
                Path(test_file).unlink(missing_ok=True)
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mcp_client())