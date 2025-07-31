# GPT Code Review GitHub Action

Automatically review pull requests using OpenAI's GPT.

## Features

- Reviews Python files in PRs
- Posts inline feedback on code quality, bugs, and best practices
- Integrates directly with GitHub Actions

## Setup

1. Add this repo to `.github/workflows/`
2. Create GitHub secrets:
   - `OPENAI_API_KEY`
   - `GITHUB_TOKEN`
3. Copy `.env.example` and adjust if running locally
