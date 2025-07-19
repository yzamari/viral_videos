#!/usr/bin/env python3
"""
Comprehensive Test Runner
Runs all tests including constructor syntax validation
"""

import unittest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def run_all_tests():
    """Run all tests including constructor syntax validation"""
    
    print("🧪 Running Comprehensive Test Suite")
    print("=" * 60)
    
    # Test loader
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Track test results
    total_tests = 0
    test_categories = []
    
    # 1. Subtitle and Overlay Fix Tests (NEW)
    print("🔧 Loading Subtitle and Overlay Fix Tests...")
    try:
        from tests.test_subtitle_timing_unit import TestSubtitleTimingUnit
        fix_suite = unittest.TestSuite()
        fix_suite.addTests(loader.loadTestsFromTestCase(TestSubtitleTimingUnit))
        suite.addTest(fix_suite)
        
        fix_count = fix_suite.countTestCases()
        total_tests += fix_count
        test_categories.append(f"Subtitle/Overlay Fix Tests: {fix_count}")
        print(f"✅ Loaded {fix_count} subtitle and overlay fix tests")
        
    except ImportError as e:
        print(f"⚠️ Failed to load subtitle/overlay tests: {e}")

    # 2. Constructor Syntax Tests (CRITICAL)
    print("🔍 Loading Constructor Syntax Tests...")
    try:
        from tests.unit.test_constructor_syntax import TestConstructorSyntax, TestConstructorParameters
        constructor_suite = unittest.TestSuite()
        constructor_suite.addTests(loader.loadTestsFromTestCase(TestConstructorSyntax))
        constructor_suite.addTests(loader.loadTestsFromTestCase(TestConstructorParameters))
        suite.addTest(constructor_suite)
        
        constructor_count = constructor_suite.countTestCases()
        total_tests += constructor_count
        test_categories.append(f"Constructor Tests: {constructor_count}")
        print(f"✅ Loaded {constructor_count} constructor syntax tests")
        
    except ImportError as e:
        print(f"⚠️ Failed to load constructor tests: {e}")
    
    # 2. Core Unit Tests
    print("🧪 Loading Core Unit Tests...")
    try:
        from tests.unit.test_agents import (
            TestDirectorAgent, TestVoiceDirectorAgent, TestContinuityDecisionAgent,
            TestVideoCompositionAgents, TestScriptProcessor, TestTrendingAnalyzer
        )
        
        core_tests = [
            TestDirectorAgent, TestVoiceDirectorAgent, TestContinuityDecisionAgent,
            TestVideoCompositionAgents, TestScriptProcessor, TestTrendingAnalyzer
        ]
        
        core_count = 0
        for test_class in core_tests:
            test_suite = loader.loadTestsFromTestCase(test_class)
            suite.addTest(test_suite)
            core_count += test_suite.countTestCases()
        
        total_tests += core_count
        test_categories.append(f"Core Unit Tests: {core_count}")
        print(f"✅ Loaded {core_count} core unit tests")
        
    except ImportError as e:
        print(f"⚠️ Failed to load core unit tests: {e}")
    
    # 3. Orchestrator Tests
    print("🎬 Loading Orchestrator Tests...")
    try:
        from tests.unit.test_orchestrators import TestWorkingOrchestrator, TestOrchestratorComparison
        
        orchestrator_tests = [TestWorkingOrchestrator, TestOrchestratorComparison]
        orchestrator_count = 0
        
        for test_class in orchestrator_tests:
            test_suite = loader.loadTestsFromTestCase(test_class)
            suite.addTest(test_suite)
            orchestrator_count += test_suite.countTestCases()
        
        total_tests += orchestrator_count
        test_categories.append(f"Orchestrator Tests: {orchestrator_count}")
        print(f"✅ Loaded {orchestrator_count} orchestrator tests")
        
    except ImportError as e:
        print(f"⚠️ Failed to load orchestrator tests: {e}")
    
    # 4. Core Entity Tests
    print("🏗️ Loading Core Entity Tests...")
    try:
        from tests.unit.test_core_entities import TestVideoEntity, TestSessionEntity, TestAgentEntity
        
        entity_tests = [TestVideoEntity, TestSessionEntity, TestAgentEntity]
        entity_count = 0
        
        for test_class in entity_tests:
            test_suite = loader.loadTestsFromTestCase(test_class)
            suite.addTest(test_suite)
            entity_count += test_suite.countTestCases()
        
        total_tests += entity_count
        test_categories.append(f"Entity Tests: {entity_count}")
        print(f"✅ Loaded {entity_count} entity tests")
        
    except ImportError as e:
        print(f"⚠️ Failed to load entity tests: {e}")
    
    # 5. Resilience Pattern Tests
    print("🔄 Loading Resilience Pattern Tests...")
    try:
        from tests.unit.test_resilience_patterns import TestCircuitBreaker, TestRetryManager
        
        resilience_tests = [TestCircuitBreaker, TestRetryManager]
        resilience_count = 0
        
        for test_class in resilience_tests:
            test_suite = loader.loadTestsFromTestCase(test_class)
            suite.addTest(test_suite)
            resilience_count += test_suite.countTestCases()
        
        total_tests += resilience_count
        test_categories.append(f"Resilience Tests: {resilience_count}")
        print(f"✅ Loaded {resilience_count} resilience pattern tests")
        
    except ImportError as e:
        print(f"⚠️ Failed to load resilience tests: {e}")
    
    # Print test summary
    print("\n" + "=" * 60)
    print("📊 Test Suite Summary:")
    print(f"   Total Tests: {total_tests}")
    for category in test_categories:
        print(f"   {category}")
    
    if total_tests == 0:
        print("❌ No tests loaded! Check test imports and dependencies.")
        return False
    
    # Run the tests
    print("\n" + "=" * 60)
    print("🚀 Running All Tests...")
    print("=" * 60)
    
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    # Print detailed results
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Skipped: {len(result.skipped)}")
    print(f"   Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    # Report failures
    if result.failures:
        print(f"\n❌ {len(result.failures)} Test Failures:")
        for i, (test, traceback) in enumerate(result.failures, 1):
            error_msg = traceback.split('AssertionError:')[-1].strip() if 'AssertionError:' in traceback else traceback.split('\n')[-2]
            print(f"   {i}. {test}: {error_msg}")
    
    # Report errors
    if result.errors:
        print(f"\n💥 {len(result.errors)} Test Errors:")
        for i, (test, traceback) in enumerate(result.errors, 1):
            error_msg = traceback.split('\n')[-2] if '\n' in traceback else traceback
            print(f"   {i}. {test}: {error_msg}")
    
    # Special focus on constructor syntax tests
    constructor_failures = [f for f in result.failures if 'constructor_syntax' in str(f[0])]
    constructor_errors = [e for e in result.errors if 'constructor_syntax' in str(e[0])]
    
    if constructor_failures or constructor_errors:
        print(f"\n🚨 CRITICAL: {len(constructor_failures + constructor_errors)} Constructor Issues Found!")
        print("These should be fixed immediately as they indicate syntax errors that")
        print("prevent classes from being instantiated properly.")
    
    # Overall result
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if success:
        print("\n🎉 All tests passed!")
        print("✅ System is ready for deployment.")
    else:
        print(f"\n❌ {len(result.failures + result.errors)} tests failed!")
        print("🔧 Please fix the failing tests before deployment.")
        
        # Prioritize constructor issues
        if constructor_failures or constructor_errors:
            print("\n🔥 PRIORITY: Fix constructor syntax errors first!")
    
    return success


def run_quick_validation():
    """Run a quick validation of critical systems"""
    print("⚡ Quick System Validation")
    print("-" * 40)
    
    critical_imports = [
        ("SessionManager", "src.utils.session_manager"),
        ("Director", "src.generators.director"),
        ("VideoGenerator", "src.generators.video_generator"),
        ("WorkingOrchestrator", "src.agents.working_orchestrator"),
    ]
    
    failed_imports = []
    
    for name, module_path in critical_imports:
        try:
            __import__(module_path)
            print(f"✅ {name}: Import OK")
        except Exception as e:
            print(f"❌ {name}: Import failed - {e}")
            failed_imports.append((name, str(e)))
    
    print("-" * 40)
    
    if failed_imports:
        print(f"❌ {len(failed_imports)} critical import failures!")
        return False
    else:
        print("✅ All critical imports successful!")
        return True


if __name__ == "__main__":
    print("🧪 Comprehensive Test Suite Runner")
    print("=" * 60)
    
    # Run quick validation first
    quick_success = run_quick_validation()
    
    if not quick_success:
        print("\n💥 Critical import failures detected!")
        print("Fix import issues before running full test suite.")
        sys.exit(1)
    
    print("\n")
    
    # Run full test suite
    full_success = run_all_tests()
    
    # Exit with appropriate code
    if full_success:
        print("\n🎉 All tests passed! System is ready.")
        sys.exit(0)
    else:
        print("\n💥 Tests failed! Fix issues before deployment.")
        sys.exit(1) 