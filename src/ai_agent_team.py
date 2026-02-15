"""
AI Agent Software Team POC
A multi-agent system for software development using LangGraph

Agents:
- Planning Agent: Breaks down requirements into tasks
- Coding Agent: Implements the code
- Testing Agent: Writes and runs tests
- Reviewing Agent: Reviews code quality and security
"""

import os
from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import operator

# State definition for the agent workflow
class AgentState(TypedDict):
    """State shared across all agents"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    requirement: str
    plan: str
    code: str
    tests: str
    review: str
    iteration_count: int
    needs_revision: bool
    final_output: dict


class AIAgentTeam:
    """Multi-agent software development team"""
    
    def __init__(self, api_key: str = None):
        """Initialize the agent team with Qwen API"""
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")

        # Initialize Qwen for each agent role via DashScope OpenAI-compatible API (using cost-effective model for POC)
        base_url = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"  # Singapore region
        
        self.planner_llm = ChatOpenAI(
            model="qwen-turbo",  # Cost-effective model for Singapore region
            api_key=self.api_key,
            temperature=0.7,
            base_url=base_url
        )

        self.coder_llm = ChatOpenAI(
            model="qwen-turbo",  # Cost-effective model for Singapore region
            api_key=self.api_key,
            temperature=0.3,
            base_url=base_url
        )

        self.tester_llm = ChatOpenAI(
            model="qwen-turbo",  # Cost-effective model for Singapore region
            api_key=self.api_key,
            temperature=0.5,
            base_url=base_url
        )

        self.reviewer_llm = ChatOpenAI(
            model="qwen-turbo",  # Cost-effective model for Singapore region
            api_key=self.api_key,
            temperature=0.4,
            base_url=base_url
        )
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add agent nodes
        workflow.add_node("planning_agent", self.planning_agent)
        workflow.add_node("coding_agent", self.coding_agent)
        workflow.add_node("testing_agent", self.testing_agent)
        workflow.add_node("reviewing_agent", self.reviewing_agent)
        workflow.add_node("revision_decision", self.revision_decision)
        
        # Define the workflow edges
        workflow.set_entry_point("planning_agent")
        workflow.add_edge("planning_agent", "coding_agent")
        workflow.add_edge("coding_agent", "testing_agent")
        workflow.add_edge("testing_agent", "reviewing_agent")
        workflow.add_edge("reviewing_agent", "revision_decision")
        
        # Conditional edge: revision or complete
        workflow.add_conditional_edges(
            "revision_decision",
            self.should_continue,
            {
                "revise": "coding_agent",
                "complete": END
            }
        )
        
        return workflow.compile()
    
    def planning_agent(self, state: AgentState) -> AgentState:
        """Planning Agent: Breaks down requirements into technical plan"""
        print("\n[PLANNING AGENT: Analyzing requirements...]")

        prompt = f"""You are a senior software architect. Analyze the following requirement and create a detailed technical plan.

Requirement: {state['requirement']}

Provide:
1. High-level architecture overview
2. Key components/modules needed
3. Implementation approach
4. Data structures and algorithms
5. Edge cases to consider

Format your response as a structured plan."""

        response = self.planner_llm.invoke([HumanMessage(content=prompt)])
        plan = response.content

        print(f"[PLAN CREATED ({len(plan)} chars)]")

        return {
            **state,
            "plan": plan,
            "messages": [AIMessage(content=f"Planning complete: {plan[:200]}...")]
        }
    
    def coding_agent(self, state: AgentState) -> AgentState:
        """Coding Agent: Implements the code based on plan"""
        print("\n[CODING AGENT: Writing code...]")

        # Check if this is a revision
        context = ""
        if state.get("review") and state.get("needs_revision"):
            context = f"\n\nPREVIOUS CODE:\n{state.get('code', '')}\n\nREVIEW FEEDBACK:\n{state['review']}\n\nPlease revise the code addressing the feedback."

        prompt = f"""You are an expert software developer. Implement the following plan with clean, production-ready code.

PLAN:
{state['plan']}

{context}

Requirements:
- Write clean, well-documented code
- Follow best practices and design patterns
- Include docstrings and comments
- Handle edge cases
- Make it modular and testable

Provide the complete implementation."""

        response = self.coder_llm.invoke([HumanMessage(content=prompt)])
        code = response.content

        print(f"[CODE WRITTEN ({len(code)} chars)]")

        return {
            **state,
            "code": code,
            "messages": state["messages"] + [AIMessage(content=f"Code implementation complete")]
        }
    
    def testing_agent(self, state: AgentState) -> AgentState:
        """Testing Agent: Creates comprehensive tests"""
        print("\n[TESTING AGENT: Writing tests...]")

        prompt = f"""You are a QA engineer specialized in test automation. Write comprehensive tests for the following code.

CODE TO TEST:
{state['code']}

ORIGINAL PLAN:
{state['plan']}

Create:
1. Unit tests for individual functions/methods
2. Integration tests for component interactions
3. Edge case tests
4. Test data/fixtures as needed

Use pytest framework. Include assertions and test descriptions."""

        response = self.tester_llm.invoke([HumanMessage(content=prompt)])
        tests = response.content

        print(f"[TESTS WRITTEN ({len(tests)} chars)]")

        return {
            **state,
            "tests": tests,
            "messages": state["messages"] + [AIMessage(content=f"Test suite created")]
        }
    
    def reviewing_agent(self, state: AgentState) -> AgentState:
        """Reviewing Agent: Reviews code quality and security"""
        print("\n[REVIEWING AGENT: Conducting code review...]")

        prompt = f"""You are a senior code reviewer. Review the following code and tests for quality, security, and best practices.

CODE:
{state['code']}

TESTS:
{state['tests']}

ORIGINAL PLAN:
{state['plan']}

Evaluate:
1. Code quality and readability
2. Adherence to best practices
3. Security vulnerabilities
4. Performance considerations
5. Test coverage and quality
6. Error handling
7. Documentation quality

Provide:
- Overall assessment (APPROVED / NEEDS_REVISION)
- Specific issues found (if any)
- Recommendations for improvement

Format: Start with "APPROVED" or "NEEDS_REVISION" on first line, then detailed feedback."""

        response = self.reviewer_llm.invoke([HumanMessage(content=prompt)])
        review = response.content

        # Check if revision is needed
        needs_revision = review.strip().upper().startswith("NEEDS_REVISION")

        print(f"[REVIEW COMPLETE - {'[NEEDS REVISION]' if needs_revision else '[APPROVED]'}]")

        return {
            **state,
            "review": review,
            "needs_revision": needs_revision,
            "messages": state["messages"] + [AIMessage(content=f"Code review complete")]
        }
    
    def revision_decision(self, state: AgentState) -> AgentState:
        """Decision node: Track iterations and prepare final output"""
        iteration = state.get("iteration_count", 0) + 1

        if not state.get("needs_revision") or iteration >= 3:
            # Prepare final output
            print(f"\n[WORKFLOW COMPLETE (Iterations: {iteration})]")
            final_output = {
                "requirement": state["requirement"],
                "plan": state["plan"],
                "code": state["code"],
                "tests": state["tests"],
                "review": state["review"],
                "iterations": iteration,
                "status": "approved" if not state.get("needs_revision") else "max_iterations_reached"
            }
            return {
                **state,
                "iteration_count": iteration,
                "needs_revision": False,
                "final_output": final_output
            }
        else:
            print(f"\n[REVISION NEEDED (Iteration {iteration})]")
            return {
                **state,
                "iteration_count": iteration
            }
    
    def should_continue(self, state: AgentState) -> str:
        """Determine if workflow should continue or end"""
        if state.get("needs_revision") and state.get("iteration_count", 0) < 3:
            return "revise"
        return "complete"
    
    def run(self, requirement: str) -> dict:
        """Execute the agent workflow"""
        print("="*80)
        print("[AI AGENT SOFTWARE TEAM - STARTING WORKFLOW]")
        print("="*80)
        
        initial_state = {
            "messages": [],
            "requirement": requirement,
            "plan": "",
            "code": "",
            "tests": "",
            "review": "",
            "iteration_count": 0,
            "needs_revision": False,
            "final_output": {}
        }
        
        # Run the workflow
        final_state = self.workflow.invoke(initial_state)
        
        return final_state["final_output"]


def main():
    """Example usage of the AI Agent Team"""
    
    # Example requirement
    requirement = """
    Create a Python function that calculates the Fibonacci sequence up to n terms.
    The function should:
    - Accept an integer n as input
    - Return a list of Fibonacci numbers
    - Handle edge cases (n <= 0, n = 1, n = 2)
    - Be optimized for performance (use memoization if needed)
    - Include proper error handling
    """
    
    # Initialize and run the team
    team = AIAgentTeam()
    result = team.run(requirement)
    
    # Display results
    print("\n" + "="*80)
    print("[FINAL OUTPUT]")
    print("="*80)
    print(f"\nStatus: {result['status'].upper()}")
    print(f"Iterations: {result['iterations']}")
    print("\n--- PLAN ---")
    print(result['plan'][:500] + "..." if len(result['plan']) > 500 else result['plan'])
    print("\n--- CODE ---")
    print(result['code'][:500] + "..." if len(result['code']) > 500 else result['code'])
    print("\n--- REVIEW ---")
    print(result['review'][:500] + "..." if len(result['review']) > 500 else result['review'])


if __name__ == "__main__":
    main()
