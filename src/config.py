"""Configuration management for the Live Document Editor."""
import os
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


class Config(BaseModel):
    """Application configuration."""
    
    # Gemini Configuration
    gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
    
    # Daytona Configuration
    daytona_api_key: Optional[str] = os.getenv("DAYTONA_API_KEY")
    daytona_api_url: Optional[str] = os.getenv("DAYTONA_API_URL", "https://app.daytona.io/api")
    
    # Galileo Configuration
    galileo_api_key: Optional[str] = os.getenv("GALILEO_API_KEY")
    galileo_project_id: Optional[str] = os.getenv("GALILEO_PROJECT_ID")
    
    # CodeRabbit Configuration
    coderabbit_api_key: Optional[str] = os.getenv("CODERABBIT_API_KEY")
    coderabbit_api_url: Optional[str] = os.getenv("CODERABBIT_API_URL", "https://api.coderabbit.ai")
    
    # Git Configuration
    git_repo_path: Optional[str] = os.getenv("GIT_REPO_PATH", ".")
    git_branch: str = os.getenv("GIT_BRANCH", "main")
    
    # Server Configuration
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    
    # Quality Thresholds
    min_doc_quality_score: float = float(os.getenv("MIN_DOC_QUALITY_SCORE", "0.7"))
    max_self_correction_attempts: int = int(os.getenv("MAX_SELF_CORRECTION_ATTEMPTS", "3"))


config = Config()

