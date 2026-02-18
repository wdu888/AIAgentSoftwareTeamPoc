"""
Tool Registry

Central registry for discovering and using agent tools.
"""

from typing import Dict, List, Optional, Type
from .base import Tool, ToolContext, ToolResult


class ToolRegistry:
    """
    Registry for agent tools.
    
    Tools are registered by name and can be discovered and executed
    by agents.
    """
    
    _instance: Optional['ToolRegistry'] = None
    _tools: Dict[str, Tool]
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tools = {}
        return cls._instance
    
    @classmethod
    def reset(cls):
        """Reset the registry (for testing)"""
        cls._instance = None
    
    def register(self, tool: Tool):
        """
        Register a tool instance.
        
        Args:
            tool: Tool instance to register
        """
        self._tools[tool.name] = tool
    
    def register_class(self, tool_class: Type[Tool], **kwargs):
        """
        Register a tool class (instantiates with kwargs).
        
        Args:
            tool_class: Tool class to instantiate and register
            **kwargs: Arguments to pass to tool constructor
        """
        tool = tool_class(**kwargs)
        self.register(tool)
        return tool
    
    def get(self, name: str) -> Optional[Tool]:
        """
        Get a tool by name.
        
        Args:
            name: Tool name
            
        Returns:
            Tool instance or None if not found
        """
        return self._tools.get(name)
    
    def execute(self, name: str, context: ToolContext, **kwargs) -> ToolResult:
        """
        Execute a tool by name.
        
        Args:
            name: Tool name
            context: Tool context
            **kwargs: Tool-specific parameters
            
        Returns:
            ToolResult from tool execution
            
        Raises:
            KeyError: If tool not found
        """
        tool = self.get(name)
        if tool is None:
            return ToolResult.fail(f"Tool not found: {name}")
        return tool.execute(context, **kwargs)
    
    def list_tools(self) -> List[str]:
        """List all registered tool names"""
        return list(self._tools.keys())
    
    def get_tool_info(self, name: str) -> Optional[Dict]:
        """
        Get information about a tool.
        
        Args:
            name: Tool name
            
        Returns:
            Dict with tool info or None
        """
        tool = self.get(name)
        if tool is None:
            return None
        return {
            'name': tool.name,
            'description': tool.description,
            'class': tool.__class__.__name__
        }
    
    def __contains__(self, name: str) -> bool:
        """Check if tool is registered"""
        return name in self._tools
    
    def __len__(self) -> int:
        """Get number of registered tools"""
        return len(self._tools)


# Global registry instance
def get_registry() -> ToolRegistry:
    """Get the global tool registry"""
    return ToolRegistry()
