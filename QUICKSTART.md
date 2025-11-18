# Quick Start Guide

## Prerequisites

- Python 3.9 or higher
- Git installed
- API keys for:
  - Google Gemini API
  - Daytona API
  - Galileo.ai API

## Setup Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Initialize Git Repository (if not already)

```bash
git init
```

### 4. Start the Server

```bash
python main.py
```

The server will start on `http://localhost:8000`

## Usage

### Web Interface

1. Open `http://localhost:8000` in your browser
2. Click "Process Code Changes" to generate documentation from Git diff
3. Edit the documentation in the editor
4. Click "Save Documentation" to save locally
5. Click "Commit to Git" to commit changes

### API Usage

#### Process Code Changes

```bash
curl -X POST http://localhost:8000/api/process-changes \
  -H "Content-Type: application/json" \
  -d '{
    "diff_content": "diff --git a/file.py b/file.py\n...",
    "repo_path": "."
  }'
```

#### Update Documentation

```bash
curl -X POST http://localhost:8000/api/update-documentation \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "DOCUMENTATION.md",
    "content": "# Documentation\n\n...",
    "commit_message": "docs: Update documentation"
  }'
```

### Python Script Usage

See `example_usage.py` for a complete example:

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

However, for best results, configure all API keys.

## Troubleshooting

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

- Read `ARCHITECTURE.md` for system design details
- Read `SYSTEM_DESIGN.md` for workflow diagrams
- Customize quality thresholds in `.env`
- Integrate with CI/CD pipelines for automated documentation

