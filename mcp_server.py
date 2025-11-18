"""Standalone MCP Server for Live Document Editor.

This server exposes the documentation generation functionality as MCP tools
that can be used directly in Cursor.
"""
import asyncio
import sys
from typing import Any, Sequence, Optional
import json

# MCP servers must ONLY output JSON-RPC messages to stdout
# All error messages must go to stderr to avoid breaking the protocol
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError as e:
    # Write to stderr, not stdout
    sys.stderr.write(f"Error: MCP SDK not installed. Run: pip install mcp\n")
    sys.stderr.write(f"Details: {e}\n")
    sys.stderr.flush()
    sys.exit(1)

# Initialize components with error handling
orchestrator: Optional[Any] = None
git_handler: Optional[Any] = None

try:
    from src.orchestrator import MCPOrchestrator
    from src.git_handler import GitHandler
    from src.config import config
    
    orchestrator = MCPOrchestrator()
    git_handler = GitHandler(config.git_repo_path)
except Exception as e:
    sys.stderr.write(f"Warning: Error initializing components: {e}\n")
    sys.stderr.write("MCP server will start but some features may not work.\n")
    sys.stderr.flush()
    # Continue - server can still provide basic functionality

# Create MCP server
server = Server("live-document-editor")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="process_code_changes",
            description="Process Git code changes and generate documentation. Automatically analyzes code diffs, generates documentation using AI, evaluates quality, and provides the result.",
            inputSchema={
                "type": "object",
                "properties": {
                    "diff_content": {
                        "type": "string",
                        "description": "Git diff content to process. If empty, will fetch from current repository."
                    },
                    "repo_path": {
                        "type": "string",
                        "description": "Path to the repository (default: current directory)",
                        "default": "."
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_git_diff",
            description="Get Git diff for the current repository. Returns uncommitted changes or diff against a branch.",
            inputSchema={
                "type": "object",
                "properties": {
                    "branch": {
                        "type": "string",
                        "description": "Branch to compare against (default: main)",
                        "default": "main"
                    },
                    "uncommitted_only": {
                        "type": "boolean",
                        "description": "If true, only return uncommitted changes",
                        "default": False
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="update_documentation",
            description="Update or create a documentation file with the provided content.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the documentation file (e.g., DOCUMENTATION.md)"
                    },
                    "content": {
                        "type": "string",
                        "description": "Documentation content in Markdown format"
                    },
                    "commit_message": {
                        "type": "string",
                        "description": "Git commit message (default: 'docs: Update documentation')",
                        "default": "docs: Update documentation"
                    }
                },
                "required": ["file_path", "content"]
            }
        ),
        Tool(
            name="commit_documentation",
            description="Commit documentation changes to Git repository.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the documentation file"
                    },
                    "content": {
                        "type": "string",
                        "description": "Documentation content to commit"
                    },
                    "commit_message": {
                        "type": "string",
                        "description": "Git commit message",
                        "default": "docs: Update documentation"
                    }
                },
                "required": ["file_path", "content"]
            }
        ),
        Tool(
            name="get_recent_commits",
            description="Get recent Git commits from the repository.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of commits to retrieve (default: 10)",
                        "default": 10
                    }
                },
                "required": []
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    """Handle tool calls."""
    try:
        if name == "process_code_changes":
            if not orchestrator:
                return [TextContent(
                    type="text",
                    text="Error: Orchestrator not initialized. Check server logs for details."
                )]
            
            diff_content = arguments.get("diff_content", "")
            repo_path = arguments.get("repo_path", ".")
            
            # If no diff provided, try to get from Git
            if not diff_content or diff_content.strip() == "":
                if not git_handler:
                    return [TextContent(
                        type="text",
                        text="Error: Git handler not initialized. Cannot fetch Git diff."
                    )]
                diff_content = git_handler.get_uncommitted_changes()
                if not diff_content or diff_content.strip() == "":
                    from src.config import config
                    diff_content = git_handler.get_diff(config.git_branch)
            
            if not diff_content or diff_content.strip() == "":
                return [TextContent(
                    type="text",
                    text="No code changes found. Please make some changes to your code or provide a Git diff."
                )]
            
            # Process code changes
            update = orchestrator.process_code_changes(diff_content, repo_path)
            
            result = {
                "documentation": update.content,
                "file_path": update.file_path,
                "evaluation_score": update.evaluation_score,
                "ready_to_commit": update.ready_to_commit,
                "code_snippets_count": len(update.code_snippets)
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "get_git_diff":
            if not git_handler:
                return [TextContent(
                    type="text",
                    text="Error: Git handler not initialized. Check server logs for details."
                )]
            
            branch = arguments.get("branch", "main")
            uncommitted_only = arguments.get("uncommitted_only", False)
            
            if uncommitted_only:
                diff = git_handler.get_uncommitted_changes()
            else:
                diff = git_handler.get_diff(branch)
            
            if not diff or diff.strip() == "":
                return [TextContent(
                    type="text",
                    text="No changes found."
                )]
            
            return [TextContent(
                type="text",
                text=diff
            )]
        
        elif name == "update_documentation":
            if not git_handler:
                return [TextContent(
                    type="text",
                    text="Error: Git handler not initialized. Check server logs for details."
                )]
            
            file_path = arguments["file_path"]
            content = arguments["content"]
            commit_message = arguments.get("commit_message", "docs: Update documentation")
            
            success = git_handler.commit_documentation(file_path, content, commit_message)
            
            if success:
                return [TextContent(
                    type="text",
                    text=f"Documentation updated successfully: {file_path}"
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"Failed to update documentation: {file_path}"
                )]
        
        elif name == "commit_documentation":
            if not git_handler:
                return [TextContent(
                    type="text",
                    text="Error: Git handler not initialized. Check server logs for details."
                )]
            
            file_path = arguments["file_path"]
            content = arguments["content"]
            commit_message = arguments.get("commit_message", "docs: Update documentation")
            
            success = git_handler.commit_documentation(file_path, content, commit_message)
            
            if success:
                return [TextContent(
                    type="text",
                    text=f"Documentation committed successfully: {file_path}\nCommit message: {commit_message}"
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"Failed to commit documentation: {file_path}"
                )]
        
        elif name == "get_recent_commits":
            if not git_handler:
                return [TextContent(
                    type="text",
                    text="Error: Git handler not initialized. Check server logs for details."
                )]
            
            limit = arguments.get("limit", 10)
            commits = git_handler.get_recent_commits(limit)
            
            if not commits:
                return [TextContent(
                    type="text",
                    text="No commits found."
                )]
            
            result = json.dumps(commits, indent=2)
            return [TextContent(
                type="text",
                text=result
            )]
        
        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
    
    except Exception as e:
        # Log error to stderr (not stdout)
        import traceback
        sys.stderr.write(f"Error in tool '{name}': {e}\n")
        sys.stderr.write(traceback.format_exc())
        sys.stderr.flush()
        
        return [TextContent(
            type="text",
            text=f"Error executing tool '{name}': {str(e)}"
        )]


async def main():
    """Run the MCP server."""
    try:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
    except Exception as e:
        # Log to stderr, not stdout
        import traceback
        sys.stderr.write(f"Fatal error in MCP server: {e}\n")
        sys.stderr.write(traceback.format_exc())
        sys.stderr.flush()
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Normal shutdown
        sys.stderr.write("MCP server shutting down...\n")
        sys.stderr.flush()
    except Exception as e:
        sys.stderr.write(f"Fatal error: {e}\n")
        sys.stderr.flush()
        sys.exit(1)

