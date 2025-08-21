# The Portia PR Guardian 🛡️

![AgentHack 2025](https://img.shields.io/badge/AgentHack-2025-blueviolet)
![Powered By Portia AI](https://img.shields.io/badge/Powered%20By-Portia%20AI-orange)
![UI Streamlit](https://img.shields.io/badge/UI-Streamlit-ff4b4b)
![Language Python](https://img.shields.io/badge/Language-Python-blue)

The Portia PR Guardian is an AI-powered assistant that automates the tedious first-pass review of GitHub Pull Requests. It acts as a junior developer and security specialist, meticulously scanning code changes for common issues and vulnerabilities, and then presents its findings in a professional review comment.

Built for AgentHack 2025, this project showcases the power of Portia AI's controllable agent framework to create useful, safe, and interactive developer tools.

## ✨ Live Demo

🚀 [View the live application on Streamlit Community Cloud](https://portia-pr-guardian-5e.streamlit.app/)


## 🎬 App in Action

A quick demonstration of the PR Guardian analyzing a flawed pull request and posting a review comment after user approval.

![Demo](https://youtu.be/4lL4rcODJlU)


## 🌟 Key Features

- **Automated PR Analysis**: Fetches pull request details and code diffs directly from GitHub.
- **Security Vulnerability Detection**: Intelligently scans for hardcoded secrets and API keys, preventing critical security flaws from being merged.
- **Clarity and Best Practice Checks**: Ensures pull requests have clear titles and descriptions, promoting better team communication.
- **Human-in-the-Loop Approval**: The agent generates a draft review but never acts without explicit user approval. You have the final say, always.
- **Bring Your Own Keys (BYOK)**: A secure sidebar allows users to enter their own API keys, making the application portable and safe.
- **Interactive UI**: Built with Streamlit, the app provides a clean, conversational interface for a seamless user experience.

## 🏆 Why This Project Wins (Hackathon Judging Criteria)

This project was built from the ground up to excel in every category of the AgentHack 2025 judging criteria.

- **💡 Potential Impact**: The PR Guardian addresses a universal pain point for every software development team, saving countless hours of manual review and improving overall code quality and security.
- **🎨 Creativity & Originality**: It goes beyond simple linting by using an LLM to understand the context of code changes. The "human-in-the-loop" approval is a creative and crucial implementation of safe AI, perfectly aligned with Portia's philosophy.
- **🚀 Implementation of the Idea**: This is a fully functional, end-to-end application. It masterfully uses Portia's core features—structured planning, tool integration (GitHub API), and controllable execution—to solve a real-world problem.
- **✨ Aesthetics & UX**: The clean, conversational Streamlit interface is intuitive and user-friendly. The chat-based workflow makes interacting with the AI agent feel natural and engaging.
- **📈 Learning & Growth**: The project journey, from a command-line script to a polished, deployable web application, demonstrates a significant learning curve in building and presenting a complete AI-powered product.

## 🛠️ Tech Stack

<p align="left">
<img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" alt="Python" width="40" height="40"/>
<strong style="margin-left: 10px;">Portia AI</strong>
<strong style="margin-left: 10px;">&nbsp;&nbsp;•&nbsp;&nbsp;</strong>
<img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/google/google-original.svg" alt="Google Gemini" width="35" height="35" style="margin-left: 10px;"/>
<strong style="margin-left: 5px;">Google Gemini</strong>
<strong style="margin-left: 10px;">&nbsp;&nbsp;•&nbsp;&nbsp;</strong>
<img src="https://streamlit.io/images/brand/streamlit-logo-secondary-colormark-darktext.svg" alt="Streamlit" width="40" height="40" style="margin-left: 10px;"/>
<strong style="margin-left: 5px;">Streamlit</strong>
<strong style="margin-left: 10px;">&nbsp;&nbsp;•&nbsp;&nbsp;</strong>
<img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/github/github-original.svg" alt="GitHub API" width="40" height="40" style="margin-left: 10px;"/>
<strong style="margin-left: 5px;">GitHub API</strong>
</p>

## ⚙️ How to Run Locally

Follow these steps to run the PR Guardian on your own machine.

### 1. Clone the Repository

```bash
git clone https://github.com/Ashish-Patnaik/Portia-PR-Guardian.git
cd your-repo-name
```

### 2. Set Up a Virtual Environment

```bash
python -m venv myenv
source myenv/bin/activate  # On Windows, use `myenv\Scripts\activate`
```

### 3. Install Dependencies

The project requires the packages listed in requirements.txt.

```bash
pip install -r requirements.txt
```

*(Make sure your requirements.txt file contains streamlit, portia-sdk-python[google], PyGithub, requests, and python-dotenv.)*

### 4. Run the Streamlit App

```bash
streamlit run full.py
```

The application will open in your web browser.

### 5. Configure API Keys

Open the app and use the sidebar to enter your:
- Google Gemini API Key
- GitHub Personal Access Token (with repo scope)
- Portia API Key

Click "Save Keys" to activate the agent.

## 🚀 Future Ideas

- **Expanded Analysis**: Add more sophisticated checks for code complexity, performance issues, and dependency vulnerabilities (e.g., integrating with safety library).
- **Ticket Integration**: Connect to Jira or Linear to automatically update ticket statuses or add review comments.
- **Multi-Platform Support**: Extend functionality to support GitLab and Bitbucket merge requests.
- **Custom Rule Sets**: Allow users to define their own review rules and standards for the agent to enforce.

## 📜 License

This project is licensed under the MIT License. See the LICENSE file for details.
