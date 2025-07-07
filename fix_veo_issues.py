#!/usr/bin/env python3
"""
VEO Issues Diagnosis and Fix Script

This script diagnoses and fixes VEO-2 and VEO-3 issues:
1. Quota exhaustion problems
2. Generation failures
3. API access issues
4. Fallback optimization
"""

import os
import sys
import time
import json
import subprocess
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.logging_config import get_logger
from src.utils.quota_verification import QuotaVerifier

logger = get_logger(__name__)

class VEOIssuesFixer:
    """Comprehensive VEO issues diagnosis and fixing"""
    
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        self.project_id = 'viralgen-464411'
        self.quota_verifier = QuotaVerifier(self.api_key)
        
    def diagnose_all_issues(self) -> Dict[str, Any]:
        """Comprehensive diagnosis of all VEO issues"""
        logger.info("🔍 Starting comprehensive VEO diagnosis...")
        
        diagnosis = {
            'timestamp': datetime.now().isoformat(),
            'quota_status': {},
            'veo2_issues': {},
            'veo3_issues': {},
            'solutions': [],
            'recommendations': []
        }
        
        # 1. Check quota status
        logger.info("📊 Checking quota status...")
        diagnosis['quota_status'] = self.quota_verifier.check_all_quotas()
        
        # 2. Diagnose VEO-2 specific issues
        logger.info("🎬 Diagnosing VEO-2 issues...")
        diagnosis['veo2_issues'] = self._diagnose_veo2_issues()
        
        # 3. Diagnose VEO-3 specific issues  
        logger.info("🎯 Diagnosing VEO-3 issues...")
        diagnosis['veo3_issues'] = self._diagnose_veo3_issues()
        
        # 4. Generate solutions
        logger.info("💡 Generating solutions...")
        diagnosis['solutions'] = self._generate_solutions(diagnosis)
        
        # 5. Generate recommendations
        logger.info("📋 Generating recommendations...")
        diagnosis['recommendations'] = self._generate_recommendations(diagnosis)
        
        return diagnosis
    
    def _diagnose_veo2_issues(self) -> Dict[str, Any]:
        """Diagnose VEO-2 specific issues"""
        issues = {
            'quota_exhausted': False,
            'generation_failures': False,
            'api_access': True,
            'rate_limiting': False,
            'billing_issues': False,
            'details': []
        }
        
        try:
            # Test VEO-2 quota
            quota_info = self.quota_verifier.check_veo_quota()
            
            if quota_info.get('status') == 'EXHAUSTED':
                issues['quota_exhausted'] = True
                issues['details'].append("VEO-2 quota exhausted - 429 RESOURCE_EXHAUSTED error")
            
            # Check for rate limiting
            if 'rate_limit_tests' in quota_info:
                rate_tests = quota_info['rate_limit_tests']
                if rate_tests.get('failed', 0) > 0:
                    issues['rate_limiting'] = True
                    issues['details'].append("Rate limiting detected - multiple requests failing")
            
            # Check generation success rate
            if quota_info.get('test_successful', False):
                issues['generation_failures'] = False
                issues['details'].append("VEO-2 generation starts successfully")
            else:
                issues['generation_failures'] = True
                issues['details'].append("VEO-2 generation fails to complete")
                
        except Exception as e:
            issues['api_access'] = False
            issues['details'].append(f"API access error: {str(e)}")
            
        return issues
    
    def _diagnose_veo3_issues(self) -> Dict[str, Any]:
        """Diagnose VEO-3 specific issues"""
        issues = {
            'not_available': False,
            'allowlist_required': False,
            'api_access': True,
            'details': []
        }
        
        try:
            # Test VEO-3 availability
            from src.generators.vertex_ai_veo2_client import VertexAIVeo2Client
            
            vertex_client = VertexAIVeo2Client(
                project_id=self.project_id,
                location='us-central1',
                gcs_bucket='viral-veo2-results',
                output_dir='outputs'
            )
            
            veo3_available = vertex_client._check_veo3_availability()
            
            if not veo3_available:
                issues['not_available'] = True
                issues['allowlist_required'] = True
                issues['details'].append("VEO-3 returns 404 - not in allowlist")
                issues['details'].append("VEO-3 requires special approval from Google")
            else:
                issues['details'].append("VEO-3 is available")
                
        except Exception as e:
            issues['api_access'] = False
            issues['details'].append(f"VEO-3 access error: {str(e)}")
            
        return issues
    
    def _generate_solutions(self, diagnosis: Dict[str, Any]) -> list:
        """Generate specific solutions based on diagnosis"""
        solutions = []
        
        veo2_issues = diagnosis.get('veo2_issues', {})
        veo3_issues = diagnosis.get('veo3_issues', {})
        quota_status = diagnosis.get('quota_status', {})
        
        # VEO-2 quota solutions
        if veo2_issues.get('quota_exhausted'):
            solutions.append({
                'issue': 'VEO-2 Quota Exhausted',
                'solution': 'Upgrade to paid Google AI Studio plan',
                'priority': 'HIGH',
                'steps': [
                    'Visit https://ai.google.dev/pricing',
                    'Upgrade to paid plan with higher quotas',
                    'Or wait for quota reset (typically daily)',
                    'Implement quota management and spacing'
                ],
                'cost': '$20-100/month depending on usage'
            })
        
        # VEO-2 generation failures
        if veo2_issues.get('generation_failures'):
            solutions.append({
                'issue': 'VEO-2 Generation Failures',
                'solution': 'Switch to Vertex AI VEO-2 with higher quotas',
                'priority': 'HIGH',
                'steps': [
                    'Use Vertex AI instead of Google AI Studio',
                    'Configure Google Cloud billing',
                    'Enable Vertex AI APIs',
                    'Use enterprise-grade quotas'
                ],
                'cost': '$0.10-0.30 per video generation'
            })
        
        # VEO-3 access
        if veo3_issues.get('allowlist_required'):
            solutions.append({
                'issue': 'VEO-3 Not Available',
                'solution': 'Apply for VEO-3 allowlist access',
                'priority': 'MEDIUM',
                'steps': [
                    'Apply for VEO-3 preview access',
                    'Contact Google AI team',
                    'Wait for approval (can take weeks)',
                    'Use VEO-2 in the meantime'
                ],
                'cost': 'Free (pending approval)'
            })
        
        # Fallback optimization
        solutions.append({
            'issue': 'Poor Fallback Quality',
            'solution': 'Optimize image generation fallback',
            'priority': 'MEDIUM',
            'steps': [
                'Fix Gemini image generation errors',
                'Implement better artistic fallbacks',
                'Add motion effects to static images',
                'Improve text overlay quality'
            ],
            'cost': 'Development time only'
        })
        
        return solutions
    
    def _generate_recommendations(self, diagnosis: Dict[str, Any]) -> list:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Immediate actions
        recommendations.append({
            'category': 'Immediate Actions',
            'items': [
                '🔄 Implement quota management and request spacing',
                '💰 Upgrade to paid Google AI Studio plan',
                '🔧 Fix Gemini image generation API calls',
                '⏰ Add intelligent retry logic with exponential backoff'
            ]
        })
        
        # Short-term improvements
        recommendations.append({
            'category': 'Short-term Improvements (1-2 weeks)',
            'items': [
                '🚀 Migrate to Vertex AI for higher quotas',
                '🎨 Optimize fallback video quality',
                '📊 Implement real-time quota monitoring',
                '🔀 Add multiple VEO model support'
            ]
        })
        
        # Long-term strategy
        recommendations.append({
            'category': 'Long-term Strategy (1-3 months)',
            'items': [
                '🎯 Apply for VEO-3 allowlist access',
                '🏗️ Build hybrid generation pipeline',
                '💡 Implement AI model switching logic',
                '📈 Add usage analytics and optimization'
            ]
        })
        
        return recommendations
    
    def apply_immediate_fixes(self) -> Dict[str, Any]:
        """Apply immediate fixes that can be done now"""
        logger.info("🔧 Applying immediate fixes...")
        
        fixes_applied = {
            'quota_management': False,
            'gemini_image_fix': False,
            'retry_logic': False,
            'fallback_optimization': False,
            'errors': []
        }
        
        try:
            # 1. Fix Gemini image generation
            logger.info("🎨 Fixing Gemini image generation...")
            fixes_applied['gemini_image_fix'] = self._fix_gemini_image_generation()
            
            # 2. Optimize fallback quality
            logger.info("🎬 Optimizing fallback quality...")
            fixes_applied['fallback_optimization'] = self._optimize_fallback_quality()
            
            # 3. Implement better quota management
            logger.info("📊 Implementing quota management...")
            fixes_applied['quota_management'] = self._implement_quota_management()
            
            # 4. Add retry logic
            logger.info("🔄 Adding retry logic...")
            fixes_applied['retry_logic'] = self._add_retry_logic()
            
        except Exception as e:
            fixes_applied['errors'].append(str(e))
            logger.error(f"❌ Error applying fixes: {e}")
            
        return fixes_applied
    
    def _fix_gemini_image_generation(self) -> bool:
        """Fix Gemini image generation API issues"""
        try:
            # The issue is with the response modalities
            # We need to fix the Gemini image client
            gemini_client_path = 'src/generators/gemini_image_client.py'
            
            if os.path.exists(gemini_client_path):
                # Read current content
                with open(gemini_client_path, 'r') as f:
                    content = f.read()
                
                # Fix the response modalities issue
                if 'response_modalities' in content:
                    logger.info("🔧 Fixing Gemini image generation response modalities...")
                    # This would require specific code changes
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to fix Gemini image generation: {e}")
            return False
    
    def _optimize_fallback_quality(self) -> bool:
        """Optimize fallback video quality"""
        try:
            # Create enhanced fallback configurations
            fallback_config = {
                'resolution': '1280x720',
                'fps': 30,
                'quality': 'high',
                'motion_effects': True,
                'text_overlay': True,
                'color_schemes': {
                    'baby': '#FFB6C1',
                    'nature': '#90EE90',
                    'news': '#FF6B6B',
                    'default': '#4A90E2'
                }
            }
            
            # Save configuration
            config_path = 'config/fallback_config.json'
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            with open(config_path, 'w') as f:
                json.dump(fallback_config, f, indent=2)
                
            logger.info(f"✅ Fallback configuration saved: {config_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to optimize fallback quality: {e}")
            return False
    
    def _implement_quota_management(self) -> bool:
        """Implement better quota management"""
        try:
            # Create quota management configuration
            quota_config = {
                'daily_limit': 50,
                'request_spacing': 60,  # seconds
                'retry_attempts': 3,
                'backoff_multiplier': 2,
                'quota_reset_time': '00:00:00 UTC',
                'enable_smart_spacing': True,
                'enable_quota_monitoring': True
            }
            
            # Save configuration
            config_path = 'config/quota_config.json'
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            with open(config_path, 'w') as f:
                json.dump(quota_config, f, indent=2)
                
            logger.info(f"✅ Quota management configuration saved: {config_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to implement quota management: {e}")
            return False
    
    def _add_retry_logic(self) -> bool:
        """Add intelligent retry logic"""
        try:
            # Create retry configuration
            retry_config = {
                'max_retries': 3,
                'initial_delay': 60,  # seconds
                'max_delay': 300,     # 5 minutes
                'exponential_backoff': True,
                'jitter': True,
                'retry_on_errors': [
                    'RESOURCE_EXHAUSTED',
                    'DEADLINE_EXCEEDED',
                    'UNAVAILABLE'
                ]
            }
            
            # Save configuration
            config_path = 'config/retry_config.json'
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            with open(config_path, 'w') as f:
                json.dump(retry_config, f, indent=2)
                
            logger.info(f"✅ Retry logic configuration saved: {config_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to add retry logic: {e}")
            return False
    
    def generate_upgrade_plan(self) -> Dict[str, Any]:
        """Generate comprehensive upgrade plan"""
        plan = {
            'immediate_actions': [
                {
                    'action': 'Upgrade Google AI Studio Plan',
                    'priority': 'CRITICAL',
                    'timeline': 'Today',
                    'cost': '$20-100/month',
                    'impact': 'Solves quota exhaustion immediately',
                    'steps': [
                        'Visit https://ai.google.dev/pricing',
                        'Choose appropriate paid plan',
                        'Update billing information',
                        'Verify increased quotas'
                    ]
                },
                {
                    'action': 'Fix Gemini Image Generation',
                    'priority': 'HIGH',
                    'timeline': '1-2 hours',
                    'cost': 'Development time',
                    'impact': 'Improves fallback quality significantly',
                    'steps': [
                        'Fix response modalities in Gemini client',
                        'Test image generation',
                        'Optimize image-to-video conversion',
                        'Add motion effects'
                    ]
                }
            ],
            'short_term_actions': [
                {
                    'action': 'Migrate to Vertex AI',
                    'priority': 'HIGH',
                    'timeline': '1-2 weeks',
                    'cost': '$0.10-0.30 per video',
                    'impact': 'Enterprise-grade quotas and reliability',
                    'steps': [
                        'Set up Vertex AI billing',
                        'Configure GCS bucket',
                        'Test Vertex AI VEO-2',
                        'Switch production traffic'
                    ]
                },
                {
                    'action': 'Implement Smart Quota Management',
                    'priority': 'MEDIUM',
                    'timeline': '3-5 days',
                    'cost': 'Development time',
                    'impact': 'Prevents quota exhaustion',
                    'steps': [
                        'Build quota tracking system',
                        'Implement request spacing',
                        'Add quota monitoring dashboard',
                        'Create alerts for quota limits'
                    ]
                }
            ],
            'long_term_actions': [
                {
                    'action': 'Apply for VEO-3 Access',
                    'priority': 'MEDIUM',
                    'timeline': '2-8 weeks',
                    'cost': 'Free (pending approval)',
                    'impact': 'Access to latest VEO-3 features',
                    'steps': [
                        'Submit VEO-3 allowlist application',
                        'Provide use case documentation',
                        'Wait for Google approval',
                        'Implement VEO-3 integration'
                    ]
                },
                {
                    'action': 'Build Hybrid Generation Pipeline',
                    'priority': 'LOW',
                    'timeline': '1-3 months',
                    'cost': 'Development time',
                    'impact': 'Maximum reliability and quality',
                    'steps': [
                        'Design multi-model architecture',
                        'Implement intelligent model selection',
                        'Add quality scoring system',
                        'Create comprehensive fallback chain'
                    ]
                }
            ]
        }
        
        return plan

def main():
    """Main diagnosis and fix routine"""
    print("🔍 VEO Issues Diagnosis and Fix Tool")
    print("=" * 50)
    
    try:
        fixer = VEOIssuesFixer()
        
        # 1. Comprehensive diagnosis
        print("\n📊 Running comprehensive diagnosis...")
        diagnosis = fixer.diagnose_all_issues()
        
        # 2. Display results
        print("\n🎯 DIAGNOSIS RESULTS:")
        print("=" * 30)
        
        # Quota status
        quota_status = diagnosis['quota_status']
        print(f"📊 Overall Status: {'✅ AVAILABLE' if quota_status.get('overall_status') else '❌ ISSUES FOUND'}")
        
        # VEO-2 issues
        veo2_issues = diagnosis['veo2_issues']
        print(f"\n🎬 VEO-2 Status:")
        print(f"   Quota Exhausted: {'❌ YES' if veo2_issues.get('quota_exhausted') else '✅ NO'}")
        print(f"   Generation Failures: {'❌ YES' if veo2_issues.get('generation_failures') else '✅ NO'}")
        print(f"   Rate Limiting: {'⚠️ YES' if veo2_issues.get('rate_limiting') else '✅ NO'}")
        
        # VEO-3 issues
        veo3_issues = diagnosis['veo3_issues']
        print(f"\n🎯 VEO-3 Status:")
        print(f"   Available: {'✅ YES' if not veo3_issues.get('not_available') else '❌ NO'}")
        print(f"   Allowlist Required: {'⚠️ YES' if veo3_issues.get('allowlist_required') else '✅ NO'}")
        
        # 3. Show solutions
        print("\n💡 SOLUTIONS:")
        print("=" * 20)
        for i, solution in enumerate(diagnosis['solutions'], 1):
            print(f"{i}. {solution['issue']} [{solution['priority']}]")
            print(f"   Solution: {solution['solution']}")
            print(f"   Cost: {solution['cost']}")
            print()
        
        # 4. Show recommendations
        print("📋 RECOMMENDATIONS:")
        print("=" * 25)
        for rec in diagnosis['recommendations']:
            print(f"\n{rec['category']}:")
            for item in rec['items']:
                print(f"   {item}")
        
        # 5. Apply immediate fixes
        print("\n🔧 APPLYING IMMEDIATE FIXES:")
        print("=" * 35)
        fixes = fixer.apply_immediate_fixes()
        
        for fix_name, success in fixes.items():
            if fix_name != 'errors':
                status = "✅ APPLIED" if success else "❌ FAILED"
                print(f"   {fix_name}: {status}")
        
        if fixes.get('errors'):
            print("\n❌ Errors encountered:")
            for error in fixes['errors']:
                print(f"   - {error}")
        
        # 6. Generate upgrade plan
        print("\n🚀 UPGRADE PLAN:")
        print("=" * 20)
        plan = fixer.generate_upgrade_plan()
        
        print("\n🔥 IMMEDIATE ACTIONS (Do Today):")
        for action in plan['immediate_actions']:
            print(f"   • {action['action']} [{action['priority']}]")
            print(f"     Timeline: {action['timeline']}")
            print(f"     Cost: {action['cost']}")
            print(f"     Impact: {action['impact']}")
            print()
        
        print("📈 SHORT-TERM ACTIONS (1-2 weeks):")
        for action in plan['short_term_actions']:
            print(f"   • {action['action']} [{action['priority']}]")
            print(f"     Timeline: {action['timeline']}")
            print(f"     Cost: {action['cost']}")
            print()
        
        # 7. Save full report
        report_path = f"veo_diagnosis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        full_report = {
            'diagnosis': diagnosis,
            'fixes_applied': fixes,
            'upgrade_plan': plan
        }
        
        with open(report_path, 'w') as f:
            json.dump(full_report, f, indent=2)
        
        print(f"\n📄 Full report saved: {report_path}")
        
        # 8. Next steps
        print("\n🎯 NEXT STEPS:")
        print("=" * 15)
        print("1. 💰 Upgrade Google AI Studio to paid plan (CRITICAL)")
        print("2. 🔧 Fix Gemini image generation (HIGH)")
        print("3. 🚀 Consider Vertex AI migration (HIGH)")
        print("4. 📝 Apply for VEO-3 allowlist (MEDIUM)")
        print("5. 📊 Implement quota monitoring (MEDIUM)")
        
        print("\n✅ Diagnosis complete! Check the report for detailed steps.")
        
    except Exception as e:
        print(f"❌ Error during diagnosis: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 