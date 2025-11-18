"""MCP Client Orchestrator - Coordinates all MCP servers using Gemini."""
import google.generativeai as genai
from typing import Dict, Any, Optional, List
import json
import sys
from dataclasses import dataclass

from src.mcp_servers.coderabbit import CodeRabbitServer
from src.mcp_servers.daytona_server import DaytonaServer
from src.mcp_servers.galileo_server import GalileoServer
from src.config import config


@dataclass
class DocumentationUpdate:
    """Represents a documentation update."""
    file_path: str
    content: str
    code_snippets: List[Dict[str, Any]]
    evaluation_score: float
    ready_to_commit: bool


class MCPOrchestrator:
    """MCP Client Orchestrator using Gemini as the brain."""
    
    def __init__(self):
        self.gemini_client = None
        self.coderabbit = CodeRabbitServer(
            api_key=config.coderabbit_api_key,
            api_url=config.coderabbit_api_url
        )
        self.daytona = DaytonaServer(
            api_key=config.daytona_api_key,
            api_url=config.daytona_api_url
        )
        self.galileo = GalileoServer(
            api_key=config.galileo_api_key,
            project_id=config.galileo_project_id
        )
        self._initialize_gemini()
    
    def _initialize_gemini(self):
        """Initialize Gemini client."""
        if config.gemini_api_key:
            genai.configure(api_key=config.gemini_api_key)
            self.gemini_client = genai.GenerativeModel('gemini-pro')
    
    def process_code_changes(self, diff_content: str, repo_path: str = ".") -> DocumentationUpdate:
        """
        Process code changes and generate documentation updates.
        
        Args:
            diff_content: Git diff content
            repo_path: Repository path
            
        Returns:
            DocumentationUpdate with generated documentation
        """
        # Validate input
        if not diff_content or not diff_content.strip():
            raise ValueError("Diff content is empty")
        
        # Step 1: Structure code changes using CodeRabbit
        structured_changes = self.coderabbit.structure_code_changes(diff_content, repo_path)
        
        # Check if we have any changes
        if not structured_changes.get('changes') or len(structured_changes.get('changes', [])) == 0:
            # Return a basic documentation update for empty changes
            return DocumentationUpdate(
                file_path="DOCUMENTATION.md",
                content="# Documentation\n\nNo code changes detected to document.",
                code_snippets=[],
                evaluation_score=0.5,
                ready_to_commit=False
            )
        
        # Step 2: Use Gemini to draft documentation
        documentation = self._draft_documentation(structured_changes)
        
        # Step 3: Extract code snippets and execute them
        code_snippets = self._extract_code_snippets(documentation, structured_changes)
        execution_results = self._execute_code_snippets(code_snippets)
        
        # Step 4: Evaluate documentation using Galileo
        evaluation = self.galileo.evaluate_documentation(
            documentation,
            code_context=json.dumps(structured_changes),
            code_snippets=execution_results
        )
        
        # Step 5: Self-correction if needed
        if evaluation.overall_score < config.min_doc_quality_score:
            documentation, evaluation = self._self_correct(
                documentation,
                structured_changes,
                evaluation,
                execution_results
            )
        
        return DocumentationUpdate(
            file_path=self._determine_doc_path(structured_changes),
            content=documentation,
            code_snippets=execution_results,
            evaluation_score=evaluation.overall_score,
            ready_to_commit=evaluation.overall_score >= config.min_doc_quality_score
        )
    
    def _draft_documentation(self, structured_changes: Dict[str, Any]) -> str:
        """Use Gemini to draft documentation."""
        prompt = self._create_documentation_prompt(structured_changes)
        
        if self.gemini_client:
            try:
                response = self.gemini_client.generate_content(prompt)
                return response.text
            except Exception as e:
                sys.stderr.write(f"Error generating documentation with Gemini: {e}\n")
                sys.stderr.flush()
                return self._fallback_documentation(structured_changes)
        else:
            return self._fallback_documentation(structured_changes)
    
    def _create_documentation_prompt(self, structured_changes: Dict[str, Any]) -> str:
        """Create prompt for Gemini to generate documentation."""
        changes_summary = json.dumps(structured_changes, indent=2)
        
        prompt = f"""You are a technical documentation expert. Generate clear, accurate documentation for the following code changes:

{changes_summary}

Requirements:
1. Write clear, professional documentation
2. Include code examples where relevant
3. Explain what changed and why
4. Use proper markdown formatting
5. Include code snippets in markdown code blocks

Generate the documentation:"""
        
        return prompt
    
    def _fallback_documentation(self, structured_changes: Dict[str, Any]) -> str:
        """Fallback documentation generation if Gemini is unavailable."""
        doc_lines = ["# Documentation Update\n"]
        
        for change in structured_changes.get('changes', []):
            doc_lines.append(f"## {change['file_path']}\n")
            doc_lines.append(f"**Change Type:** {change['change_type']}\n")
            doc_lines.append(f"**Summary:** {change.get('summary', 'N/A')}\n")
            doc_lines.append(f"**Language:** {change.get('language', 'unknown')}\n")
            
            if change.get('code_snippets', {}).get('added'):
                doc_lines.append("\n### Added Code\n```")
                doc_lines.append("\n".join(change['code_snippets']['added'][:5]))
                doc_lines.append("```\n")
        
        return "\n".join(doc_lines)
    
    def _extract_code_snippets(
        self, 
        documentation: str, 
        structured_changes: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Extract code snippets from documentation."""
        snippets = []
        
        # Extract from markdown code blocks
        import re
        code_blocks = re.findall(r'```(\w+)?\n(.*?)```', documentation, re.DOTALL)
        
        for i, (lang, code) in enumerate(code_blocks):
            snippets.append({
                'id': f'snippet_{i}',
                'code': code.strip(),
                'language': lang or 'python',
                'source': 'documentation'
            })
        
        # Also include snippets from structured changes
        for change in structured_changes.get('changes', []):
            added_code = change.get('code_snippets', {}).get('added', [])
            if added_code:
                snippets.append({
                    'id': f'change_{change["file_path"]}',
                    'code': '\n'.join(added_code[:20]),
                    'language': change.get('language', 'python'),
                    'source': 'code_change'
                })
        
        return snippets
    
    def _execute_code_snippets(
        self, 
        code_snippets: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """Execute code snippets using Daytona."""
        results = self.daytona.execute_code_snippets(code_snippets)
        
        # Format results
        formatted_results = []
        for snippet in code_snippets:
            snippet_id = snippet['id']
            result = results.get(snippet_id)
            
            formatted_results.append({
                'id': snippet_id,
                'code': snippet['code'],
                'language': snippet['language'],
                'execution_result': {
                    'success': result.success if result else False,
                    'exit_code': result.exit_code if result else -1,
                    'output': result.output if result else '',
                    'error': result.error if result else None
                } if result else None
            })
        
        return formatted_results
    
    def _self_correct(
        self,
        documentation: str,
        structured_changes: Dict[str, Any],
        evaluation: Any,
        execution_results: List[Dict[str, Any]]
    ) -> tuple[str, Any]:
        """Self-correction loop using Gemini."""
        attempts = 0
        max_attempts = config.max_self_correction_attempts
        
        while attempts < max_attempts and evaluation.overall_score < config.min_doc_quality_score:
            attempts += 1
            
            # Create correction prompt
            correction_prompt = f"""The following documentation was evaluated and received a score of {evaluation.overall_score:.2f}.

Issues identified:
{chr(10).join(evaluation.issues)}

Feedback:
{chr(10).join(evaluation.feedback)}

Original documentation:
{documentation}

Please revise the documentation to address these issues. Generate improved documentation:"""
            
            if self.gemini_client:
                try:
                    response = self.gemini_client.generate_content(correction_prompt)
                    documentation = response.text
                except Exception as e:
                    sys.stderr.write(f"Error in self-correction: {e}\n")
                    sys.stderr.flush()
                    break
            
            # Re-evaluate
            evaluation = self.galileo.evaluate_documentation(
                documentation,
                code_context=json.dumps(structured_changes),
                code_snippets=execution_results
            )
        
        return documentation, evaluation
    
    def _determine_doc_path(self, structured_changes: Dict[str, Any]) -> str:
        """Determine documentation file path based on changes."""
        changes = structured_changes.get('changes', [])
        if not changes:
            return "README.md"
        
        # Use the first changed file's directory
        first_file = changes[0]['file_path']
        if '/' in first_file:
            doc_dir = '/'.join(first_file.split('/')[:-1])
            return f"{doc_dir}/DOCUMENTATION.md"
        
        return "DOCUMENTATION.md"
    
    def cleanup(self):
        """Cleanup resources."""
        self.daytona.cleanup()

