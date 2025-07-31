import os
import requests
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
repo = os.getenv("GITHUB_REPOSITORY")
pr_number = os.getenv("GITHUB_REF").split("/")[-1]
github_token = os.getenv("GITHUB_TOKEN")

headers = {
    "Authorization": f"token {github_token}",
    "Accept": "application/vnd.github.v3+json"
}

def get_changed_files():
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def review_code_with_gpt(diff):
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
