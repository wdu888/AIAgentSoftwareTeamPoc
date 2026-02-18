"""
Code Cleaner Tool

Cleans AI-generated code by removing markdown formatting,
code fences, and other artifacts.
"""

import re
from typing import List, Dict, Tuple
from ..base import Tool, ToolContext, ToolResult


class CodeCleanerTool(Tool):
    """
    Tool for cleaning AI-generated code.
    
    Removes:
    - Markdown code fences (```)
    - Markdown headers (##, ###)
    - File markers and comments that aren't valid code
    - Leading/trailing whitespace
    """
    
    def __init__(self):
        super().__init__(
            name="code_cleaner",
            description="Cleans AI-generated code by removing markdown formatting"
        )
    
    def execute(self, context: ToolContext, code: str = None, language: str = "auto") -> ToolResult:
        """
        Clean AI-generated code.
        
        Args:
            context: Tool context
            code: Code to clean (if not provided, uses context.working_files)
            language: Language hint ('csharp', 'python', 'auto')
            
        Returns:
            ToolResult with cleaned code
        """
        if code is None:
            return ToolResult.fail("No code provided to clean")
        
        try:
            # Auto-detect language if needed
            if language == "auto":
                language = self._detect_language(code)
            
            # Clean the code
            cleaned = self._clean_code(code, language)
            
            return ToolResult.ok(
                "Code cleaned successfully",
                data={'cleaned_code': cleaned, 'language': language}
            )
        except Exception as e:
            return ToolResult.fail(f"Error cleaning code: {str(e)}")
    
    def _detect_language(self, code: str) -> str:
        """Detect programming language from code content"""
        code_lower = code.lower()
        
        # C# indicators
        if any(x in code for x in ['namespace ', 'using System;', 'public class', 'static void Main']):
            return 'csharp'
        
        # Python indicators
        if 'def ' in code and ('import ' in code or 'class ' in code):
            return 'python'
        
        # JavaScript indicators
        if 'function ' in code or 'const ' in code or 'let ' in code:
            return 'javascript'
        
        # Java indicators
        if 'public static void main' in code and 'String[] args' in code:
            return 'java'
        
        return 'unknown'
    
    def _clean_code(self, code: str, language: str) -> str:
        """Clean code based on language"""
        # Remove markdown code fences
        code = re.sub(r'```[a-z]*\n', '\n', code)
        code = re.sub(r'```\n?', '', code)

        # Remove markdown headers that appear in code
        code = re.sub(r'^##+\s+', '', code, flags=re.MULTILINE)

        # Remove file markers like "## Filename.cs" or "// File: xxx.cs"
        code = re.sub(r'^##\s*`?[\w\.]+`?\s*$', '', code, flags=re.MULTILINE)
        code = re.sub(r'^//\s*(Filename|File):\s*[\w\.]+\s*$', '', code, flags=re.MULTILINE)

        # Remove "Here's..." introductory text
        code = re.sub(r"^Here's.*?\n+", '', code, flags=re.IGNORECASE | re.MULTILINE)
        code = re.sub(r"^Below is.*?\n+", '', code, flags=re.IGNORECASE | re.MULTILINE)
        
        # Remove AI response preamble and markdown documentation
        # Filter out lines that are clearly documentation, not code
        lines = code.split('\n')
        filtered_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            # Always keep using statements and namespace declarations
            if stripped.startswith('using ') or stripped.startswith('namespace '):
                filtered_lines.append(line)
                continue
            
            # Skip markdown headers
            if stripped.startswith('# ') or stripped.startswith('## ') or stripped.startswith('### '):
                continue
            
            # Skip list items
            if stripped.startswith('- ') or stripped.startswith('* '):
                continue
            
            # Skip emoji-prefixed lines
            if stripped.startswith('✅') or stripped.startswith('🧪') or stripped.startswith('📁'):
                continue
            
            # Skip AI role descriptions
            if stripped.startswith('As a ') or stripped.startswith('I will'):
                continue
            
            # Keep the line
            filtered_lines.append(line)
        
        code = '\n'.join(filtered_lines)

        # Language-specific cleaning
        if language == 'csharp':
            code = self._clean_csharp(code)
        elif language == 'python':
            code = self._clean_python(code)

        # Clean up multiple blank lines
        code = re.sub(r'\n\s*\n\s*\n', '\n\n', code)

        # Trim whitespace
        code = code.strip()

        return code
    
    def _clean_csharp(self, code: str) -> str:
        """Clean C# specific artifacts"""
        # Remove markdown code fences first
        code = re.sub(r'```[a-z]*\n', '\n', code)
        code = re.sub(r'```\n?', '', code)
        
        # Remove markdown headers that appear in code
        code = re.sub(r'^##+\s+', '', code, flags=re.MULTILINE)
        
        # Remove file markers like "## Filename.cs" or "// File: xxx.cs"
        code = re.sub(r'^##\s*`?[\w\.]+`?\s*$', '', code, flags=re.MULTILINE)
        code = re.sub(r'^//\s*(Filename|File):\s*[\w\.]+\s*$', '', code, flags=re.MULTILINE)
        
        # Remove "Here's..." introductory text
        code = re.sub(r"^Here's.*?\n+", '', code, flags=re.IGNORECASE | re.MULTILINE)
        code = re.sub(r"^Below is.*?\n+", '', code, flags=re.IGNORECASE | re.MULTILINE)
        
        # Clean up multiple blank lines but preserve single ones
        code = re.sub(r'\n\s*\n\s*\n', '\n\n', code)
        
        # Trim whitespace but preserve structure
        code = code.strip()
        
        # Add common using statements if missing
        code = self._ensure_using_statements(code)
        
        return code
    
    def _ensure_using_statements(self, code: str) -> str:
        """Add common using statements if they're missing and the code uses related types"""
        if not code:
            return code
        
        # Check if code already has using statements
        has_usings = 'using ' in code.split('\n')[0:5]
        if has_usings:
            return code
        
        # Common using statements to add
        needed_usings = []
        
        # Check for Console usage
        if 'Console.' in code:
            needed_usings.append('using System;')
        
        # Check for LINQ usage
        if 'IEnumerable' in code or '.ToList()' in code or '.Select(' in code:
            needed_usings.append('using System.Linq;')
        if 'List<' in code or 'Dictionary<' in code:
            needed_usings.append('using System.Collections.Generic;')
        
        # Check for Exception types
        if 'ArgumentNullException' in code or 'ArgumentException' in code:
            needed_usings.append('using System;')
        
        # Check for Regex usage
        if 'Regex.' in code or 'Regex.IsMatch' in code:
            needed_usings.append('using System.Text.RegularExpressions;')
        
        # Check for Task/async usage
        if 'Task<' in code or 'async ' in code:
            needed_usings.append('using System.Threading.Tasks;')
        
        # Check for NUnit test attributes
        if '[Test]' in code or '[TestFixture]' in code or '[TestCase]' in code:
            needed_usings.append('using NUnit.Framework;')
        
        # Check for Moq usage
        if 'Mock<' in code or '.Object' in code and 'Moq' in code:
            needed_usings.append('using Moq;')
        
        if needed_usings:
            # Remove duplicates and add at the beginning
            unique_usings = list(dict.fromkeys(needed_usings))
            using_block = '\n'.join(unique_usings) + '\n'
            code = using_block + '\n' + code
        
        return code
    
    def _clean_python(self, code: str) -> str:
        """Clean Python specific artifacts"""
        # Remove markdown backticks
        lines = code.split('\n')
        cleaned_lines = []
        
        for line in lines:
            if line.strip().startswith('`') and line.strip().endswith('`'):
                line = line.strip('`').strip()
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)


class CodeSplitterTool(Tool):
    """
    Tool for splitting AI-generated code into separate files.
    
    Detects file boundaries based on:
    - File markers in comments
    - Namespace/class declarations
    - Language-specific patterns
    """
    
    def __init__(self):
        super().__init__(
            name="code_splitter",
            description="Splits AI-generated code into separate files"
        )
    
    def execute(self, context: ToolContext, code: str = None, language: str = "auto") -> ToolResult:
        """
        Split code into files.
        
        Args:
            context: Tool context
            code: Code to split
            language: Language hint
            
        Returns:
            ToolResult with dict of {filename: content}
        """
        if code is None:
            return ToolResult.fail("No code provided to split")
        
        try:
            if language == "auto":
                # Import here to avoid circular dependency
                cleaner = CodeCleanerTool()
                language = cleaner._detect_language(code)
            
            files = self._split_code(code, language)
            
            return ToolResult.ok(
                f"Code split into {len(files)} files",
                data={'files': files, 'language': language}
            )
        except Exception as e:
            return ToolResult.fail(f"Error splitting code: {str(e)}")
    
    def _split_code(self, code: str, language: str) -> Dict[str, str]:
        """Split code into files based on language"""
        files = {}
        
        if language == 'csharp':
            files = self._split_csharp(code)
        elif language == 'python':
            files = self._split_python(code)
        else:
            # Default: treat as single file
            files['main' + self._get_extension(language)] = code
        
        return files
    
    def _split_csharp(self, code: str) -> Dict[str, str]:
        """Split C# code into files"""
        files = {}
        
        # First, check if this looks like test code (contains NUnit attributes)
        is_test_code = any(x in code for x in [
            '[TestFixture]', '[Test]', '[TestCase]', 
            'NUnit', 'Assert.', 'Tests'
        ])
        
        # Pattern 1: Look for file markers like "// File: xxx.cs"
        file_pattern = r'//\s*File:\s*([\w\.]+\.cs)\s*\n'
        matches = list(re.finditer(file_pattern, code, re.IGNORECASE))
        
        if matches:
            # Split by file markers
            for i, match in enumerate(matches):
                filename = match.group(1)
                start = match.end()
                end = matches[i + 1].start() if i + 1 < len(matches) else len(code)
                content = code[start:end].strip()
                
                files[filename] = content
        else:
            # Pattern 2: Split by namespace/class declarations
            # Find all class declarations
            class_pattern = r'(?:public\s+)?(?:static\s+)?class\s+(\w+)'
            class_matches = list(re.finditer(class_pattern, code))
            
            if class_matches:
                for i, match in enumerate(class_matches):
                    class_name = match.group(1)
                    start = match.start()
                    
                    # Find end of this class
                    brace_count = 0
                    end = start
                    started = False
                    
                    for j, char in enumerate(code[start:]):
                        if char == '{':
                            brace_count += 1
                            started = True
                        elif char == '}':
                            brace_count -= 1
                        
                        if started and brace_count == 0:
                            end = start + j + 1
                            break
                    
                    if end == start:
                        end = len(code)
                    
                    content = code[start:end].strip()
                    
                    # Determine filename based on class name and content
                    if is_test_code or class_name.endswith('Tests') or class_name.endswith('Test'):
                        filename = f"{class_name}.cs"
                    elif class_name == 'Program':
                        filename = "Program.cs"
                    else:
                        filename = f"{class_name}.cs"
                    
                    files[filename] = content
            else:
                # Pattern 3: Check if entire code is test code
                if is_test_code:
                    # Try to find test class name
                    test_match = re.search(r'public\s+class\s+(\w+Tests)', code)
                    if test_match:
                        files[f"{test_match.group(1)}.cs"] = code
                    else:
                        files["UnitTests.cs"] = code
                else:
                    # Default: save as Program.cs for console apps
                    files["Program.cs"] = code
        
        return files
    
    def _split_python(self, code: str) -> Dict[str, str]:
        """Split Python code into files"""
        files = {}
        
        # Look for file markers
        file_pattern = r'#\s*File:\s*([\w\.]+\.py)\s*\n'
        matches = list(re.finditer(file_pattern, code, re.IGNORECASE))
        
        if matches:
            for i, match in enumerate(matches):
                filename = match.group(1)
                start = match.end()
                end = matches[i + 1].start() if i + 1 < len(matches) else len(code)
                files[filename] = code[start:end].strip()
        else:
            # Single file
            files['main.py'] = code
        
        return files
    
    def _get_extension(self, language: str) -> str:
        """Get file extension for language"""
        extensions = {
            'csharp': '.cs',
            'python': '.py',
            'javascript': '.js',
            'java': '.java',
            'typescript': '.ts'
        }
        return extensions.get(language, '.txt')
