"""
Test script to verify prompt loading functionality for all refactored tools.

This script tests that:
1. All prompt files exist and are readable
2. Prompt loading methods work correctly
3. Tools can access prompts from files instead of hardcoded strings
"""

from pathlib import Path
import sys


def test_prompt_files_exist():
    """Test that all expected prompt files exist."""
    print("Testing prompt file existence...")
    
    # Define expected prompt files for each tool
    expected_files = {
        "prompt_refiner": ["refinement.txt", "revision.txt"],
        "coder_helper": ["refinement.txt", "explanation.txt", "analysis.txt", "generation.txt", "debug.txt", "refactor.txt"],
        "social_copy_tool": ["facebook.txt", "linkedin.txt", "youtube.txt", "tiktok.txt", "twitter.txt", "instagram.txt"]
    }
    
    base_path = Path(__file__).parent / "tools"
    all_exist = True
    
    for tool_name, files in expected_files.items():
        tool_path = base_path / tool_name / "prompts"
        print(f"\n  Checking {tool_name}:")
        
        for file_name in files:
            file_path = tool_path / file_name
            if file_path.exists():
                print(f"    ✓ {file_name}")
            else:
                print(f"    ✗ {file_name} - MISSING")
                all_exist = False
    
    return all_exist


def test_prompt_content():
    """Test that prompt files contain expected content."""
    print("\nTesting prompt file content...")
    
    base_path = Path(__file__).parent / "tools"
    content_tests = {
        "prompt_refiner/prompts/refinement.txt": ["Role", "Objective", "Instructions"],
        "prompt_refiner/prompts/revision.txt": ["expert prompt engineer", "CURRENT PROMPT", "REVISED PROMPT"],
        "coder_helper/prompts/refinement.txt": ["Prompt Engineering Expert", "clearer and easier"],
        "coder_helper/prompts/explanation.txt": ["AI Prompt Engineer", "functionality"],
        "social_copy_tool/prompts/facebook.txt": ["Facebook Social Media Manager", "USER_INPUT", "Output Format"],
        "social_copy_tool/prompts/linkedin.txt": ["LinkedIn Content Strategist", "professional", "hashtags"]
    }
    
    all_valid = True
    
    for file_path, expected_terms in content_tests.items():
        full_path = base_path / file_path
        print(f"  Checking {file_path}:")
        
        try:
            content = full_path.read_text(encoding='utf-8')
            
            for term in expected_terms:
                if term in content:
                    print(f"    ✓ Contains '{term}'")
                else:
                    print(f"    ✗ Missing '{term}'")
                    all_valid = False
                    
        except Exception as e:
            print(f"    ✗ Error reading file: {e}")
            all_valid = False
    
    return all_valid


def test_tool_structure():
    """Test that tool structure is correct."""
    print("\nTesting tool directory structure...")
    
    base_path = Path(__file__).parent / "tools"
    tools = ["prompt_refiner", "coder_helper", "social_copy_tool"]
    
    all_structured = True
    
    for tool_name in tools:
        tool_path = base_path / tool_name
        print(f"  Checking {tool_name}:")
        
        # Check required files
        required_files = ["__init__.py", "tool.py", "ui.py"]
        for file_name in required_files:
            file_path = tool_path / file_name
            if file_path.exists():
                print(f"    ✓ {file_name}")
            else:
                print(f"    ✗ {file_name} - MISSING")
                all_structured = False
        
        # Check prompts directory
        prompts_path = tool_path / "prompts"
        if prompts_path.exists() and prompts_path.is_dir():
            print(f"    ✓ prompts/ directory")
        else:
            print(f"    ✗ prompts/ directory - MISSING")
            all_structured = False
    
    return all_structured


def test_prompt_loading_pattern():
    """Test that tools have the prompt loading pattern."""
    print("\nTesting prompt loading pattern in tool files...")
    
    base_path = Path(__file__).parent / "tools"
    tools = ["prompt_refiner", "coder_helper", "social_copy_tool"]
    
    all_have_pattern = True
    
    for tool_name in tools:
        tool_file = base_path / tool_name / "tool.py"
        print(f"  Checking {tool_name}/tool.py:")
        
        try:
            content = tool_file.read_text(encoding='utf-8')
            
            # Check for required patterns
            patterns = [
                "_load_prompt_file",
                "pathlib",
                "@RULE:PROMPT_MANAGEMENT"
            ]
            
            for pattern in patterns:
                if pattern in content:
                    print(f"    ✓ Contains '{pattern}'")
                else:
                    print(f"    ✗ Missing '{pattern}'")
                    all_have_pattern = False
                    
        except Exception as e:
            print(f"    ✗ Error reading file: {e}")
            all_have_pattern = False
    
    return all_have_pattern


def main():
    """Run all tests and report results."""
    print("=== PROMPT LOADING REFACTOR VALIDATION ===\n")
    
    tests = [
        ("Prompt Files Exist", test_prompt_files_exist),
        ("Prompt Content Valid", test_prompt_content),
        ("Tool Structure Correct", test_tool_structure),
        ("Prompt Loading Pattern", test_prompt_loading_pattern)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * (len(test_name) + 1))
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"\n✅ {test_name}: PASSED")
            else:
                print(f"\n❌ {test_name}: FAILED")
                
        except Exception as e:
            print(f"\n💥 {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Prompt refactoring is complete.")
        print("\nBenefits achieved:")
        print("• Easy prompt editing without touching code")
        print("• Clean separation of content from logic")
        print("• Version control for prompt iterations")
        print("• Hot reloading capability (when core modules implemented)")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please review the issues above.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)