#!/usr/bin/env python3
"""
Test runner for VEO clients and audio generator
Run comprehensive tests to verify portrait video generation and audio functionality
"""

import unittest
import sys
import os
import argparse

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def run_unit_tests():
    """Run unit tests (mocked, fast)"""
    print("🧪 Running unit tests...")
    
    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def run_integration_tests():
    """Run integration tests (real API calls)"""
    print("🔗 Running integration tests...")
    print("⚠️  These tests make real API calls and may incur costs!")
    
    # Set environment to not skip integration tests
    os.environ.pop('SKIP_INTEGRATION_TESTS', None)
    
    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def run_specific_test(test_name):
    """Run a specific test module"""
    print(f"🎯 Running specific test: {test_name}")
    
    # Load the specific test module
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(test_name)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description='Run VEO and audio generator tests')
    parser.add_argument('--unit', action='store_true', help='Run unit tests only (fast, mocked)')
    parser.add_argument('--integration', action='store_true', help='Run integration tests (real API calls)')
    parser.add_argument('--test', type=str, help='Run specific test module (e.g., test_veo2_client)')
    parser.add_argument('--all', action='store_true', help='Run all tests (unit and integration)')
    
    args = parser.parse_args()
    
    # Check for API key
    if not os.getenv('GOOGLE_API_KEY'):
        print("❌ Error: GOOGLE_API_KEY environment variable is required")
        print("Please set your Google API key:")
        print("export GOOGLE_API_KEY='your-api-key-here'")
        return False
    
    success = True
    
    if args.test:
        # Run specific test
        success = run_specific_test(args.test)
    elif args.unit:
        # Run unit tests only
        os.environ['SKIP_INTEGRATION_TESTS'] = 'true'
        success = run_unit_tests()
    elif args.integration:
        # Run integration tests only
        success = run_integration_tests()
    elif args.all:
        # Run all tests
        print("🚀 Running all tests...")
        print("\n" + "="*50)
        print("1. Unit Tests (mocked, fast)")
        print("="*50)
        os.environ['SKIP_INTEGRATION_TESTS'] = 'true'
        unit_success = run_unit_tests()
        
        print("\n" + "="*50)
        print("2. Integration Tests (real API calls)")
        print("="*50)
        os.environ.pop('SKIP_INTEGRATION_TESTS', None)
        integration_success = run_integration_tests()
        
        success = unit_success and integration_success
    else:
        # Default: run unit tests only
        print("📝 Running unit tests by default (use --help for options)")
        os.environ['SKIP_INTEGRATION_TESTS'] = 'true'
        success = run_unit_tests()
    
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
    
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)