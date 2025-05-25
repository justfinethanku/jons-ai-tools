# test_token_direct.py
from notion_client import Client
import os

# Get token from environment variables - never hardcode!
token = os.getenv("NOTION_API_KEY")
if not token:
    print("❌ NOTION_API_KEY environment variable not set")
    print("Set it with: export NOTION_API_KEY=your_token_here")
    exit(1)

try:
    notion = Client(auth=token)
    me = notion.users.me()
    print(f"✅ Token works! User: {me}")
except Exception as e:
    print(f"❌ Token failed: {str(e)}")
    print("Make sure NOTION_API_KEY environment variable is set correctly")