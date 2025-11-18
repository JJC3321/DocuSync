"""Git integration for monitoring changes and committing documentation."""
import git
from typing import Optional, List, Dict, Any
from pathlib import Path
import os
import sys


class GitHandler:
    """Handles Git operations for the live document editor."""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        self.repo = None
        self._initialize_repo()
    
    def _initialize_repo(self):
        """Initialize Git repository."""
        try:
            self.repo = git.Repo(self.repo_path)
        except git.exc.InvalidGitRepositoryError:
            # Try to initialize if not a git repo
            try:
                self.repo = git.Repo.init(self.repo_path)
            except Exception as e:
                sys.stderr.write(f"Error initializing Git repository: {e}\n")
                sys.stderr.flush()
                self.repo = None
    
    def get_diff(self, branch: str = "main", compare_branch: Optional[str] = None) -> str:
        """
        Get diff between branches or commits.
        
        Args:
            branch: Branch to compare from
            compare_branch: Branch to compare to (default: HEAD)
            
        Returns:
            Git diff content
        """
        if not self.repo:
            return ""
        
        try:
            if compare_branch:
                diff = self.repo.git.diff(compare_branch, branch)
            else:
                # Compare with HEAD
                diff = self.repo.git.diff(branch)
            
            return diff
        except Exception as e:
            sys.stderr.write(f"Error getting diff: {e}\n")
            sys.stderr.flush()
            return ""
    
    def get_uncommitted_changes(self) -> str:
        """Get uncommitted changes."""
        if not self.repo:
            return ""
        
        try:
            return self.repo.git.diff()
        except Exception as e:
            sys.stderr.write(f"Error getting uncommitted changes: {e}\n")
            sys.stderr.flush()
            return ""
    
    def commit_documentation(
        self, 
        file_path: str, 
        content: str, 
        commit_message: str = "docs: Update documentation"
    ) -> bool:
        """
        Commit documentation update.
        
        Args:
            file_path: Path to documentation file
            content: Documentation content
            commit_message: Commit message
            
        Returns:
            True if successful
        """
        if not self.repo:
            return False
        
        try:
            # Write file
            full_path = self.repo_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding='utf-8')
            
            # Stage file
            self.repo.index.add([file_path])
            
            # Commit
            self.repo.index.commit(commit_message)
            
            return True
        except Exception as e:
            sys.stderr.write(f"Error committing documentation: {e}\n")
            sys.stderr.flush()
            return False
    
    def push_changes(self, branch: str = "main", remote: str = "origin") -> bool:
        """Push changes to remote repository."""
        if not self.repo:
            return False
        
        try:
            origin = self.repo.remote(remote)
            origin.push(branch)
            return True
        except Exception as e:
            sys.stderr.write(f"Error pushing changes: {e}\n")
            sys.stderr.flush()
            return False
    
    def get_recent_commits(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent commit information."""
        if not self.repo:
            return []
        
        try:
            commits = []
            for commit in self.repo.iter_commits(max_count=limit):
                commits.append({
                    'hash': commit.hexsha,
                    'message': commit.message.strip(),
                    'author': commit.author.name,
                    'date': commit.committed_datetime.isoformat()
                })
            return commits
        except Exception as e:
            sys.stderr.write(f"Error getting commits: {e}\n")
            sys.stderr.flush()
            return []
    
    def watch_changes(self, callback, branch: str = "main"):
        """Watch for changes (simplified - in production use file watcher or webhooks)."""
        # This is a placeholder - in production, use watchdog or Git hooks
        pass

