#!/usr/bin/env python3
"""Debug utils issues."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from shared.utils import sanitize_input

# Debug the sanitize_input function
result = sanitize_input("Hello<script>alert('xss')</script>World")
print(f"Result type: {type(result)}")
print(f"Result value: {result}")

# Test direct call to _sanitize_string
try:
    from shared.utils import _sanitize_string
    result2 = _sanitize_string("Hello<script>alert('xss')</script>World")
    print(f"Direct _sanitize_string result: {result2}")
except Exception as e:
    print(f"Error calling _sanitize_string: {e}")

# Test calling with more specific debug
if result is None:
    print("Result is None - debugging...")
    # Test each step
    test_text = "Hello<script>alert('xss')</script>World"
    print(f"Input text: {test_text}")
    print(f"Is string? {isinstance(test_text, str)}")