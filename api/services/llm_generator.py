# api/services/llm_generator.py

import os
import openai
import json

# Load OpenAI API key from .env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY


def generate_app_code(brief: str) -> dict:
    """
    Generate a minimal web app (HTML/CSS/JS) based on the brief.

    Args:
        brief: Task description or prompt for the app.

    Returns:
        code_files: dict of filename -> file content
    """
    prompt = f"""
You are an assistant that generates a minimal, functional HTML/CSS/JS web app
based on the following brief. Return the output as a JSON object with filenames
as keys and file contents as values.

Brief:
{brief}

Requirements:
- index.html must exist
- If JS or CSS is needed, include main.js and style.css
- Keep code minimal and functional
- Do not include secrets in the code
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You generate minimal, functional web apps."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=2000
        )

        content = response.choices[0].message.content.strip()
        code_files = json.loads(content)
        return code_files

    except Exception as e:
        print(f"Error generating app code: {e}")
        # Fallback minimal HTML
        return {
            "index.html": "<!DOCTYPE html><html><head><title>Fallback App</title></head><body><h1>Fallback App</h1></body></html>"
        }



def generate_test_app_code(brief: str):
    """
    Dummy code generator for testing.
    Returns a minimal HTML page regardless of brief.
    """
    code_files = {
        "index.html": f"""
<!DOCTYPE html>
<html>
<head>
    <title>Dummy App</title>
</head>
<body>
    <h1>{brief}</h1>
    <p>This is a dummy app for testing GitHub push & Pages.</p>
</body>
</html>
"""
    }
    return code_files