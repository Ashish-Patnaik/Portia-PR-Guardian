# tools.py
import os
import requests
from github import Github
from portia import tool

@tool
def get_pr_details_and_diff(repo_name: str, pr_number: int) -> str:
    """
    Gets the title, body, and code differences (diff) for a specific GitHub Pull Request.
    Use this as the first step to get the context of the changes.
    """
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        return "Error: GITHUB_TOKEN environment variable not set. Please provide it in the sidebar."
    
    print(f"TOOL EXECUTED: Getting details for PR #{pr_number} in {repo_name}...")
    try:
        g = Github(github_token) # Initialize client with the latest token
        repo = g.get_repo(repo_name)
        pr = repo.get_pull(pr_number)

        headers = {'Authorization': f'token {github_token}'}
        response = requests.get(pr.patch_url, headers=headers)
        response.raise_for_status()
        diff_content = response.text

        return f"Title: {pr.title}\nBody: {pr.body}\n\nCode Diff:\n{diff_content}"
    except Exception as e:
        return f"Error fetching PR details: {e}"

@tool
def post_comment_to_pr(repo_name: str, pr_number: int, comment_body: str) -> str:
    """
    Posts a comment to a specific GitHub Pull Request.
    IMPORTANT: Only call this tool AFTER the user has explicitly approved the comment_body.
    """
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        return "Error: GITHUB_TOKEN environment variable not set. Please provide it in the sidebar."
        
    print(f"TOOL EXECUTED: Posting comment to PR #{pr_number} in {repo_name}...")
    try:
        g = Github(github_token) # Initialize client with the latest token
        repo = g.get_repo(repo_name)
        pr = repo.get_pull(pr_number)
        pr.create_issue_comment(comment_body)
        return "Comment posted successfully."
    except Exception as e:
        return f"Error posting comment: {e}"

def parse_pr_url(url: str) -> tuple[str, int]:
    """Parses a GitHub PR URL into (repo_name, pr_number)."""
    try:
        parts = url.strip('/').split('/')
        repo_name = f"{parts[-4]}/{parts[-3]}"
        pr_number = int(parts[-1])
        return repo_name, pr_number
    except (IndexError, ValueError) as e:
        raise ValueError(f"Invalid GitHub PR URL format: {url}") from e