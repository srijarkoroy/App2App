# api/services/notifier.py

import requests
import time
import json


def notify_evaluation(
    evaluation_url: str,
    email: str,
    task: str,
    round_number: int,
    nonce: str,
    repo_url: str,
    commit_sha: str,
    pages_url: str,
    max_retries: int = 5
) -> None:
    """
    POSTs evaluation JSON back to the instructor's server.
    Retries with exponential backoff on failure.

    Args:
        evaluation_url: URL to POST repo info
        email: student email
        task: task identifier
        round_number: round (1 or 2)
        nonce: unique nonce from request
        repo_url: GitHub repo URL
        commit_sha: latest commit SHA
        pages_url: GitHub Pages URL
        max_retries: max retry attempts
    """

    payload = {
        "email": email,
        "task": task,
        "round": round_number,
        "nonce": nonce,
        "repo_url": repo_url,
        "commit_sha": commit_sha,
        "pages_url": pages_url
    }

    headers = {"Content-Type": "application/json"}

    delay = 1  # initial delay in seconds

    for attempt in range(max_retries):
        try:
            resp = requests.post(evaluation_url, headers=headers, data=json.dumps(payload))
            if resp.status_code == 200:
                print(f"Successfully notified evaluation server (attempt {attempt+1})")
                return
            else:
                print(f"Server responded with {resp.status_code}: {resp.text}")
        except Exception as e:
            print(f"Error notifying server: {e}")

        print(f"⏳ Retrying in {delay} seconds...")
        time.sleep(delay)
        delay *= 2  # exponential backoff

    print(f"Failed to notify evaluation server after {max_retries} attempts")
