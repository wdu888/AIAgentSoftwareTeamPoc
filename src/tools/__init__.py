"""
Agent Tools Package

Tools that AI agents can use to accomplish specific tasks.

Usage:
    from tools import ToolRegistry, get_registry
    from tools.generators import CSharpProjectGeneratorTool
    from tools.utilities import CodeCleanerTool, CodeSplitterTool
    
    # Get registry
    registry = get_registry()
    
    # Register tools
    registry.register(CodeCleanerTool())
    registry.register(CSharpProjectGeneratorTool())
    
    # Execute tools
    from tools.base import ToolContext
    context = ToolContext(project_dir="./output")
    result = registry.execute("code_cleaner", context, code=generated_code)
"""

from .base import Tool, ToolResult, ToolContext, FileTool
from .registry import ToolRegistry, get_registry

# Import all tools for easy access
from .utilities.code_cleaner import CodeCleanerTool, CodeSplitterTool
from .generators.csharp_generator import CSharpProjectGeneratorTool
from .generators.python_generator import PythonProjectGeneratorTool

__all__ = [
    # Base classes
    'Tool',
    'ToolResult', 
    'ToolContext',
    'FileTool',
    'ToolRegistry',
    'get_registry',
    
    # Utility tools
    'CodeCleanerTool',
    'CodeSplitterTool',
    
    # Generator tools
    'CSharpProjectGeneratorTool',
    'PythonProjectGeneratorTool',
]


def register_default_tools(registry: ToolRegistry = None) -> ToolRegistry:
    """
    Register all default tools in the registry.
    
    Args:
        registry: Tool registry to use (creates new if not provided)
        
    Returns:
        ToolRegistry with tools registered
    """
    if registry is None:
        registry = get_registry()
    
    # Register utility tools
    registry.register(CodeCleanerTool())
    registry.register(CodeSplitterTool())
    
    # Register generator tools
    registry.register(CSharpProjectGeneratorTool())
    registry.register(PythonProjectGeneratorTool())
    
    return registry
