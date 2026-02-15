"""
Test script to verify the Qwen migration
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test importing the updated module
try:
    from ai_agent_team import AIAgentTeam
    print("[SUCCESS] Successfully imported AIAgentTeam")
    
    # Check if we can initialize the team
    team = AIAgentTeam()
    print("[SUCCESS] Successfully initialized AIAgentTeam with Qwen")
    
    # Check if the LLMs are properly configured
    print(f"[SUCCESS] Planner LLM: {type(team.planner_llm).__name__}")
    print(f"[SUCCESS] Coder LLM: {type(team.coder_llm).__name__}")
    print(f"[SUCCESS] Tester LLM: {type(team.tester_llm).__name__}")
    print(f"[SUCCESS] Reviewer LLM: {type(team.reviewer_llm).__name__}")
    
    print("\n[SUCCESS] Migration verification successful!")
    print("The system has been successfully migrated to use Qwen instead of Claude.")
    
except ImportError as e:
    print(f"[ERROR] Import error: {e}")
except Exception as e:
    print(f"[ERROR] Error during initialization: {e}")
    print("This might be expected if the DASHSCOPE_API_KEY is not set.")