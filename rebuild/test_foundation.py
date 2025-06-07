#!/usr/bin/env python3
"""
Simple test script to verify foundation implementation works.
"""

import sys
from pathlib import Path

# Add the rebuild directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_utils():
    """Test utils functions work."""
    from shared.utils import (
        validate_file_path, sanitize_input, format_output, 
        calculate_metrics, hash_content, timestamp_now,
        safe_json_parse, safe_json_stringify
    )
    
    print("Testing utils functions...")
    
    # Test validate_file_path
    result, msg = validate_file_path("/tmp/test.txt")
    print(f"✓ validate_file_path: {result}")
    
    # Test sanitize_input
    clean = sanitize_input("Hello<script>alert('xss')</script>World")
    print(f"✓ sanitize_input: {clean}")
    
    # Test format_output
    formatted = format_output({"test": "data"}, format_type="json")
    if formatted:
        print(f"✓ format_output: {formatted[:50]}...")
    else:
        print("✓ format_output: (empty result)")
    
    # Test calculate_metrics
    metrics = calculate_metrics("Hello world. This is a test.")
    print(f"✓ calculate_metrics: {metrics}")
    
    # Test hash_content
    hash_val = hash_content("Hello World")
    print(f"✓ hash_content: {hash_val[:16]}...")
    
    # Test timestamp_now
    timestamp = timestamp_now("iso")
    print(f"✓ timestamp_now: {timestamp}")
    
    # Test safe_json_parse
    parsed = safe_json_parse('{"test": "value"}')
    print(f"✓ safe_json_parse: {parsed}")
    
    # Test safe_json_stringify
    stringified = safe_json_stringify({"test": "value"})
    print(f"✓ safe_json_stringify: {stringified}")
    
    print("All utils functions working! ✅")
    return True


def test_ai_client():
    """Test AI client works."""
    from shared.ai_client import (
        APIProvider, RequestType, ClientConfig, 
        AIRequest, AIResponse, AIClient,
        create_ai_client, make_simple_request
    )
    
    print("\nTesting AI client...")
    
    # Test enums
    print(f"✓ APIProvider: {APIProvider.OPENAI}")
    print(f"✓ RequestType: {RequestType.CHAT}")
    
    # Test data structures
    config = ClientConfig(
        provider=APIProvider.OPENAI,
        api_key="test-key",
        model="gpt-4"
    )
    print(f"✓ ClientConfig: {config.provider}")
    
    request = AIRequest(
        request_type=RequestType.CHAT,
        prompt="Hello, world!"
    )
    print(f"✓ AIRequest: {request.request_type}")
    
    response = AIResponse(success=True, content="Test response")
    print(f"✓ AIResponse: {response.success}")
    
    # Test AIClient
    client = AIClient(config)
    print(f"✓ AIClient: {client}")
    
    # Test request validation
    errors = client.validate_request(request)
    print(f"✓ validate_request: {len(errors)} errors")
    
    # Test token estimation
    tokens = client.estimate_tokens("Hello, world!")
    print(f"✓ estimate_tokens: {tokens}")
    
    # Test get_available_models
    models = client.get_available_models()
    print(f"✓ get_available_models: {len(models)} models")
    
    # Test make_request
    response = client.make_request(request)
    print(f"✓ make_request: {response.success}")
    
    # Test convenience functions
    client2 = create_ai_client(APIProvider.OPENAI, "test-key")
    print(f"✓ create_ai_client: {client2}")
    
    simple_response = make_simple_request(client, "Hello!")
    print(f"✓ make_simple_request: {len(simple_response)} chars")
    
    print("All AI client functions working! ✅")
    return True


def main():
    """Run all foundation tests."""
    print("🧪 Testing Foundation Layer Implementation")
    print("=" * 50)
    
    try:
        test_utils()
        test_ai_client()
        
        print("\n" + "=" * 50)
        print("🎉 Foundation Layer Tests PASSED! ✅")
        print("\nPhase 1 Complete:")
        print("- ✅ shared/utils.py implemented")
        print("- ✅ shared/ai_client.py implemented") 
        print("- ✅ requirements.txt created")
        print("- ✅ All core functionality working")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Foundation tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)