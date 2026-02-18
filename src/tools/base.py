"""
Base Tool Interface and Classes

All agent tools should inherit from the Tool base class.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import os


@dataclass
class ToolContext:
    """Context information available to all tools"""
    project_dir: str
    api_key: Optional[str] = None
    working_files: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_file(self, filepath: str) -> Optional[str]:
        """Get content of a file from working files"""
        return self.working_files.get(filepath)
    
    def set_file(self, filepath: str, content: str):
        """Set content of a file in working files"""
        self.working_files[filepath] = content


@dataclass
class ToolResult:
    """Result from executing a tool"""
    success: bool
    message: str
    data: Optional[Any] = None
    files_created: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    @classmethod
    def ok(cls, message: str, data: Any = None, files_created: List[str] = None):
        """Create a successful result"""
        return cls(
            success=True,
            message=message,
            data=data,
            files_created=files_created or []
        )
    
    @classmethod
    def fail(cls, message: str, errors: List[str] = None):
        """Create a failed result"""
        return cls(
            success=False,
            message=message,
            errors=errors or [message]
        )


class Tool(ABC):
    """
    Abstract base class for all agent tools.
    
    Tools are reusable components that agents can use to accomplish
    specific tasks like parsing code, generating files, etc.
    """
    
    def __init__(self, name: str = None, description: str = None):
        self.name = name or self.__class__.__name__
        self.description = description or ""
    
    @abstractmethod
    def execute(self, context: ToolContext, **kwargs) -> ToolResult:
        """
        Execute the tool with the given context and parameters.
        
        Args:
            context: ToolContext with project info and working files
            **kwargs: Tool-specific parameters
            
        Returns:
            ToolResult with success status and data
        """
        pass
    
    def __str__(self):
        return f"{self.name}: {self.description}"


class FileTool(Tool):
    """Base class for tools that work with files"""
    
    def _ensure_dir(self, filepath: str):
        """Ensure directory exists for a file path"""
        directory = os.path.dirname(filepath)
        if directory:
            os.makedirs(directory, exist_ok=True)
    
    def _read_file(self, filepath: str) -> str:
        """Read file content"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _write_file(self, filepath: str, content: str):
        """Write content to file"""
        self._ensure_dir(filepath)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
