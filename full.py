# app.py
import os
import streamlit as st
from dotenv import load_dotenv
import json
import requests
from github import Github
import time

from portia import (
    ToolRegistry, Config, LLMProvider, Portia, StorageClass, PlanRunState, tool
)
@tool
def get_pr_details_and_diff(repo_name: str, pr_number: int) -> str:
    """Gets the title, body, and code differences (diff) for a GitHub Pull Request."""
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        return "Error: GITHUB_TOKEN has not been set. Please provide it in the sidebar."
    
    try:
        g = Github(github_token)
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
    """Posts a comment to a specific GitHub Pull Request."""
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        return "Error: GITHUB_TOKEN has not been set. Please provide it in the sidebar."
    try:
        g = Github(github_token)
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
        raise ValueError(f"Invalid GitHub PR URL format: {url}")

# --- Page Configuration ---
st.set_page_config(page_title="Portia PR Guardian", page_icon="🛡️", layout="centered")

# --- Agent Configuration ---
@st.cache_resource
def setup_portia_agent(google_key, portia_key):
    """Sets up the Portia agent."""
    if not google_key or not portia_key: return None
    
    # *** SUGGESTION 1 APPLIED HERE ***
    guardian_config = Config(
        llm_provider=LLMProvider.GOOGLE,
        storage_class=StorageClass.CLOUD,  # Use the Portia cloud!
        portia_api_key=portia_key,
        google_api_key=google_key,
        default_model="models/gemini-2.9-flash", # More standard model name
    )
    guardian_tool_registry = ToolRegistry([
        get_pr_details_and_diff(),
        post_comment_to_pr(),
    ])
    return Portia(config=guardian_config, tools=guardian_tool_registry)

# --- Agent Logic Functions ---
def run_analysis(pr_url):
    st.session_state.messages.append({"role": "user", "content": f"Please review this PR: {pr_url}"})
    portia = setup_portia_agent(st.session_state.google_api_key, st.session_state.portia_api_key)
    
    with st.chat_message("assistant", avatar="🛡️"):
        with st.spinner("🔍 Analyzing the pull request..."):
            try:
                repo_name, pr_number = parse_pr_url(pr_url)
                analysis_task = f"""Your first job is to analyze PR #{pr_number} in '{repo_name}'. Use `get_pr_details_and_diff`, analyze for issues, and synthesize a review comment. Your final output must be ONLY the markdown text of the draft comment."""
                plan_run = portia.run(analysis_task)

                if plan_run and plan_run.state == PlanRunState.COMPLETE and plan_run.outputs:
                    outputs_dict = json.loads(plan_run.outputs.model_dump_json())
                    draft = outputs_dict.get("final_output", {}).get("value")
                    if draft:
                        st.session_state.draft_comment = draft
                        st.session_state.stage = "awaiting_approval"
                    else:
                        st.session_state.messages.append({"role": "assistant", "avatar": "🛡️", "content": "Agent failed to produce a draft."})
                        st.session_state.stage = "initial"
                else:
                    st.session_state.messages.append({"role": "assistant", "avatar": "🛡️", "content": f"Agent run failed. State: {plan_run.state.value if plan_run else 'N/A'}"})
                    st.session_state.stage = "initial"
            except Exception as e:
                st.session_state.messages.append({"role": "assistant", "avatar": "🛡️", "content": f"An error occurred: {e}"})
                st.session_state.stage = "initial"

def post_comment():
    st.session_state.messages.append({"role": "user", "content": "Yes, approve and post."})
    st.session_state.stage = "posting"
    portia = setup_portia_agent(st.session_state.google_api_key, st.session_state.portia_api_key)

    with st.chat_message("assistant", avatar="🛡️"):
        with st.spinner("🚀 Posting comment to GitHub..."):
            try:
                repo_name, pr_number = parse_pr_url(st.session_state.pr_url)
                posting_task = f"Use `post_comment_to_pr` to post this comment to PR #{pr_number} in repo '{repo_name}':\n\n{st.session_state.draft_comment}"
                plan_run = portia.run(posting_task)
                
                if plan_run and plan_run.state == PlanRunState.COMPLETE:
                    st.session_state.messages.append({"role": "assistant", "avatar": "🛡️", "content": "✅ **Success!** Comment posted."})
                else:
                    st.session_state.messages.append({"role": "assistant", "avatar": "🛡️", "content": "❌ Failed to post the comment."})
            except Exception as e:
                st.session_state.messages.append({"role": "assistant", "avatar": "🛡️", "content": f"An error occurred while posting: {e}"})
    st.session_state.stage = "done"

# --- Sidebar and Main UI ---
with st.sidebar:
    st.title("🔑 API Configuration")
    st.markdown("Enter your API keys to activate the agent.")
    
    google_api_key_input = st.text_input("Google Gemini API Key", type="password")
    github_token_input = st.text_input("GitHub Access Token", type="password")
    portia_api_key_input = st.text_input("Portia API Key", type="password")

    if st.button("Save Keys", use_container_width=True, type="primary"):
        if google_api_key_input and github_token_input and portia_api_key_input:
            st.session_state.google_api_key = google_api_key_input
            st.session_state.github_token = github_token_input
            st.session_state.portia_api_key = portia_api_key_input
            os.environ["GOOGLE_API_KEY"] = google_api_key_input
            os.environ["GITHUB_TOKEN"] = github_token_input
            os.environ["PORTIA_API_KEY"] = portia_api_key_input
            st.session_state.keys_set = True
            st.success("API keys ready!")
            time.sleep(1)
            st.rerun()
        else:
            st.error("Please provide all three API keys.")

st.title("The Portia PR Guardian 🛡️")

# *** SUGGESTION 2 APPLIED HERE ***
if not st.session_state.get("keys_set", False):
    st.info("👋 Welcome! Please enter all three API keys in the sidebar to activate the PR Guardian.")
    st.stop()

# --- Main App Logic (runs only if keys are set) ---
st.markdown("Your Portia AI agent is ready! Paste a GitHub Pull Request URL in the chat box below.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=message.get("avatar")):
        st.markdown(message["content"])

if st.session_state.get("stage") == "awaiting_approval":
    with st.chat_message("assistant", avatar="🛡️"):
        st.markdown("📝 **Here is my draft review comment:**")
        st.info(st.session_state.draft_comment)
        st.markdown("**Should I post this to the pull request?**")
        
        col1, col2 = st.columns(2)
        if col1.button("✅ Approve & Post", use_container_width=True, type="primary"):
            post_comment()
            st.rerun()
        if col2.button("❌ Reject & Cancel", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "No, reject."})
            st.session_state.messages.append({"role": "assistant", "avatar": "🛡️", "content": "👍 Understood. Operation cancelled."})
            st.session_state.stage = "done"
            st.rerun()

prompt = st.chat_input("Paste a GitHub PR URL here...")
if prompt:
    st.session_state.stage = "analyzing"
    st.session_state.pr_url = prompt
    st.session_state.messages = []
    run_analysis(prompt)
    st.rerun()
