# app.py
import os
import streamlit as st
from dotenv import load_dotenv
import json

# --- All your Portia imports ---
from portia import (
    ToolRegistry, Config, LLMProvider, Portia, StorageClass, PlanRunState
)
from tools import get_pr_details_and_diff, post_comment_to_pr, parse_pr_url

# 1. Load environment variables from .env (as a fallback for local dev)
load_dotenv()

# --- Page Configuration ---
st.set_page_config(page_title="Portia PR Guardian", page_icon="🛡️", layout="centered")

# --- Sidebar for API Key Configuration ---
with st.sidebar:
    st.title("🔑 API Configuration")
    st.markdown("Enter your API keys below to use the app.")
    
    google_api_key_input = st.text_input(
        "Google Gemini API Key", 
        type="password",
        help="Get your key from Google AI Studio.",
        value=st.session_state.get("google_api_key", "")
    )
    github_token_input = st.text_input(
        "GitHub Personal Access Token", 
        type="password",
        help="Requires `repo` scope for private repos and posting comments.",
        value=st.session_state.get("github_token", "")
    )

    portia_input = st.text_input(
        "Portia API Key",
        type="password",
        help="Get your key from Portia.",
        value=st.session_state.get("portia_api_key", "")
    )

    if st.button("Save Keys", use_container_width=True, type="primary"):
        if google_api_key_input and github_token_input:
            st.session_state.google_api_key = google_api_key_input
            st.session_state.github_token = github_token_input
            # Set environment variables for the current session for tools.py to use
            os.environ["GOOGLE_API_KEY"] = google_api_key_input
            os.environ["GITHUB_TOKEN"] = github_token_input
            st.session_state.keys_set = True
            st.success("API keys saved for this session!")
            st.rerun()
        else:
            st.error("Please provide all API keys.")

# --- Agent Configuration (runs only when keys change) ---
@st.cache_resource
def setup_portia_agent(google_key):
    """Sets up the Portia agent. This function is cached."""
    # This check is important for the caching mechanism
    if not google_key:
        return None
    
    guardian_config = Config(
        llm_provider=LLMProvider.GOOGLE,
        storage_class=StorageClass.MEMORY,
        google_api_key=google_key,
        default_model="models/gemini-2.0-flash",
    )
    guardian_tool_registry = ToolRegistry([
        get_pr_details_and_diff(),
        post_comment_to_pr(),
    ])
    return Portia(config=guardian_config, tools=guardian_tool_registry)

# --- Agent Logic Functions ---
def run_analysis(pr_url):
    st.session_state.messages.append({"role": "user", "content": f"Please review this PR: {pr_url}"})
    portia = setup_portia_agent(st.session_state.get("google_api_key"))
    
    with st.chat_message("assistant", avatar="🛡️"):
        with st.spinner("🔍 Analyzing the pull request..."):
            try:
                repo_name, pr_number = parse_pr_url(pr_url)
                analysis_task = f"""
                Your first job is to analyze PR #{pr_number} in the repository '{repo_name}'.
                1. Use the `get_pr_details_and_diff` tool.
                2. Analyze the content for clarity and security issues.
                3. Synthesize a professional markdown review comment.
                4. CRITICAL: Your final output must be ONLY the markdown text of the draft comment.
                """
                plan_run = portia.run(analysis_task)

                if plan_run and plan_run.state == PlanRunState.COMPLETE and plan_run.outputs:
                    outputs_dict = json.loads(plan_run.outputs.model_dump_json())
                    draft = outputs_dict.get("final_output", {}).get("value")
                    if draft:
                        st.session_state.draft_comment = draft
                        st.session_state.stage = "awaiting_approval"
                    else:
                        st.session_state.messages.append({"role": "assistant", "avatar": "🛡️", "content": "Agent failed to produce a draft comment."})
                        st.session_state.stage = "initial"
                else:
                    st.session_state.messages.append({"role": "assistant", "avatar": "🛡️", "content": f"Agent run failed. Final state: {plan_run.state.value if plan_run else 'N/A'}"})
                    st.session_state.stage = "initial"
            except Exception as e:
                st.session_state.messages.append({"role": "assistant", "avatar": "🛡️", "content": f"An unexpected error occurred: {e}"})
                st.session_state.stage = "initial"

def post_comment():
    st.session_state.messages.append({"role": "user", "content": "Yes, approve and post."})
    st.session_state.stage = "posting"
    portia = setup_portia_agent(st.session_state.get("google_api_key"))

    with st.chat_message("assistant", avatar="🛡️"):
        with st.spinner("🚀 Posting comment to GitHub..."):
            try:
                repo_name, pr_number = parse_pr_url(st.session_state.pr_url)
                posting_task = f"Use `post_comment_to_pr` to post this comment to PR #{pr_number} in repo '{repo_name}':\n\n{st.session_state.draft_comment}"
                plan_run = portia.run(posting_task)
                
                if plan_run and plan_run.state == PlanRunState.COMPLETE:
                    st.session_state.messages.append({"role": "assistant", "avatar": "🛡️", "content": "✅ **Success!** The review comment has been posted to GitHub."})
                else:
                    st.session_state.messages.append({"role": "assistant", "avatar": "🛡️", "content": "❌ Failed to post the comment."})
            except Exception as e:
                st.session_state.messages.append({"role": "assistant", "avatar": "🛡️", "content": f"An error occurred while posting: {e}"})
    st.session_state.stage = "done"

# --- Main UI Rendering ---
st.title("The Portia PR Guardian 🛡️")

# Initialize session state if it doesn't exist
if "stage" not in st.session_state:
    st.session_state.stage = "initial"
if "keys_set" not in st.session_state:
    st.session_state.keys_set = False

if not st.session_state.keys_set:
    st.info("👋 Welcome! Please enter your API keys in the sidebar to activate the Portia PR Guardian.")
    st.stop()

# This part of the UI will only be shown after keys are saved
st.markdown("Your Portia AI agent is ready! Paste a GitHub Pull Request URL in the chat box below.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=message.get("avatar")):
        st.markdown(message["content"])

if st.session_state.stage == "awaiting_approval":
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
            st.session_state.messages.append({"role": "assistant", "avatar": "🛡️", "content": "👍 Understood. Operation cancelled. Paste a new URL to start over."})
            st.session_state.stage = "done"
            st.rerun()

prompt = st.chat_input("Paste a GitHub PR URL here...")
if prompt:
    st.session_state.stage = "analyzing"
    st.session_state.pr_url = prompt
    st.session_state.messages = []
    run_analysis(prompt)
    st.rerun()