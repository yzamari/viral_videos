#!/usr/bin/env python3
"""VEO Clients Test Runner
Runs all VEO-2 and VEO-3 client tests to ensure they're always working """import subprocess
import sys
import os

 def run_test_suite(test_path, description): """Run a test suite and return the result"""print(f"\n{'=' * 60}") print(f"🧪 {description}") print(f"{'=' * 60}")

    try:
        result = subprocess.run([ sys.executable, "-m", "pytest", test_path, "-v", "--tb=short"], capture_output=True, text=True, cwd=os.getcwd())

        print(result.stdout)
        if result.stderr: print("STDERR:", result.stderr)

        return result.returncode == 0
    except Exception as e: print(f"❌ Error running tests: {e}")
        return False

 def main(): """Run all VEO client tests"""print("🎬 VEO Clients Test Suite") print("Testing VEO-2 and VEO-3 clients to ensure they're always working")

    test_results = []

    # Test 1: VEO Client Unit Tests
    success = run_test_suite( "tests/unit/test_veo_clients.py", "VEO Client Unit Tests (Regular + Continuous Mode)") test_results.append(("VEO Client Unit Tests", success))

    # Test 2: VEO Client Integration Tests
    success = run_test_suite( "tests/integration/test_video_generation.py::TestVeoClientIntegration", "VEO Client Integration Tests") test_results.append(("VEO Client Integration Tests", success))

    # Test 3: Quick VEO Client Functionality Test print(f"\n{'=' * 60}") print("🔧 Quick VEO Client Functionality Test") print(f"{'=' * 60}")

    try:
        # Test VEO-2 client initialization
        from src.generators.vertex_ai_veo2_client import VertexAIVeo2Client
        veo2_client = VertexAIVeo2Client( project_id='test-project', location='us-central1', gcs_bucket='test-bucket', output_dir='test_output')
        print( f"✅ VEO-2 Client: {veo2_client.get_model_name()} - Available: {veo2_client.is_available}")

        # Test VEO-3 client initialization
        from src.generators.vertex_veo3_client import VertexAIVeo3Client
        veo3_client = VertexAIVeo3Client( project_id='test-project', location='us-central1', gcs_bucket='test-bucket', output_dir='test_output')
        print( f"✅ VEO-3 Client: {veo3_client.get_model_name()} - Available: {veo3_client.is_available}")

        functionality_success = True

    except Exception as e: print(f"❌ VEO Client Functionality Test Failed: {e}")
        functionality_success = False
 test_results.append(("VEO Client Functionality Test", functionality_success))
 # Summary print(f"\n{'=' * 60}") print("📊 TEST SUMMARY") print(f"{'=' * 60}")

    all_passed = True
    for test_name, success in test_results: status = "✅ PASSED" if success else "❌ FAILED"print(f"{status} {test_name}")
        if not success:
            all_passed = False print(f"\n{'=' * 60}")
    if all_passed: print("🎉 ALL VEO CLIENT TESTS PASSED!") print("Both VEO-2 and VEO-3 clients are working correctly with regular and continuous mode") else: print("⚠️  SOME VEO CLIENT TESTS FAILED!") print("Please check the test output above for details") print(f"{'=' * 60}")

    return 0 if all_passed else 1

 if __name__ == "__main__":
    sys.exit(main())
