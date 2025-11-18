"""FastAPI application for the Live Document Editor."""
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json

from src.orchestrator import MCPOrchestrator
from src.git_handler import GitHandler
from src.config import config

app = FastAPI(title="Live Document Editor", version="1.0.0")

# Initialize components
orchestrator = MCPOrchestrator()
git_handler = GitHandler(config.git_repo_path)


class CodeChangeRequest(BaseModel):
    """Request model for processing code changes."""
    diff_content: str
    repo_path: Optional[str] = None


class DocumentationUpdateRequest(BaseModel):
    """Request model for updating documentation."""
    file_path: str
    content: str
    commit_message: Optional[str] = "docs: Update documentation"


class WebSocketManager:
    """Manages WebSocket connections for live updates."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients."""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error broadcasting message: {e}")


ws_manager = WebSocketManager()


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main editor interface."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Live Document Editor</title>
        <meta charset="utf-8">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #1e1e1e;
                color: #d4d4d4;
                display: flex;
                height: 100vh;
            }
            .sidebar {
                width: 300px;
                background: #252526;
                border-right: 1px solid #3e3e42;
                padding: 20px;
                overflow-y: auto;
            }
            .main {
                flex: 1;
                display: flex;
                flex-direction: column;
            }
            .editor-container {
                flex: 1;
                display: flex;
                flex-direction: column;
                padding: 20px;
            }
            textarea {
                flex: 1;
                background: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3e3e42;
                border-radius: 4px;
                padding: 15px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 14px;
                resize: none;
            }
            .toolbar {
                display: flex;
                gap: 10px;
                margin-bottom: 15px;
            }
            button {
                padding: 8px 16px;
                background: #0e639c;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
            }
            button:hover { background: #1177bb; }
            button:disabled { background: #3e3e42; cursor: not-allowed; }
            .status {
                padding: 10px;
                background: #252526;
                border-top: 1px solid #3e3e42;
                font-size: 12px;
            }
            .file-list {
                list-style: none;
            }
            .file-item {
                padding: 8px;
                cursor: pointer;
                border-radius: 4px;
                margin-bottom: 5px;
            }
            .file-item:hover { background: #2a2d2e; }
            .file-item.active { background: #37373d; }
            h2 { margin-bottom: 15px; font-size: 18px; }
            .score {
                display: inline-block;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                margin-left: 10px;
            }
            .score.good { background: #0e7c0e; }
            .score.warning { background: #d19a66; }
            .score.bad { background: #d32f2f; }
        </style>
    </head>
    <body>
        <div class="sidebar">
            <h2>Files</h2>
            <ul class="file-list" id="fileList"></ul>
            <h2 style="margin-top: 20px;">Status</h2>
            <div id="status">Ready</div>
        </div>
        <div class="main">
            <div class="editor-container">
                <div class="toolbar">
                    <button onclick="processChanges()">Process Code Changes</button>
                    <button onclick="saveDocumentation()">Save Documentation</button>
                    <button onclick="commitChanges()">Commit to Git</button>
                </div>
                <textarea id="editor" placeholder="Documentation will appear here..."></textarea>
            </div>
            <div class="status" id="statusBar">
                Connected | Score: <span id="score">-</span>
            </div>
        </div>
        <script>
            const ws = new WebSocket('ws://localhost:8000/ws');
            const editor = document.getElementById('editor');
            const statusBar = document.getElementById('statusBar');
            const scoreSpan = document.getElementById('score');
            
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.type === 'documentation_update') {
                    editor.value = data.content;
                    if (data.score !== undefined) {
                        const score = data.score;
                        scoreSpan.textContent = (score * 100).toFixed(0) + '%';
                        scoreSpan.className = 'score ' + 
                            (score >= 0.7 ? 'good' : score >= 0.5 ? 'warning' : 'bad');
                    }
                } else if (data.type === 'status') {
                    statusBar.textContent = data.message;
                }
            };
            
            async function processChanges() {
                statusBar.textContent = 'Processing code changes...';
                const response = await fetch('/api/process-changes', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        diff_content: editor.value || 'No changes detected',
                        repo_path: '.'
                    })
                });
                const data = await response.json();
                if (data.documentation) {
                    editor.value = data.documentation;
                    if (data.evaluation_score !== undefined) {
                        scoreSpan.textContent = (data.evaluation_score * 100).toFixed(0) + '%';
                    }
                }
                statusBar.textContent = 'Processing complete';
            }
            
            async function saveDocumentation() {
                const content = editor.value;
                const response = await fetch('/api/update-documentation', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        file_path: 'DOCUMENTATION.md',
                        content: content
                    })
                });
                const result = await response.json();
                statusBar.textContent = result.message || 'Saved';
            }
            
            async function commitChanges() {
                const content = editor.value;
                const response = await fetch('/api/commit-documentation', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        file_path: 'DOCUMENTATION.md',
                        content: content,
                        commit_message: 'docs: Update documentation'
                    })
                });
                const result = await response.json();
                statusBar.textContent = result.message || 'Committed';
            }
        </script>
    </body>
    </html>
    """


@app.post("/api/process-changes")
async def process_changes(request: CodeChangeRequest):
    """Process code changes and generate documentation."""
    try:
        update = orchestrator.process_code_changes(
            request.diff_content,
            request.repo_path or config.git_repo_path
        )
        
        # Broadcast update via WebSocket
        await ws_manager.broadcast({
            'type': 'documentation_update',
            'content': update.content,
            'score': update.evaluation_score,
            'file_path': update.file_path
        })
        
        return {
            'documentation': update.content,
            'file_path': update.file_path,
            'evaluation_score': update.evaluation_score,
            'ready_to_commit': update.ready_to_commit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/update-documentation")
async def update_documentation(request: DocumentationUpdateRequest):
    """Update documentation file."""
    try:
        success = git_handler.commit_documentation(
            request.file_path,
            request.content,
            request.commit_message or "docs: Update documentation"
        )
        
        if success:
            await ws_manager.broadcast({
                'type': 'status',
                'message': f'Documentation updated: {request.file_path}'
            })
            return {'message': 'Documentation updated successfully', 'success': True}
        else:
            raise HTTPException(status_code=500, detail="Failed to update documentation")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/commit-documentation")
async def commit_documentation(request: DocumentationUpdateRequest):
    """Commit documentation to Git."""
    try:
        success = git_handler.commit_documentation(
            request.file_path,
            request.content,
            request.commit_message or "docs: Update documentation"
        )
        
        if success:
            await ws_manager.broadcast({
                'type': 'status',
                'message': f'Committed: {request.file_path}'
            })
            return {'message': 'Documentation committed successfully', 'success': True}
        else:
            raise HTTPException(status_code=500, detail="Failed to commit documentation")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/git/diff")
async def get_git_diff(branch: str = "main"):
    """Get Git diff."""
    diff = git_handler.get_diff(branch)
    return {'diff': diff}


@app.get("/api/git/commits")
async def get_commits(limit: int = 10):
    """Get recent commits."""
    commits = git_handler.get_recent_commits(limit)
    return {'commits': commits}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for live updates."""
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back or process message
            await websocket.send_json({'type': 'echo', 'data': data})
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown."""
    orchestrator.cleanup()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.host, port=config.port)

