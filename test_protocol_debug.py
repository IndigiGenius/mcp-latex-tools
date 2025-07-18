#!/usr/bin/env python3
"""Debug MCP protocol interaction."""

import asyncio
import json
import subprocess
import sys
from pathlib import Path
import time

async def test_protocol():
    """Test protocol interaction with debug output."""
    print("🚀 Testing MCP Protocol Interaction")
    print("=" * 50)
    
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
        
        # Give server time to start
        time.sleep(0.5)
        
        # Test direct tools/list without initialization
        print("\n📋 Test 1: Direct tools/list (no init)")
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        
        print(f"Sending: {json.dumps(request)}")
        process.stdin.write(json.dumps(request) + "\n")
        process.stdin.flush()
        
        # Read response with timeout
        response_line = process.stdout.readline()
        if response_line:
            print(f"Response: {response_line.strip()}")
        else:
            print("No response")
        
        # Test initialization first
        print("\n📋 Test 2: Initialize then tools/list")
        init_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }
        
        print(f"Sending init: {json.dumps(init_request)}")
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        response_line = process.stdout.readline()
        if response_line:
            print(f"Init response: {response_line.strip()}")
            
            # Now try tools/list with proper params
            tools_request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/list",
                "params": {"cursor": None}
            }
            
            print(f"\nSending tools/list: {json.dumps(tools_request)}")
            process.stdin.write(json.dumps(tools_request) + "\n")
            process.stdin.flush()
            
            response_line = process.stdout.readline()
            if response_line:
                print(f"Tools response: {response_line.strip()}")
                response = json.loads(response_line)
                if 'result' in response and 'tools' in response['result']:
                    print(f"Found {len(response['result']['tools'])} tools")
        
        # Don't block on stderr read
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if process:
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()

if __name__ == "__main__":
    asyncio.run(test_protocol())