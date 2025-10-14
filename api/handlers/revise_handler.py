# api/handlers/revise_handler.py

from api.services.llm_generator import generate_app_code
from api.services.github_service import push_to_github
from api.services.notifier import notify_evaluation
from github import Github, GithubException
import os
from typing import Dict
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USER = os.getenv("GITHUB_USER")


def handle_revise_request(payload) -> dict:
    """
    Handles round 2 (Revise) requests:
    1. Generate updated code from new brief
    2. Update the existing GitHub repo
    3. Notify evaluation server
    """

    # Step 1: Generate updated app code using LLM
    print(f"Generating updated app code for task '{payload.task}'...")
    code_files = generate_app_code(payload.brief)
    print(f"Updated app code generated: {list(code_files.keys())}")

    # Step 2: Connect to GitHub and get repo
    g = Github(GITHUB_TOKEN)
    try:
        user = g.get_user()
        repo = user.get_repo(payload.task)
        print(f"Found existing repo {repo.full_name}")
    except GithubException as e:
        print(f"Repo not found: {e}")
        raise e

    # Step 3: Update files in repo
    for filename, content in code_files.items():
        try:
            existing_file = repo.get_contents(filename, ref="main")
            repo.update_file(
                path=filename,
                message=f"Update {filename} (round 2)",
                content=content,
                sha=existing_file.sha,
                branch="main"
            )
            print(f"Updated {filename} in {repo.full_name}")
        except GithubException:
            repo.create_file(
                path=filename,
                message=f"Add {filename} (round 2)",
                content=content,
                branch="main"
            )
            print(f"Created {filename} in {repo.full_name}")

    # Get latest commit SHA after updates
    commit_sha = repo.get_commits()[0].sha

    # Step 4: Notify evaluation server
    if payload.evaluation_url:
        print(f"Notifying evaluation server at {payload.evaluation_url}...")
        notify_evaluation(
            evaluation_url=payload.evaluation_url,
            email=payload.email,
            task=payload.task,
            round_number=payload.round,
            nonce=payload.nonce,
            repo_url=repo.html_url,
            commit_sha=commit_sha,
            pages_url=f"https://{GITHUB_USER}.github.io/{payload.task}/"
        )
    else:
        print("No evaluation URL provided; skipping notification.")

    # Step 5: Return response
    response = {
        "status": "ok",
        "message": f"Round {payload.round} revision applied",
        "email": payload.email,
        "task": payload.task,
        "round": payload.round,
        "nonce": payload.nonce,
        "repo_url": repo.html_url,
        "commit_sha": commit_sha,
        "pages_url": f"https://{GITHUB_USER}.github.io/{payload.task}/"
    }

    return response
