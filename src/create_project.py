r"""
Create a new project using AI Agent Team at any location

Usage:
    python create_project.py "C:/Users/wayne/source/repos/MyProject" "Your requirement here"
"""
import sys
from dotenv import load_dotenv
from ai_agent_team import AIAgentTeam

load_dotenv()

if len(sys.argv) < 3:
    print("Usage: python create_project.py <project_directory> <requirement>")
    print("\nExample:")
    print('  python create_project.py "C:/Users/wayne/source/repos/MyProject" "Create a calculator..."')
    print("\nFor C# projects, a complete Visual Studio solution will be created automatically.")
    sys.exit(1)

project_dir = sys.argv[1]
requirement = sys.argv[2]

print(f"Creating project at: {project_dir}")
print(f"Requirement: {requirement}")
print("="*80)

# Create team with project directory
team = AIAgentTeam(project_dir=project_dir)

# Run and automatically create proper project structure
# create_project=True will generate .sln, .csproj, .cs files for C# projects
result = team.run(requirement, save=True)

print("\n" + "="*80)
print(f"Project created successfully at: {project_dir}")
print("="*80)
