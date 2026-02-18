"""
C# Project Generator Tool

Creates complete Visual Studio solution structure for C# projects.
"""

import os
import re
import uuid
from typing import Dict, List
from ..base import Tool, ToolContext, ToolResult
from ..utilities.code_cleaner import CodeCleanerTool, CodeSplitterTool


class CSharpProjectGeneratorTool(Tool):
    """
    Tool for generating C# Visual Studio projects.
    
    Creates:
    - .sln solution file
    - .csproj project files
    - .cs source files
    - Test project with NUnit
    - .gitignore
    - README.md
    """
    
    def __init__(self):
        super().__init__(
            name="csharp_project_generator",
            description="Generates complete C# Visual Studio solution structure"
        )
    
    def execute(
        self,
        context: ToolContext,
        code: str = None,
        test_code: str = None,
        project_name: str = None,
        target_framework: str = "net10.0"
    ) -> ToolResult:
        """
        Generate C# project structure.
        
        Args:
            context: Tool context with project_dir
            code: Main project code
            test_code: Test project code
            project_name: Name for the project (uses folder name if not provided)
            target_framework: .NET target framework
            
        Returns:
            ToolResult with list of created files
        """
        try:
            project_dir = context.project_dir
            
            # Use folder name as project name if not provided
            if project_name is None:
                project_name = self._get_folder_name(project_dir)
            
            # Clean the code once
            cleaner = CodeCleanerTool()
            cleaner_result = cleaner.execute(context, code=code, language='csharp')
            if cleaner_result.success:
                code = cleaner_result.data['cleaned_code']
            
            if test_code:
                test_cleaner_result = cleaner.execute(context, code=test_code, language='csharp')
                if test_cleaner_result.success:
                    test_code = test_cleaner_result.data['cleaned_code']
            
            # Split code into files
            splitter = CodeSplitterTool()
            files = {}
            test_files = {}
            
            if code:
                split_result = splitter.execute(context, code=code, language='csharp')
                if split_result.success:
                    # Filter out test files from main code
                    all_files = split_result.data['files']
                    for filename, content in all_files.items():
                        # Check if this is a test file
                        if 'Test' in filename or 'Tests' in filename:
                            test_files[filename] = content
                        else:
                            files[filename] = content
            
            if test_code:
                test_split_result = splitter.execute(context, code=test_code, language='csharp')
                if test_split_result.success:
                    test_files.update(test_split_result.data['files'])
            
            # Create directory structure
            main_dir = os.path.join(project_dir, project_name)
            test_dir = os.path.join(project_dir, f"{project_name}.Tests")
            
            os.makedirs(main_dir, exist_ok=True)
            os.makedirs(test_dir, exist_ok=True)
            
            created_files = []
            
            # Generate .csproj for main project
            csproj_path = os.path.join(main_dir, f"{project_name}.csproj")
            self._write_csproj(csproj_path, project_name, target_framework)
            created_files.append(csproj_path)
            
            # Generate .csproj for test project
            test_csproj_path = os.path.join(test_dir, f"{project_name}.Tests.csproj")
            self._write_test_csproj(test_csproj_path, project_name, target_framework)
            created_files.append(test_csproj_path)
            
            # Generate .sln file
            sln_path = os.path.join(project_dir, f"{project_name}.sln")
            self._write_solution(sln_path, project_name)
            created_files.append(sln_path)
            
            # Write C# source files
            for filename, content in files.items():
                filepath = os.path.join(main_dir, filename)
                self._write_file(filepath, content)
                created_files.append(filepath)
            
            # Write test files
            for filename, content in test_files.items():
                filepath = os.path.join(test_dir, filename)
                self._write_file(filepath, content)
                created_files.append(filepath)
            
            # Create .gitignore
            gitignore_path = os.path.join(project_dir, ".gitignore")
            self._write_gitignore(gitignore_path)
            created_files.append(gitignore_path)
            
            # Create README
            readme_path = os.path.join(project_dir, "README.md")
            self._write_readme(readme_path, project_name)
            created_files.append(readme_path)
            
            return ToolResult.ok(
                f"C# project '{project_name}' created successfully",
                data={
                    'project_name': project_name,
                    'main_dir': main_dir,
                    'test_dir': test_dir
                },
                files_created=created_files
            )
            
        except Exception as e:
            return ToolResult.fail(f"Error generating C# project: {str(e)}")
    
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
        
        # Sanitize: remove invalid chars, keep only alphanumeric
        folder_name = re.sub(r'[^a-zA-Z0-9_.]', '', folder_name)
        
        # Ensure it starts with a letter
        if folder_name and not folder_name[0].isalpha():
            folder_name = 'App' + folder_name
        
        # Default fallback
        if not folder_name:
            folder_name = 'GeneratedApp'
        
        # Limit length
        return folder_name[:50]
    
    def _write_file(self, filepath: str, content: str):
        """Write content to file"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _write_csproj(self, filepath: str, project_name: str, target_framework: str):
        """Write .csproj file"""
        content = f'''<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>{target_framework}</TargetFramework>
    <ImplicitUsings>disable</ImplicitUsings>
    <Nullable>enable</Nullable>
    <GenerateDocumentationFile>true</GenerateDocumentationFile>
  </PropertyGroup>

</Project>
'''
        self._write_file(filepath, content)
    
    def _write_test_csproj(self, filepath: str, project_name: str, target_framework: str):
        """Write test .csproj file"""
        content = f'''<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <TargetFramework>{target_framework}</TargetFramework>
    <ImplicitUsings>disable</ImplicitUsings>
    <Nullable>enable</Nullable>
    <IsPackable>false</IsPackable>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.8.0" />
    <PackageReference Include="NUnit" Version="3.14.0" />
    <PackageReference Include="NUnit3TestAdapter" Version="4.5.0" />
    <PackageReference Include="Moq" Version="4.20.70" />
    <PackageReference Include="coverlet.collector" Version="6.0.0">
      <IncludeAssets>runtime; build; native; contentfiles; analyzers; buildtransitive</IncludeAssets>
      <PrivateAssets>all</PrivateAssets>
    </PackageReference>
  </ItemGroup>

  <ItemGroup>
    <ProjectReference Include="..\\{project_name}\\{project_name}.csproj" />
  </ItemGroup>

</Project>
'''
        self._write_file(filepath, content)
    
    def _write_solution(self, filepath: str, project_name: str):
        """Write .sln file"""
        main_guid = str(uuid.uuid4()).upper()
        test_guid = str(uuid.uuid4()).upper()
        
        content = f'''Microsoft Visual Studio Solution File, Format Version 12.00
# Visual Studio Version 17
VisualStudioVersion = 17.0.31903.59
MinimumVisualStudioVersion = 10.0.40219.1
Project("{{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}}") = "{project_name}", "{project_name}\\{project_name}.csproj", "{{{main_guid}}}"
EndProject
Project("{{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}}") = "{project_name}.Tests", "{project_name}.Tests\\{project_name}.Tests.csproj", "{{{test_guid}}}"
EndProject
Global
	GlobalSection(SolutionConfigurationPlatforms) = preSolution
		Debug|Any CPU = Debug|Any CPU
		Release|Any CPU = Release|Any CPU
	EndGlobalSection
	GlobalSection(ProjectConfigurationPlatforms) = postSolution
		{{{main_guid}}}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
		{{{main_guid}}}.Debug|Any CPU.Build.0 = Debug|Any CPU
		{{{main_guid}}}.Release|Any CPU.ActiveCfg = Release|Any CPU
		{{{main_guid}}}.Release|Any CPU.Build.0 = Release|Any CPU
		{{{test_guid}}}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
		{{{test_guid}}}.Debug|Any CPU.Build.0 = Debug|Any CPU
		{{{test_guid}}}.Release|Any CPU.ActiveCfg = Release|Any CPU
		{{{test_guid}}}.Release|Any CPU.Build.0 = Release|Any CPU
	EndGlobalSection
	GlobalSection(SolutionProperties) = preSolution
		HideSolutionNode = FALSE
	EndGlobalSection
EndGlobal
'''
        self._write_file(filepath, content)
    
    def _write_gitignore(self, filepath: str):
        """Write .gitignore file"""
        content = '''## Visual Studio / .NET
.vs/
*.user
*.suo
*.userosscache
*.userprefs
bin/
obj/
*.dll
*.exe
*.pdb
*.mdb

# NuGet
*.nupkg
packages/

# Test results
TestResults/
*.trx

# Build results
[Dd]ebug/
[Rr]elease/
x64/
x86/
bld/

# IDE
.idea/
*.swp
*.swo
'''
        self._write_file(filepath, content)
    
    def _write_readme(self, filepath: str, project_name: str):
        """Write README.md file"""
        content = f'''# {project_name}

Generated by AI Agent Software Team

## Build and Run

### Using Visual Studio
1. Open `{project_name}.sln` in Visual Studio
2. Build the solution (Ctrl+Shift+B)
3. Run with F5 or Ctrl+F5

### Using .NET CLI
```bash
# Build
dotnet build {project_name}.sln

# Run
dotnet run --project {project_name}/{project_name}.csproj

# Run Tests
dotnet test {project_name}.sln
```

## Project Structure

```
{project_name}/
├── {project_name}.sln
├── {project_name}/
│   ├── {project_name}.csproj
│   └── *.cs
└── {project_name}.Tests/
    ├── {project_name}.Tests.csproj
    └── *.cs
```
'''
        self._write_file(filepath, content)
