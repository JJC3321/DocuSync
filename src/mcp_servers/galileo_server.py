"""Galileo MCP Server - Evaluates documentation quality."""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import json


@dataclass
class EvaluationResult:
    """Result of documentation evaluation."""
    accuracy_score: float  # 0.0 to 1.0
    tone_score: float  # 0.0 to 1.0
    clarity_score: float  # 0.0 to 1.0
    overall_score: float  # 0.0 to 1.0
    feedback: List[str]
    issues: List[str]


class GalileoServer:
    """MCP Server for Galileo - evaluates documentation quality."""
    
    def __init__(self, api_key: Optional[str] = None, project_id: Optional[str] = None):
        self.api_key = api_key
        self.project_id = project_id
    
    def evaluate_documentation(
        self, 
        documentation: str, 
        code_context: Optional[str] = None,
        code_snippets: Optional[List[Dict[str, Any]]] = None
    ) -> EvaluationResult:
        """
        Evaluate documentation quality.
        
        Args:
            documentation: Documentation text to evaluate
            code_context: Related code context
            code_snippets: List of code snippets with execution results
            
        Returns:
            EvaluationResult with scores and feedback
        """
        # Basic evaluation logic
        # In production, this would call Galileo.ai API
        
        accuracy_score = self._evaluate_accuracy(documentation, code_context, code_snippets)
        tone_score = self._evaluate_tone(documentation)
        clarity_score = self._evaluate_clarity(documentation)
        overall_score = (accuracy_score + tone_score + clarity_score) / 3.0
        
        feedback = []
        issues = []
        
        if accuracy_score < 0.7:
            issues.append("Documentation may contain inaccuracies")
            feedback.append("Review code examples for correctness")
        
        if tone_score < 0.7:
            issues.append("Tone may not be appropriate")
            feedback.append("Consider making the tone more professional and clear")
        
        if clarity_score < 0.7:
            issues.append("Documentation clarity could be improved")
            feedback.append("Add more examples and explanations")
        
        return EvaluationResult(
            accuracy_score=accuracy_score,
            tone_score=tone_score,
            clarity_score=clarity_score,
            overall_score=overall_score,
            feedback=feedback,
            issues=issues
        )
    
    def _evaluate_accuracy(
        self, 
        documentation: str, 
        code_context: Optional[str],
        code_snippets: Optional[List[Dict[str, Any]]]
    ) -> float:
        """Evaluate documentation accuracy."""
        score = 0.8  # Base score
        
        # Check if code snippets match execution results
        if code_snippets:
            for snippet in code_snippets:
                exec_result = snippet.get('execution_result')
                if exec_result and exec_result.get('success'):
                    score += 0.05
                elif exec_result and not exec_result.get('success'):
                    score -= 0.1
        
        # Check for code examples in documentation
        if '```' in documentation or 'code' in documentation.lower():
            score += 0.05
        
        return min(1.0, max(0.0, score))
    
    def _evaluate_tone(self, documentation: str) -> float:
        """Evaluate documentation tone."""
        score = 0.7  # Base score
        
        # Check for professional language
        professional_words = ['function', 'method', 'parameter', 'returns', 'example']
        unprofessional_words = ['gonna', 'wanna', 'kinda', 'yeah']
        
        doc_lower = documentation.lower()
        for word in professional_words:
            if word in doc_lower:
                score += 0.02
        
        for word in unprofessional_words:
            if word in doc_lower:
                score -= 0.05
        
        return min(1.0, max(0.0, score))
    
    def _evaluate_clarity(self, documentation: str) -> float:
        """Evaluate documentation clarity."""
        score = 0.7  # Base score
        
        # Check for structure
        if '# ' in documentation or '## ' in documentation:
            score += 0.1  # Has headings
        
        # Check for examples
        if 'example' in documentation.lower() or '```' in documentation:
            score += 0.1
        
        # Check length (not too short, not too long)
        word_count = len(documentation.split())
        if 50 <= word_count <= 1000:
            score += 0.05
        
        return min(1.0, max(0.0, score))
    
    def batch_evaluate(self, documentation_list: List[str]) -> List[EvaluationResult]:
        """Evaluate multiple documentation pieces."""
        return [self.evaluate_documentation(doc) for doc in documentation_list]

