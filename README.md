# Live Document Editor - MCP Server for Cursor

An intelligent MCP (Model Context Protocol) server that automatically generates and updates documentation based on code changes, designed to work directly with Cursor.

## Features

- **AI-Powered Documentation**: Uses Gemini to generate clear, accurate documentation
- **Code Analysis**: CodeRabbit structures and analyzes code changes
- **Code Execution**: Daytona executes code snippets in secure sandboxes
- **Quality Evaluation**: Galileo.ai evaluates documentation accuracy and tone
- **Self-Correction**: Automatic improvement loop when quality thresholds aren't met
- **Git Integration**: Automatic commits and version control
- **MCP Integration**: Works directly in Cursor via Model Context Protocol

## Quick Start (MCP for Cursor)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file with your API keys (optional - system works with fallbacks):

```env
# Gemini Configuration (recommended)
GEMINI_API_KEY=your_gemini_api_key

# Daytona Configuration (optional)
DAYTONA_API_KEY=your_daytona_api_key
DAYTONA_API_URL=https://app.daytona.io/api

# Galileo Configuration (optional)
GALILEO_API_KEY=your_galileo_api_key
GALILEO_PROJECT_ID=your_project_id

# CodeRabbit Configuration (optional)
CODERABBIT_API_KEY=your_coderabbit_api_key

# Git Configuration
GIT_REPO_PATH=.
GIT_BRANCH=main

# Quality Thresholds
MIN_DOC_QUALITY_SCORE=0.7
MAX_SELF_CORRECTION_ATTEMPTS=3
```

### 3. Set Up MCP in Cursor

Run the configuration helper:

```bash
python update_mcp_config.py
```

Or manually edit `%USERPROFILE%\.cursor\mcp.json` (Windows) or `~/.cursor/mcp.json` (macOS/Linux):

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

### 4. Restart Cursor

After updating the configuration, restart Cursor completely to load the MCP server.

## Usage in Cursor

Once connected, you can use these MCP tools directly in Cursor:

### Available MCP Tools

1. **`process_code_changes`** - Process Git code changes and generate documentation
   ```
   Use the process_code_changes tool to generate documentation for my recent code changes
   ```

2. **`get_git_diff`** - Get Git diff for the current repository
   ```
   Use the get_git_diff tool to show me the current Git diff
   ```

3. **`update_documentation`** - Update or create a documentation file
   ```
   Use the update_documentation tool to update README.md with [content]
   ```

4. **`commit_documentation`** - Commit documentation changes to Git
   ```
   Use the commit_documentation tool to commit the documentation
   ```

5. **`get_recent_commits`** - Get recent Git commits
   ```
   Use the get_recent_commits tool to show me the last 5 commits
   ```

## Architecture

```
Git Repository → MCP Server (mcp_server.py)
    ↓
    ├─ CodeRabbit: Structure code changes
    ├─ Gemini: Generate documentation
    ├─ Daytona: Execute code snippets
    ├─ Galileo: Evaluate documentation quality
    └─ Self-Correction Loop: Improve until quality threshold met
    ↓
Final Output → Git Repository (Commit to main)
```

## Project Structure

```
.
├── mcp_server.py              # Main MCP server entry point (for Cursor)
├── src/
│   ├── orchestrator.py        # MCP orchestrator with Gemini
│   ├── git_handler.py         # Git integration
│   ├── config.py              # Configuration management
│   └── mcp_servers/
│       ├── coderabbit.py      # CodeRabbit server
│       ├── daytona_server.py  # Daytona server
│       └── galileo_server.py  # Galileo server
├── requirements.txt           # Dependencies
└── MCP_SETUP.md              # Detailed MCP setup guide
```

## System Components

### MCP Orchestrator (`src/orchestrator.py`)
- Coordinates all MCP servers
- Uses Gemini for intelligent decision-making
- Manages self-correction loops

### CodeRabbit Server (`src/mcp_servers/coderabbit.py`)
- Structures code changes from Git diffs
- Analyzes code complexity
- Categorizes modifications

### Daytona Server (`src/mcp_servers/daytona_server.py`)
- Executes code snippets in secure sandboxes
- Reports execution success/failure
- Handles code validation

### Galileo Server (`src/mcp_servers/galileo_server.py`)
- Evaluates documentation quality
- Assesses accuracy, tone, and clarity
- Provides feedback for improvement

### Git Handler (`src/git_handler.py`)
- Monitors repository changes
- Commits documentation updates
- Manages version control

## Workflow

1. **Code Changes Detected**: Git diff triggers the system
2. **Structure Analysis**: CodeRabbit analyzes and structures the changes
3. **Documentation Generation**: Gemini generates initial documentation
4. **Code Execution**: Daytona executes code snippets to validate examples
5. **Quality Evaluation**: Galileo evaluates documentation quality
6. **Self-Correction**: If quality is low, the system self-corrects using Gemini
7. **Final Output**: High-quality documentation is committed to Git

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

### Git Operations Fail

- Ensure the directory is a Git repository (`git init`)
- Check file permissions
- Verify Git is installed and in PATH

## Documentation

- **MCP_SETUP.md** - Detailed MCP setup and usage guide
- **ARCHITECTURE.md** - System architecture details
- **SYSTEM_DESIGN.md** - Workflow diagrams and design

## License

MIT License

