# Quick Start Guide - MCP Server for Cursor

## Prerequisites

- Python 3.9 or higher
- Git installed
- Cursor IDE
- API keys (optional - system works with fallbacks):
  - Google Gemini API (recommended)
  - Daytona API
  - Galileo.ai API 
  - CodeRabbit API 

## Setup Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)

Create a `.env` file with your API keys:

```bash
# Create .env file
# Gemini Configuration (recommended)
GEMINI_API_KEY=your_gemini_api_key

# Daytona Configuration
DAYTONA_API_KEY=your_daytona_api_key
DAYTONA_API_URL=https://app.daytona.io/api

# Galileo Configuration
GALILEO_API_KEY=your_galileo_api_key
GALILEO_PROJECT_ID=your_project_id

# CodeRabbit Configuration
CODERABBIT_API_KEY=your_coderabbit_api_key

# Git Configuration
GIT_REPO_PATH=.
GIT_BRANCH=main

# Quality Thresholds
MIN_DOC_QUALITY_SCORE=0.7
MAX_SELF_CORRECTION_ATTEMPTS=3
```

### 3. Initialize Git Repository (if not already)

```bash
git init
```

### 4. Set Up MCP in Cursor

Run the configuration helper:

```bash
python update_mcp_config.py
```

Or manually edit your Cursor MCP configuration:
- **Windows**: `%USERPROFILE%\.cursor\mcp.json`
- **macOS/Linux**: `~/.cursor/mcp.json`

Add:

```json
{
  "mcpServers": {
    "live-document-editor": {
      "command": "python",
      "args": ["C:\\path\\to\\HackSprint\\mcp_server.py"],
      "env": {}
    }
  }
}
```

**Important**: Update the path in `args` to match your actual project path.

### 5. Restart Cursor

After updating the configuration, restart Cursor completely to load the MCP server.

## Usage in Cursor

Once connected, use the MCP tools directly in Cursor's chat:

### Process Code Changes

```
Use the process_code_changes tool to generate documentation for my recent code changes
```

### Get Git Diff

```
Use the get_git_diff tool to show me the current Git diff
```

### Get Recent Commits

```
Use the get_recent_commits tool with limit 5 to show me the last 5 commits
```

### Update Documentation

```
Use the update_documentation tool to update README.md with [your content]
```

### Commit Documentation

```
Use the commit_documentation tool to commit the documentation changes
```

## Python Script Usage

See `example_usage.py` for programmatic usage:

```python
from src.orchestrator import MCPOrchestrator

orchestrator = MCPOrchestrator()
update = orchestrator.process_code_changes(diff_content)
print(update.content)
```

## Testing Without API Keys

The system includes fallback mechanisms:
- If Gemini is unavailable, basic documentation is generated
- CodeRabbit uses local parsing (no API required)
- Galileo uses local evaluation algorithms
- Daytona is optional for code execution

However, for best results, configure all API keys.

## Troubleshooting

### MCP Server Not Connecting

1. **Check the path**: Ensure the path in `mcp.json` is correct
2. **Check Python path**: Make sure `python` is in your PATH
3. **Check dependencies**: Ensure all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```
4. **Check logs**: Look for errors in Cursor's Developer Console (`Ctrl+Shift+I`)

### Daytona Sandbox Creation Fails
- Verify `DAYTONA_API_KEY` is set correctly
- Check network connectivity to Daytona API
- Ensure you have available sandbox quota

### Gemini API Errors
- Verify `GEMINI_API_KEY` is valid
- Check API quota limits
- System will fall back to basic documentation generation

### Git Operations Fail
- Ensure the directory is a Git repository (`git init`)
- Check file permissions
- Verify Git is installed and in PATH

## Next Steps

- Read `MCP_SETUP.md` for detailed MCP setup instructions
- Read `ARCHITECTURE.md` for system design details
- Read `SYSTEM_DESIGN.md` for workflow diagrams
- Customize quality thresholds in `.env`
