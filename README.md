# App2App

App2App is a developer-focused toolkit for automating the lifecycle of applications: building, deploying, and updating projects programmatically. It provides an API, evaluation tools, and helper scripts to streamline iteration and testing.

## Features

- API for project orchestration (located in `api/`).
- Evaluation harness and test utilities under `tests/` and `results/`.
- Helper scripts for bootstrapping and running the system (`install.sh`, `start_main.sh`, `start_eval.sh`).

## Prerequisites

- macOS / Linux / Windows (WSL)
- Python 3.9+ (the repository includes a sample virtualenv at `agent/`)
- pip

We recommend using a virtual environment.

## Quick start

1. Clone the repo:

```bash
git clone https://github.com/srijarkoroy/App2App.git
cd App2App
```

2. Create and activate a virtual environment (example using venv):

```bash
python3 -m venv .venv
source .venv/bin/activate   # macOS / Linux (zsh/bash)
# On Windows PowerShell: .\.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. (Optional) Run the convenience installer script if present:

```bash
./install.sh
```

## Running the API

The API server is implemented under the `api/` package. You can run it with uvicorn:

```bash
uvicorn api.main:app --reload --port 8000
```

There are also convenience scripts in the repo:

- `start_main.sh` — helper to start the main API (inspect the script to confirm behavior).
- `start_eval.sh` — helper to start the evaluation server used by tests.

## Postman collection

A Postman collection for the API is included at `tests/App2App.postman_collection.json`.

How to use it:

- Open Postman and choose Import -> File, then select `tests/App2App.postman_collection.json` (or drag the file into Postman).
- The collection contains two folders: `Main` (build/revise/health) and `Eval` (evaluation endpoints).
- The requests in the collection point to the hosted endpoints (for example `https://app2app.onrender.com` and `https://app2appeval.onrender.com`). That means you can send requests immediately after importing — you only need to edit the JSON payload's `brief` field to describe the task you want to submit.
- If you want to test against a local server instead, update the request URL or use a Postman environment set to `http://localhost:8000` (or wherever your instance is running). Also update `evaluation_url` in the JSON body if you want evaluation callbacks pointed at a different URL.
- Ensure requests use the `Content-Type: application/json` header when sending JSON bodies.

Quick note: start the API with the uvicorn command above before running collection requests against your local instance.

## Execute from Terminal (curl)

You can send a build/revise request directly from the terminal using curl against the hosted endpoint. Change the `brief` field in the JSON to describe your task.

```bash
curl -X POST https://app2app.onrender.com/ \
 -H "Content-Type: application/json" \
 -d '{
	"email": "srijarko@gmail.com",
	"secret": "cutu",
	"task": "captcha-solver-001",
	"round": 1,
	"nonce": "1234",
	"brief": "Create a captcha solver",
	"checks": ["Repo has MIT license"],
	"evaluation_url": "https://app2appeval.onrender.com/notify",
	"attachments": []
}'
```

Notes:

- The example above posts to the hosted URL (no local server required) — update the URL to `http://localhost:8000/` if you prefer to hit a local instance.
- Edit `brief` (and other fields) as needed before sending.
- To submit a revision request set `"round": 2` in the payload (the collection's `Revise - Round2` request already uses round 2).

```bash
curl -X POST https://app2app.onrender.com/ \
 -H "Content-Type: application/json" \
 -d '{
	"email": "srijarko@gmail.com",
	"secret": "cutu",
	"task": "captcha-solver-001",
	"round": 2,
	"nonce": "1234",
	"brief": "Add support for SVG Images",
	"checks": ["Repo has MIT license"],
	"evaluation_url": "https://app2appeval.onrender.com/notify",
	"attachments": []
}'
```

## Running tests

This project uses pytest. From the repository root (and with your virtualenv activated):

```bash
pytest -q
```

If you need to run a single test file (for example the evaluation server tests):

```bash
pytest tests/test_post.py -q
```

## Project structure

- `api/` — FastAPI application and handlers.
- `agent/` — example or bundled virtualenv and helper binaries.
- `tests/` — unit and integration tests.
- `results/` — artifacts and evaluation database.
- `requirements.txt` — Python dependencies.

## Contributing

Contributions are welcome. A good workflow is:

1. Fork the repository.
2. Create a branch for your change.
3. Add tests for new behavior.
4. Open a pull request with a clear description.

Please follow the existing code style and keep changes focused and small.

## License

This repository includes a `LICENSE` file — follow the terms there.

## Issue

If you have questions or want help getting started, open an issue in the repository.

---
