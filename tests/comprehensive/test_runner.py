#!/usr/bin/env python3
"""
Comprehensive Test Runner for AI Video Generator
Runs all tests and provides detailed reporting
"""

import os
import sys
import time
import subprocess
import json
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

class TestResult:
    """Test result container"""
    
    def __init__(self, name: str, passed: bool, duration: float, 
                 error: str = None, details: Dict[str, Any] = None):
        self.name = name
        self.passed = passed
        self.duration = duration
        self.error = error
        self.details = details or {}
        self.timestamp = datetime.now()


class ComprehensiveTestRunner:
    """Comprehensive test runner for the AI Video Generator"""
    
    def __init__(self, project_root: str = None):
        """
        Initialize test runner
        
        Args:
            project_root: Root directory of the project
        """
        self.project_root = project_root or os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.test_results: List[TestResult] = []
        self.start_time = None
        self.end_time = None
        
        # Test categories
        self.test_categories = {
            "unit": "tests/unit",
            "integration": "tests/integration", 
            "e2e": "tests/e2e",
            "comprehensive": "tests/comprehensive"
        }
        
        print(f"🧪 Comprehensive Test Runner initialized")
        print(f"📁 Project root: {self.project_root}")
    
    def run_all_tests(self) -> Dict[str, Any]:
        """
        Run all test categories
        
        Returns:
            Dictionary with test results summary
        """
        print("\n🚀 Starting comprehensive test run...")
        self.start_time = time.time()
        
        # Run each test category
        for category, path in self.test_categories.items():
            print(f"\n📋 Running {category} tests...")
            self._run_test_category(category, path)
        
        # Run specific critical tests
        print(f"\n🔍 Running critical system tests...")
        self._run_critical_tests()
        
        self.end_time = time.time()
        
        # Generate report
        report = self._generate_report()
        self._save_report(report)
        self._print_summary(report)
        
        return report
    
    def _run_test_category(self, category: str, path: str):
        """Run tests in a specific category"""
        test_dir = os.path.join(self.project_root, path)
        
        if not os.path.exists(test_dir):
            print(f"⚠️ Test directory not found: {test_dir}")
            return
        
        # Find all test files
        test_files = []
        for root, dirs, files in os.walk(test_dir):
            for file in files:
                if file.startswith('test_') and file.endswith('.py'):
                    test_files.append(os.path.join(root, file))
        
        if not test_files:
            print(f"⚠️ No test files found in {test_dir}")
            return
        
        print(f"🔍 Found {len(test_files)} test files in {category}")
        
        # Run each test file
        for test_file in test_files:
            self._run_test_file(category, test_file)
    
    def _run_test_file(self, category: str, test_file: str):
        """Run a specific test file"""
        test_name = f"{category}:{os.path.basename(test_file)}"
        print(f"  🧪 Running {test_name}...")
        
        start_time = time.time()
        
        try:
            # Run pytest on the file
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                test_file, 
                "-v",
                "--tb=short",
                "--json-report",
                "--json-report-file=/tmp/test_report.json"
            ], 
            capture_output=True, 
            text=True,
            cwd=self.project_root
            )
            
            duration = time.time() - start_time
            
            # Parse results
            if result.returncode == 0:
                self.test_results.append(TestResult(
                    name=test_name,
                    passed=True,
                    duration=duration,
                    details={"stdout": result.stdout}
                ))
                print(f"    ✅ PASSED ({duration:.2f}s)")
            else:
                self.test_results.append(TestResult(
                    name=test_name,
                    passed=False,
                    duration=duration,
                    error=result.stderr,
                    details={"stdout": result.stdout, "stderr": result.stderr}
                ))
                print(f"    ❌ FAILED ({duration:.2f}s)")
                if result.stderr:
                    print(f"    Error: {result.stderr[:200]}...")
        
        except Exception as e:
            duration = time.time() - start_time
            self.test_results.append(TestResult(
                name=test_name,
                passed=False,
                duration=duration,
                error=str(e)
            ))
            print(f"    ❌ ERROR ({duration:.2f}s): {e}")
    
    def _run_critical_tests(self):
        """Run critical system tests"""
        critical_tests = [
            ("Session Management", self._test_session_management),
            ("Circuit Breaker", self._test_circuit_breaker),
            ("Retry Manager", self._test_retry_manager),
            ("Video Generator Integration", self._test_video_generator_integration),
            ("GUI Functionality", self._test_gui_functionality)
        ]
        
        for test_name, test_func in critical_tests:
            print(f"  🔍 Running {test_name}...")
            start_time = time.time()
            
            try:
                test_func()
                duration = time.time() - start_time
                self.test_results.append(TestResult(
                    name=f"critical:{test_name}",
                    passed=True,
                    duration=duration
                ))
                print(f"    ✅ PASSED ({duration:.2f}s)")
            
            except Exception as e:
                duration = time.time() - start_time
                self.test_results.append(TestResult(
                    name=f"critical:{test_name}",
                    passed=False,
                    duration=duration,
                    error=str(e)
                ))
                print(f"    ❌ FAILED ({duration:.2f}s): {e}")
    
    def _test_session_management(self):
        """Test session management functionality"""
        from utils.session_manager import session_manager
        from utils.session_context import create_session_context
        
        # Create test session
        session_id = session_manager.create_session(
            topic="Test Session",
            platform="tiktok",
            duration=15,
            category="Educational"
        )
        
        # Test session context
        context = create_session_context(session_id)
        assert context.session_id == session_id
        
        # Test file operations
        test_path = context.get_output_path("video_clips", "test.mp4")
        assert session_id in test_path
        
        # Cleanup
        session_manager.cleanup_session(session_id)
    
    def _test_circuit_breaker(self):
        """Test circuit breaker functionality"""
        from shared.resilience.circuit_breaker import CircuitBreaker, CircuitBreakerConfig
        
        # Create circuit breaker
        config = CircuitBreakerConfig(failure_threshold=2, reset_timeout=1)
        cb = CircuitBreaker("test_cb", config)
        
        # Test successful call
        def success_func():
            return "success"
        
        result = cb.call(success_func)
        assert result == "success"
        
        # Test failure handling
        def failure_func():
            raise Exception("test failure")
        
        failure_count = 0
        try:
            cb.call(failure_func)
        except:
            failure_count += 1
        
        assert failure_count == 1
    
    def _test_retry_manager(self):
        """Test retry manager functionality"""
        from shared.resilience.retry_manager import RetryManager, RetryConfig
        
        # Create retry manager
        config = RetryConfig(max_retries=2, base_delay=0.1)
        rm = RetryManager("test_rm", config)
        
        # Test successful call
        def success_func():
            return "success"
        
        result = rm.retry(success_func)
        assert result == "success"
        
        # Test retry on failure
        attempt_count = 0
        def retry_func():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 2:
                raise Exception("temporary failure")
            return "success after retry"
        
        result = rm.retry(retry_func)
        assert result == "success after retry"
        assert attempt_count == 2
    
    def _test_video_generator_integration(self):
        """Test video generator integration"""
        # Test imports
        from generators.video_generator import VideoGenerator
        from models.video_models import GeneratedVideoConfig, Platform, VideoCategory
        
        # Test configuration creation
        config = GeneratedVideoConfig(
            target_platform=Platform.TIKTOK,
            category=VideoCategory.EDUCATIONAL,
            duration_seconds=15,
            topic="Test Integration",
            style="viral",
            tone="engaging",
            target_audience="general",
            hook="Test hook",
            main_content=["Test content"],
            call_to_action="Test CTA",
            visual_style="dynamic",
            color_scheme=["#FF0000"],
            transitions=["fade"],
            background_music_style="upbeat",
            voiceover_style="energetic"
        )
        
        # Test generator initialization
        generator = VideoGenerator(api_key="test_key")
        assert generator.api_key == "test_key"
    
    def _test_gui_functionality(self):
        """Test GUI functionality"""
        import requests
        import subprocess
        import time
        
        # Start GUI in background
        gui_process = subprocess.Popen([
            sys.executable, "modern_ui.py"
        ], cwd=self.project_root)
        
        try:
            # Wait for startup
            time.sleep(5)
            
            # Test GUI accessibility
            response = requests.get("http://localhost:7860/", timeout=5)
            assert response.status_code == 200
            
            # Test GUI content
            content = response.text.lower()
            assert "video" in content
            assert "generate" in content
            
        finally:
            # Stop GUI
            gui_process.terminate()
            gui_process.wait()
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.passed)
        failed_tests = total_tests - passed_tests
        
        total_duration = self.end_time - self.start_time if self.end_time and self.start_time else 0
        
        # Group by category
        categories = {}
        for result in self.test_results:
            category = result.name.split(':')[0]
            if category not in categories:
                categories[category] = {"passed": 0, "failed": 0, "duration": 0}
            
            if result.passed:
                categories[category]["passed"] += 1
            else:
                categories[category]["failed"] += 1
            
            categories[category]["duration"] += result.duration
        
        # Generate report
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "total_duration": total_duration
            },
            "categories": categories,
            "failed_tests": [
                {
                    "name": r.name,
                    "error": r.error,
                    "duration": r.duration
                } for r in self.test_results if not r.passed
            ],
            "all_results": [
                {
                    "name": r.name,
                    "passed": r.passed,
                    "duration": r.duration,
                    "error": r.error,
                    "timestamp": r.timestamp.isoformat()
                } for r in self.test_results
            ]
        }
        
        return report
    
    def _save_report(self, report: Dict[str, Any]):
        """Save test report to file"""
        report_file = os.path.join(self.project_root, "test_report.json")
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Test report saved to: {report_file}")
    
    def _print_summary(self, report: Dict[str, Any]):
        """Print test summary"""
        summary = report["summary"]
        
        print("\n" + "="*60)
        print("🧪 COMPREHENSIVE TEST SUMMARY")
        print("="*60)
        
        print(f"📊 Total Tests: {summary['total_tests']}")
        print(f"✅ Passed: {summary['passed']}")
        print(f"❌ Failed: {summary['failed']}")
        print(f"📈 Success Rate: {summary['success_rate']:.1f}%")
        print(f"⏱️ Total Duration: {summary['total_duration']:.2f}s")
        
        print("\n📋 Results by Category:")
        for category, stats in report["categories"].items():
            total = stats["passed"] + stats["failed"]
            success_rate = (stats["passed"] / total * 100) if total > 0 else 0
            print(f"  {category}: {stats['passed']}/{total} ({success_rate:.1f}%) - {stats['duration']:.2f}s")
        
        if report["failed_tests"]:
            print("\n❌ Failed Tests:")
            for test in report["failed_tests"]:
                print(f"  - {test['name']}: {test['error'][:100]}...")
        
        # Overall status
        if summary["failed"] == 0:
            print("\n🎉 ALL TESTS PASSED! 🎉")
        else:
            print(f"\n⚠️ {summary['failed']} TESTS FAILED")
        
        print("="*60)


def main():
    """Main entry point"""
    runner = ComprehensiveTestRunner()
    report = runner.run_all_tests()
    
    # Exit with appropriate code
    exit_code = 0 if report["summary"]["failed"] == 0 else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main() 