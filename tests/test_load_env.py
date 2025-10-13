from dotenv import load_dotenv
import os

load_dotenv()

print("GITHUB_TOKEN:", os.getenv("GITHUB_TOKEN"))
print("GITHUB_USER:", os.getenv("GITHUB_USER"))