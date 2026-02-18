"""
Example: Running the AI Agent Software Team
"""

from ai_agent_team import AIAgentTeam
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def example_1_simple_function():
    """Example 1: Simple function implementation"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Simple Fibonacci Function")
    print("="*80)

    requirement = """
    Create a Python function that calculates the Fibonacci sequence up to n terms.
    Requirements:
    - Accept an integer n as input
    - Return a list of Fibonacci numbers
    - Handle edge cases (n <= 0, n = 1, n = 2)
    - Be optimized for performance
    - Include proper error handling and documentation
    """

    # Specify project directory for output
    team = AIAgentTeam(project_dir="./output/fibonacci_example")
    result = team.run(requirement)

    print_summary(result)


def example_2_class_design():
    """Example 2: Class-based implementation"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Task Manager Class")
    print("="*80)

    requirement = """
    Create a TaskManager class in Python for managing a to-do list.
    Requirements:
    - Add tasks with title, description, priority (low/medium/high), and due date
    - Mark tasks as complete
    - List all tasks, filter by status or priority
    - Get overdue tasks
    - Persist tasks to JSON file
    - Include input validation
    - Thread-safe operations
    """

    team = AIAgentTeam(project_dir="./output/task_manager_example")
    result = team.run(requirement)

    print_summary(result)


def example_3_api_integration():
    """Example 3: API integration"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Weather API Client")
    print("="*80)

    requirement = """
    Create a Weather API client class that fetches weather data.
    Requirements:
    - Support multiple weather API providers (OpenWeather, WeatherAPI)
    - Get current weather by city name or coordinates
    - Get 5-day forecast
    - Cache results for 30 minutes to reduce API calls
    - Handle rate limiting and errors gracefully
    - Return structured data (temperature, humidity, conditions)
    - Include retry logic with exponential backoff
    - Async/await support
    """

    team = AIAgentTeam(project_dir="./output/weather_api_example")
    result = team.run(requirement)

    print_summary(result)


def print_summary(result: dict):
    """Print a summary of the workflow result"""
    print("\n" + "="*80)
    print("[WORKFLOW SUMMARY]")
    print("="*80)
    print(f"Status: {result['status'].upper()}")
    print(f"Iterations: {result['iterations']}")
    print(f"Plan length: {len(result['plan'])} characters")
    print(f"Code length: {len(result['code'])} characters")
    print(f"Tests length: {len(result['tests'])} characters")
    print(f"Review length: {len(result['review'])} characters")

    # Show review status
    review_first_line = result['review'].split('\n')[0]
    print(f"\nReview Status: {review_first_line}")


def interactive_mode():
    """Interactive mode for custom requirements"""
    print("\n" + "="*80)
    print("[AI AGENT SOFTWARE TEAM - INTERACTIVE MODE]")
    print("="*80)
    print("\nEnter your software requirement (or 'quit' to exit):")
    print("(Press Enter twice when done)")

    while True:
        print("\n" + "-"*80)
        lines = []
        while True:
            line = input()
            if line:
                lines.append(line)
            else:
                if lines:
                    break
                else:
                    continue

        requirement = "\n".join(lines)

        if requirement.lower().strip() == 'quit':
            break

        # Generate a simple project directory name from requirement
        import re
        dirname = re.sub(r'[^a-z0-9]+', '_', requirement[:50].lower()).strip('_')
        project_dir = f"./output/{dirname}"

        team = AIAgentTeam(project_dir=project_dir)
        result = team.run(requirement)

        print_summary(result)

        print("\nEnter another requirement (or 'quit' to exit):")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_mode()
    else:
        # Run examples
        print("Running predefined examples...")
        print("(Use 'python examples.py interactive' for interactive mode)")
        
        example_1_simple_function()
        
        # Uncomment to run more examples
        # example_2_class_design()
        # example_3_api_integration()
