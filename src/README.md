# AI Agent Software Team POC

A proof-of-concept multi-agent system for autonomous software development using LangGraph and Qwen AI.

## 🎯 Overview

This POC demonstrates a collaborative AI agent team that can:
- **Plan** software implementations from requirements
- **Code** production-ready solutions
- **Test** with comprehensive test suites
- **Review** code quality and security
- **Iterate** based on feedback

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Agent Software Team                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Planning Agent  │
                    │  (Architecture) │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Coding Agent   │◄─────┐
                    │ (Implementation)│      │
                    └────────┬────────┘      │
                             │               │
                             ▼               │
                    ┌─────────────────┐      │
                    │  Testing Agent  │      │
                    │  (QA & Tests)   │      │
                    └────────┬────────┘      │
                             │               │
                             ▼               │
                    ┌─────────────────┐      │
                    │ Reviewing Agent │      │
                    │ (Code Review)   │      │
                    └────────┬────────┘      │
                             │               │
                             ▼               │
                    ┌─────────────────┐      │
                    │    Decision     │      │
                    │  Needs Revision?│──────┘
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Final Output   │
                    └─────────────────┘
```

### Agent Roles

1. **Planning Agent** 🎯
   - Analyzes requirements
   - Creates technical architecture
   - Defines implementation approach
   - Identifies edge cases

2. **Coding Agent** 💻
   - Implements the plan
   - Writes clean, documented code
   - Follows best practices
   - Handles edge cases

3. **Testing Agent** 🧪
   - Creates unit tests
   - Writes integration tests
   - Develops edge case tests
   - Uses pytest framework

4. **Reviewing Agent** 👁️
   - Reviews code quality
   - Checks security vulnerabilities
   - Validates test coverage
   - Approves or requests revisions

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Qwen API key from Alibaba Cloud ([get one here](https://dashscope.console.aliyun.com/))

### Installation

1. Clone or download the project files

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

4. Run the examples:
```bash
# Run predefined example
python examples.py

# Run in interactive mode
python examples.py interactive
```

### Basic Usage

```python
from ai_agent_team import AIAgentTeam

# Define your requirement
requirement = """
Create a function that validates email addresses.
Include proper error handling and comprehensive tests.
"""

# Run the agent team with custom project directory
team = AIAgentTeam(project_dir="./email_validator_project")
result = team.run(requirement)

# Access outputs
print(result['code'])     # Implementation
print(result['tests'])    # Test suite
print(result['review'])   # Code review

# Results are automatically saved to:
# ./email_validator_project/
#   - email_validator_project_result.json
#   - email_validator_project_code.py
#   - email_validator_project_tests.py
#   - email_validator_project_plan.md
#   - email_validator_project_review.md
```

To disable automatic saving:

```python
team = AIAgentTeam(project_dir="./my_project")
result = team.run(requirement, save=False)  # Don't save automatically
```

## 📁 Project Structure

```
.
├── src/
│   ├── ai_agent_team.py      # Core agent team implementation
│   ├── examples.py           # Example usage and interactive mode
│   ├── requirements.txt      # Python dependencies
│   ├── .env.example         # Environment variables template
│   └── README.md            # This file
├── tools/                   # Integration modules (post-POC)
│   ├── __init__.py
│   ├── github_integration.py
│   ├── jira_integration.py
│   └── azure_devops_integration.py
└── tests/                   # Unit tests
    ├── __init__.py
    ├── test_structure.py
    ├── test_corrected_config.py
    └── test_qwen_migration.py
```

### Output Directory

When you run the agent team, generated code is saved to a project directory:

```
./output/
├── fibonacci_example/
│   ├── fibonacci_example_result.json
│   ├── fibonacci_example_code.py
│   ├── fibonacci_example_tests.py
│   ├── fibonacci_example_plan.md
│   └── fibonacci_example_review.md
└── task_manager_example/
    └── ...
```

You can customize the output directory using the `project_dir` parameter:

```python
team = AIAgentTeam(project_dir="./my_project")
result = team.run(requirement)
```

## 🔧 Configuration

Edit `.env` file:

```bash
# Required
DASHSCOPE_API_KEY=your_api_key_here

# Optional
MAX_ITERATIONS=3          # Max revision cycles
LOG_LEVEL=INFO           # Logging verbosity
```

## 🎮 Usage Examples

### Example 1: Simple Function
```python
requirement = """
Create a function to calculate factorial of a number.
Include recursion and iterative approaches.
Handle edge cases and add comprehensive tests.
"""

team = AIAgentTeam()
result = team.run(requirement)
```

### Example 2: Class Implementation
```python
requirement = """
Create a BankAccount class with:
- Deposit and withdrawal methods
- Transaction history
- Overdraft protection
- Thread-safe operations
"""

team = AIAgentTeam()
result = team.run(requirement)
```

### Example 3: API Integration
```python
requirement = """
Create a REST API client for a todo service.
Support CRUD operations, error handling,
rate limiting, and async requests.
"""

team = AIAgentTeam()
result = team.run(requirement)
```

## 🔄 Workflow Process

1. **User provides requirement** → Planning Agent analyzes
2. **Planning Agent** → Creates technical plan
3. **Coding Agent** → Implements code based on plan
4. **Testing Agent** → Writes comprehensive tests
5. **Reviewing Agent** → Reviews code quality
6. **Decision Point**:
   - ✅ **Approved** → Output final deliverables
   - ⚠️ **Needs Revision** → Loop back to Coding Agent (max 3 iterations)

## 📊 Output Format

Each workflow produces:

```json
{
  "requirement": "Original requirement text",
  "plan": "Technical architecture and approach",
  "code": "Production-ready implementation",
  "tests": "Comprehensive test suite",
  "review": "Code review with feedback",
  "iterations": 2,
  "status": "approved"
}
```

## 🚧 Future Enhancements (Post-POC)

### Phase 2: Tool Integrations

- **GitHub Integration**
  - Automatic PR creation
  - Code commits
  - Issue tracking
  
- **Jira Integration**
  - Ticket creation and updates
  - Status tracking
  - Sprint management

- **Azure DevOps Integration**
  - Work item management
  - Pipeline triggers
  - Build monitoring

### Phase 3: Advanced Features

- **Code Execution Environment**
  - Docker container for safe execution
  - Runtime validation
  - Performance benchmarking

- **Human-in-the-Loop**
  - Approval checkpoints
  - Interactive feedback
  - Customization options

- **Memory & Context**
  - Project history tracking
  - Code style learning
  - Team preferences

- **CI/CD Integration**
  - Automated testing
  - Deployment pipelines
  - Monitoring and alerts

## 🎯 POC Success Criteria

✅ Successfully breaks down requirements into technical plans
✅ Generates working, well-documented code
✅ Creates comprehensive test suites
✅ Provides meaningful code reviews
✅ Iterates based on feedback
✅ Produces production-ready deliverables

## 📝 Customization

### Adjust Agent Behavior

Edit `ai_agent_team.py`:

```python
# Customize LLM parameters
self.coder_llm = ChatOpenAI(
    model="qwen-turbo",  # Cost-effective model for Singapore region
    temperature=0.3,  # Lower = more deterministic
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
)

# Adjust max iterations
MAX_ITERATIONS = 5  # in revision_decision method
```

### Add Custom Agents

```python
def architecture_agent(self, state: AgentState) -> AgentState:
    """Custom agent for architecture decisions"""
    # Your implementation
    pass

# Add to workflow
workflow.add_node("architecture_agent", self.architecture_agent)
workflow.add_edge("planning_agent", "architecture_agent")
```

## 🐛 Troubleshooting

**Issue: API Key Error**
```
Solution: Ensure DASHSCOPE_API_KEY is set in .env file
```

**Issue: Import Errors**
```
Solution: Run `pip install -r requirements.txt`
```

**Issue: Workflow Hangs**
```
Solution: Check API rate limits, increase timeout values
```

## 📚 Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Qwen API Docs](https://dashscope.console.aliyun.com/)
- [LangChain Qwen Integration](https://docs.langchain.com/oss/python/integrations/chat/qwen)

## 📄 License

This is a POC project for demonstration purposes.

## 🤝 Contributing

This is a POC. For production use, consider:
- Adding proper error handling
- Implementing logging
- Adding unit tests for the agents
- Setting up CI/CD
- Adding monitoring and metrics

## 📞 Support

For issues or questions about Qwen AI, visit [Alibaba Cloud Support](https://www.alibabacloud.com/support)
