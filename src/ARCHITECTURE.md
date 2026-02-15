# Architecture Overview - AI Agent Software Team

## System Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────────────┐
│                     User Interface / API                         │
│                   (examples.py / your code)                      │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AIAgentTeam Orchestrator                      │
│                     (ai_agent_team.py)                           │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │             LangGraph State Management                    │  │
│  │  - Tracks workflow state                                  │  │
│  │  - Manages message history                                │  │
│  │  - Controls iteration count                               │  │
│  │  - Stores artifacts (plan, code, tests, review)          │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
                ▼               ▼               ▼
┌───────────────────┐  ┌──────────────┐  ┌──────────────┐
│  Planning Agent   │  │ Coding Agent │  │Testing Agent │
│                   │  │              │  │              │
│ - Requirements    │  │ - Code gen   │  │ - Test gen   │
│   analysis        │  │ - Best       │  │ - Edge cases │
│ - Architecture    │  │   practices  │  │ - Pytest     │
│ - Approach        │  │ - Docs       │  │   framework  │
└─────────┬─────────┘  └──────┬───────┘  └──────┬───────┘
          │                   │                  │
          └───────────────────┼──────────────────┘
                              ▼
                    ┌──────────────────┐
                    │ Reviewing Agent  │
                    │                  │
                    │ - Quality check  │
                    │ - Security scan  │
                    │ - Best practices │
                    │ - Approval/      │
                    │   Revision       │
                    └────────┬─────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │  Decision Logic     │
                  │  - Check approval   │
                  │  - Count iterations │
                  │  - Route workflow   │
                  └──────┬──────────────┘
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
        [REVISION]            [COMPLETE]
         (back to              (output
          coding)               results)
```

## Component Details

### 1. State Management (AgentState)

**Type Definition:**
```python
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    requirement: str          # User's original requirement
    plan: str                # Planning agent's output
    code: str                # Coding agent's output
    tests: str               # Testing agent's output
    review: str              # Reviewing agent's output
    iteration_count: int     # Current iteration number
    needs_revision: bool     # Review result
    final_output: dict       # Final deliverable
```

**Purpose:**
- Maintains workflow state across all agents
- Enables communication between agents
- Tracks iteration progress
- Stores all artifacts

### 2. Agent Roles & Responsibilities

#### Planning Agent 🎯

**Input:**
- User requirement (natural language)

**Processing:**
1. Analyzes requirements
2. Creates high-level architecture
3. Identifies key components
4. Defines implementation approach
5. Lists edge cases

**Output:**
- Technical plan (structured text)
- Architecture overview
- Implementation strategy

**LLM Config:**
- Model: Qwen-Turbo (cost-effective for POC, Singapore region)
- Temperature: 0.7 (creative)

---

#### Coding Agent 💻

**Input:**
- Technical plan
- Previous code (if revision)
- Review feedback (if revision)

**Processing:**
1. Implements plan in code
2. Follows best practices
3. Adds documentation
4. Handles edge cases
5. Makes code modular

**Output:**
- Production-ready code
- Docstrings
- Comments

**LLM Config:**
- Model: Qwen-Turbo (cost-effective for POC, Singapore region)
- Temperature: 0.3 (precise)

**Revision Handling:**
- Receives review feedback
- Incorporates changes
- Maintains code quality

---

#### Testing Agent 🧪

**Input:**
- Implementation code
- Technical plan

**Processing:**
1. Analyzes code structure
2. Creates unit tests
3. Adds integration tests
4. Covers edge cases
5. Uses pytest framework

**Output:**
- Comprehensive test suite
- Test fixtures
- Assertions

**LLM Config:**
- Model: Qwen-Turbo (cost-effective for POC, Singapore region)
- Temperature: 0.5 (balanced)

---

#### Reviewing Agent 👁️

**Input:**
- Code implementation
- Test suite
- Technical plan

**Processing:**
1. Reviews code quality
2. Checks security issues
3. Validates best practices
4. Assesses test coverage
5. Verifies documentation

**Output:**
- Review report
- Approval status (APPROVED/NEEDS_REVISION)
- Specific issues
- Recommendations

**LLM Config:**
- Model: Qwen-Turbo (cost-effective for POC, Singapore region)
- Temperature: 0.4 (analytical)

**Decision Criteria:**
- Code quality score
- Security vulnerabilities
- Test coverage
- Documentation completeness

---

### 3. Workflow Control

#### Decision Points

```python
def should_continue(state: AgentState) -> str:
    """
    Routing logic for workflow continuation

    Returns:
        "revise": Send back to coding agent
        "complete": End workflow
    """
    if needs_revision and iterations < 3:
        return "revise"
    return "complete"
```

**Conditions for Revision:**
- Review status is NEEDS_REVISION
- Iteration count < 3

**Conditions for Completion:**
- Review status is APPROVED
- Max iterations (3) reached

#### Iteration Tracking

```
Iteration 1: Plan → Code → Test → Review
              ↓
         [Decision]
              ↓
Iteration 2: Code (with feedback) → Test → Review
              ↓
         [Decision]
              ↓
Iteration 3: Code (with feedback) → Test → Review
              ↓
         [Decision]
              ↓
           [END]
```

### 4. Communication Flow

```
User Requirement
      ↓
Planning Agent → state.plan
      ↓
Coding Agent → state.code
      ↓
Testing Agent → state.tests
      ↓
Reviewing Agent → state.review + state.needs_revision
      ↓
Decision Node → iteration_count++
      ↓
   [Branch]
   /     \
Revise   Complete
  ↓         ↓
Coding   Output
 (with
feedback)
```

### 5. LangGraph Integration

**Graph Structure:**

```python
workflow = StateGraph(AgentState)

# Nodes (agents)
workflow.add_node("planning_agent", planning_agent)
workflow.add_node("coding_agent", coding_agent)
workflow.add_node("testing_agent", testing_agent)
workflow.add_node("reviewing_agent", reviewing_agent)
workflow.add_node("revision_decision", revision_decision)

# Edges (flow)
workflow.set_entry_point("planning_agent")
workflow.add_edge("planning_agent", "coding_agent")
workflow.add_edge("coding_agent", "testing_agent")
workflow.add_edge("testing_agent", "reviewing_agent")
workflow.add_edge("reviewing_agent", "revision_decision")

# Conditional routing
workflow.add_conditional_edges(
    "revision_decision",
    should_continue,
    {"revise": "coding_agent", "complete": END}
)
```

## Data Flow

### Request Flow

```
1. User submits requirement
   ↓
2. Initialize state with requirement
   ↓
3. Execute workflow.invoke(state)
   ↓
4. LangGraph orchestrates agent calls
   ↓
5. Each agent updates state
   ↓
6. Decision logic determines next step
   ↓
7. Return final_output
```

### State Updates

```python
# Each agent returns updated state
return {
    **state,                    # Preserve existing state
    "plan": new_plan,          # Add/update specific field
    "messages": state["messages"] + [new_message]  # Append to list
}
```

## Error Handling

### Agent-Level Errors

```python
try:
    response = llm.invoke([message])
except Exception as e:
    # Handle API errors
    # Log error
    # Return error state
```

### Workflow-Level Errors

```python
try:
    final_state = workflow.invoke(initial_state)
except Exception as e:
    # Workflow execution error
    # Return partial results
    # Log failure point
```

## Performance Characteristics

### Time Complexity

**Single Iteration:**
- Planning: ~30-60s
- Coding: ~45-90s
- Testing: ~30-60s
- Reviewing: ~30-45s
- **Total: 2-4 minutes**

**With Revisions:**
- Iteration 2: +2-3 minutes
- Iteration 3: +2-3 minutes
- **Max Total: 8-10 minutes**

### API Usage

**Tokens per Agent:**
- Planning: 2,000-4,000 tokens
- Coding: 3,000-6,000 tokens
- Testing: 2,000-4,000 tokens
- Reviewing: 2,000-3,000 tokens

**Total per Iteration:**
- ~9,000-17,000 tokens
- With revisions: 18,000-51,000 tokens

### Cost Estimation

**Qwen-Turbo Pricing (Current, Singapore region):**
- Input: ~$0.001 / 1M tokens
- Output: ~$0.002 / 1M tokens

**Per Request (single iteration):**
- Input: ~10,000 tokens = ~$0.00001
- Output: ~7,000 tokens = ~$0.000014
- **Total: ~$0.000024**

**With 2 Revisions:**
- **Total: ~$0.000072**

## Scalability

### Parallel Processing

Current: Sequential execution
Future: Parallel testing and review

```python
# Future optimization
async def parallel_test_review():
    testing_task = asyncio.create_task(testing_agent())
    reviewing_task = asyncio.create_task(reviewing_agent())
    await asyncio.gather(testing_task, reviewing_task)
```

### Caching

**Opportunities:**
- Cache common patterns
- Reuse similar plans
- Template library

### Load Distribution

**For High Volume:**
- Queue management
- Rate limiting
- Batch processing

## Security Considerations

### Input Validation

```python
# Sanitize user input
def validate_requirement(req: str) -> bool:
    if len(req) > 10000:
        return False
    if contains_malicious_code(req):
        return False
    return True
```

### Code Execution

**Current:** No execution (POC)
**Future:** Sandboxed execution
- Docker containers
- Resource limits
- Timeout controls

### API Key Protection

```python
# Never log or expose
self.api_key = os.getenv("DASHSCOPE_API_KEY")
# Use environment variables only
```

## Future Enhancements

### Phase 2: Integrations

```
AIAgentTeam
    ↓
[GitHub Integration]
    ↓
Create PR → Review → Merge

[Jira Integration]
    ↓
Create Tickets → Track → Close

[Azure DevOps Integration]
    ↓
Create Work Items → Pipeline → Deploy
```

### Phase 3: Advanced Features

1. **Code Execution**
   - Safe sandbox
   - Runtime validation
   - Performance metrics

2. **Human-in-the-Loop**
   - Approval gates
   - Interactive feedback
   - Custom modifications

3. **Learning & Adaptation**
   - Pattern recognition
   - Style learning
   - Quality improvement

4. **Multi-Language Support**
   - JavaScript/TypeScript
   - Java
   - Go
   - Rust

## Monitoring & Observability

### Metrics to Track

```python
metrics = {
    "iteration_count": int,
    "approval_rate": float,
    "avg_execution_time": float,
    "token_usage": int,
    "cost_per_request": float,
    "quality_score": float
}
```

### Logging

```python
import logging

logger.info(f"Agent: {agent_name}")
logger.info(f"Input size: {len(input_text)}")
logger.info(f"Output size: {len(output_text)}")
logger.info(f"Duration: {duration}s")
```

## Conclusion

The AI Agent Software Team uses a multi-agent architecture with LangGraph orchestration to transform requirements into production-ready code. Each specialized agent contributes its expertise, with built-in quality control through iterative review and revision cycles.
