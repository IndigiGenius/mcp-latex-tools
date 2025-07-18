#!/usr/bin/env python3
"""Test script to interact with the MCP LaTeX Tools server."""

import asyncio
import json
import subprocess
import sys
from pathlib import Path
import tempfile

async def test_mcp_server():
    """Test the MCP server functionality."""
    print("🚀 Testing MCP LaTeX Tools Server")
    print("=" * 50)
    
    # Start the MCP server process
    server_path = Path(__file__).parent / "src" / "mcp_latex_tools" / "server.py"
    cmd = [sys.executable, str(server_path)]
    
    print(f"Starting server: {' '.join(cmd)}")
    
    try:
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0
        )
        
        # Test 1: Initialize the server
        print("\n📋 Test 1: Server Initialization")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }
        
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # Read response
        response_line = process.stdout.readline()
        if response_line:
            try:
                response = json.loads(response_line.strip())
                print(f"✅ Server initialized: {response.get('result', {}).get('serverInfo', {}).get('name', 'Unknown')}")
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON response: {response_line}")
        else:
            print("❌ No response from server")
        
        # Test 2: List available tools
        print("\n🔧 Test 2: List Available Tools")
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        process.stdin.write(json.dumps(tools_request) + "\n")
        process.stdin.flush()
        
        response_line = process.stdout.readline()
        if response_line:
            try:
                response = json.loads(response_line.strip())
                tools = response.get('result', {}).get('tools', [])
                print(f"✅ Found {len(tools)} tools:")
                for tool in tools:
                    print(f"   • {tool.get('name')}: {tool.get('description', 'No description')}")
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON response: {response_line}")
        
        # Test 3: Create a simple LaTeX file and test compilation
        print("\n📝 Test 3: LaTeX Compilation")
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False) as tmp:
            tmp.write(r"""
\documentclass{article}
\usepackage[utf8]{inputenc}
\title{Test Document}
\author{MCP LaTeX Tools}
\date{\today}

\begin{document}
\maketitle

\section{Introduction}
This is a test document compiled by the MCP LaTeX Tools server.

\subsection{Features}
\begin{itemize}
    \item LaTeX compilation
    \item PDF generation
    \item Error handling
\end{itemize}

\end{document}
""")
            tmp.flush()
            
            compile_request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "compile_latex",
                    "arguments": {
                        "tex_path": tmp.name,
                        "timeout": 30
                    }
                }
            }
            
            process.stdin.write(json.dumps(compile_request) + "\n")
            process.stdin.flush()
            
            response_line = process.stdout.readline()
            if response_line:
                try:
                    response = json.loads(response_line.strip())
                    result = response.get('result', {})
                    content = result.get('content', [])
                    if content:
                        output_text = content[0].get('text', '')
                        if '✓' in output_text:
                            print("✅ LaTeX compilation successful!")
                            if 'Output: ' in output_text:
                                output_path = output_text.split('Output: ')[1].split('\n')[0]
                                print(f"   Output: {output_path}")
                            else:
                                print("   Output: Generated")
                        else:
                            print(f"❌ LaTeX compilation failed: {output_text}")
                    else:
                        print("❌ No content in response")
                except json.JSONDecodeError:
                    print(f"❌ Invalid JSON response: {response_line}")
            
            # Cleanup
            Path(tmp.name).unlink(missing_ok=True)
        
        print("\n🎉 MCP Server Test Complete!")
        
    except Exception as e:
        print(f"❌ Error testing server: {e}")
    finally:
        # Clean up process
        if process:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

if __name__ == "__main__":
    asyncio.run(test_mcp_server())