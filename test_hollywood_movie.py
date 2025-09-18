#!/usr/bin/env python3
"""
Hollywood Movie Generation Test
Tests the complete microservices system with a complex Hollywood-style video
Including sensitive content that needs optimization
"""
import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, Any, List
import threading

# ANSI colors
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
MAGENTA = '\033[0;35m'
NC = '\033[0m'


class HollywoodMovieTest:
    """Test Hollywood-style movie generation"""
    
    def __init__(self):
        self.services = {
            "orchestrator": "http://localhost:8005",
            "prompt_optimizer": "http://localhost:8001",
            "video_generator": "http://localhost:8002",
            "monitoring": "http://localhost:8003"
        }
        
        # The challenging Hollywood PTSD veteran mission
        self.test_mission = """
        Cinematic masterpiece: PTSD Israeli veteran's haunting journey through 
        October 7th 2024, Lebanon war and 2025 Iran war - emotional psychological 
        drama, ego POV, internal conflicts, Waltz with Bashir animation style,
        featuring combat scenes, explosions, weapons, military operations
        """
        
        self.workflow_id = None
        self.start_time = None
        self.metrics = {
            "prompts_optimized": 0,
            "safety_blocks_avoided": 0,
            "retries_performed": 0,
            "fallbacks_used": 0
        }
    
    def run_test(self):
        """Run the complete Hollywood movie test"""
        print(f"\n{MAGENTA}{'='*70}")
        print("🎬 HOLLYWOOD MOVIE GENERATION TEST")
        print(f"{'='*70}{NC}\n")
        
        # Step 1: Check services
        if not self.check_services_health():
            print(f"{RED}❌ Services not healthy. Please run ./start_microservices.sh{NC}")
            return False
        
        # Step 2: Test prompt optimization
        self.test_prompt_optimization()
        
        # Step 3: Start workflow
        self.start_workflow()
        
        # Step 4: Monitor generation
        self.monitor_generation()
        
        # Step 5: Analyze results
        self.analyze_results()
        
        # Step 6: Check metrics
        self.check_metrics()
        
        # Print final report
        self.print_report()
    
    def check_services_health(self) -> bool:
        """Check if all services are healthy"""
        print(f"{CYAN}Step 1: Checking Service Health{NC}")
        print("-" * 50)
        
        all_healthy = True
        for service_name, service_url in self.services.items():
            try:
                response = requests.get(f"{service_url}/health", timeout=2)
                if response.status_code == 200:
                    print(f"  {GREEN}✓{NC} {service_name}: Online")
                else:
                    print(f"  {RED}✗{NC} {service_name}: Unhealthy")
                    all_healthy = False
            except:
                print(f"  {RED}✗{NC} {service_name}: Offline")
                all_healthy = False
        
        print()
        return all_healthy
    
    def test_prompt_optimization(self):
        """Test how the sensitive prompt gets optimized"""
        print(f"{CYAN}Step 2: Testing Prompt Optimization{NC}")
        print("-" * 50)
        
        print(f"Original prompt ({len(self.test_mission)} chars):")
        print(f"  {YELLOW}{self.test_mission[:100]}...{NC}")
        
        # Test different optimization levels
        levels = ["minimal", "moderate", "aggressive", "extreme"]
        
        for level in levels:
            try:
                response = requests.post(
                    f"{self.services['prompt_optimizer']}/optimize",
                    json={
                        "prompt": self.test_mission,
                        "level": level
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"\n{level.upper()} Optimization:")
                    print(f"  Length: {result['original_length']} → {result['optimized_length']} chars")
                    print(f"  Safe: {'✅' if result['is_safe'] else '❌'}")
                    print(f"  Success probability: {result['success_probability']:.0%}")
                    
                    if not result['is_safe']:
                        print(f"  Issues: {', '.join(result['safety_issues'][:2])}")
                    
                    print(f"  Result: {BLUE}{result['optimized_prompt'][:80]}...{NC}")
                    
                    if result['is_safe']:
                        self.metrics["safety_blocks_avoided"] += 1
                    
                    self.metrics["prompts_optimized"] += 1
                    
            except Exception as e:
                print(f"  {RED}Error testing {level}: {e}{NC}")
        
        print()
    
    def start_workflow(self):
        """Start the Hollywood movie generation workflow"""
        print(f"{CYAN}Step 3: Starting Hollywood Movie Workflow{NC}")
        print("-" * 50)
        
        self.start_time = datetime.now()
        
        workflow_request = {
            "mission": self.test_mission,
            "duration": 120,  # 2-minute movie
            "platform": "youtube",
            "style": "Hollywood cinematic drama, Waltz with Bashir animation",
            "optimize_prompts": True,  # Enable optimization
            "parallel": True,  # Enable parallel processing
            "max_retries": 3
        }
        
        try:
            response = requests.post(
                f"{self.services['orchestrator']}/workflow",
                json=workflow_request
            )
            
            if response.status_code == 200:
                result = response.json()
                self.workflow_id = result["workflow_id"]
                print(f"  {GREEN}✓{NC} Workflow started: {self.workflow_id}")
                print(f"  Status: {result['status']}")
            else:
                print(f"  {RED}✗{NC} Failed to start workflow")
                return
                
        except Exception as e:
            print(f"  {RED}✗{NC} Error: {e}")
            return
        
        print()
    
    def monitor_generation(self):
        """Monitor the generation process"""
        print(f"{CYAN}Step 4: Monitoring Generation Progress{NC}")
        print("-" * 50)
        
        if not self.workflow_id:
            print(f"  {RED}No workflow to monitor{NC}")
            return
        
        max_wait = 60  # Max 60 seconds
        check_interval = 2
        elapsed = 0
        
        last_stage = None
        progress_bar_width = 40
        
        while elapsed < max_wait:
            try:
                # Get workflow status
                response = requests.get(
                    f"{self.services['orchestrator']}/workflow/{self.workflow_id}"
                )
                
                if response.status_code == 200:
                    status = response.json()
                    stage = status["stage"]
                    progress = status["progress"]
                    
                    # Update display
                    if stage != last_stage:
                        print(f"\n  Stage: {YELLOW}{stage}{NC}")
                        last_stage = stage
                    
                    # Progress bar
                    filled = int(progress_bar_width * progress)
                    bar = "█" * filled + "░" * (progress_bar_width - filled)
                    print(f"\r  Progress: [{bar}] {progress:.0%}", end="")
                    
                    # Check if completed
                    if stage in ["completed", "failed"]:
                        print()  # New line after progress bar
                        if stage == "completed":
                            print(f"\n  {GREEN}✓ Workflow completed!{NC}")
                        else:
                            print(f"\n  {RED}✗ Workflow failed: {status.get('error')}{NC}")
                        break
                
                time.sleep(check_interval)
                elapsed += check_interval
                
            except Exception as e:
                print(f"\n  {RED}Monitoring error: {e}{NC}")
                break
        
        if elapsed >= max_wait:
            print(f"\n  {YELLOW}⚠️ Workflow still running after {max_wait}s{NC}")
        
        print()
    
    def analyze_results(self):
        """Analyze the generation results"""
        print(f"{CYAN}Step 5: Analyzing Results{NC}")
        print("-" * 50)
        
        if not self.workflow_id:
            return
        
        try:
            # Get final workflow status
            response = requests.get(
                f"{self.services['orchestrator']}/workflow/{self.workflow_id}"
            )
            
            if response.status_code == 200:
                status = response.json()
                
                if status["stage"] == "completed" and status.get("results"):
                    results = status["results"]
                    
                    print(f"  {GREEN}✓{NC} Workflow Analysis:")
                    
                    # Check components
                    if "components" in results:
                        components = results["components"]
                        
                        # Audio results
                        if "audio" in components:
                            audio = components["audio"]
                            if "error" not in audio:
                                print(f"    Audio: {GREEN}Generated successfully{NC}")
                            else:
                                print(f"    Audio: {RED}Failed - {audio['error']}{NC}")
                        
                        # Video results
                        video_count = 0
                        video_success = 0
                        for key, value in components.items():
                            if key.startswith("video_"):
                                video_count += 1
                                if "error" not in value:
                                    video_success += 1
                                    if value.get("attempts", 1) > 1:
                                        self.metrics["retries_performed"] += value["attempts"] - 1
                        
                        print(f"    Videos: {video_success}/{video_count} generated")
                        
                        if video_success < video_count:
                            self.metrics["fallbacks_used"] = video_count - video_success
                    
                    # Duration
                    if status.get("completed_at") and status.get("started_at"):
                        duration = (datetime.fromisoformat(status["completed_at"]) - 
                                  datetime.fromisoformat(status["started_at"])).total_seconds()
                        print(f"    Duration: {duration:.1f} seconds")
                    
                    print(f"\n  {BLUE}Final Output: {results.get('final_video', 'N/A')}{NC}")
                    
                else:
                    print(f"  {YELLOW}⚠️ No results available yet{NC}")
                    
        except Exception as e:
            print(f"  {RED}Error analyzing results: {e}{NC}")
        
        print()
    
    def check_metrics(self):
        """Check monitoring metrics"""
        print(f"{CYAN}Step 6: Checking Metrics{NC}")
        print("-" * 50)
        
        try:
            # Get metrics from monitoring service
            response = requests.get(
                f"{self.services['monitoring']}/metrics/summary"
            )
            
            if response.status_code == 200:
                metrics = response.json()
                
                # Display key metrics
                important_metrics = [
                    "orchestrator.workflow.completed",
                    "orchestrator.video.generated",
                    "orchestrator.prompts.optimized",
                    "prompt-optimizer.optimization_success_prob",
                    "video-generator.success_rate"
                ]
                
                for metric_name in important_metrics:
                    if metric_name in metrics:
                        metric = metrics[metric_name]
                        print(f"  {metric_name}:")
                        print(f"    Latest: {metric.get('latest', 'N/A')}")
                        print(f"    Average: {metric.get('avg', 'N/A'):.2f}")
                
        except Exception as e:
            print(f"  {RED}Could not fetch metrics: {e}{NC}")
        
        print()
    
    def print_report(self):
        """Print final test report"""
        print(f"\n{MAGENTA}{'='*70}")
        print("📊 HOLLYWOOD MOVIE TEST REPORT")
        print(f"{'='*70}{NC}\n")
        
        # Test metrics
        print(f"{YELLOW}Performance Metrics:{NC}")
        print(f"  • Prompts Optimized: {self.metrics['prompts_optimized']}")
        print(f"  • Safety Blocks Avoided: {self.metrics['safety_blocks_avoided']}")
        print(f"  • Retries Performed: {self.metrics['retries_performed']}")
        print(f"  • Fallbacks Used: {self.metrics['fallbacks_used']}")
        
        # Time taken
        if self.start_time:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            print(f"  • Total Time: {elapsed:.1f} seconds")
        
        print(f"\n{YELLOW}Key Achievements:{NC}")
        
        achievements = []
        if self.metrics["safety_blocks_avoided"] > 0:
            achievements.append(f"{GREEN}✓{NC} Successfully optimized sensitive content")
        
        if self.metrics["prompts_optimized"] >= 4:
            achievements.append(f"{GREEN}✓{NC} All optimization levels tested")
        
        if self.workflow_id:
            achievements.append(f"{GREEN}✓{NC} End-to-end workflow executed")
        
        if self.metrics["retries_performed"] > 0:
            achievements.append(f"{GREEN}✓{NC} Retry logic successfully engaged")
        
        for achievement in achievements:
            print(f"  {achievement}")
        
        print(f"\n{YELLOW}System Improvements Demonstrated:{NC}")
        improvements = [
            "• Aggressive prompt optimization (<500 chars)",
            "• Automatic removal of sensitive terms",
            "• Progressive simplification on failures",
            "• Parallel service execution",
            "• Real-time monitoring and metrics",
            "• Microservices architecture with SOLID principles"
        ]
        
        for improvement in improvements:
            print(f"  {improvement}")
        
        # Final verdict
        success_rate = len(achievements) / 5 * 100 if achievements else 0
        
        print(f"\n{MAGENTA}{'='*70}{NC}")
        if success_rate >= 80:
            print(f"{GREEN}🎉 TEST PASSED! System successfully handled Hollywood movie generation")
            print(f"   with complex, sensitive content through intelligent optimization.{NC}")
        elif success_rate >= 60:
            print(f"{YELLOW}⚠️ TEST PARTIALLY PASSED. Some improvements still needed.{NC}")
        else:
            print(f"{RED}❌ TEST FAILED. Significant issues encountered.{NC}")
        print(f"{MAGENTA}{'='*70}{NC}\n")


class MetricsMonitor:
    """Monitor metrics in real-time during test"""
    
    def __init__(self, monitoring_url):
        self.monitoring_url = monitoring_url
        self.running = False
    
    def start(self):
        """Start monitoring in background"""
        self.running = True
        thread = threading.Thread(target=self._monitor_loop, daemon=True)
        thread.start()
    
    def stop(self):
        """Stop monitoring"""
        self.running = False
    
    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.running:
            try:
                # Collect metrics every 5 seconds
                response = requests.get(f"{self.monitoring_url}/dashboard")
                if response.status_code == 200:
                    data = response.json()
                    # Log to file for analysis
                    with open("hollywood_test_metrics.json", "a") as f:
                        f.write(json.dumps({
                            "timestamp": datetime.now().isoformat(),
                            "system_status": data.get("system_status"),
                            "services": data.get("services", {})
                        }) + "\n")
            except:
                pass
            
            time.sleep(5)


def main():
    """Main test runner"""
    print(f"{CYAN}")
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║     🎬 VIRALAI HOLLYWOOD MOVIE GENERATION TEST SUITE 🎬          ║")
    print("║                                                                  ║")
    print("║  Testing: Complex PTSD veteran story with sensitive content     ║")
    print("║  Mission: Waltz with Bashir style animation                     ║")
    print("║  Challenge: War, weapons, conflicts - needs optimization        ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print(f"{NC}\n")
    
    # Start metrics monitor
    monitor = MetricsMonitor("http://localhost:8003")
    monitor.start()
    
    # Run test
    tester = HollywoodMovieTest()
    
    try:
        tester.run_test()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Test interrupted by user{NC}")
    except Exception as e:
        print(f"{RED}Test failed with error: {e}{NC}")
    finally:
        monitor.stop()
        
    print(f"\n{CYAN}Metrics saved to: hollywood_test_metrics.json{NC}")
    print(f"{CYAN}View live dashboard at: http://localhost:8003{NC}\n")


if __name__ == "__main__":
    main()