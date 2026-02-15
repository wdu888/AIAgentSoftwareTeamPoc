# Quick Start Guide - AI Agent Software Team POC

Get your AI Agent Software Team running in 5 minutes!

## 🚀 Installation

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Configure API Key

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your Qwen API key:

```
DASHSCOPE_API_KEY=your-dashscope-api-key-here
```

Get your API key from: https://dashscope.console.aliyun.com/

### Step 3: Run Your First Agent Team

```bash
python examples.py
```

This will run a simple Fibonacci function example and show you the full workflow.

## 📚 Basic Usage

### Option 1: Run Predefined Examples

```bash
# Run the default example
python examples.py

# The output files will be in the outputs/ directory
```

### Option 2: Interactive Mode

```bash
python examples.py interactive
```

Then enter your requirement when prompted:

```
Enter your software requirement (or 'quit' to exit):
(Press Enter twice when done)

Create a function to validate email addresses with proper error handling and tests
[Press Enter]
[Press Enter]
```

### Option 3: Use in Your Code

```python
from ai_agent_team import AIAgentTeam

# Define what you want built
requirement = """
Create a calculator class that supports:
- Basic operations (add, subtract, multiply, divide)
- Memory functions (store, recall, clear)
- History of calculations
- Error handling for division by zero
Include comprehensive tests.
"""

# Run the agent team
team = AIAgentTeam()
result = team.run(requirement)

# Access the outputs
print("Code:", result['code'])
print("Tests:", result['tests'])
print("Review:", result['review'])
```

## 📂 Understanding the Output

After running, you'll find in the `outputs/` directory:

```
outputs/
├── [name]_result.json   # Complete workflow result
├── [name]_code.py       # Generated code
└── [name]_tests.py      # Generated tests
```

### Output Structure

```json
{
  "requirement": "Your original requirement",
  "plan": "Technical architecture and approach",
  "code": "Production-ready Python code",
  "tests": "Pytest test suite",
  "review": "Code review with feedback",
  "iterations": 1,
  "status": "approved"
}
```

## 🔍 What Happens Behind the Scenes

When you run the agent team, here's the workflow:

1. **Planning Agent** 🎯
   - Analyzes your requirement
   - Creates technical architecture
   - Defines implementation approach
   - ~30-60 seconds

2. **Coding Agent** 💻
   - Writes the implementation
   - Follows best practices
   - Adds documentation
   - ~45-90 seconds

3. **Testing Agent** 🧪
   - Creates unit tests
   - Adds integration tests
   - Covers edge cases
   - ~30-60 seconds

4. **Reviewing Agent** 👁️
   - Reviews code quality
   - Checks security
   - Validates tests
   - ~30-45 seconds
   - Either APPROVES or requests REVISION

5. **Iteration** (if needed)
   - If review requests changes
   - Goes back to Coding Agent
   - Maximum 3 iterations
   - Additional ~2-3 minutes per iteration

**Total Time:** 2-5 minutes for simple requests, 5-15 minutes for complex ones

## 💡 Example Requirements

### Simple Function
```
Create a function to check if a string is a palindrome.
Include edge cases and comprehensive tests.
```

### Class Implementation
```
Create a BankAccount class with deposit, withdraw, 
and get_balance methods. Include overdraft protection
and transaction history. Add full test coverage.
```

### API Integration
```
Create a GitHub API client that can:
- List repositories
- Create issues
- Get pull requests
Include error handling and retry logic.
```

### Data Processing
```
Create a CSV parser that handles:
- Different delimiters
- Quoted fields with commas
- Header detection
- Type inference
Include validation and tests.
```

## 🎛️ Customization

### Adjust Number of Iterations

Edit `ai_agent_team.py`:

```python
def should_continue(self, state: AgentState) -> str:
    if state.get("needs_revision") and state.get("iteration_count", 0) < 3:  # Change 3 to desired max
        return "revise"
    return "complete"
```

### Change LLM Model

Edit `ai_agent_team.py`:

```python
self.coder_llm = ChatAnthropic(
    model="claude-opus-4-20250514",  # Use Opus for more complex tasks
    api_key=self.api_key,
    temperature=0.3
)
```

### Adjust Agent Behavior

Modify the prompts in each agent function to customize behavior:

```python
def coding_agent(self, state: AgentState) -> AgentState:
    prompt = f"""You are an expert software developer...
    
    Additional instructions:
    - Use type hints
    - Follow PEP 8
    - Add detailed docstrings
    
    PLAN: {state['plan']}
    """
    # ...
```

## 🐛 Troubleshooting

### "API Key Error"
**Problem:** Invalid or missing API key
**Solution:**
```bash
# Check your .env file has the correct key
cat .env | grep DASHSCOPE_API_KEY
```

### "Import Error: No module named 'langgraph'"
**Problem:** Dependencies not installed
**Solution:**
```bash
pip install -r requirements.txt
```

### "Rate Limit Error"
**Problem:** Too many API requests
**Solution:** Wait a few minutes and try again, or upgrade your Anthropic API plan

### "Workflow Takes Too Long"
**Problem:** Complex requirement causing long execution
**Solution:** 
- Break into smaller requirements
- Reduce max iterations
- Use a simpler requirement for testing

### Output Files Not Created
**Problem:** Script finished but no files in outputs/
**Solution:**
```bash
# Check if outputs directory exists
ls -la outputs/

# If not, create it
mkdir -p outputs

# Run again
python examples.py
```

## 📊 Performance Tips

### For Faster Results
- Use simpler, more focused requirements
- Start with clear specifications
- Reduce max iterations to 1 or 2

### For Better Quality
- Provide detailed requirements
- Specify edge cases
- Mention performance needs
- Allow full 3 iterations

### For Cost Optimization
- Test with small examples first
- Use Haiku model for simple tasks (cheaper)
- Cache common patterns
- Batch similar requirements

## ⏭️ Next Steps

1. ✅ Run the examples
2. ✅ Try interactive mode with your own requirements
3. ✅ Review the generated code and tests
4. 📖 Read the full README.md for advanced features
5. 🔧 Customize for your team's needs
6. 🚀 Explore integrations (GitHub, Jira, Azure DevOps)

## 🆘 Getting Help

- **Documentation:** See README.md
- **Examples:** Check examples.py
- **Qwen API Docs:** https://dashscope.console.aliyun.com/
- **LangGraph Docs:** https://langchain-ai.github.io/langgraph/
- **LangChain Qwen Integration:** https://docs.langchain.com/oss/python/integrations/chat/qwen

## 🎉 You're Ready!

Start building with:
```bash
python examples.py interactive
```

Happy coding! 🚀
