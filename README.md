# Live Document Editor for Codebases

An intelligent live document editor that automatically generates and updates documentation based on code changes, using MCP (Model Context Protocol) orchestration with Gemini, CodeRabbit, Daytona, and Galileo.ai.

## Features

- 🤖 **AI-Powered Documentation**: Uses Gemini to generate clear, accurate documentation
- 🔍 **Code Analysis**: CodeRabbit structures and analyzes code changes
- ✅ **Code Execution**: Daytona executes code snippets in secure sandboxes
- 📊 **Quality Evaluation**: Galileo.ai evaluates documentation accuracy and tone
- 🔄 **Self-Correction**: Automatic improvement loop when quality thresholds aren't met
- 💻 **Live Editor**: Web-based interface for real-time documentation editing
- 🔀 **Git Integration**: Automatic commits and version control

## Architecture

```
Git Repository → MCP Client (Gemini Orchestrator)
    ↓
    ├─ CodeRabbit Server: Structure code changes
    ├─ Draft Documentation: Generate docs with code snippets
    ├─ Daytona Server: Execute code snippets
    ├─ Galileo Server: Evaluate documentation quality
    └─ Self-Correction Loop: Improve until quality threshold met
    ↓
Final Output → Git Repository (Commit to main)
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd HackSprint
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file:
```env
# Gemini Configuration
GEMINI_API_KEY=your_gemini_api_key

# Daytona Configuration
DAYTONA_API_KEY=your_daytona_api_key
DAYTONA_API_URL=https://app.daytona.io/api

# Galileo Configuration
GALILEO_API_KEY=your_galileo_api_key
GALILEO_PROJECT_ID=your_project_id

# CodeRabbit Configuration (optional)
CODERABBIT_API_KEY=your_coderabbit_api_key

# Git Configuration
GIT_REPO_PATH=.
GIT_BRANCH=main

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Quality Thresholds
MIN_DOC_QUALITY_SCORE=0.7
MAX_SELF_CORRECTION_ATTEMPTS=3
```

## Usage

1. Start the server:
```bash
python main.py
```

2. Open your browser:
```
http://localhost:8000
```

3. Use the web interface to:
   - Process code changes
   - Edit documentation
   - Save and commit changes

## API Endpoints

### POST `/api/process-changes`
Process code changes and generate documentation.

**Request:**
```json
{
  "diff_content": "git diff content...",
  "repo_path": "."
}
```

**Response:**
```json
{
  "documentation": "Generated documentation...",
  "file_path": "DOCUMENTATION.md",
  "evaluation_score": 0.85,
  "ready_to_commit": true
}
```

### POST `/api/update-documentation`
Update documentation file.

### POST `/api/commit-documentation`
Commit documentation to Git.

### GET `/api/git/diff`
Get Git diff for a branch.

### GET `/api/git/commits`
Get recent commits.

### WebSocket `/ws`
Real-time updates for documentation changes.

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

1. **Code Changes Detected**: Git diff or file changes trigger the system
2. **Structure Analysis**: CodeRabbit analyzes and structures the changes
3. **Documentation Generation**: Gemini generates initial documentation
4. **Code Execution**: Daytona executes code snippets to validate examples
5. **Quality Evaluation**: Galileo evaluates documentation quality
6. **Self-Correction**: If quality is low, the system self-corrects using Gemini
7. **Final Output**: High-quality documentation is committed to Git

## Development

### Project Structure
```
.
├── src/
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   ├── orchestrator.py        # MCP orchestrator with Gemini
│   ├── api.py                 # FastAPI application
│   ├── git_handler.py         # Git integration
│   └── mcp_servers/
│       ├── coderabbit.py      # CodeRabbit server
│       ├── daytona_server.py  # Daytona server
│       └── galileo_server.py  # Galileo server
├── main.py                    # Entry point
├── requirements.txt           # Dependencies
├── ARCHITECTURE.md           # System architecture
└── README.md                 # This file
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

