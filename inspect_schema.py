#!/usr/bin/env python3
"""
Diagnostic script to inspect MCP tool schemas
Run this inside the Docker container to see what schemas are being generated
"""

import json
import sys
from fastmcp import FastMCP
from pydantic import Field
from typing import Annotated, Any

# Create a test MCP server with the problematic parameter types
mcp = FastMCP("Test")

@mcp.tool
def test_tool(
    object_id: float,
    limit: Annotated[float, Field(default=5.0, ge=1.0, le=100.0)] = 5.0,
    offset: Annotated[float, Field(default=0.0, ge=0.0)] = 0.0,
    filters: dict[str, Any] = {},
    fields: list[str] | None = None,
):
    """Test tool to inspect schema generation"""
    pass

# Try to get the tool schema
try:
    # FastMCP should have a way to get tool definitions
    if hasattr(mcp, '_tools'):
        print("=== Available Tools ===")
        for tool_name, tool_info in mcp._tools.items():
            print(f"\nTool: {tool_name}")
            if hasattr(tool_info, 'fn'):
                import inspect
                sig = inspect.signature(tool_info.fn)
                print(f"Signature: {sig}")

                # Try to get the JSON schema
                if hasattr(tool_info, 'input_schema'):
                    print(f"\nInput Schema:")
                    print(json.dumps(tool_info.input_schema, indent=2))

    # Try alternative method
    print("\n=== Checking FastMCP internals ===")
    print(f"FastMCP attributes: {dir(mcp)}")

except Exception as e:
    print(f"Error inspecting schema: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
