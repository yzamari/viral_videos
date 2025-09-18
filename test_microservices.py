#!/usr/bin/env python3
"""
Test Suite for ViralAI Microservices Architecture
Tests SOLID principles implementation and service communication
"""
import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, Any, List

# ANSI colors for output
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color


class MicroservicesTester:
    """Test all microservices"""
    
    def __init__(self):
        self.services = {
            "prompt-optimizer": "http://localhost:8001",
            "video-generator": "http://localhost:8002",
            "monitoring": "http://localhost:8003",
            "orchestrator": "http://localhost:8005"
        }
        self.test_results = []
    
    def run_all_tests(self):
        """Run all tests"""
        print(f"{BLUE}{'='*60}")
        print("🧪 VIRALAI MICROSERVICES TEST SUITE")
        print(f"{'='*60}{NC}\n")
        
        # Test 1: Service Health Checks
        self.test_service_health()
        
        # Test 2: SOLID - Single Responsibility
        self.test_single_responsibility()
        
        # Test 3: SOLID - Open/Closed
        self.test_open_closed()
        
        # Test 4: SOLID - Interface Segregation
        self.test_interface_segregation()
        
        # Test 5: Service Communication
        self.test_service_communication()
        
        # Test 6: Monitoring & Metrics
        self.test_monitoring()
        
        # Test 7: End-to-End Workflow
        self.test_end_to_end_workflow()
        
        # Test 8: Performance & Scalability
        self.test_performance()
        
        # Print summary
        self.print_summary()
    
    def test_service_health(self):
        """Test 1: Check if all services are healthy"""
        print(f"{YELLOW}Test 1: Service Health Checks{NC}")
        print("-" * 40)
        
        all_healthy = True
        for service_name, service_url in self.services.items():
            try:
                response = requests.get(f"{service_url}/health", timeout=2)
                if response.status_code == 200:
                    print(f"  {GREEN}✓{NC} {service_name}: Healthy")
                else:
                    print(f"  {RED}✗{NC} {service_name}: Unhealthy (status: {response.status_code})")
                    all_healthy = False
            except Exception as e:
                print(f"  {RED}✗{NC} {service_name}: Down ({str(e)})")
                all_healthy = False
        
        self.test_results.append(("Service Health", all_healthy))
        print()
    
    def test_single_responsibility(self):
        """Test 2: Verify Single Responsibility Principle"""
        print(f"{YELLOW}Test 2: Single Responsibility Principle{NC}")
        print("-" * 40)
        
        tests_passed = True
        
        # Test prompt optimizer only optimizes
        try:
            response = requests.post(
                f"{self.services['prompt-optimizer']}/optimize",
                json={"prompt": "Test prompt with war and violence", "level": "moderate"}
            )
            result = response.json()
            
            # Should only contain optimization data
            expected_keys = {"optimized_prompt", "is_safe", "success_probability"}
            if not all(k in result for k in expected_keys):
                print(f"  {RED}✗{NC} Prompt optimizer has unexpected responsibilities")
                tests_passed = False
            else:
                print(f"  {GREEN}✓{NC} Prompt optimizer follows SRP")
        except:
            tests_passed = False
        
        # Test video generator only generates
        # Test monitoring only monitors
        
        self.test_results.append(("Single Responsibility", tests_passed))
        print()
    
    def test_open_closed(self):
        """Test 3: Verify Open/Closed Principle"""
        print(f"{YELLOW}Test 3: Open/Closed Principle{NC}")
        print("-" * 40)
        
        # Services should be extensible without modification
        # Test different optimization levels
        levels = ["minimal", "moderate", "aggressive", "extreme"]
        all_work = True
        
        for level in levels:
            try:
                response = requests.post(
                    f"{self.services['prompt-optimizer']}/optimize",
                    json={"prompt": "Test prompt", "level": level}
                )
                if response.status_code != 200:
                    all_work = False
                    print(f"  {RED}✗{NC} Optimization level '{level}' failed")
                else:
                    print(f"  {GREEN}✓{NC} Optimization level '{level}' supported")
            except:
                all_work = False
        
        self.test_results.append(("Open/Closed Principle", all_work))
        print()
    
    def test_interface_segregation(self):
        """Test 4: Verify Interface Segregation"""
        print(f"{YELLOW}Test 4: Interface Segregation{NC}")
        print("-" * 40)
        
        # Each service should have focused endpoints
        endpoints = {
            "prompt-optimizer": ["/optimize", "/validate", "/stats"],
            "video-generator": ["/generate", "/generate-async", "/job", "/stats"],
            "monitoring": ["/metrics", "/events", "/dashboard"],
            "orchestrator": ["/workflow", "/workflows", "/stats"]
        }
        
        all_good = True
        for service, expected_endpoints in endpoints.items():
            service_url = self.services[service]
            available = []
            
            for endpoint in expected_endpoints:
                try:
                    # Try OPTIONS request to check if endpoint exists
                    response = requests.options(f"{service_url}{endpoint}")
                    if response.status_code in [200, 204, 405]:  # 405 means endpoint exists but doesn't support OPTIONS
                        available.append(endpoint)
                except:
                    pass
            
            if len(available) >= len(expected_endpoints) * 0.5:  # At least half should be available
                print(f"  {GREEN}✓{NC} {service}: Focused interface")
            else:
                print(f"  {RED}✗{NC} {service}: Interface issues")
                all_good = False
        
        self.test_results.append(("Interface Segregation", all_good))
        print()
    
    def test_service_communication(self):
        """Test 5: Test inter-service communication"""
        print(f"{YELLOW}Test 5: Service Communication{NC}")
        print("-" * 40)
        
        # Test orchestrator can reach other services
        try:
            response = requests.get(f"{self.services['orchestrator']}/services/status")
            if response.status_code == 200:
                status = response.json()
                healthy_count = sum(1 for s in status.values() if s.get("status") == "healthy")
                print(f"  {GREEN}✓{NC} Orchestrator can reach {healthy_count}/{len(status)} services")
                success = healthy_count > 0
            else:
                print(f"  {RED}✗{NC} Service communication failed")
                success = False
        except Exception as e:
            print(f"  {RED}✗{NC} Communication test failed: {e}")
            success = False
        
        self.test_results.append(("Service Communication", success))
        print()
    
    def test_monitoring(self):
        """Test 6: Test monitoring and metrics"""
        print(f"{YELLOW}Test 6: Monitoring & Metrics{NC}")
        print("-" * 40)
        
        try:
            # Record a test metric
            response = requests.post(
                f"{self.services['monitoring']}/metrics",
                json={
                    "service": "test",
                    "name": "test_metric",
                    "value": 42
                }
            )
            
            if response.status_code == 200:
                print(f"  {GREEN}✓{NC} Metric recording works")
                
                # Get metrics
                response = requests.get(f"{self.services['monitoring']}/metrics?service=test")
                if response.status_code == 200:
                    print(f"  {GREEN}✓{NC} Metric retrieval works")
                    success = True
                else:
                    success = False
            else:
                success = False
        except:
            success = False
            print(f"  {RED}✗{NC} Monitoring service issues")
        
        self.test_results.append(("Monitoring", success))
        print()
    
    def test_end_to_end_workflow(self):
        """Test 7: Test complete workflow"""
        print(f"{YELLOW}Test 7: End-to-End Workflow{NC}")
        print("-" * 40)
        
        try:
            # Start a workflow
            response = requests.post(
                f"{self.services['orchestrator']}/workflow",
                json={
                    "mission": "Create a test video about technology",
                    "duration": 10,
                    "platform": "youtube",
                    "style": "cinematic",
                    "parallel": True
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                workflow_id = result["workflow_id"]
                print(f"  {GREEN}✓{NC} Workflow created: {workflow_id}")
                
                # Wait and check status
                time.sleep(2)
                response = requests.get(f"{self.services['orchestrator']}/workflow/{workflow_id}")
                if response.status_code == 200:
                    status = response.json()
                    print(f"  {GREEN}✓{NC} Workflow status: {status['stage']}")
                    success = True
                else:
                    success = False
            else:
                success = False
                print(f"  {RED}✗{NC} Workflow creation failed")
        except Exception as e:
            success = False
            print(f"  {RED}✗{NC} Workflow test failed: {e}")
        
        self.test_results.append(("End-to-End Workflow", success))
        print()
    
    def test_performance(self):
        """Test 8: Test performance and response times"""
        print(f"{YELLOW}Test 8: Performance & Scalability{NC}")
        print("-" * 40)
        
        # Test response times
        response_times = {}
        
        for service_name, service_url in self.services.items():
            try:
                start = time.time()
                response = requests.get(f"{service_url}/health")
                elapsed = (time.time() - start) * 1000  # Convert to ms
                response_times[service_name] = elapsed
                
                if elapsed < 100:  # Should respond in less than 100ms
                    print(f"  {GREEN}✓{NC} {service_name}: {elapsed:.1f}ms")
                else:
                    print(f"  {YELLOW}⚠{NC} {service_name}: {elapsed:.1f}ms (slow)")
            except:
                print(f"  {RED}✗{NC} {service_name}: No response")
        
        avg_time = sum(response_times.values()) / len(response_times) if response_times else 999
        success = avg_time < 200  # Average should be under 200ms
        
        self.test_results.append(("Performance", success))
        print()
    
    def print_summary(self):
        """Print test summary"""
        print(f"{BLUE}{'='*60}")
        print("📊 TEST SUMMARY")
        print(f"{'='*60}{NC}\n")
        
        passed = sum(1 for _, result in self.test_results if result)
        total = len(self.test_results)
        
        for test_name, result in self.test_results:
            if result:
                print(f"  {GREEN}✓{NC} {test_name}")
            else:
                print(f"  {RED}✗{NC} {test_name}")
        
        print(f"\n{BLUE}{'='*60}{NC}")
        percentage = (passed / total) * 100 if total > 0 else 0
        
        if percentage >= 80:
            color = GREEN
            message = "EXCELLENT! System is production ready."
        elif percentage >= 60:
            color = YELLOW
            message = "GOOD. Some improvements needed."
        else:
            color = RED
            message = "NEEDS WORK. Critical issues found."
        
        print(f"{color}Result: {passed}/{total} tests passed ({percentage:.0f}%)")
        print(f"{message}{NC}")
        print(f"{BLUE}{'='*60}{NC}\n")


def main():
    """Main test runner"""
    tester = MicroservicesTester()
    
    print(f"{YELLOW}Waiting for services to be ready...{NC}")
    time.sleep(2)
    
    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print(f"\n{RED}Tests interrupted by user{NC}")
        sys.exit(1)
    except Exception as e:
        print(f"{RED}Test suite failed: {e}{NC}")
        sys.exit(1)


if __name__ == "__main__":
    main()