# api/handlers/build_handler.py

from api.services.llm_generator import generate_app_code, generate_test_app_code
from api.services.github_service import push_to_github
from api.services.notifier import notify_evaluation


def handle_build_request(payload) -> dict:
    """
    Handles round 1 (Build) requests:
    1. Generate code from brief
    2. Push to GitHub and enable Pages
    3. Notify evaluation server
    """

    # Generate minimal app code using LLM
    print(f"Generating app code for task '{payload.task}'...")
    code_files = generate_app_code(payload.brief)
    print(f"App code generated: {list(code_files.keys())}")

    # Log README.md snippet if it exists
    if "README.md" in code_files:
        readme_snippet = "\n".join(code_files["README.md"].splitlines()[:5])
        print(f"README.md preview:\n{readme_snippet}")

    # Push code to GitHub
    print(f"Pushing code to GitHub...")
    repo_url, commit_sha, pages_url = push_to_github(payload.task, code_files)
    print(f"Repo URL: {repo_url}, Commit SHA: {commit_sha}, Pages URL: {pages_url}")

    # Notify evaluation server
    if payload.evaluation_url:
        print(f"Notifying evaluation server at {payload.evaluation_url}...")
        notify_evaluation(
            evaluation_url=payload.evaluation_url,
            email=payload.email,
            task=payload.task,
            round_number=payload.round,
            nonce=payload.nonce,
            repo_url=repo_url,
            commit_sha=commit_sha,
            pages_url=pages_url
        )
    else:
        print("No evaluation URL provided; skipping notification.")

    # Return response for FastAPI
    response = {
        "status": "ok",
        "message": "Request accepted",
        "email": payload.email,
        "task": payload.task,
        "round": payload.round,
        "nonce": payload.nonce,
        "repo_url": repo_url,
        "commit_sha": commit_sha,
        "pages_url": pages_url
    }

    return response
