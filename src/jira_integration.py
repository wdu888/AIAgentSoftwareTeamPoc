"""
Jira Integration Module (Post-POC)
For integrating the AI Agent Team with Jira project management
"""

from typing import Dict, List, Optional
import os
from jira import JIRA
from datetime import datetime


class JiraIntegration:
    """
    Jira integration for AI Agent Team
    Handles ticket creation, updates, and status tracking
    """
    
    def __init__(
        self,
        url: str = None,
        email: str = None,
        api_token: str = None
    ):
        """
        Initialize Jira integration
        
        Args:
            url: Jira instance URL (e.g., https://your-domain.atlassian.net)
            email: Jira account email
            api_token: Jira API token
        """
        self.url = url or os.getenv("JIRA_URL")
        self.email = email or os.getenv("JIRA_EMAIL")
        self.api_token = api_token or os.getenv("JIRA_API_TOKEN")
        
        if not all([self.url, self.email, self.api_token]):
            raise ValueError(
                "Jira credentials required. Set JIRA_URL, JIRA_EMAIL, "
                "and JIRA_API_TOKEN environment variables."
            )
        
        self.client = JIRA(
            server=self.url,
            basic_auth=(self.email, self.api_token)
        )
        
        print(f"✅ Connected to Jira: {self.url}")
    
    def create_story(
        self,
        project_key: str,
        summary: str,
        description: str,
        assignee: str = None,
        labels: List[str] = None,
        story_points: int = None
    ) -> str:
        """
        Create a user story
        
        Args:
            project_key: Jira project key (e.g., 'PROJ')
            summary: Story title
            description: Story description
            assignee: Assignee username
            labels: List of labels
            story_points: Story point estimate
            
        Returns:
            Issue key (e.g., 'PROJ-123')
        """
        fields = {
            'project': {'key': project_key},
            'summary': summary,
            'description': description,
            'issuetype': {'name': 'Story'}
        }
        
        if assignee:
            fields['assignee'] = {'name': assignee}
        
        if labels:
            fields['labels'] = labels
        
        if story_points:
            # Customfield for story points (varies by Jira setup)
            fields['customfield_10016'] = story_points
        
        issue = self.client.create_issue(fields=fields)
        
        print(f"✅ Created story: {issue.key} - {summary}")
        return issue.key
    
    def create_task(
        self,
        project_key: str,
        summary: str,
        description: str,
        parent_key: str = None,
        assignee: str = None,
        labels: List[str] = None
    ) -> str:
        """
        Create a task (optionally as subtask)
        
        Args:
            project_key: Jira project key
            summary: Task title
            description: Task description
            parent_key: Parent issue key (for subtasks)
            assignee: Assignee username
            labels: List of labels
            
        Returns:
            Issue key
        """
        fields = {
            'project': {'key': project_key},
            'summary': summary,
            'description': description,
            'issuetype': {'name': 'Task'}
        }
        
        if parent_key:
            fields['parent'] = {'key': parent_key}
            fields['issuetype'] = {'name': 'Sub-task'}
        
        if assignee:
            fields['assignee'] = {'name': assignee}
        
        if labels:
            fields['labels'] = labels
        
        issue = self.client.create_issue(fields=fields)
        
        print(f"✅ Created task: {issue.key} - {summary}")
        return issue.key
    
    def update_status(self, issue_key: str, status: str):
        """
        Update issue status
        
        Args:
            issue_key: Issue key (e.g., 'PROJ-123')
            status: Target status (e.g., 'In Progress', 'Done')
        """
        issue = self.client.issue(issue_key)
        transitions = self.client.transitions(issue)
        
        # Find matching transition
        transition_id = None
        for t in transitions:
            if t['name'].lower() == status.lower():
                transition_id = t['id']
                break
        
        if transition_id:
            self.client.transition_issue(issue, transition_id)
            print(f"✅ Updated {issue_key} status to: {status}")
        else:
            available = [t['name'] for t in transitions]
            raise ValueError(
                f"Status '{status}' not available. Options: {available}"
            )
    
    def add_comment(self, issue_key: str, comment: str):
        """Add comment to issue"""
        self.client.add_comment(issue_key, comment)
        print(f"✅ Added comment to {issue_key}")
    
    def create_implementation_tickets(
        self,
        agent_output: Dict,
        project_key: str,
        assignee: str = None
    ) -> Dict[str, str]:
        """
        Create Jira tickets from AI Agent Team output
        
        Args:
            agent_output: Output from AIAgentTeam.run()
            project_key: Jira project key
            assignee: Default assignee
            
        Returns:
            Dict with created issue keys
        """
        # Create parent story
        story_summary = f"AI Implementation: {agent_output['requirement'][:60]}"
        story_description = f"""
h2. Requirement
{agent_output['requirement']}

h2. Technical Plan
{agent_output['plan'][:1000]}

h2. Implementation Status
* Status: {agent_output['status']}
* Iterations: {agent_output['iterations']}

h2. Code Review Summary
{agent_output['review'][:500]}

---
_Generated by AI Agent Software Team_
        """
        
        story_key = self.create_story(
            project_key=project_key,
            summary=story_summary,
            description=story_description,
            assignee=assignee,
            labels=['ai-generated', 'code-review-needed']
        )
        
        # Create subtasks
        tasks = {
            'story': story_key,
            'code_review': None,
            'testing': None
        }
        
        # Code review task
        review_key = self.create_task(
            project_key=project_key,
            summary=f"Code Review: {agent_output['requirement'][:40]}",
            description=f"""
h3. Review the AI-generated code

{agent_output['review']}

h4. Action Items
* Review code quality
* Validate test coverage
* Check security considerations
* Approve or request changes
            """,
            parent_key=story_key,
            assignee=assignee,
            labels=['code-review', 'ai-generated']
        )
        tasks['code_review'] = review_key
        
        # Testing task
        test_key = self.create_task(
            project_key=project_key,
            summary=f"Run Tests: {agent_output['requirement'][:40]}",
            description=f"""
h3. Execute and validate test suite

The AI agent has generated tests. Please:
* Run the test suite
* Verify all tests pass
* Check edge case coverage
* Report any failures

h4. Test Summary
* Test count: {agent_output['tests'].count('def test_')}
* Framework: pytest
            """,
            parent_key=story_key,
            assignee=assignee,
            labels=['testing', 'ai-generated']
        )
        tasks['testing'] = test_key
        
        print(f"\n✅ Created Jira tickets for {story_key}")
        print(f"   Story: {story_key}")
        print(f"   Code Review: {review_key}")
        print(f"   Testing: {test_key}")
        
        return tasks
    
    def get_sprint_tasks(self, sprint_id: int) -> List[Dict]:
        """Get all tasks in a sprint"""
        jql = f"sprint = {sprint_id}"
        issues = self.client.search_issues(jql)
        
        return [
            {
                'key': issue.key,
                'summary': issue.fields.summary,
                'status': issue.fields.status.name,
                'assignee': issue.fields.assignee.displayName if issue.fields.assignee else None
            }
            for issue in issues
        ]
    
    def track_agent_progress(
        self,
        issue_key: str,
        stage: str,
        details: str = None
    ):
        """
        Track AI agent progress on a ticket
        
        Args:
            issue_key: Jira issue key
            stage: Current stage (planning, coding, testing, reviewing)
            details: Additional details
        """
        stage_map = {
            'planning': 'In Progress',
            'coding': 'In Progress',
            'testing': 'In Progress',
            'reviewing': 'In Review',
            'complete': 'Done'
        }
        
        # Update status if needed
        status = stage_map.get(stage, 'In Progress')
        
        # Add comment with progress
        comment = f"🤖 *AI Agent Update*\n\nStage: {stage.upper()}\n"
        if details:
            comment += f"\n{details}"
        
        self.add_comment(issue_key, comment)
        
        # Move to appropriate status
        try:
            self.update_status(issue_key, status)
        except ValueError:
            pass  # Status transition not available


# Example usage
def example_usage():
    """Example of using Jira integration with AI Agent Team"""
    from ai_agent_team import AIAgentTeam
    
    # Run AI Agent Team
    team = AIAgentTeam()
    result = team.run("Create a user authentication system")
    
    # Create Jira tickets
    jira = JiraIntegration()
    tickets = jira.create_implementation_tickets(
        agent_output=result,
        project_key="PROJ",
        assignee="developer@example.com"
    )
    
    print(f"\n📋 Jira tickets created:")
    print(f"   Story: {tickets['story']}")
    print(f"   Review: {tickets['code_review']}")
    print(f"   Tests: {tickets['testing']}")


if __name__ == "__main__":
    print("Jira Integration Module")
    print("Configure JIRA_URL, JIRA_EMAIL, and JIRA_API_TOKEN to use")
