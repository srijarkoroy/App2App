import requests

url = "http://127.0.0.1:8000/"
payload = {
    "email": "student@example.com",
    "secret": "cutu",
    "task": "captcha-solver-001",
    "round": 1,
    "nonce": "1234",
    "brief": "Create a captcha solver",
    "checks": ["Repo has MIT license"],
    "evaluation_url": "https://example.com/notify",
    "attachments": []
}

response = requests.post(url, json=payload)
print(response.json())