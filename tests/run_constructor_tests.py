#!/usr/bin/env python3
"""
Constructor Syntax Test Runner
Runs comprehensive tests to ensure all class constructors have correct syntax.
This should catch issues like missing underscores in __init__ methods.
"""

import unittest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def run_constructor_tests():
    """Run all constructor syntax tests"""
    
    print("🔍 Running Constructor Syntax Tests...")
    print("=" * 60)
    
    # Discover and run constructor tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Load constructor syntax tests
    try:
        from tests.unit.test_constructor_syntax import TestConstructorSyntax, TestConstructorParameters
        
        # Add all constructor tests
        suite.addTests(loader.loadTestsFromTestCase(TestConstructorSyntax))
        suite.addTests(loader.loadTestsFromTestCase(TestConstructorParameters))
        
        print(f"✅ Loaded {suite.countTestCases()} constructor tests")
        
    except ImportError as e:
        print(f"❌ Failed to load constructor tests: {e}")
        return False
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("🔍 Constructor Syntax Test Summary:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Skipped: {len(result.skipped)}")
    
    if result.failures:
        print(f"\n❌ {len(result.failures)} Constructor Failures:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print(f"\n💥 {len(result.errors)} Constructor Errors:")
        for test, traceback in result.errors:
            error_msg = traceback.split('\n')[-2] if '\n' in traceback else traceback
            print(f"   - {test}: {error_msg}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if success:
        print("\n✅ All constructor syntax tests passed!")
        print("🎉 No constructor syntax errors found.")
    else:
        print(f"\n❌ Constructor syntax tests failed!")
        print("🚨 Found constructor syntax errors that need to be fixed.")
    
    return success


def run_quick_constructor_check():
    """Run a quick check of critical constructors"""
    
    print("🚀 Quick Constructor Check...")
    print("-" * 40)
    
    critical_classes = [
        ("SessionManager", "src.utils.session_manager", "SessionManager", []),
        ("Director", "src.generators.director", "Director", ["test_api_key"]),
        ("VideoGenerator", "src.generators.video_generator", "VideoGenerator", ["test_api_key"]),
        ("WorkingOrchestrator", "src.agents.working_orchestrator", "WorkingOrchestrator", None),  # Complex constructor
        ("MultiAgentDiscussionSystem", "src.agents.multi_agent_discussion", "MultiAgentDiscussionSystem", ["test_api_key", "test_session"]),
    ]
    
    failed_classes = []
    
    for class_name, module_path, class_attr, args in critical_classes:
        try:
            # Import the module
            module = __import__(module_path, fromlist=[class_attr])
            cls = getattr(module, class_attr)
            
            # Try to instantiate
            if args is None:
                # Skip complex constructors for quick check
                print(f"⏭️  {class_name}: Skipped (complex constructor)")
                continue
            elif len(args) == 0:
                instance = cls()
            elif len(args) == 1:
                instance = cls(args[0])
            elif len(args) == 2:
                instance = cls(args[0], args[1])
            else:
                instance = cls(*args)
            
            print(f"✅ {class_name}: Constructor syntax OK")
            
        except SyntaxError as e:
            print(f"❌ {class_name}: SYNTAX ERROR - {e}")
            failed_classes.append((class_name, "Syntax Error", str(e)))
        except TypeError as e:
            if "__init__() takes no arguments" in str(e) or "missing" in str(e).lower():
                print(f"❌ {class_name}: CONSTRUCTOR ERROR - {e}")
                failed_classes.append((class_name, "Constructor Error", str(e)))
            else:
                print(f"⚠️  {class_name}: Parameter issue - {e}")
        except Exception as e:
            print(f"⚠️  {class_name}: Other issue - {e}")
    
    print("-" * 40)
    
    if failed_classes:
        print(f"❌ Found {len(failed_classes)} critical constructor issues:")
        for class_name, error_type, error_msg in failed_classes:
            print(f"   {class_name}: {error_type} - {error_msg}")
        return False
    else:
        print("✅ All critical constructors passed quick check!")
        return True


if __name__ == "__main__":
    print("🧪 Constructor Syntax Validation")
    print("=" * 60)
    
    # Run quick check first
    quick_success = run_quick_constructor_check()
    
    print("\n")
    
    # Run full test suite
    full_success = run_constructor_tests()
    
    # Exit with appropriate code
    if quick_success and full_success:
        print("\n🎉 All constructor tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Constructor tests failed!")
        sys.exit(1) 