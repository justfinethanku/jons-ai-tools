# test_token_direct.py
from notion_client import Client

# Copy the EXACT token from your secrets file
token = "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"

try:
    notion = Client(auth=token)
    me = notion.users.me()
    print(f"✅ Token works! User: {me}")
except Exception as e:
    print(f"❌ Token failed: {str(e)}")