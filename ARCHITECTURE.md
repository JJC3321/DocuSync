# Live Document Editor System Architecture

## Overview
A live document editor for codebases that automatically generates and updates documentation based on code changes, using an MCP (Model Context Protocol) orchestration system.

## System Components

### 1. MCP Client (Orchestrator)
- **Technology**: Python with Gemini API
- **Role**: Central brain that coordinates all operations
- **Responsibilities**:
  - Monitor code changes (Git webhooks or file watchers)
  - Orchestrate workflow between tools
  - Make decisions on documentation updates
  - Handle self-correction loops

### 2. MCP Servers (Tools)

#### A. CodeRabbit Server
- **Role**: Structure and analyze code changes
- **Function**: Parse code diffs, identify changes, categorize modifications
- **Output**: Structured code change analysis

#### B. Daytona Server
- **Role**: Execute code snippets and handle success/failure
- **Function**: 
  - Run code examples in isolated sandboxes
  - Validate code execution
  - Report execution results
- **Output**: Execution results (success/failure, output)

#### C. Galileo Server
- **Role**: Evaluate documentation quality
- **Function**:
  - Assess documentation accuracy
  - Evaluate tone and clarity
  - Provide quality scores
- **Output**: Evaluation metrics and feedback

### 3. Live Document Editor
- **Technology**: Web-based interface (Flask/FastAPI + React/HTML)
- **Features**:
  - Real-time document editing
  - Code snippet preview
  - Live documentation updates
  - Version history

### 4. Git Integration
- **Function**: 
  - Monitor repository changes
  - Commit documentation updates
  - Handle version control

## Workflow

```
Git Repository → Webhook/Scheduler → MCP Client (Gemini)
    ↓
MCP Client orchestrates:
    1. CodeRabbit: Structure code changes
    2. Draft documentation with code snippets
    3. Daytona: Execute code snippets
    4. Galileo: Evaluate documentation
    5. Self-correction if needed (Daytona success/failure)
    ↓
Final Output → Git Repository (Commit to main)
```

## Self-Correction Loop
- Daytona reports execution failure → Trigger self-correction
- Galileo reports low quality → Trigger revision
- Iterate until quality thresholds are met

## Technology Stack
- **Backend**: Python, FastAPI
- **AI Orchestration**: Google Gemini API
- **Code Execution**: Daytona SDK
- **Evaluation**: Galileo.ai MCP
- **Code Analysis**: CodeRabbit (custom integration)
- **Frontend**: HTML/CSS/JavaScript (or React)
- **Version Control**: GitPython

