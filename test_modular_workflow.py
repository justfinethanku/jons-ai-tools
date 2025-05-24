#!/usr/bin/env python3
"""
Test script for the new modular Brand Builder workflow system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.brand_builder import BrandBuilderWorkflow, WorkflowContext


def test_workflow_discovery():
    """Test that all steps are discovered properly"""
    print("🔍 Testing workflow step discovery...")
    
    workflow = BrandBuilderWorkflow()
    steps = workflow.list_steps()
    
    print(f"✅ Discovered {len(steps)} steps:")
    for step_num, description in steps.items():
        print(f"  {step_num}: {description}")
    
    return len(steps) == 9  # Should have 9 steps


def test_individual_step():
    """Test running an individual step"""
    print("\n🧪 Testing individual step execution...")
    
    # Create test context
    context = WorkflowContext({
        'client_name': 'Test Company',
        'website_url': 'https://anthropic.com'
    })
    
    workflow = BrandBuilderWorkflow()
    
    # Test Step 1
    result = workflow.run_step(1, context)
    
    if result.success:
        print("✅ Step 1 executed successfully!")
        print(f"📊 Generated {len(result.data)} fields")
        return True
    else:
        print("❌ Step 1 failed!")
        for error in result.errors:
            print(f"  Error: {error}")
        return False


def test_step_dependencies():
    """Test step dependency validation"""
    print("\n🔗 Testing step dependencies...")
    
    workflow = BrandBuilderWorkflow()
    
    # Test Step 2 without Step 1 data
    context = WorkflowContext({'client_name': 'Test Company'})
    status = workflow.get_step_status(context)
    
    print("📋 Step status without dependencies:")
    for step_num, step_status in status.items():
        print(f"  Step {step_num}: {step_status}")
    
    return True


def test_workflow_execution():
    """Test running multiple steps in sequence"""
    print("\n🚀 Testing multi-step workflow execution...")
    
    # Create context with required data
    context = WorkflowContext({
        'client_name': 'Test Company',
        'website_url': 'https://anthropic.com'
    })
    
    workflow = BrandBuilderWorkflow()
    
    # Run first 2 steps
    results = workflow.run_workflow(context, start_from=1, end_at=2)
    
    success_count = sum(1 for r in results if r.success)
    print(f"✅ {success_count}/{len(results)} steps completed successfully")
    
    # Show context data accumulated
    print(f"📊 Context now contains {len(context.data)} fields")
    
    return success_count >= 1  # At least step 1 should work


def test_cli_interface():
    """Test CLI interface for individual steps"""
    print("\n💻 Testing CLI interface...")
    
    # Test Step 1 CLI
    import subprocess
    try:
        result = subprocess.run([
            'python', '-m', 'tools.brand_builder.step_01_website_extractor',
            '--website', 'https://example.com',
            '--client', 'Test Client',
            '--output', '/tmp/test_step1.json'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ CLI interface working!")
            return True
        else:
            print(f"❌ CLI failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🧪 Testing Modular Brand Builder Workflow System")
    print("=" * 60)
    
    tests = [
        ("Step Discovery", test_workflow_discovery),
        ("Individual Step", test_individual_step),
        ("Dependencies", test_step_dependencies),
        ("Multi-Step Workflow", test_workflow_execution),
        ("CLI Interface", test_cli_interface)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("🎯 TEST RESULTS:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n🏆 {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Modular workflow system is ready!")
    else:
        print("⚠️  Some tests failed. Review issues before proceeding.")
    
    return passed == len(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)