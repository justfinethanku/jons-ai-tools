# Jon’s AI Tools

## Overview

This is a modular, AI-powered content and workflow toolkit for creators, video producers, and prompt engineers.  
It uses Streamlit and OpenAI/Google Gemini APIs to refine prompts, generate copy for multiple social platforms, and automate your creative workflow.  
All tools are managed under version control and automatically backed up to GitHub daily.

## Features

- **Prompt Refiner:**  
  Instantly clarifies and optimizes user prompts for LLMs.

- **Copy Generator:**  
  Upload notes or scripts once, and auto-generate high-quality social copy for Facebook, LinkedIn, TikTok, YouTube, and more—each using its own custom prompt.

- **Dynamic Modular Framework:**  
  New tools and platforms can be added just by dropping prompt files into the right folder—no code changes required.

- **Automated GitHub Backup:**  
  All changes are committed and pushed to GitHub nightly via a cron job, so nothing is ever lost.

## Usage

1. **Install requirements:**
    ```bash
    pip install -r requirements.txt
    ```
note: you need to add your own Gemini API key into a .env file
2. **Run the app:**
    ```bash
    streamlit run app.py
    ```

3. **Add new platforms:**  
   Drop a new prompt file in `prompts/copy_prompts/social_prompts/` with a `PROMPT` variable.  
   The UI and code generation will update automatically.

## Repo Structure
jons-ai-tools/
│
├─ app.py                  # Main launcher
├─ frameworks/             # Frameworks for different tool types
├─ tools/                  # Individual tools (Prompt Refiner, Copy Generator, etc)
├─ prompts/
│   └─ copy_prompts/
│        └─ social_prompts/ # One .py file per platform (e.g., facebook_copy.py)
│
├─ .gitignore
├─ git_backup.sh           # Daily auto-backup script
└─ README.md
## Automated Backups

Every day at 6:00 PM, a scheduled script commits and pushes all new work to GitHub.  
To manually back up at any time, just run:
```bash
bash git_backup.sh
License

MIT License.
Questions or feature ideas? Open an issue or send a pull request!
