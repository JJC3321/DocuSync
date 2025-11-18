"""Daytona MCP Server - Executes code snippets and handles success/failure."""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from daytona import Daytona, DaytonaConfig
import os


@dataclass
class ExecutionResult:
    """Result of code execution."""
    success: bool
    exit_code: int
    output: str
    error: Optional[str] = None
    execution_time: Optional[float] = None


class DaytonaServer:
    """MCP Server for Daytona - executes code and handles success/failure."""
    
    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("DAYTONA_API_KEY")
        self.api_url = api_url
        self.daytona = None
        self.sandbox = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Daytona client."""
        if self.api_key:
            config = DaytonaConfig(api_key=self.api_key)
            if self.api_url:
                config.api_url = self.api_url
            self.daytona = Daytona(config)
    
    def create_sandbox(self, language: str = "python") -> bool:
        """Create a new sandbox for code execution."""
        try:
            if not self.daytona:
                return False
            self.sandbox = self.daytona.create()
            return True
        except Exception as e:
            print(f"Error creating sandbox: {e}")
            return False
    
    def execute_code(self, code: str, language: str = "python") -> ExecutionResult:
        """
        Execute code snippet in Daytona sandbox.
        
        Args:
            code: Code to execute
            language: Programming language
            
        Returns:
            ExecutionResult with success status and output
        """
        if not self.sandbox:
            if not self.create_sandbox(language):
                return ExecutionResult(
                    success=False,
                    exit_code=-1,
                    output="",
                    error="Failed to create sandbox"
                )
        
        try:
            if language == "python":
                response = self.sandbox.process.code_run(code)
            else:
                # For other languages, use exec
                response = self.sandbox.process.exec(code)
            
            return ExecutionResult(
                success=response.exit_code == 0,
                exit_code=response.exit_code,
                output=response.result or "",
                error=None if response.exit_code == 0 else response.result
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                exit_code=-1,
                output="",
                error=str(e)
            )
    
    def execute_code_snippets(self, code_snippets: List[Dict[str, str]]) -> Dict[str, ExecutionResult]:
        """
        Execute multiple code snippets.
        
        Args:
            code_snippets: List of dicts with 'code' and 'language' keys
            
        Returns:
            Dictionary mapping snippet IDs to execution results
        """
        results = {}
        
        for i, snippet in enumerate(code_snippets):
            code = snippet.get('code', '')
            language = snippet.get('language', 'python')
            snippet_id = snippet.get('id', f'snippet_{i}')
            
            result = self.execute_code(code, language)
            results[snippet_id] = result
        
        return results
    
    def cleanup(self):
        """Clean up sandbox resources."""
        if self.sandbox:
            try:
                self.sandbox.delete()
                self.sandbox = None
            except Exception as e:
                print(f"Error cleaning up sandbox: {e}")
    
    def __del__(self):
        """Cleanup on deletion."""
        self.cleanup()

