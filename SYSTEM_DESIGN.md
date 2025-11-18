# System Design Diagram

## Overview
This document describes the system design for the Live Document Editor using MCP (Model Context Protocol) orchestration.

## Architecture Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Git Repository                                │
│              (GitHub/GitLab/Monitored)                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Code Changes
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              Webhook / Scheduled Trigger                         │
│         (PR Merge / File Watcher / Cron)                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Trigger Event
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              MCP Client (Orchestrator)                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         Gemini Agent - The Brain                         │  │
│  │  • Decision Making                                       │  │
│  │  • Workflow Orchestration                                │  │
│  │  • Documentation Generation                              │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │    Daytona Server - Success/Failure Handler              │  │
│  │  • Code Execution Results                                │  │
│  │  • Self-Correction Triggers                              │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────┬───────────────────────────┬────────────────────────────┘
         │                           │
         │ Orchestrates              │ Self-Correction Loop
         │                           │
         ▼                           │
┌─────────────────────────────────────────────────────────────────┐
│              MCP Servers (Tools)                                 │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  CodeRabbit Server                                       │  │
│  │  • Structure code changes                                │  │
│  │  • Analyze diffs                                         │  │
│  │  • Categorize modifications                              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │                                      │
│                           │ Structured Changes                   │
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Documentation Drafting                                   │  │
│  │  • Generate docs with code snippets                      │  │
│  │  • Execute code snippets (Daytona)                       │  │
│  │  • Collect execution results                             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │                                      │
│                           │ Draft + Execution Results            │
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Galileo Server                                          │  │
│  │  • Evaluate accuracy                                     │  │
│  │  • Assess tone                                           │  │
│  │  • Check clarity                                         │  │
│  │  • Provide quality scores                                │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         │ Evaluated Documentation
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Quality Check                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Score >= Threshold?                                     │  │
│  │  ┌──────────┐         ┌──────────┐                      │  │
│  │  │   YES    │         │    NO     │                      │  │
│  │  └────┬─────┘         └────┬─────┘                      │  │
│  │       │                     │                            │  │
│  │       │                     │ Trigger Self-Correction     │  │
│  │       │                     └───────────┐                │  │
│  │       │                                 │                │  │
│  │       │                                 ▼                │  │
│  │       │                    ┌──────────────────────┐     │  │
│  │       │                    │  Gemini Revision     │     │  │
│  │       │                    │  (Max 3 attempts)    │     │  │
│  │       │                    └──────────┬───────────┘     │  │
│  │       │                                 │                │  │
│  │       │                                 └───────────────┘  │
│  │       │                                                     │  │
│  └───────┼─────────────────────────────────────────────────────┘  │
└──────────┼────────────────────────────────────────────────────────┘
           │
           │ Verified Documentation
           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Final Output                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Git Repository Update                                   │  │
│  │  • Commit to 'main' branch                               │  │
│  │  • Verified Documentation Update                         │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. MCP Client (Orchestrator)
**Technology**: Python with Gemini API
**Responsibilities**:
- Monitor code changes (Git webhooks, file watchers, scheduled checks)
- Coordinate workflow between MCP servers
- Make intelligent decisions using Gemini
- Manage self-correction loops
- Handle error recovery

### 2. CodeRabbit Server
**Role**: Code Structure Analysis
**Input**: Git diff content
**Output**: Structured code change analysis
**Key Functions**:
- Parse git diffs
- Identify file changes (added/modified/deleted)
- Detect programming languages
- Assess code complexity
- Generate change summaries

### 3. Daytona Server
**Role**: Code Execution & Validation
**Input**: Code snippets from documentation
**Output**: Execution results (success/failure, output)
**Key Functions**:
- Create isolated sandboxes
- Execute code snippets
- Validate code correctness
- Report execution status
- Trigger self-correction on failure

### 4. Galileo Server
**Role**: Documentation Quality Evaluation
**Input**: Documentation text + code context + execution results
**Output**: Quality scores and feedback
**Key Functions**:
- Evaluate accuracy (0.0-1.0)
- Assess tone (0.0-1.0)
- Check clarity (0.0-1.0)
- Calculate overall score
- Provide improvement feedback

### 5. Self-Correction Loop
**Trigger Conditions**:
- Daytona execution failure
- Galileo quality score below threshold
- Maximum attempts not exceeded

**Process**:
1. Analyze failure/quality issues
2. Generate correction prompt for Gemini
3. Revise documentation
4. Re-execute code snippets
5. Re-evaluate quality
6. Repeat until threshold met or max attempts reached

## Data Flow

```
1. Git Change Detected
   ↓
2. CodeRabbit structures changes
   ↓
3. Gemini generates initial documentation
   ↓
4. Extract code snippets from documentation
   ↓
5. Daytona executes snippets
   ↓
6. Galileo evaluates documentation quality
   ↓
7. Quality check:
   - If score >= threshold → Commit
   - If score < threshold → Self-correct (max 3 attempts)
   ↓
8. Final verified documentation → Git commit
```

## Technology Stack

- **Orchestration**: Python, Gemini API
- **Code Analysis**: CodeRabbit (custom integration)
- **Code Execution**: Daytona SDK
- **Quality Evaluation**: Galileo.ai MCP
- **Web Interface**: FastAPI, WebSockets
- **Version Control**: GitPython
- **Frontend**: HTML/CSS/JavaScript

## Scalability Considerations

1. **Async Processing**: All MCP server calls are async-capable
2. **Sandbox Management**: Daytona handles sandbox lifecycle
3. **Caching**: Can cache structured changes and evaluations
4. **Queue System**: Can integrate message queues for high volume
5. **Horizontal Scaling**: Stateless design allows multiple instances

## Security

1. **Sandbox Isolation**: Daytona provides secure code execution
2. **API Keys**: Stored in environment variables
3. **Git Authentication**: Uses Git credentials securely
4. **Input Validation**: All inputs validated before processing

## Error Handling

1. **Graceful Degradation**: Falls back to basic documentation if services unavailable
2. **Retry Logic**: Self-correction loop handles transient failures
3. **Logging**: All operations logged for debugging
4. **User Feedback**: WebSocket provides real-time status updates

