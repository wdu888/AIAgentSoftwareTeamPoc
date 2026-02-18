# Agent Tools Architecture

## Overview

The AI Agent Software Team uses a **tool-based architecture** where specialized tools are available for agents to accomplish specific tasks. This design makes the system:

- **Extensible**: Easy to add new tools for new languages or tasks
- **Maintainable**: Each tool is independent and testable
- **Reusable**: Tools can be used across different agents
- **Language-agnostic**: Support for multiple programming languages

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AIAgentTeam                               │
│                     (Orchestrator)                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    ToolRegistry                              │
│              (Central tool discovery)                        │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   Parsers   │  │ Generators  │  │  Utilities  │
│             │  │             │  │             │
│ - C#        │  │ - C#        │  │ - Code      │
│ - Python    │  │ - Python    │  │   Cleaner   │
│ - JS/TS     │  │ - Java      │  │ - File I/O  │
│ - Java      │  │ - Go        │  │ - Validators│
└─────────────┘  └─────────────┘  └─────────────┘
```

## Directory Structure

```
src/
├── ai_agent_team.py          # Main orchestrator
├── tools/                     # Agent tools
│   ├── __init__.py           # Package exports
│   ├── base.py               # Tool interfaces
│   ├── registry.py           # Tool registry
│   ├── parsers/              # Code parsers
│   │   ├── __init__.py
│   │   └── code_cleaner.py   # Code cleaning & splitting
│   ├── generators/           # Project generators
│   │   ├── __init__.py
│   │   ├── csharp_generator.py
│   │   └── python_generator.py
│   └── utilities/            # Common utilities
│       ├── __init__.py
│       └── code_cleaner.py
└── integrations/             # External integrations
    ├── github.py
    ├── jira.py
    └── azure_devops.py
```

## Core Components

### 1. Tool Base Class

All tools inherit from `Tool`:

```python
from tools.base import Tool, ToolContext, ToolResult

class MyCustomTool(Tool):
    def __init__(self):
        super().__init__(
            name="my_custom_tool",
            description="Does something useful"
        )
    
    def execute(self, context: ToolContext, **kwargs) -> ToolResult:
        # Tool implementation
        return ToolResult.ok("Success", data={'result': 'value'})
```

### 2. ToolContext

Provides context to all tools:

```python
context = ToolContext(
    project_dir="./output",
    api_key="...",
    working_files={'file.py': 'content'},
    metadata={'requirement': '...'}
)
```

### 3. ToolResult

Standardized result format:

```python
# Success
ToolResult.ok("Message", data={'key': 'value'}, files_created=['file.py'])

# Failure
ToolResult.fail("Error message", errors=['error1', 'error2'])
```

### 4. ToolRegistry

Central registry for tool discovery:

```python
from tools import get_registry, register_default_tools

# Get registry
registry = get_registry()

# Register default tools
register_default_tools(registry)

# Execute a tool
context = ToolContext(project_dir="./output")
result = registry.execute("code_cleaner", context, code=generated_code)
```

## Available Tools

### CodeCleanerTool

Cleans AI-generated code by removing markdown formatting.

```python
from tools import CodeCleanerTool, ToolContext

tool = CodeCleanerTool()
context = ToolContext(project_dir="./output")
result = tool.execute(context, code=ai_generated_code, language="csharp")

if result.success:
    clean_code = result.data['cleaned_code']
```

### CodeSplitterTool

Splits AI-generated code into separate files.

```python
from tools import CodeSplitterTool, ToolContext

tool = CodeSplitterTool()
context = ToolContext(project_dir="./output")
result = tool.execute(context, code=multi_file_code, language="csharp")

if result.success:
    files = result.data['files']  # Dict[filename, content]
```

### CSharpProjectGeneratorTool

Creates complete Visual Studio solution structure.

```python
from tools import CSharpProjectGeneratorTool, ToolContext

tool = CSharpProjectGeneratorTool()
context = ToolContext(project_dir="./MyProject")
result = tool.execute(
    context,
    code=main_code,
    test_code=test_code,
    project_name="MyApp"
)

# Creates:
# - MyProject.sln
# - MyProject/MyProject.csproj
# - MyProject/*.cs
# - MyProject.Tests/MyProject.Tests.csproj
# - MyProject.Tests/*.cs
# - .gitignore
# - README.md
```

### PythonProjectGeneratorTool

Creates Python project structure.

```python
from tools import PythonProjectGeneratorTool, ToolContext

tool = PythonProjectGeneratorTool()
context = ToolContext(project_dir="./my_project")
result = tool.execute(
    context,
    code=main_code,
    test_code=test_code,
    project_name="my_app"
)

# Creates:
# - my_project/my_project/__init__.py
# - my_project/my_project/*.py
# - my_project/tests/__init__.py
# - my_project/tests/test_*.py
# - my_project/requirements.txt
# - my_project/setup.py
# - my_project/.gitignore
# - my_project/README.md
```

## Creating Custom Tools

### Example: JavaScript Project Generator

```python
# tools/generators/javascript_generator.py
from tools.base import Tool, ToolContext, ToolResult
import os

class JavaScriptProjectGeneratorTool(Tool):
    def __init__(self):
        super().__init__(
            name="javascript_project_generator",
            description="Generates Node.js project structure"
        )
    
    def execute(self, context: ToolContext, code: str = None, **kwargs) -> ToolResult:
        project_dir = context.project_dir
        
        # Create package.json
        package_json = {
            "name": "generated-app",
            "version": "1.0.0",
            "main": "index.js"
        }
        
        # Write files...
        
        return ToolResult.ok(
            "JavaScript project created",
            files_created=['package.json', 'index.js']
        )

# Register the tool
from tools import get_registry
registry = get_registry()
registry.register(JavaScriptProjectGeneratorTool())
```

## Usage in Agents

Agents use tools through the registry:

```python
class CodingAgent:
    def __init__(self, tool_registry):
        self.registry = tool_registry
    
    def generate_code(self, requirement: str) -> dict:
        # Generate code using LLM...
        code = llm.generate(requirement)
        
        # Use tools to process the code
        context = ToolContext(project_dir="./output")
        
        # Clean the code
        clean_result = self.registry.execute(
            "code_cleaner",
            context,
            code=code
        )
        
        # Generate project structure
        gen_result = self.registry.execute(
            "csharp_project_generator",
            context,
            code=clean_result.data['cleaned_code']
        )
        
        return gen_result
```

## Benefits

1. **Separation of Concerns**: Tools handle specific tasks, agents orchestrate
2. **Testability**: Each tool can be tested independently
3. **Extensibility**: Add new languages by creating new generator tools
4. **Reusability**: Same tools used by different agents
5. **Maintainability**: Fix bugs in one place, affects all users

## Future Enhancements

- **More language support**: Java, Go, TypeScript, Rust
- **Additional tools**:
  - Code formatter
  - Linter integration
  - Test runner
  - Dependency analyzer
- **Tool chaining**: Combine multiple tools in pipelines
- **Tool discovery**: Agents can discover available tools dynamically
