#!/bin/bash
cd /Users/jonathanedwards/jons-ai-tools

git add .
git commit -m "Auto-backup $(date '+%Y-%m-%d %H:%M:%S')"
git push
