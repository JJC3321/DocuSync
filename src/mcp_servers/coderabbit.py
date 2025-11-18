"""CodeRabbit MCP Server - Structures and analyzes code changes."""
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class CodeChange:
    """Represents a structured code change."""
    file_path: str
    change_type: str  # 'added', 'modified', 'deleted'
    lines_added: List[str]
    lines_removed: List[str]
    language: str
    complexity: str  # 'low', 'medium', 'high'
    summary: str


class CodeRabbitServer:
    """MCP Server for CodeRabbit - structures code changes."""
    
    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None):
        self.api_key = api_key
        self.api_url = api_url or "https://api.coderabbit.ai"
    
    def structure_code_changes(self, diff_content: str, repo_path: str = ".") -> Dict[str, Any]:
        """
        Structure code changes from a git diff.
        
        Args:
            diff_content: Git diff content
            repo_path: Path to the repository
            
        Returns:
            Structured analysis of code changes
        """
        changes = self._parse_diff(diff_content)
        structured_changes = []
        
        for change in changes:
            structured_change = {
                "file_path": change.file_path,
                "change_type": change.change_type,
                "language": change.language,
                "complexity": change.complexity,
                "summary": change.summary,
                "lines_added": len(change.lines_added),
                "lines_removed": len(change.lines_removed),
                "code_snippets": {
                    "added": change.lines_added[:10],  # First 10 lines
                    "removed": change.lines_removed[:10]
                }
            }
            structured_changes.append(structured_change)
        
        return {
            "total_changes": len(structured_changes),
            "changes": structured_changes,
            "analysis": self._analyze_changes(changes)
        }
    
    def _parse_diff(self, diff_content: str) -> List[CodeChange]:
        """Parse git diff content into structured changes."""
        changes = []
        current_file = None
        current_type = "modified"
        added_lines = []
        removed_lines = []
        
        for line in diff_content.split('\n'):
            if line.startswith('diff --git'):
                if current_file:
                    changes.append(CodeChange(
                        file_path=current_file,
                        change_type=current_type,
                        lines_added=added_lines,
                        lines_removed=removed_lines,
                        language=self._detect_language(current_file),
                        complexity=self._assess_complexity(added_lines, removed_lines),
                        summary=self._generate_summary(added_lines, removed_lines)
                    ))
                added_lines = []
                removed_lines = []
            elif line.startswith('+++') or line.startswith('---'):
                if line.startswith('+++'):
                    current_file = line.replace('+++ b/', '').replace('+++ a/', '')
            elif line.startswith('+') and not line.startswith('+++'):
                added_lines.append(line[1:])
            elif line.startswith('-') and not line.startswith('---'):
                removed_lines.append(line[1:])
        
        # Add last file
        if current_file:
            changes.append(CodeChange(
                file_path=current_file,
                change_type=current_type,
                lines_added=added_lines,
                lines_removed=removed_lines,
                language=self._detect_language(current_file),
                complexity=self._assess_complexity(added_lines, removed_lines),
                summary=self._generate_summary(added_lines, removed_lines)
            ))
        
        return changes
    
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension."""
        ext_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
            '.md': 'markdown',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml'
        }
        for ext, lang in ext_map.items():
            if file_path.endswith(ext):
                return lang
        return 'unknown'
    
    def _assess_complexity(self, added: List[str], removed: List[str]) -> str:
        """Assess code complexity based on changes."""
        total_lines = len(added) + len(removed)
        if total_lines < 10:
            return 'low'
        elif total_lines < 50:
            return 'medium'
        else:
            return 'high'
    
    def _generate_summary(self, added: List[str], removed: List[str]) -> str:
        """Generate a summary of the code changes."""
        if not added and not removed:
            return "No changes detected"
        
        if not removed:
            return f"Added {len(added)} lines"
        if not added:
            return f"Removed {len(removed)} lines"
        
        return f"Modified: {len(added)} lines added, {len(removed)} lines removed"

