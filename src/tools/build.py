"""
Build Tool for C# and Python Projects

Compiles generated solutions and provides error feedback for LLM-based bug fixing.
"""

import os
import subprocess
import re
from typing import Dict, List, Optional
from .base import Tool, ToolContext, ToolResult


class BuildTool(Tool):
    """
    Tool for building C# and Python projects.

    Supports:
    - C# (.NET CLI) - dotnet build
    - Python - syntax check and import validation
    """

    def __init__(self):
        super().__init__(
            name="build_tool",
            description="Builds C# solutions and Python projects, returns build errors for LLM fixing"
        )

    def execute(
        self,
        context: ToolContext,
        project_dir: str = None,
        language: str = "csharp",
        max_iterations: int = 5
    ) -> ToolResult:
        """
        Build the project and iterate until success or max iterations.

        Args:
            context: Tool context with project_dir
            project_dir: Directory containing the project (defaults to context.project_dir)
            language: Project language ('csharp' or 'python')
            max_iterations: Maximum build-fix iterations

        Returns:
            ToolResult with build status and errors
        """
        project_dir = project_dir or context.project_dir

        if language == "csharp":
            return self._build_csharp(context, project_dir, max_iterations)
        elif language == "python":
            return self._build_python(context, project_dir, max_iterations)
        else:
            return ToolResult.fail(f"Unsupported language: {language}")

    def _build_csharp(
        self,
        context: ToolContext,
        project_dir: str,
        max_iterations: int
    ) -> ToolResult:
        """
        Build C# solution with iterative error fixing.

        Args:
            context: Tool context
            project_dir: Directory containing .sln file
            max_iterations: Maximum build-fix iterations

        Returns:
            ToolResult with build output and errors
        """
        # Find .sln file
        sln_file = self._find_solution_file(project_dir)
        if not sln_file:
            return ToolResult.fail(f"No .sln file found in {project_dir}")

        print(f"\n[BUILD] Building solution: {sln_file}")

        all_errors = []
        build_output = ""
        success = False

        for iteration in range(1, max_iterations + 1):
            print(f"\n[BUILD] Attempt {iteration}/{max_iterations}...")

            # Run dotnet build
            result = subprocess.run(
                ["dotnet", "build", sln_file, "--no-incremental"],
                capture_output=True,
                text=True,
                timeout=120
            )

            build_output = result.stdout + result.stderr
            errors = self._parse_csharp_errors(build_output, project_dir)

            if result.returncode == 0:
                print(f"[BUILD] SUCCESS on attempt {iteration}!")
                success = True
                break
            else:
                print(f"[BUILD] FAILED with {len(errors)} error(s)")
                all_errors.extend(errors)

                # For now, we just report errors - the LLM will need to fix them
                # In a future enhancement, we could integrate with the LLM here
                if iteration < max_iterations:
                    print(f"[BUILD] Errors collected for LLM fixing...")
                    # Store errors in context for the LLM to access
                    context.metadata['build_errors'] = errors
                    context.metadata['build_output'] = build_output
                else:
                    print(f"[BUILD] Max iterations reached")

        # Clean up context
        errors_for_llm = all_errors[-5:] if len(all_errors) > 5 else all_errors

        if success:
            return ToolResult.ok(
                f"Build successful after {iteration} iteration(s)",
                data={
                    'success': True,
                    'iterations': iteration,
                    'build_output': build_output,
                    'errors': [],
                    'errors_for_llm': ""
                }
            )
        else:
            errors_text = self._format_errors_for_llm(errors_for_llm)
            result = ToolResult.fail(
                f"Build failed after {max_iterations} iterations"
            )
            # Add data to the result object
            result.data = {
                'success': False,
                'iterations': max_iterations,
                'build_output': build_output,
                'errors': all_errors,
                'errors_for_llm': errors_text
            }
            return result

    def _build_python(
        self,
        context: ToolContext,
        project_dir: str,
        max_iterations: int
    ) -> ToolResult:
        """
        Build (validate) Python project with iterative error fixing.

        Args:
            context: Tool context
            project_dir: Directory containing Python files
            max_iterations: Maximum build-fix iterations

        Returns:
            ToolResult with validation status and errors
        """
        print(f"\n[BUILD] Validating Python project: {project_dir}")

        all_errors = []
        success = True

        # Find all .py files
        py_files = []
        for root, dirs, files in os.walk(project_dir):
            # Skip __pycache__ and hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            for file in files:
                if file.endswith('.py'):
                    py_files.append(os.path.join(root, file))

        if not py_files:
            return ToolResult.fail(f"No Python files found in {project_dir}")

        for iteration in range(1, max_iterations + 1):
            print(f"\n[BUILD] Validation attempt {iteration}/{max_iterations}...")

            errors = []
            for py_file in py_files:
                # Syntax check
                result = subprocess.run(
                    ["python", "-m", "py_compile", py_file],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode != 0:
                    error_msg = self._parse_python_error(result.stderr, py_file)
                    errors.append(error_msg)

            if not errors:
                print(f"[BUILD] Python validation successful!")
                success = True
                break
            else:
                print(f"[BUILD] FAILED with {len(errors)} error(s)")
                all_errors.extend(errors)

                if iteration < max_iterations:
                    context.metadata['build_errors'] = errors
                else:
                    print(f"[BUILD] Max iterations reached")

        errors_for_llm = all_errors[-5:] if len(all_errors) > 5 else all_errors

        if success:
            return ToolResult.ok(
                f"Python validation successful",
                data={
                    'success': True,
                    'iterations': 1,
                    'errors': [],
                    'errors_for_llm': ""
                }
            )
        else:
            errors_text = self._format_errors_for_llm(errors_for_llm)
            return ToolResult.fail(
                f"Python validation failed",
                data={
                    'success': False,
                    'iterations': max_iterations,
                    'errors': all_errors,
                    'errors_for_llm': errors_text
                }
            )

    def _find_solution_file(self, project_dir: str) -> Optional[str]:
        """Find .sln file in directory"""
        for file in os.listdir(project_dir):
            if file.endswith('.sln'):
                return os.path.join(project_dir, file)
        return None

    def _parse_csharp_errors(self, build_output: str, project_dir: str) -> List[Dict]:
        """
        Parse C# build errors from output.

        Returns list of error dicts with file, line, column, code, message
        """
        errors = []
        # Pattern: filepath(line,column): error CS####: message
        pattern = r'([^\(]+)\((\d+),(\d+)\):\s+(error|warning)\s+(\w+\d+):\s+(.+)'

        for match in re.finditer(pattern, build_output):
            filepath, line, column, severity, code, message = match.groups()

            # Make path relative
            rel_path = os.path.relpath(filepath.strip(), project_dir)

            errors.append({
                'file': rel_path,
                'line': int(line),
                'column': int(column),
                'severity': severity,
                'code': code,
                'message': message.strip()
            })

        # Also catch errors without line numbers
        if not errors:
            # Look for general error patterns
            for line in build_output.split('\n'):
                if ' error ' in line.lower() and ': ' in line:
                    errors.append({
                        'file': 'unknown',
                        'line': 0,
                        'column': 0,
                        'severity': 'error',
                        'code': 'BUILD_ERROR',
                        'message': line.strip()
                    })

        return errors

    def _parse_python_error(self, error_output: str, filepath: str) -> Dict:
        """Parse Python syntax error"""
        # Pattern: File "path", line N
        pattern = r'File "([^"]+)", line (\d+)'
        match = re.search(pattern, error_output)

        if match:
            line_num = int(match.group(2))
            # Extract error message
            error_msg = error_output.split('\n')[-1].strip()

            return {
                'file': os.path.basename(filepath),
                'line': line_num,
                'column': 0,
                'severity': 'error',
                'code': 'SYNTAX_ERROR',
                'message': error_msg
            }

        return {
            'file': os.path.basename(filepath),
            'line': 0,
            'column': 0,
            'severity': 'error',
            'code': 'UNKNOWN',
            'message': error_output.strip()
        }

    def _format_errors_for_llm(self, errors: List[Dict]) -> str:
        """Format errors in a way that's easy for LLM to understand"""
        if not errors:
            return ""

        formatted = ["BUILD ERRORS (fix these in your code):"]
        formatted.append("=" * 60)

        for i, error in enumerate(errors, 1):
            formatted.append(f"\n{i}. {error['severity'].upper()} {error['code']}")
            formatted.append(f"   File: {error['file']}")
            if error['line'] > 0:
                formatted.append(f"   Line: {error['line']}")
            formatted.append(f"   Issue: {error['message']}")

        formatted.append("\n" + "=" * 60)
        formatted.append("\nPlease provide corrected code that fixes these build errors.")

        return "\n".join(formatted)


class BuildAndFixAgent:
    """
    Agent that builds code and iteratively fixes build errors with LLM help.

    This agent:
    1. Builds the generated solution
    2. If build fails, sends errors to LLM for fixing
    3. Applies the fixes
    4. Repeats until build succeeds or max iterations reached
    """

    def __init__(self, llm, max_iterations: int = 5):
        """
        Initialize the build and fix agent.

        Args:
            llm: LLM instance for fixing code
            max_iterations: Maximum build-fix iterations
        """
        self.llm = llm
        self.max_iterations = max_iterations
        self.build_tool = BuildTool()

    def build_and_fix(
        self,
        context: ToolContext,
        code: str,
        language: str = "csharp",
        project_dir: str = None
    ) -> tuple:
        """
        Build code and iteratively fix errors.

        Args:
            context: Tool context
            code: Original code that was generated
            language: Project language
            project_dir: Project directory

        Returns:
            Tuple of (success: bool, fixed_code: str, build_result: ToolResult)
        """
        project_dir = project_dir or context.project_dir
        current_code = code
        errors_for_llm = ""

        for iteration in range(1, self.max_iterations + 1):
            print(f"\n[BUILD & FIX] Iteration {iteration}/{self.max_iterations}")

            # First, save the code to files if this is a revision
            if iteration > 1:
                # Update working files
                context.working_files['current_code'] = current_code

            # Build the project
            build_result = self.build_tool.execute(
                context,
                project_dir=project_dir,
                language=language,
                max_iterations=1  # We control iterations at this level
            )

            if build_result.success:
                print(f"[BUILD & FIX] Build successful!")
                return True, current_code, build_result

            # Build failed - get errors for LLM
            errors_for_llm = build_result.data.get('errors_for_llm', '')

            if iteration >= self.max_iterations:
                print(f"[BUILD & FIX] Max iterations reached")
                return False, current_code, build_result

            # Ask LLM to fix the errors
            print(f"[BUILD & FIX] Requesting LLM to fix errors...")
            fixed_code = self._ask_llm_to_fix(current_code, errors_for_llm, language)

            if not fixed_code or fixed_code == current_code:
                print(f"[BUILD & FIX] LLM did not provide different code")
                # Try one more time with stronger prompt
                fixed_code = self._ask_llm_to_fix(
                    current_code,
                    errors_for_llm + "\n\nCRITICAL: You MUST provide corrected code!",
                    language
                )

            current_code = fixed_code

        return False, current_code, build_result

    def _ask_llm_to_fix(self, code: str, errors: str, language: str) -> str:
        """Ask LLM to fix build errors"""
        lang_name = "C#" if language == "csharp" else "Python"

        prompt = f"""You are an expert {lang_name} developer. Your code has build errors that must be fixed.

ORIGINAL CODE:
```{language}
{code}
```

{errors}

Please provide the COMPLETE corrected code that fixes all build errors.
- Do not explain - just provide the fixed code
- Ensure all syntax is correct
- Maintain the original functionality
- Wrap code in ```{language} ``` blocks

FIXED CODE:"""

        from langchain_core.messages import HumanMessage
        response = self.llm.invoke([HumanMessage(content=prompt)])

        # Extract code from response
        fixed_code = response.content

        # Remove markdown code blocks if present
        if "```" in fixed_code:
            import re
            matches = re.findall(r'```(?:\w+)?\n(.*?)```', fixed_code, re.DOTALL)
            if matches:
                fixed_code = matches[0]

        return fixed_code.strip()
