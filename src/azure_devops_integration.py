"""
Azure DevOps Integration Module (Post-POC)
For integrating the AI Agent Team with Azure DevOps
"""

from typing import Dict, List, Optional
import os
from azure.devops.connection import Connection
from azure.devops.v7_0.work_item_tracking.models import JsonPatchOperation
from msrest.authentication import BasicAuthentication
from datetime import datetime


class AzureDevOpsIntegration:
    """
    Azure DevOps integration for AI Agent Team
    Handles work items, pull requests, and pipeline triggers
    """
    
    def __init__(
        self,
        organization_url: str = None,
        personal_access_token: str = None,
        project_name: str = None
    ):
        """
        Initialize Azure DevOps integration
        
        Args:
            organization_url: Azure DevOps org URL (e.g., https://dev.azure.com/your-org)
            personal_access_token: PAT for authentication
            project_name: Project name
        """
        self.org_url = organization_url or os.getenv("AZURE_DEVOPS_ORG")
        self.pat = personal_access_token or os.getenv("AZURE_DEVOPS_PAT")
        self.project_name = project_name or os.getenv("AZURE_DEVOPS_PROJECT")
        
        if not all([self.org_url, self.pat]):
            raise ValueError(
                "Azure DevOps credentials required. Set AZURE_DEVOPS_ORG "
                "and AZURE_DEVOPS_PAT environment variables."
            )
        
        # Create connection
        credentials = BasicAuthentication('', self.pat)
        self.connection = Connection(base_url=self.org_url, creds=credentials)
        
        # Get clients
        self.wit_client = self.connection.clients.get_work_item_tracking_client()
        self.git_client = self.connection.clients.get_git_client()
        self.build_client = self.connection.clients.get_build_client()
        
        print(f"✅ Connected to Azure DevOps: {self.org_url}")
    
    def create_user_story(
        self,
        title: str,
        description: str,
        assigned_to: str = None,
        tags: List[str] = None,
        story_points: int = None
    ) -> int:
        """
        Create a user story work item
        
        Args:
            title: Story title
            description: Story description
            assigned_to: Assignee email/username
            tags: List of tags
            story_points: Story point estimate
            
        Returns:
            Work item ID
        """
        document = [
            JsonPatchOperation(
                op="add",
                path="/fields/System.Title",
                value=title
            ),
            JsonPatchOperation(
                op="add",
                path="/fields/System.Description",
                value=description
            ),
            JsonPatchOperation(
                op="add",
                path="/fields/System.WorkItemType",
                value="User Story"
            )
        ]
        
        if assigned_to:
            document.append(
                JsonPatchOperation(
                    op="add",
                    path="/fields/System.AssignedTo",
                    value=assigned_to
                )
            )
        
        if tags:
            document.append(
                JsonPatchOperation(
                    op="add",
                    path="/fields/System.Tags",
                    value="; ".join(tags)
                )
            )
        
        if story_points:
            document.append(
                JsonPatchOperation(
                    op="add",
                    path="/fields/Microsoft.VSTS.Scheduling.StoryPoints",
                    value=story_points
                )
            )
        
        work_item = self.wit_client.create_work_item(
            document=document,
            project=self.project_name,
            type="User Story"
        )
        
        print(f"✅ Created User Story #{work_item.id}: {title}")
        return work_item.id
    
    def create_task(
        self,
        title: str,
        description: str,
        parent_id: int = None,
        assigned_to: str = None,
        tags: List[str] = None,
        estimated_hours: float = None
    ) -> int:
        """
        Create a task work item
        
        Args:
            title: Task title
            description: Task description
            parent_id: Parent work item ID
            assigned_to: Assignee
            tags: List of tags
            estimated_hours: Time estimate
            
        Returns:
            Work item ID
        """
        document = [
            JsonPatchOperation(
                op="add",
                path="/fields/System.Title",
                value=title
            ),
            JsonPatchOperation(
                op="add",
                path="/fields/System.Description",
                value=description
            )
        ]
        
        if parent_id:
            document.append(
                JsonPatchOperation(
                    op="add",
                    path="/relations/-",
                    value={
                        "rel": "System.LinkTypes.Hierarchy-Reverse",
                        "url": f"{self.org_url}/{self.project_name}/_apis/wit/workItems/{parent_id}"
                    }
                )
            )
        
        if assigned_to:
            document.append(
                JsonPatchOperation(
                    op="add",
                    path="/fields/System.AssignedTo",
                    value=assigned_to
                )
            )
        
        if tags:
            document.append(
                JsonPatchOperation(
                    op="add",
                    path="/fields/System.Tags",
                    value="; ".join(tags)
                )
            )
        
        if estimated_hours:
            document.append(
                JsonPatchOperation(
                    op="add",
                    path="/fields/Microsoft.VSTS.Scheduling.OriginalEstimate",
                    value=estimated_hours
                )
            )
        
        work_item = self.wit_client.create_work_item(
            document=document,
            project=self.project_name,
            type="Task"
        )
        
        print(f"✅ Created Task #{work_item.id}: {title}")
        return work_item.id
    
    def update_work_item_state(self, work_item_id: int, state: str):
        """
        Update work item state
        
        Args:
            work_item_id: Work item ID
            state: New state (e.g., 'Active', 'Resolved', 'Closed')
        """
        document = [
            JsonPatchOperation(
                op="add",
                path="/fields/System.State",
                value=state
            )
        ]
        
        self.wit_client.update_work_item(
            document=document,
            id=work_item_id,
            project=self.project_name
        )
        
        print(f"✅ Updated work item #{work_item_id} state to: {state}")
    
    def add_comment(self, work_item_id: int, comment: str):
        """Add comment to work item"""
        document = [
            JsonPatchOperation(
                op="add",
                path="/fields/System.History",
                value=comment
            )
        ]
        
        self.wit_client.update_work_item(
            document=document,
            id=work_item_id,
            project=self.project_name
        )
        
        print(f"✅ Added comment to work item #{work_item_id}")
    
    def create_pull_request(
        self,
        repository_id: str,
        source_branch: str,
        target_branch: str,
        title: str,
        description: str,
        reviewers: List[str] = None
    ) -> int:
        """
        Create a pull request
        
        Args:
            repository_id: Repository ID or name
            source_branch: Source branch name
            target_branch: Target branch name
            title: PR title
            description: PR description
            reviewers: List of reviewer IDs
            
        Returns:
            Pull request ID
        """
        pr_request = {
            'sourceRefName': f'refs/heads/{source_branch}',
            'targetRefName': f'refs/heads/{target_branch}',
            'title': title,
            'description': description
        }
        
        if reviewers:
            pr_request['reviewers'] = [{'id': r} for r in reviewers]
        
        pr = self.git_client.create_pull_request(
            git_pull_request_to_create=pr_request,
            repository_id=repository_id,
            project=self.project_name
        )
        
        print(f"✅ Created pull request #{pr.pull_request_id}: {title}")
        return pr.pull_request_id
    
    def trigger_pipeline(
        self,
        pipeline_id: int,
        branch: str = "main",
        parameters: Dict = None
    ) -> int:
        """
        Trigger a pipeline build
        
        Args:
            pipeline_id: Pipeline ID
            branch: Branch to build
            parameters: Build parameters
            
        Returns:
            Build ID
        """
        build_request = {
            'definition': {'id': pipeline_id},
            'sourceBranch': f'refs/heads/{branch}'
        }
        
        if parameters:
            build_request['parameters'] = parameters
        
        build = self.build_client.queue_build(
            build=build_request,
            project=self.project_name
        )
        
        print(f"✅ Triggered pipeline build #{build.id}")
        return build.id
    
    def deploy_agent_output(
        self,
        agent_output: Dict,
        repository_id: str,
        assignee: str = None
    ) -> Dict[str, int]:
        """
        Deploy AI Agent Team output to Azure DevOps
        
        Args:
            agent_output: Output from AIAgentTeam.run()
            repository_id: Repository ID
            assignee: Default assignee
            
        Returns:
            Dict with work item IDs and PR ID
        """
        # Create user story
        story_title = f"AI Implementation: {agent_output['requirement'][:60]}"
        story_description = f"""
<h2>Requirement</h2>
<p>{agent_output['requirement']}</p>

<h2>Technical Plan</h2>
<pre>{agent_output['plan'][:1000]}</pre>

<h2>Implementation Status</h2>
<ul>
<li>Status: {agent_output['status']}</li>
<li>Iterations: {agent_output['iterations']}</li>
</ul>

<h2>Code Review</h2>
<pre>{agent_output['review'][:500]}</pre>

<hr/>
<em>Generated by AI Agent Software Team</em>
        """
        
        story_id = self.create_user_story(
            title=story_title,
            description=story_description,
            assigned_to=assignee,
            tags=['ai-generated', 'code-review']
        )
        
        # Create tasks
        review_task_id = self.create_task(
            title=f"Code Review: {agent_output['requirement'][:40]}",
            description="Review AI-generated code for quality and security",
            parent_id=story_id,
            assigned_to=assignee,
            tags=['code-review']
        )
        
        test_task_id = self.create_task(
            title=f"Run Tests: {agent_output['requirement'][:40]}",
            description="Execute and validate the AI-generated test suite",
            parent_id=story_id,
            assigned_to=assignee,
            tags=['testing']
        )
        
        result = {
            'story_id': story_id,
            'review_task_id': review_task_id,
            'test_task_id': test_task_id
        }
        
        print(f"\n✅ Created Azure DevOps work items")
        print(f"   Story: #{story_id}")
        print(f"   Review Task: #{review_task_id}")
        print(f"   Test Task: #{test_task_id}")
        
        return result


# Example usage
def example_usage():
    """Example of using Azure DevOps integration"""
    from ai_agent_team import AIAgentTeam
    
    # Run AI Agent Team
    team = AIAgentTeam()
    result = team.run("Create a REST API endpoint")
    
    # Deploy to Azure DevOps
    azure = AzureDevOpsIntegration(project_name="MyProject")
    work_items = azure.deploy_agent_output(
        agent_output=result,
        repository_id="my-repo",
        assignee="developer@example.com"
    )
    
    print(f"\n📋 Work items created:")
    print(f"   Story: #{work_items['story_id']}")
    print(f"   Review: #{work_items['review_task_id']}")
    print(f"   Tests: #{work_items['test_task_id']}")


if __name__ == "__main__":
    print("Azure DevOps Integration Module")
    print("Configure AZURE_DEVOPS_ORG, AZURE_DEVOPS_PAT, and AZURE_DEVOPS_PROJECT to use")
