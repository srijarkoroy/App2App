# api/services/llm_generator.py

import os
import json
# import google.generativeai as genai
from dotenv import load_dotenv
from google import genai

# Load .env
load_dotenv()

# Configure Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# Initialize the Gemini client
client = genai.Client(api_key=GOOGLE_API_KEY)


def generate_app_code(brief: str) -> dict:
    """
    Generate minimal web app files using Gemini.
    """

    prompt = f"""
You are an assistant that generates a minimal, functional HTML/CSS/JS web app
based on the following brief. Return the output as a JSON object with filenames
as keys and file contents as values.

Brief:
{brief}

Requirements:
- index.html must exist
- Include main.js and style.css if needed
- Include a README.md with: summary, setup, usage, and license
- Output as a JSON object where keys are filenames and values are contents
- Keep code minimal and functional
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        content = response.text.strip()

        # Attempt to extract JSON safely
        try:
            start = content.index('{')
            end = content.rindex('}') + 1
            content = content[start:end]
        except ValueError:
            pass

        code_files = json.loads(content)
        return code_files

    except Exception as e:
        print(f"Error generating app code with Gemini: {e}")
        # Fallback minimal HTML
        return {
            "index.html": "<!DOCTYPE html><html><head><title>Fallback App</title></head><body><h1>Fallback App</h1></body></html>",
            "README.md": "# Fallback App\nThis is a fallback README generated due to LLM error."
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