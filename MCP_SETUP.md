# MCP Server Setup for Cursor

This project is an MCP (Model Context Protocol) server that connects directly to Cursor, allowing you to use the documentation generation features directly within Cursor.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Update Cursor MCP Configuration

Edit your Cursor MCP configuration file at:
- **Windows**: `%USERPROFILE%\.cursor\mcp.json`
- **macOS/Linux**: `~/.cursor/mcp.json`

Add the following configuration:

```json
{
  "mcpServers": {
    "galileo_mcp_server": {
      "url": "https://api.galileo.ai/mcp/http/mcp",
      "headers": {
        "Accept": "text/event-stream"
      }
    },
    "live-document-editor": {
      "command": "python",
      "args": ["C:\\Users\\Jian Jin Chen\\Documents\\Code\\HackSprint\\mcp_server.py"],
      "env": {}
    }
  }
}
```

**Important**: Update the path in `args` to match your actual project path.

You can also use the helper script:

```bash
python update_mcp_config.py
```

### 3. Restart Cursor

After updating the configuration, restart Cursor completely to load the MCP server.

## Available MCP Tools

Once connected, you can use these tools in Cursor:

### 1. `process_code_changes`
Process Git code changes and generate documentation automatically.

**Parameters:**
- `diff_content` (optional): Git diff content. If empty, fetches from current repository.
- `repo_path` (optional): Path to repository (default: current directory)

**Example usage in Cursor:**
```
Use the process_code_changes tool to generate documentation for my recent code changes.
```

### 2. `get_git_diff`
Get Git diff for the current repository.

**Parameters:**
- `branch` (optional): Branch to compare against (default: main)
- `uncommitted_only` (optional): If true, only return uncommitted changes

**Example usage:**
```
Use the get_git_diff tool to show me the current Git diff
```

### 3. `update_documentation`
Update or create a documentation file.

**Parameters:**
- `file_path` (required): Path to documentation file
- `content` (required): Documentation content in Markdown
- `commit_message` (optional): Git commit message

**Example usage:**
```
Use the update_documentation tool to update README.md with [your content]
```

### 4. `commit_documentation`
Commit documentation changes to Git.

**Parameters:**
- `file_path` (required): Path to documentation file
- `content` (required): Documentation content
- `commit_message` (optional): Git commit message

**Example usage:**
```
Use the commit_documentation tool to commit the documentation changes
```

### 5. `get_recent_commits`
Get recent Git commits from the repository.

**Parameters:**
- `limit` (optional): Number of commits to retrieve (default: 10)

**Example usage:**
```
Use the get_recent_commits tool with limit 5 to show me the last 5 commits
```

## Usage in Cursor

Once the MCP server is connected, you can:

1. **Ask Cursor to generate documentation:**
   ```
   Generate documentation for my recent code changes using the process_code_changes tool.
   ```

2. **Review Git changes:**
   ```
   Show me the Git diff for the main branch using get_git_diff.
   ```

3. **Update documentation:**
   ```
   Update the README.md file with the following content: [your content]
   ```

## Troubleshooting

### Server Not Connecting

1. **Check the path**: Ensure the path in `mcp.json` is correct and uses forward slashes or escaped backslashes on Windows.

2. **Check Python path**: Make sure `python` is in your PATH, or use the full path to Python executable.

3. **Check dependencies**: Ensure all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```

4. **Check logs**: Look for errors in Cursor's developer console or terminal output.

### Testing the Server

You can test the MCP server manually:

```bash
python mcp_server.py
```

The server communicates via stdio, so it won't produce visible output when run directly. It's designed to be used by Cursor.

### Environment Variables

Make sure your `.env` file is configured with API keys if you want to use:
- Gemini API (for documentation generation)
- Daytona API (for code execution)
- Galileo API (for quality evaluation)

The system will work with fallbacks if APIs are not configured.

The MCP server runs as a standalone process and communicates with Cursor via stdio, providing direct integration without any web server needed.
