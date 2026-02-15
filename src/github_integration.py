"""
GitHub Integration Module (Post-POC)
For integrating the AI Agent Team with GitHub repositories
"""

from typing import Dict, List, Optional
import os
from github import Github, GithubException
from datetime import datetime


class GitHubIntegration:
    """
    GitHub integration for AI Agent Team
    Handles repository operations, PR creation, and issue management
    """
    
    def __init__(self, token: str = None, repo_name: str = None):
        """
        Initialize GitHub integration
        
        Args:
            token: GitHub personal access token
            repo_name: Repository name in format 'owner/repo'
        """
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.repo_name = repo_name
        
        if not self.token:
            raise ValueError("GitHub token required. Set GITHUB_TOKEN env variable.")
        
        self.client = Github(self.token)
        self.repo = None
        
        if repo_name:
            self.set_repository(repo_name)
    
    def set_repository(self, repo_name: str):
        """Set the active repository"""
        try:
            self.repo = self.client.get_repo(repo_name)
            self.repo_name = repo_name
            print(f"✅ Connected to repository: {repo_name}")
        except GithubException as e:
            raise ValueError(f"Failed to access repository {repo_name}: {e}")
    
    def create_branch(self, branch_name: str, from_branch: str = "main") -> str:
        """
        Create a new branch
        
        Args:
            branch_name: Name for the new branch
            from_branch: Base branch to create from
            
        Returns:
            Name of created branch
        """
        if not self.repo:
            raise ValueError("No repository set. Call set_repository() first.")
        
        try:
            # Get the base branch
            base_ref = self.repo.get_git_ref(f"heads/{from_branch}")
            base_sha = base_ref.object.sha
            
            # Create new branch
            self.repo.create_git_ref(
                ref=f"refs/heads/{branch_name}",
                sha=base_sha
            )
            
            print(f"✅ Created branch: {branch_name}")
            return branch_name
            
        except GithubException as e:
            if e.status == 422:
                print(f"⚠️ Branch {branch_name} already exists")
                return branch_name
            raise e
    
    def commit_files(
        self,
        branch_name: str,
        files: Dict[str, str],
        commit_message: str
    ) -> str:
        """
        Commit files to a branch
        
        Args:
            branch_name: Branch to commit to
            files: Dict of {filepath: content}
            commit_message: Commit message
            
        Returns:
            Commit SHA
        """
        if not self.repo:
            raise ValueError("No repository set")
        
        # Get branch reference
        ref = self.repo.get_git_ref(f"heads/{branch_name}")
        
        # Get latest commit
        latest_commit = self.repo.get_git_commit(ref.object.sha)
        base_tree = latest_commit.tree
        
        # Create tree elements for each file
        tree_elements = []
        for filepath, content in files.items():
            blob = self.repo.create_git_blob(content, "utf-8")
            tree_elements.append({
                "path": filepath,
                "mode": "100644",
                "type": "blob",
                "sha": blob.sha
            })
        
        # Create new tree
        new_tree = self.repo.create_git_tree(tree_elements, base_tree)
        
        # Create commit
        new_commit = self.repo.create_git_commit(
            message=commit_message,
            tree=new_tree,
            parents=[latest_commit]
        )
        
        # Update reference
        ref.edit(sha=new_commit.sha)
        
        print(f"✅ Committed {len(files)} files to {branch_name}")
        print(f"   Commit: {new_commit.sha[:8]} - {commit_message}")
        
        return new_commit.sha
    
    def create_pull_request(
        self,
        title: str,
        body: str,
        head_branch: str,
        base_branch: str = "main",
        labels: List[str] = None
    ) -> str:
        """
        Create a pull request
        
        Args:
            title: PR title
            body: PR description
            head_branch: Source branch
            base_branch: Target branch
            labels: List of label names
            
        Returns:
            PR URL
        """
        if not self.repo:
            raise ValueError("No repository set")
        
        try:
            pr = self.repo.create_pull(
                title=title,
                body=body,
                head=head_branch,
                base=base_branch
            )
            
            # Add labels if provided
            if labels:
                pr.add_to_labels(*labels)
            
            print(f"✅ Created pull request: {pr.html_url}")
            print(f"   #{pr.number}: {title}")
            
            return pr.html_url
            
        except GithubException as e:
            raise ValueError(f"Failed to create PR: {e}")
    
    def create_issue(
        self,
        title: str,
        body: str,
        labels: List[str] = None,
        assignees: List[str] = None
    ) -> str:
        """
        Create an issue
        
        Args:
            title: Issue title
            body: Issue description
            labels: List of label names
            assignees: List of GitHub usernames
            
        Returns:
            Issue URL
        """
        if not self.repo:
            raise ValueError("No repository set")
        
        issue = self.repo.create_issue(
            title=title,
            body=body,
            labels=labels or [],
            assignees=assignees or []
        )
        
        print(f"✅ Created issue: {issue.html_url}")
        print(f"   #{issue.number}: {title}")
        
        return issue.html_url
    
    def deploy_agent_output(
        self,
        agent_output: Dict,
        branch_prefix: str = "ai-agent",
        create_pr: bool = True
    ) -> Dict[str, str]:
        """
        Deploy AI Agent Team output to GitHub
        
        Args:
            agent_output: Output from AIAgentTeam.run()
            branch_prefix: Prefix for branch name
            create_pr: Whether to create a PR
            
        Returns:
            Dict with branch name, commit SHA, and PR URL (if created)
        """
        if not self.repo:
            raise ValueError("No repository set")
        
        # Generate branch name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        requirement_slug = agent_output['requirement'][:30].replace(" ", "_")
        branch_name = f"{branch_prefix}/{requirement_slug}_{timestamp}"
        
        # Create branch
        self.create_branch(branch_name)
        
        # Prepare files
        files = {
            "implementation.py": agent_output['code'],
            "tests/test_implementation.py": agent_output['tests'],
            "docs/PLAN.md": agent_output['plan'],
            "docs/REVIEW.md": agent_output['review']
        }
        
        # Commit files
        commit_message = f"AI Agent Implementation: {agent_output['requirement'][:50]}"
        commit_sha = self.commit_files(branch_name, files, commit_message)
        
        result = {
            "branch": branch_name,
            "commit_sha": commit_sha,
            "files_committed": list(files.keys())
        }
        
        # Create PR if requested
        if create_pr:
            pr_body = f"""
## AI Agent Team Implementation

**Requirement:**
{agent_output['requirement']}

**Status:** {agent_output['status']}
**Iterations:** {agent_output['iterations']}

### 📋 Plan
{agent_output['plan'][:500]}...

### 👁️ Code Review
{agent_output['review'][:500]}...

### 📁 Files Changed
- `implementation.py` - Main implementation
- `tests/test_implementation.py` - Test suite
- `docs/PLAN.md` - Technical plan
- `docs/REVIEW.md` - Code review notes

---
*Generated by AI Agent Software Team*
            """
            
            pr_url = self.create_pull_request(
                title=f"[AI Agent] {agent_output['requirement'][:60]}",
                body=pr_body,
                head_branch=branch_name,
                labels=["ai-generated", "needs-review"]
            )
            
            result["pr_url"] = pr_url
        
        return result


# Example usage
def example_usage():
    """Example of using GitHub integration with AI Agent Team"""
    from ai_agent_team import AIAgentTeam
    
    # Run AI Agent Team
    team = AIAgentTeam()
    result = team.run("Create a function to parse CSV files")
    
    # Deploy to GitHub
    github = GitHubIntegration(repo_name="your-org/your-repo")
    deployment = github.deploy_agent_output(result)
    
    print(f"\n🚀 Deployed to GitHub!")
    print(f"   Branch: {deployment['branch']}")
    print(f"   Commit: {deployment['commit_sha']}")
    print(f"   PR: {deployment.get('pr_url', 'N/A')}")


if __name__ == "__main__":
    # This would require actual GitHub credentials
    print("GitHub Integration Module")
    print("Configure GITHUB_TOKEN environment variable to use")
