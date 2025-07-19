#!/usr/bin/env python3
"""
Comprehensive Unit Test Runner
Executes all unit tests and provides detailed coverage reporting
"""

import unittest
import sys
import os
import time
from io import StringIO
from datetime import datetime
import json

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import test modules
from unit.test_video_generator import TestVideoGenerator
from unit.test_visual_style_agent import TestVisualStyleAgent
from unit.test_voice_director_agent import TestVoiceDirectorAgent
from unit.test_working_orchestrator import TestWorkingOrchestrator
from unit.test_multi_agent_discussion import TestMultiAgentDiscussionSystem


class ComprehensiveTestRunner:
    """Comprehensive test runner with detailed reporting"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = None
        self.end_time = None
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.error_tests = 0
        self.skipped_tests = 0
        
    def run_all_tests(self):
        """Run all unit tests and generate comprehensive report"""
        print("🧪 COMPREHENSIVE UNIT TEST EXECUTION")
        print("=" * 60)
        
        self.start_time = datetime.now()
        
        # Create test suite
        test_suite = unittest.TestSuite()
        
        # Add all test classes
        test_classes = [
            TestVideoGenerator,
            TestVisualStyleAgent,
            TestVoiceDirectorAgent,
            TestWorkingOrchestrator,
            TestMultiAgentDiscussionSystem
        ]
        
        for test_class in test_classes:
            tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
            test_suite.addTests(tests)
        
        # Run tests with detailed output
        stream = StringIO()
        runner = unittest.TextTestRunner(
            stream=stream,
            verbosity=2,
            failfast=False
        )
        
        result = runner.run(test_suite)
        
        self.end_time = datetime.now()
        
        # Process results
        self._process_results(result, stream.getvalue())
        
        # Generate reports
        self._generate_console_report()
        self._generate_json_report()
        
        return result.wasSuccessful()
    
    def _process_results(self, result, output):
        """Process test results"""
        self.total_tests = result.testsRun
        self.passed_tests = result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)
        self.failed_tests = len(result.failures)
        self.error_tests = len(result.errors)
        self.skipped_tests = len(result.skipped)
        
        # Store detailed results
        self.test_results = {
            'summary': {
                'total': self.total_tests,
                'passed': self.passed_tests,
                'failed': self.failed_tests,
                'errors': self.error_tests,
                'skipped': self.skipped_tests,
                'success_rate': (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0,
                'duration': (self.end_time - self.start_time).total_seconds()
            },
            'failures': [
                {
                    'test': str(test),
                    'error': traceback
                }
                for test, traceback in result.failures
            ],
            'errors': [
                {
                    'test': str(test),
                    'error': traceback
                }
                for test, traceback in result.errors
            ],
            'skipped': [
                {
                    'test': str(test),
                    'reason': reason
                }
                for test, reason in result.skipped
            ],
            'output': output
        }
    
    def _generate_console_report(self):
        """Generate console report"""
        print("\n" + "=" * 60)
        print("🏆 COMPREHENSIVE TEST RESULTS")
        print("=" * 60)
        
        # Summary
        print(f"⏱️  Duration: {self.test_results['summary']['duration']:.2f} seconds")
        print(f"📊 Total Tests: {self.total_tests}")
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.failed_tests}")
        print(f"💥 Errors: {self.error_tests}")
        print(f"⏭️  Skipped: {self.skipped_tests}")
        print(f"📈 Success Rate: {self.test_results['summary']['success_rate']:.1f}%")
        
        # Class-by-class breakdown
        print("\n📋 CLASS-BY-CLASS BREAKDOWN:")
        print("-" * 40)
        
        test_classes = [
            ('VideoGenerator', 'test_video_generator'),
            ('VisualStyleAgent', 'test_visual_style_agent'),
            ('VoiceDirectorAgent', 'test_voice_director_agent'),
            ('WorkingOrchestrator', 'test_working_orchestrator'),
            ('MultiAgentDiscussionSystem', 'test_multi_agent_discussion')
        ]
        
        for class_name, test_module in test_classes:
            class_tests = [line for line in self.test_results['output'].split('\n') 
                          if test_module in line and 'test_' in line]
            passed = len([line for line in class_tests if 'ok' in line.lower()])
            failed = len([line for line in class_tests if 'fail' in line.lower()])
            errors = len([line for line in class_tests if 'error' in line.lower()])
            total = passed + failed + errors
            
            if total > 0:
                success_rate = (passed / total * 100)
                status = "✅" if success_rate == 100 else "⚠️" if success_rate >= 80 else "❌"
                print(f"{status} {class_name}: {passed}/{total} ({success_rate:.1f}%)")
        
        # Detailed failures
        if self.failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            print("-" * 40)
            for i, failure in enumerate(self.test_results['failures'], 1):
                print(f"{i}. {failure['test']}")
                print(f"   Error: {failure['error'].split('AssertionError:')[-1].strip()}")
        
        # Detailed errors
        if self.error_tests > 0:
            print("\n💥 ERROR TESTS:")
            print("-" * 40)
            for i, error in enumerate(self.test_results['errors'], 1):
                print(f"{i}. {error['test']}")
                print(f"   Error: {error['error'].split('Exception:')[-1].strip()}")
        
        # Overall status
        print("\n" + "=" * 60)
        if self.failed_tests == 0 and self.error_tests == 0:
            print("🎉 ALL TESTS PASSED! System is production-ready!")
        elif self.test_results['summary']['success_rate'] >= 90:
            print("✅ MOSTLY SUCCESSFUL! Minor issues to address.")
        elif self.test_results['summary']['success_rate'] >= 70:
            print("⚠️  NEEDS ATTENTION! Several issues found.")
        else:
            print("❌ CRITICAL ISSUES! Major problems need fixing.")
        print("=" * 60)
    
    def _generate_json_report(self):
        """Generate JSON report for CI/CD"""
        report_path = os.path.join(os.path.dirname(__file__), 'unit_test_report.json')
        
        with open(report_path, 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        print(f"\n📄 Detailed report saved to: {report_path}")
    
    def run_specific_class(self, test_class_name):
        """Run tests for a specific class"""
        print(f"🧪 RUNNING TESTS FOR: {test_class_name}")
        print("=" * 60)
        
        class_mapping = {
            'VideoGenerator': TestVideoGenerator,
            'VisualStyleAgent': TestVisualStyleAgent,
            'VoiceDirectorAgent': TestVoiceDirectorAgent,
            'WorkingOrchestrator': TestWorkingOrchestrator,
            'MultiAgentDiscussionSystem': TestMultiAgentDiscussionSystem
        }
        
        if test_class_name not in class_mapping:
            print(f"❌ Unknown test class: {test_class_name}")
            print(f"Available classes: {list(class_mapping.keys())}")
            return False
        
        test_class = class_mapping[test_class_name]
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return result.wasSuccessful()


def main():
    """Main entry point"""
    runner = ComprehensiveTestRunner()
    
    if len(sys.argv) > 1:
        # Run specific class
        class_name = sys.argv[1]
        success = runner.run_specific_class(class_name)
    else:
        # Run all tests
        success = runner.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main() 