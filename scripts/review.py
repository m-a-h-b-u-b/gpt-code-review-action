# Import standard library modules
import os  # For environment variables and system operations
import requests  # For making HTTP requests to GitHub API
import openai  # OpenAI API client
from dotenv import load_dotenv  # Load environment variables from .env file

# Load environment variables from .env file
load_dotenv()  # Loads OPENAI_API_KEY, GITHUB_REPOSITORY, GITHUB_TOKEN, etc.

# Set up API keys and repository info
openai.api_key = os.getenv("OPENAI_API_KEY")  # OpenAI API key
repo = os.getenv("GITHUB_REPOSITORY")  # GitHub repository in format "owner/repo"
pr_number = os.getenv("GITHUB_REF").split("/")[-1]  # Extract PR number from ref
github_token = os.getenv("GITHUB_TOKEN")  # GitHub personal access token

# Prepare headers for GitHub API requests
headers = {
    "Authorization": f"token {github_token}",  # Auth token
    "Accept": "application/vnd.github.v3+json"  # GitHub REST API v3
}

# Function to get list of changed files in the PR
def get_changed_files():
    # Build URL to fetch PR files
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"
    response = requests.get(url, headers=headers)  # Make GET request
    response.raise_for_status()  # Raise exception if request failed
    return response.json()  # Return JSON list of files

# Function to send diff to OpenAI and get code review feedback
def review_code_with_gpt(diff):
    # Construct prompt for GPT to review the code diff
    prompt = f"""You're an expert code reviewer. Review the following diff and provide constructive feedback.

```diff
{diff}
```

Respond only with feedback on code quality, bugs, best practices, or missing documentation."""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response['choices'][0]['message']['content']

def post_comment(file_path, comment_body):
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    payload = {"body": f"**AI Code Review for `{file_path}`**\n\n{comment_body}"}
    requests.post(url, headers=headers, json=payload)

def main():
    files = get_changed_files()
    for file in files:
        if file['filename'].endswith('.py'):
            diff = file.get('patch')
            if diff:
                print(f"Reviewing {file['filename']}...")
                feedback = review_code_with_gpt(diff)
                post_comment(file['filename'], feedback)

if __name__ == "__main__":
    main()
