"""
Python Project Generator Tool

Creates Python project structure with tests.
"""

import os
import re
from typing import Dict
from ..base import Tool, ToolContext, ToolResult
from ..utilities.code_cleaner import CodeCleanerTool, CodeSplitterTool


class PythonProjectGeneratorTool(Tool):
    """
    Tool for generating Python project structures.
    
    Creates:
    - Main package directory
    - Test directory with pytest
    - setup.py or pyproject.toml
    - requirements.txt
    - .gitignore
    - README.md
    """
    
    def __init__(self):
        super().__init__(
            name="python_project_generator",
            description="Generates complete Python project structure"
        )
    
    def execute(
        self,
        context: ToolContext,
        code: str = None,
        test_code: str = None,
        project_name: str = None,
        use_poetry: bool = False
    ) -> ToolResult:
        """
        Generate Python project structure.
        
        Args:
            context: Tool context with project_dir
            code: Main project code
            test_code: Test code
            project_name: Name for the project (uses folder name if not provided)
            use_poetry: Whether to use Poetry for dependency management
            
        Returns:
            ToolResult with list of created files
        """
        try:
            project_dir = context.project_dir
            
            # Use folder name as project name if not provided
            if project_name is None:
                project_name = self._get_folder_name(project_dir)
            
            # Clean the code
            cleaner = CodeCleanerTool()
            if code:
                code_result = cleaner.execute(context, code=code, language="python")
                if code_result.success:
                    code = code_result.data['cleaned_code']
            
            if test_code:
                test_result = cleaner.execute(context, code=test_code, language="python")
                if test_result.success:
                    test_code = test_result.data['cleaned_code']
            
            # Split code into files
            splitter = CodeSplitterTool()
            files = {}
            test_files = {}
            
            if code:
                split_result = splitter.execute(context, code=code, language="python")
                if split_result.success:
                    files = split_result.data['files']
            
            if test_code:
                test_split_result = splitter.execute(context, code=test_code, language="python")
                if test_split_result.success:
                    test_files = test_split_result.data['files']
            
            # Create directory structure
            package_dir = os.path.join(project_dir, project_name)
            test_dir = os.path.join(project_dir, "tests")
            
            os.makedirs(package_dir, exist_ok=True)
            os.makedirs(test_dir, exist_ok=True)
            
            created_files = []
            
            # Create __init__.py files
            init_path = os.path.join(package_dir, "__init__.py")
            self._write_file(init_path, f'"""{project_name} package"""\\n')
            created_files.append(init_path)
            
            test_init_path = os.path.join(test_dir, "__init__.py")
            self._write_file(test_init_path, '"""Tests package"""\\n')
            created_files.append(test_init_path)
            
            # Write Python source files
            for filename, content in files.items():
                filepath = os.path.join(package_dir, filename)
                self._write_file(filepath, content)
                created_files.append(filepath)
            
            # Write test files
            for filename, content in test_files.items():
                # Ensure test filename starts with test_
                if not filename.startswith('test_'):
                    filename = f"test_{filename}"
                filepath = os.path.join(test_dir, filename)
                self._write_file(filepath, content)
                created_files.append(filepath)
            
            # Create requirements.txt
            req_path = os.path.join(project_dir, "requirements.txt")
            self._write_requirements(req_path)
            created_files.append(req_path)
            
            # Create setup.py or pyproject.toml
            if use_poetry:
                pyproject_path = os.path.join(project_dir, "pyproject.toml")
                self._write_pyproject(pyproject_path, project_name)
                created_files.append(pyproject_path)
            else:
                setup_path = os.path.join(project_dir, "setup.py")
                self._write_setup(setup_path, project_name)
                created_files.append(setup_path)
            
            # Create .gitignore
            gitignore_path = os.path.join(project_dir, ".gitignore")
            self._write_gitignore(gitignore_path)
            created_files.append(gitignore_path)
            
            # Create README
            readme_path = os.path.join(project_dir, "README.md")
            self._write_readme(readme_path, project_name)
            created_files.append(readme_path)
            
            return ToolResult.ok(
                f"Python project '{project_name}' created successfully",
                data={
                    'project_name': project_name,
                    'package_dir': package_dir,
                    'test_dir': test_dir
                },
                files_created=created_files
            )
            
        except Exception as e:
            return ToolResult.fail(f"Error generating Python project: {str(e)}")
    
    def _get_folder_name(self, project_dir: str) -> str:
        """
        Get project name from folder path.
        
        Args:
            project_dir: Full path to project directory
            
        Returns:
            Folder name sanitized for use as project name
        """
        import re
        # Get the last folder name
        folder_name = os.path.basename(os.path.normpath(project_dir))
        
        # If empty (root path), use parent folder
        if not folder_name:
            folder_name = os.path.basename(os.path.dirname(project_dir))
        
        # Sanitize: replace invalid chars with underscore, convert to lowercase
        folder_name = re.sub(r'[^a-zA-Z0-9_]', '_', folder_name).lower()
        
        # Ensure it starts with a letter
        if folder_name and not folder_name[0].isalpha():
            folder_name = 'app_' + folder_name
        
        # Default fallback
        if not folder_name:
            folder_name = 'generated_app'
        
        # Limit length
        return folder_name[:50]
    
    def _write_file(self, filepath: str, content: str):
        """Write content to file"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _write_requirements(self, filepath: str):
        """Write requirements.txt"""
        content = '''# Core dependencies
pytest>=7.0.0
pytest-cov>=4.0.0

# Add your dependencies below
# requests>=2.28.0
'''
        self._write_file(filepath, content)
    
    def _write_setup(self, filepath: str, project_name: str):
        """Write setup.py"""
        content = f'''from setuptools import setup, find_packages

setup(
    name="{project_name}",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        # Add dependencies here
    ],
    python_requires=">=3.8",
)
'''
        self._write_file(filepath, content)
    
    def _write_pyproject(self, filepath: str, project_name: str):
        """Write pyproject.toml for Poetry"""
        content = f'''[tool.poetry]
name = "{project_name}"
version = "0.1.0"
description = "Generated by AI Agent Software Team"
authors = ["AI Agent <ai@example.com>"]

[tool.poetry.dependencies]
python = "^3.8"

[tool.poetry.group.dev.dependencies]
pytest = "^7.0.0"
pytest-cov = "^4.0.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
'''
        self._write_file(filepath, content)
    
    def _write_gitignore(self, filepath: str):
        """Write .gitignore"""
        content = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
'''
        self._write_file(filepath, content)
    
    def _write_readme(self, filepath: str, project_name: str):
        """Write README.md"""
        content = f'''# {project_name}

Generated by AI Agent Software Team

## Installation

### Using pip
```bash
pip install -e .
```

### Using Poetry
```bash
poetry install
```

## Usage

```python
from {project_name} import main
```

## Development

### Run tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov={project_name}
```

## Project Structure

```
{project_name}/
├── {project_name}/
│   ├── __init__.py
│   └── *.py
├── tests/
│   ├── __init__.py
│   └── test_*.py
├── requirements.txt
├── setup.py
└── README.md
```
'''
        self._write_file(filepath, content)
