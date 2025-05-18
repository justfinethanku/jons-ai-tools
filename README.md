# Jon’s AI Tools

## Overview

This is a modular, AI-powered content and workflow toolkit for creators, video producers, and prompt engineers.
It uses Streamlit and OpenAI/Google Gemini APIs to refine prompts, generate copy for multiple social platforms, and automate your creative workflow.
All tools are managed under version control and automatically backed up to GitHub daily.

---

## Features
- Prompt Refiner:
  - Instantly clarifies and optimizes user prompts for LLMs.
- Copy Generator:
  - Upload notes or scripts once, and auto-generate high-quality social copy for Facebook, LinkedIn, TikTok, YouTube, and more—each using its own custom prompt.
- Dynamic Modular Framework:
  - New tools and platforms can be added just by dropping prompt files into the right folder—no code changes required.
- Automated GitHub Backup:
  - All changes are committed and pushed to GitHub nightly via a cron job, so nothing is ever lost.

---

## 🚀 Feature Wishlist — AI Production Toolkit

1. Lead Generation
  - Effortlessly discover new clients with an AI-powered web crawler tailored by industry and location.
  - Prioritize opportunities using dynamic lead scoring and a visual “opportunity heatmap.”
  - Instantly deep-dive leads: get automated research on competitors, pain points, and market trends.
  - Accelerate smart outreach: auto-draft emails, proposals, and schedule follow-up reminders—all with a click.

---

2. Client Onboarding & Research
  - Instantly build 360° client profiles—branding, voice, project history, and contacts in one place.
  - Plug-and-Play Notion “AI Library Database”:
    - Get started in minutes—just duplicate our ready-to-use Notion template and connect your CRM.
    - All AI tools reference this database for up-to-date brand voice, client prompts, and project knowledge.
    - Enjoy truly “no code” onboarding—automation syncs data, so there’s zero manual copy-paste.
    - Field/column checks and automated updates keep your setup bulletproof as features evolve.
    - Built-in privacy checks, permission warnings, and unique client IDs safeguard your data.
  - Customer Voice Identifier & Generator Tool:
    - Instantly extract, create, or refine each client’s unique brand voice, auto-sync it to your library, and apply it to every proposal or campaign.
    - Interactive quiz tool: quickly capture client quirks, needs, and creative preferences.
    - Effortless import: pull in client info from emails or call sheets—no manual entry required.
    - Build a lasting client knowledge base for every recurring project.

---

3. Content & Proposal Creation
  - AI topic generator: get 20+ subtopics, full scripts, blog posts, and teleprompter copy from a single idea.
  - One-click brief builder: instantly transform research into professional project briefs.
  - Proposal generator: ready-to-send templates, instant pricing, and scope details.
  - Batch-create campaign blog and social copy for every platform.

---

4. Team & Freelancer Management
  - Build a freelancer and talent database from your emails, resumes, or call sheets.
  - Track gear, skills, certifications, and work history for every crew member.
  - Let AI recommend the best team for each project—maximize fit, minimize hassle.
  - Full permission controls to keep team and client data secure.

---

5. Asset & Project Management
  - Instantly locate assets—vehicles, equipment, locations—with smart search and auto-tagging.
  - Server and cloud integration for auto-backup and versioning.
  - Track asset usage: who, when, and for which project.
  - Quick asset check-in/check-out keeps everything moving.

---

6. Website & SEO Tools
  - Scan any site for AI and SEO optimization opportunities.
  - Auto-update your web copy for the latest search and AI best practices.
  - Instantly detect weak content and get actionable improvement suggestions.

---

7. Analytics & Feedback
  - Real-time dashboard: track leads, client happiness, repeat business, and project outcomes.
  - Monitor team performance and identify top-performing content types.
  - Collect and analyze client feedback to improve every future proposal.

---

## Stretch Goals
- Client portal: deliverables, project updates, invoices, and feedback—shared securely in one place.
- End-to-end automation: seamless workflow from lead to onboarding, production, delivery, and feedback.
- Data privacy & security: live dashboard and audit log to keep every client and project safe.

---

## Usage
1. Install requirements:

   ```
   pip install -r requirements.txt
   ```

   Note: you need to add your own Gemini API key into a .env file

2. Run the app:

   ```
   streamlit run app.py
   ```

3. Add new platforms:
   - Drop a new prompt file in `prompts/copy_prompts/social_prompts/` with a `PROMPT` variable.
   - The UI and code generation will update automatically.

---

## Repo Structure

```
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
```

---

## Automated Backups

Every day at 6:00 PM, a scheduled script commits and pushes all new work to GitHub.
To manually back up at any time, just run:

```
bash git_backup.sh
```

---

## License

MIT License.

---

Questions or feature ideas? Open an issue or send a pull request!