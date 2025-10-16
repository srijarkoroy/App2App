from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os
import tempfile
import git
from google import genai
from dotenv import load_dotenv
import json
import sqlite3
from datetime import datetime
from playwright.async_api import async_playwright
import asyncio

app = FastAPI(title="Local Evaluation Server")

# Load .env
load_dotenv()

# Configure Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# Initialize the Gemini client
client = genai.Client(api_key=GOOGLE_API_KEY)

DB_PATH = "results/evaluations.db"

# -------------------------------
# 🧩 DATABASE SETUP
# -------------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            repo_url TEXT,
            pages_url TEXT,
            brief TEXT,
            results_json TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_result(email, repo_url, pages_url, brief, results):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO results (email, repo_url, pages_url, brief, results_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        email,
        repo_url,
        pages_url,
        brief,
        json.dumps(results, ensure_ascii=False, indent=2),
        datetime.utcnow().isoformat()
    ))
    conn.commit()
    conn.close()

init_db()

# -------------------------------
# 🌐 DYNAMIC CHECKS (Playwright)
# -------------------------------
async def run_dynamic_checks(url: str):
    results = {}
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(url, timeout=15000)
            results["reachable"] = True
            results["title"] = await page.title()

            header_text = await page.text_content("h1") or "No header found"
            results["header"] = header_text.strip() if header_text else None

            # Try to click a button if present
            buttons = await page.query_selector_all("button")
            results["buttons_count"] = len(buttons)
            if buttons:
                await buttons[0].click()
                results["button_clicked"] = True
            else:
                results["button_clicked"] = False

            # Screenshot capture
            screenshot_path = os.path.join(tempfile.gettempdir(), "dynamic_check.png")
            await page.screenshot(path=screenshot_path)
            results["screenshot"] = screenshot_path

        except Exception as e:
            results["error"] = str(e)
            results["reachable"] = False
        finally:
            await browser.close()

    return results

# -------------------------------
# 🧠 MAIN EVALUATION ENTRYPOINT
# -------------------------------
@app.post("/notify")
async def receive_notification(payload: dict):
    print("📩 Received notification from student API:")
    print(payload)

    repo_url = payload.get("repo_url")
    brief = payload.get("brief", "(no brief provided)")
    email = payload.get("email", "unknown")
    pages_url = payload.get("pages_url")

    if not repo_url:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Missing repo_url in payload"},
        )

    print(f"🔍 Starting evaluation for repo: {repo_url}")

    results = {"static_checks": {}, "llm_review": {}, "dynamic_checks": {}}

    try:
        # Step 1: Clone repo
        tmpdir = tempfile.mkdtemp()
        git.Repo.clone_from(repo_url, tmpdir)
        print(f"✅ Repo cloned to {tmpdir}")

        files = os.listdir(tmpdir)
        results["static_checks"]["has_license"] = "LICENSE" in files
        results["static_checks"]["has_readme"] = "README.md" in files
        results["static_checks"]["has_index_html"] = "index.html" in files
        results["static_checks"]["has_code_files"] = any(
            f.endswith((".html", ".py", ".js")) for f in files
        )

        # Step 2: LLM review
        readme_path = os.path.join(tmpdir, "README.md")
        if os.path.exists(readme_path):
            with open(readme_path, "r", encoding="utf-8") as f:
                readme_text = f.read()

            print("🤖 Sending README to Gemini for evaluation...")
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"""
                You are an instructor evaluating a student's auto-generated web app.
                The student's brief was: {brief}

                Here is the README content:
                {readme_text}

                Provide short constructive feedback (2-3 sentences)
                on how well the README matches the task and explains the app.
                """
            )
            results["llm_review"]["readme_feedback"] = response.text
        else:
            results["llm_review"]["readme_feedback"] = "No README.md found."

        # Step 3: Dynamic checks
        if pages_url:
            print(f"🌐 Running dynamic checks on {pages_url} ...")
            results["dynamic_checks"] = await run_dynamic_checks(pages_url)
        else:
            results["dynamic_checks"]["skipped"] = "No deployment URL provided."

        # Step 4: Save results to DB
        save_result(email, repo_url, pages_url, brief, results)
        print(f"💾 Results saved for {email}")

        return JSONResponse(
            status_code=200,
            content={
                "status": "evaluation_complete",
                "results": results,
            },
        )

    except Exception as e:
        print(f"❌ Evaluation failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)},
        )


# -------------------------------
# HEALTH CHECK
# -------------------------------
@app.get("/health")
async def health():
    return {"status": "alive"}

# -------------------------------
# 🧾 VIEW SAVED RESULTS
# -------------------------------
@app.get("/results")
async def get_all_results():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # Select all columns
    cur.execute("SELECT id, email, repo_url, pages_url, brief, results_json, created_at FROM results ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()

    return {"results": [
        {
            "id": r[0],
            "email": r[1],
            "repo_url": r[2],
            "pages_url": r[3],
            "results_json": json.loads(r[5]),  # parse the JSON string back to dict
            "created_at": r[6]
        }
        for r in rows
    ]}