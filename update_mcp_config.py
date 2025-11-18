"""Script to update Cursor MCP configuration.

This script helps update your Cursor MCP configuration file to include
the Live Document Editor MCP server.
"""
import json
import os
from pathlib import Path

def get_mcp_config_path():
    """Get the path to Cursor MCP configuration file."""
    if os.name == 'nt':  # Windows
        config_path = Path.home() / '.cursor' / 'mcp.json'
    else:  # macOS/Linux
        config_path = Path.home() / '.cursor' / 'mcp.json'
    return config_path

def update_mcp_config():
    """Update Cursor MCP configuration."""
    config_path = get_mcp_config_path()
    
    # Get current working directory (project root)
    project_root = Path.cwd()
    mcp_server_path = project_root / 'mcp_server.py'
    
    # Convert to absolute path and normalize for Windows
    mcp_server_abs = mcp_server_path.resolve()
    if os.name == 'nt':
        # Windows: use forward slashes or escaped backslashes
        mcp_server_str = str(mcp_server_abs).replace('\\', '/')
    else:
        mcp_server_str = str(mcp_server_abs)
    
    # Read existing config or create new
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
    else:
        config = {"mcpServers": {}}
    
    # Ensure mcpServers exists
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    
    # Add or update live-document-editor server
    config["mcpServers"]["live-document-editor"] = {
        "command": "python",
        "args": [mcp_server_str],
        "env": {}
    }
    
    # Write updated config
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Updated MCP configuration at: {config_path}")
    print(f"   MCP server path: {mcp_server_str}")
    print("\n⚠️  Please restart Cursor for changes to take effect.")

if __name__ == "__main__":
    try:
        update_mcp_config()
    except Exception as e:
        print(f"❌ Error updating MCP configuration: {e}")
        print("\nYou can manually update the configuration:")
        print(f"   File: {get_mcp_config_path()}")
        print("   Add the following to mcpServers:")
        print(f'   "live-document-editor": {{')
        print(f'     "command": "python",')
        print(f'     "args": ["{Path.cwd() / "mcp_server.py"}"]')
        print(f'   }}')

