#!/usr/bin/env python3
"""
Comprehensive Test Runner for AI Video Generator
Runs all unit tests, integration tests, and end-to-end tests
"""

import unittest
import sys
import os
import time
import traceback
from io import StringIO
from typing import Dict, List, Tuple

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Test discovery
TEST_MODULES = [
    'tests.unit.test_agents',
    'tests.unit.test_orchestrators', 
    'tests.integration.test_video_generation',
    'tests.e2e.test_full_system'
]


class ColoredTextTestResult(unittest.TextTestResult):
    """Test result with colored output"""
    
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.success_count = 0
        self.test_results = []
        self.verbosity = verbosity  # Store verbosity
    
    def addSuccess(self, test):
        super().addSuccess(test)
        self.success_count += 1
        self.test_results.append(('PASS', test, None))
        if self.verbosity > 1:
            self.stream.write(f"✅ {self.getDescription(test)}\n")
    
    def addError(self, test, err):
        super().addError(test, err)
        self.test_results.append(('ERROR', test, err))
        if self.verbosity > 1:
            self.stream.write(f"❌ {self.getDescription(test)} - ERROR\n")
    
    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.test_results.append(('FAIL', test, err))
        if self.verbosity > 1:
            self.stream.write(f"❌ {self.getDescription(test)} - FAIL\n")
    
    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.test_results.append(('SKIP', test, reason))
        if self.verbosity > 1:
            self.stream.write(f"⏭️  {self.getDescription(test)} - SKIPPED ({reason})\n")


class ComprehensiveTestRunner:
    """Comprehensive test runner with detailed reporting"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.results = {}
        self.overall_stats = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'errors': 0,
            'skipped': 0
        }
    
    def run_test_module(self, module_name: str) -> Tuple[unittest.TestResult, float]:
        """Run tests for a specific module"""
        print(f"\n{'='*60}")
        print(f"🧪 Running {module_name}")
        print(f"{'='*60}")
        
        start_time = time.time()
        
        try:
            # Import the test module
            test_module = __import__(module_name, fromlist=[''])
            
            # Create test suite
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromModule(test_module)
            
            # Run tests with custom result class
            stream = StringIO()
            runner = unittest.TextTestRunner(
                stream=stream,
                verbosity=2,
                resultclass=ColoredTextTestResult
            )
            
            result = runner.run(suite)
            
            # Print results to console
            print(stream.getvalue())
            
            execution_time = time.time() - start_time
            
            return result, execution_time
            
        except ImportError as e:
            print(f"❌ Failed to import {module_name}: {e}")
            # Create a dummy result for failed imports
            result = unittest.TestResult()
            result.errors.append((module_name, (ImportError, e, None)))
            return result, time.time() - start_time
        
        except Exception as e:
            print(f"❌ Error running {module_name}: {e}")
            traceback.print_exc()
            result = unittest.TestResult()
            result.errors.append((module_name, (Exception, e, None)))
            return result, time.time() - start_time
    
    def run_all_tests(self) -> Dict:
        """Run all test modules"""
        print("🎬 AI Video Generator - Comprehensive Test Suite")
        print("=" * 80)
        
        self.start_time = time.time()
        
        for module_name in TEST_MODULES:
            result, execution_time = self.run_test_module(module_name)
            
            # Store results
            self.results[module_name] = {
                'result': result,
                'execution_time': execution_time,
                'tests_run': result.testsRun,
                'failures': len(result.failures),
                'errors': len(result.errors),
                'skipped': len(result.skipped) if hasattr(result, 'skipped') else 0,
                'success': result.testsRun - len(result.failures) - len(result.errors)
            }
            
            # Update overall stats
            self.overall_stats['total_tests'] += result.testsRun
            self.overall_stats['failed'] += len(result.failures)
            self.overall_stats['errors'] += len(result.errors)
            self.overall_stats['skipped'] += len(result.skipped) if hasattr(result, 'skipped') else 0
            self.overall_stats['passed'] += (result.testsRun - len(result.failures) - len(result.errors))
        
        self.end_time = time.time()
        
        return self.results
    
    def generate_report(self):
        """Generate comprehensive test report"""
        total_time = self.end_time - self.start_time
        
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST REPORT")
        print("=" * 80)
        
        # Overall summary
        print(f"\n🎯 OVERALL SUMMARY")
        print(f"   Total Tests: {self.overall_stats['total_tests']}")
        print(f"   ✅ Passed: {self.overall_stats['passed']}")
        print(f"   ❌ Failed: {self.overall_stats['failed']}")
        print(f"   💥 Errors: {self.overall_stats['errors']}")
        print(f"   ⏭️  Skipped: {self.overall_stats['skipped']}")
        print(f"   ⏱️  Total Time: {total_time:.2f}s")
        
        # Calculate success rate
        if self.overall_stats['total_tests'] > 0:
            success_rate = (self.overall_stats['passed'] / self.overall_stats['total_tests']) * 100
            print(f"   📈 Success Rate: {success_rate:.1f}%")
        
        # Module breakdown
        print(f"\n📋 MODULE BREAKDOWN")
        print("-" * 60)
        
        for module_name, stats in self.results.items():
            module_short = module_name.split('.')[-1]
            status = "✅ PASS" if stats['failures'] == 0 and stats['errors'] == 0 else "❌ FAIL"
            
            print(f"{status} {module_short:<25} | "
                  f"Tests: {stats['tests_run']:2d} | "
                  f"Pass: {stats['success']:2d} | "
                  f"Fail: {stats['failures']:2d} | "
                  f"Err: {stats['errors']:2d} | "
                  f"Skip: {stats['skipped']:2d} | "
                  f"Time: {stats['execution_time']:5.2f}s")
        
        # Detailed failures and errors
        self._print_detailed_failures()
        
        # System status
        self._print_system_status()
        
        # Recommendations
        self._print_recommendations()
    
    def _print_detailed_failures(self):
        """Print detailed failure and error information"""
        has_failures = False
        
        for module_name, stats in self.results.items():
            result = stats['result']
            
            if result.failures or result.errors:
                if not has_failures:
                    print(f"\n🔍 DETAILED FAILURES & ERRORS")
                    print("-" * 60)
                    has_failures = True
                
                print(f"\n📁 {module_name}")
                
                # Print failures
                for test, traceback_str in result.failures:
                    print(f"   ❌ FAIL: {test}")
                    print(f"      {traceback_str.split('AssertionError:')[-1].strip() if 'AssertionError:' in traceback_str else 'See details above'}")
                
                # Print errors
                for test, traceback_str in result.errors:
                    print(f"   💥 ERROR: {test}")
                    error_msg = traceback_str.split('\n')[-2] if '\n' in traceback_str else str(traceback_str)
                    print(f"      {error_msg}")
        
        if not has_failures:
            print(f"\n🎉 NO FAILURES OR ERRORS!")
    
    def _print_system_status(self):
        """Print system component status"""
        print(f"\n🔧 SYSTEM COMPONENT STATUS")
        print("-" * 60)
        
        # Check which components are available
        components = {
            'Working Simple Orchestrator': 'src.agents.working_simple_orchestrator',
            'Enhanced Working Orchestrator': 'src.agents.enhanced_working_orchestrator',
            'Simple Orchestrator': 'src.agents.simple_orchestrator',
            'Director Agent': 'src.generators.director',
            'Voice Director Agent': 'src.agents.voice_director_agent',
            'Continuity Agent': 'src.agents.continuity_decision_agent',
            'Video Composition Agents': 'src.agents.video_composition_agents',
            'Script Processor': 'src.generators.enhanced_script_processor',
            'Trending Analyzer': 'src.utils.trending_analyzer',
            'Multilingual Generator': 'src.generators.integrated_multilang_generator'
        }
        
        for component_name, module_path in components.items():
            try:
                __import__(module_path, fromlist=[''])
                print(f"✅ {component_name:<30} Available")
            except ImportError:
                print(f"❌ {component_name:<30} Not Available")
    
    def _print_recommendations(self):
        """Print recommendations based on test results"""
        print(f"\n💡 RECOMMENDATIONS")
        print("-" * 60)
        
        recommendations = []
        
        # Check success rate
        if self.overall_stats['total_tests'] > 0:
            success_rate = (self.overall_stats['passed'] / self.overall_stats['total_tests']) * 100
            
            if success_rate >= 90:
                recommendations.append("🎉 Excellent! System is highly stable and ready for production.")
            elif success_rate >= 75:
                recommendations.append("✅ Good system stability. Address remaining failures for production readiness.")
            elif success_rate >= 50:
                recommendations.append("⚠️  Moderate stability. Significant issues need attention before production.")
            else:
                recommendations.append("🚨 Low stability. Major issues require immediate attention.")
        
        # Check for specific issues
        if self.overall_stats['errors'] > 0:
            recommendations.append("🔧 Fix import errors and missing dependencies.")
        
        if self.overall_stats['skipped'] > 5:
            recommendations.append("📦 Many tests skipped - consider installing missing dependencies.")
        
        # Performance recommendations
        total_time = self.end_time - self.start_time
        if total_time > 60:
            recommendations.append("⚡ Test suite is slow - consider optimizing test performance.")
        
        # Print recommendations
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
        
        if not recommendations:
            recommendations.append("🎯 System appears to be working well!")
            print(f"1. {recommendations[0]}")


def main():
    """Main test runner function"""
    print("🚀 Starting Comprehensive Test Suite...")
    
    # Check if we're in the right directory
    if not os.path.exists('src'):
        print("❌ Error: Please run from the project root directory")
        sys.exit(1)
    
    # Check for API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("⚠️  Warning: GOOGLE_API_KEY not set - some tests may be skipped")
    else:
        print(f"✅ API key configured (length: {len(api_key)})")
    
    # Create and run test runner
    runner = ComprehensiveTestRunner()
    
    try:
        results = runner.run_all_tests()
        runner.generate_report()
        
        # Exit with appropriate code
        if runner.overall_stats['failed'] > 0 or runner.overall_stats['errors'] > 0:
            print(f"\n❌ Tests completed with failures")
            sys.exit(1)
        else:
            print(f"\n✅ All tests passed successfully!")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print(f"\n⏹️  Test run interrupted by user")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n💥 Test runner failed: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main() 