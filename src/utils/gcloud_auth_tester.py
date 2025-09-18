#!/usr/bin/env python3
"""
Comprehensive Google Cloud Authentication Tester
Tests all authentication methods and services required by the app
"""

import os
import subprocess
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import requests

from .logging_config import get_logger

logger = get_logger(__name__)

class GCloudAuthTester:
    """Comprehensive Google Cloud authentication tester"""

    def __init__(self):
        """Initialize the authentication tester"""
        self.test_results = {}
        self.critical_failures = []
        self.warnings = []

    def run_comprehensive_auth_test(self) -> Dict[str, Any]:
        """
        Run comprehensive authentication tests for all Google Cloud services

        Returns:
            Dictionary with complete test results
        """
        logger.info("🔐 Starting comprehensive Google Cloud authentication test...")

        # Test 1: gcloud CLI Authentication
        gcloud_result = self._test_gcloud_auth()
        self.test_results['gcloud_auth'] = gcloud_result

        # Test 2: Application Default Credentials (ADC)
        adc_result = self._test_application_default_credentials()
        self.test_results['adc'] = adc_result

        # Test 3: Service Account Authentication
        service_account_result = self._test_service_account_auth()
        self.test_results['service_account'] = service_account_result

        # Test 4: Google AI Studio API Access
        ai_studio_result = self._test_google_ai_studio_access()
        self.test_results['ai_studio'] = ai_studio_result

        # Test 5: Vertex AI API Access
        vertex_ai_result = self._test_vertex_ai_access()
        self.test_results['vertex_ai'] = vertex_ai_result

        # Test 6: Cloud Text-to-Speech API
        tts_result = self._test_cloud_tts_access()
        self.test_results['cloud_tts'] = tts_result

        # Test 7: Cloud Storage Access
        storage_result = self._test_cloud_storage_access()
        self.test_results['cloud_storage'] = storage_result

        # Test 8: Project and Billing Verification
        project_result = self._test_project_and_billing()
        self.test_results['project_billing'] = project_result

        # Analyze results and provide recommendations
        analysis = self._analyze_auth_results()
        self.test_results['analysis'] = analysis

        return self.test_results

    def _test_gcloud_auth(self) -> Dict[str, Any]:
        """Test gcloud CLI authentication"""
        logger.info("🔍 Testing gcloud CLI authentication...")

        try:
            # Check if gcloud is installed
            result = subprocess.run(
                ['gcloud', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return {
                    'status': 'FAILED',
                    'error': 'gcloud CLI not installed',
                    'recommendation': 'Install Google Cloud SDK: https://cloud.google.com/sdk/docs/install'
                }

            # Check authentication status
            auth_result = subprocess.run(
                ['gcloud', 'auth', 'list', '--format=json'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if auth_result.returncode != 0:
                return {
                    'status': 'FAILED',
                    'error': 'gcloud auth failed',
                    'recommendation': 'Run: gcloud auth login'
                }

            # Parse authentication info
            auth_data = json.loads(auth_result.stdout)
            active_accounts = [acc for acc in auth_data if acc.get('status') == 'ACTIVE']

            if not active_accounts:
                return {
                    'status': 'FAILED',
                    'error': 'No active gcloud accounts',
                    'recommendation': 'Run: gcloud auth login'
                }

            # Test access token generation
            token_result = subprocess.run(
                ['gcloud', 'auth', 'print-access-token'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if token_result.returncode != 0:
                return {
                    'status': 'FAILED',
                    'error': 'Cannot generate access token',
                    'recommendation': 'Run: gcloud auth login'
                }

            # Get current project
            project_result = subprocess.run(
                ['gcloud', 'config', 'get-value', 'project'],
                capture_output=True,
                text=True,
                timeout=5
            )

            project_id = project_result.stdout.strip() if project_result.returncode == 0 else "Not set"

            return {
                'status': 'SUCCESS',
                'active_account': active_accounts[0]['account'],
                'project_id': project_id,
                'access_token_available': True,
                'gcloud_version': result.stdout.split('\n')[0]
            }

        except subprocess.TimeoutExpired:
            return {
                'status': 'TIMEOUT',
                'error': 'gcloud command timed out',
                'recommendation': 'Check gcloud installation and network connection'
            }
        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e),
                'recommendation': 'Check gcloud installation and configuration'
            }

    def _test_application_default_credentials(self) -> Dict[str, Any]:
        """Test Application Default Credentials (ADC)"""
        logger.info("🔍 Testing Application Default Credentials...")

        try:
            import google.auth
            import google.auth.transport.requests

            # Try to get default credentials
            credentials, project = google.auth.default()

            if not credentials:
                return {
                    'status': 'FAILED',
                    'error': 'No default credentials found',
                    'recommendation': 'Run: gcloud auth application-default login'
                }

            # Test token refresh
            request = google.auth.transport.requests.Request()
            credentials.refresh(request)

            return {
                'status': 'SUCCESS',
                'project_id': project,
                'credentials_type': type(credentials).__name__,
                'token_available': bool(credentials.token)
            }

        except Exception as e:
            return {
                'status': 'FAILED',
                'error': str(e),
                'recommendation': 'Run: gcloud auth application-default login'
            }

    def _test_service_account_auth(self) -> Dict[str, Any]:
        """Test service account authentication"""
        logger.info("🔍 Testing service account authentication...")

        service_account_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

        if not service_account_path:
            return {
                'status': 'SKIPPED',
                'message': 'No service account credentials configured',
                'recommendation': 'Set GOOGLE_APPLICATION_CREDENTIALS if needed'
            }

        try:
            if not os.path.exists(service_account_path):
                return {
                    'status': 'FAILED',
                    'error': f'Service account file not found: {service_account_path}',
                    'recommendation': 'Check GOOGLE_APPLICATION_CREDENTIALS path'
                }

            # Try to load and validate service account
            with open(service_account_path, 'r') as f:
                service_account_data = json.load(f)

            required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
            missing_fields = [field for field in required_fields if field not in service_account_data]

            if missing_fields:
                return {
                    'status': 'FAILED',
                    'error': f'Missing required fields: {missing_fields}',
                    'recommendation': 'Check service account JSON file format'
                }

            # Test authentication with service account
            from google.oauth2  import service_account
            import google.auth.transport.requests

            credentials = service_account.Credentials.from_service_account_file(
                service_account_path,
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )

            request = google.auth.transport.requests.Request()
            credentials.refresh(request)

            return {
                'status': 'SUCCESS',
                'project_id': service_account_data['project_id'],
                'client_email': service_account_data['client_email'],
                'token_available': bool(credentials.token)
            }

        except Exception as e:
            return {
                'status': 'FAILED',
                'error': str(e),
                'recommendation': 'Check service account JSON file and permissions'
            }

    def _test_google_ai_studio_access(self) -> Dict[str, Any]:
        """Test Google AI Studio API access"""
        logger.info("🔍 Testing Google AI Studio API access...")

        api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')

        if not api_key:
            return {
                'status': 'FAILED',
                'error': 'No Google AI Studio API key found',
                'recommendation': 'Set GOOGLE_API_KEY or GEMINI_API_KEY environment variable'
            }

        try:
            # Test API key with a simple request
            url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                models_data = response.json()
                model_count = len(models_data.get('models', []))

                # Check for VEO models specifically
                veo_models = [m for m in models_data.get(
                    'models',
                    []) if 'veo' in m.get('name',
                    '').lower()]

                return {
                    'status': 'SUCCESS',
                    'total_models': model_count,
                    'veo_models_available': len(veo_models),
                    'veo_models': [m['name'] for m in veo_models]
                }
            elif response.status_code == 403:
                return {
                    'status': 'FAILED',
                    'error': 'API key invalid or insufficient permissions',
                    'recommendation': 'Check API key and enable required APIs'
                }
            else:
                return {
                    'status': 'FAILED',
                    'error': f'API request failed: {response.status_code}',
                    'recommendation': 'Check API key and network connection'
                }

        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e),
                'recommendation': 'Check API key and network connection'
            }

    def _test_vertex_ai_access(self) -> Dict[str, Any]:
        """Test Vertex AI API access"""
        logger.info("🔍 Testing Vertex AI API access...")

        # Get current project from gcloud
        try:
            project_result = subprocess.run(
                ['gcloud', 'config', 'get-value', 'project'],
                capture_output=True,
                text=True,
                timeout=5
            )
            current_project = project_result.stdout.strip() if project_result.returncode == 0 else None
        except Exception:
            current_project = None

        # Try multiple environment variable names for project ID, with current project as priority
        project_id = (
            current_project or
            os.getenv('VERTEX_AI_PROJECT_ID') or
            os.getenv('GOOGLE_CLOUD_PROJECT_ID') or
            os.getenv('GOOGLE_CLOUD_PROJECT') or
            os.getenv('VEO_PROJECT_ID') or
            "viralgen-464411"  # Fallback default
        )

        location = (
            os.getenv('VERTEX_AI_LOCATION') or
            os.getenv('GOOGLE_CLOUD_LOCATION') or
            os.getenv('VEO_LOCATION') or
            'us-central1'  # Default from config
        )

        logger.info(f"🔍 Using project ID: {project_id}")
        logger.info(f"🔍 Using location: {location}")

        try:
            # Get access token
            token_result = subprocess.run(
                ['gcloud', 'auth', 'print-access-token'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if token_result.returncode != 0:
                return {
                    'status': 'FAILED',
                    'error': 'Cannot get access token for Vertex AI',
                    'recommendation': 'Run: gcloud auth login',
                    'project_id': project_id,
                    'location': location
                }

            access_token = token_result.stdout.strip()

            # Test Vertex AI API access
            url = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models"

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            response = requests.get(url, headers=headers, timeout=15)

            if response.status_code == 200:
                # Check for VEO models
                try:
                    veo_url = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models/veo.0-generate-001"
                    veo_response = requests.get(veo_url, headers=headers, timeout=10)
                    veo_available = veo_response.status_code == 200
                except Exception:
                    veo_available = False

                return {
                    'status': 'SUCCESS',
                    'project_id': project_id,
                    'location': location,
                    'vertex_ai_accessible': True,
                    'veo_model_available': veo_available
                }
            elif response.status_code == 403:
                return {
                    'status': 'FAILED',
                    'error': 'Insufficient permissions for Vertex AI',
                    'recommendation': 'Enable Vertex AI API and check IAM permissions',
                    'project_id': project_id,
                    'location': location
                }
            else:
                return {
                    'status': 'FAILED',
                    'error': f'Vertex AI API request failed: {response.status_code}',
                    'recommendation': f'Check project {project_id}, location {location}, and API enablement',
                    'project_id': project_id,
                    'location': location
                }

        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e),
                'recommendation': 'Check Vertex AI configuration and authentication',
                'project_id': project_id,
                'location': location
            }

    def _test_cloud_tts_access(self) -> Dict[str, Any]:
        """Test Cloud Text-to-Speech API access"""
        logger.info("🔍 Testing Cloud Text-to-Speech API access...")

        try:
            from google.cloud  import texttospeech

            # Try to create client
            client = texttospeech.TextToSpeechClient()

            # Test API with a simple request
            voices = client.list_voices()

            voice_count = len(voices.voices)
            en_voices = [v for v in voices.voices if v.language_codes[0].startswith('en')]

            return {
                'status': 'SUCCESS',
                'total_voices': voice_count,
                'english_voices': len(en_voices),
                'api_accessible': True
            }

        except Exception as e:
            return {
                'status': 'FAILED',
                'error': str(e),
                'recommendation': 'Enable Cloud Text-to-Speech API and check authentication'
            }

    def _test_cloud_storage_access(self) -> Dict[str, Any]:
        """Test Cloud Storage access"""
        logger.info("🔍 Testing Cloud Storage access...")

        # Try multiple environment variable names for bucket
        bucket_name = (
            os.getenv('VERTEX_AI_GCS_BUCKET') or
            os.getenv('GCS_BUCKET') or
            os.getenv('GOOGLE_CLOUD_STORAGE_BUCKET') or
            "viral-veo-results"  # Default from config
        )

        logger.info(f"🔍 Using GCS bucket: {bucket_name}")

        try:
            from google.cloud  import storage

            # Try to create client
            client = storage.Client()

            # Test bucket access
            bucket = client.bucket(bucket_name)

            # Try to list objects (this tests read permission)
            _blobs = list(bucket.list_blobs(max_results=1))

            return {
                'status': 'SUCCESS',
                'bucket_name': bucket_name,
                'bucket_accessible': True,
                'can_list_objects': True
            }

        except Exception as e:
            return {
                'status': 'FAILED',
                'error': str(e),
                'recommendation': f'Check bucket {bucket_name} exists and permissions are correct',
                'bucket_name': bucket_name
            }

    def _test_project_and_billing(self) -> Dict[str, Any]:
        """Test project configuration and billing"""
        logger.info("🔍 Testing project and billing configuration...")

        try:
            # Get project info
            project_result = subprocess.run(
                ['gcloud', 'config', 'get-value', 'project'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if project_result.returncode != 0:
                return {
                    'status': 'FAILED',
                    'error': 'Cannot get current project',
                    'recommendation': 'Run: gcloud config set project YOUR_PROJECT_ID'
                }

            project_id = project_result.stdout.strip()

            if not project_id or project_id == '(unset)':
                return {
                    'status': 'FAILED',
                    'error': 'No project set',
                    'recommendation': 'Run: gcloud config set project YOUR_PROJECT_ID'
                }

            # Check billing (if possible)
            billing_result = subprocess.run(
                ['gcloud', 'billing', 'projects', 'describe', project_id, '--format=json'],
                capture_output=True,
                text=True,
                timeout=10
            )

            billing_enabled = False
            if billing_result.returncode == 0:
                try:
                    billing_data = json.loads(billing_result.stdout)
                    billing_enabled = billing_data.get('billingEnabled', False)
                except Exception:
                    pass

            return {
                'status': 'SUCCESS',
                'project_id': project_id,
                'billing_enabled': billing_enabled,
                'billing_check_available': billing_result.returncode == 0
            }

        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e),
                'recommendation': 'Check project configuration and billing setup'
            }

    def _analyze_auth_results(self) -> Dict[str, Any]:
        """Analyze authentication test results and provide recommendations"""

        # Count successes and failures
        successes = sum(1 for result in self.test_results.values()
                       if isinstance(result, dict) and result.get('status') == 'SUCCESS')
        failures = sum(1 for result in self.test_results.values()
                      if isinstance(result, dict) and result.get('status') == 'FAILED')

        # Determine overall status
        critical_services = ['gcloud_auth', 'ai_studio']
        critical_failures = [service for service in critical_services
                           if self.test_results.get(service, {}).get('status') == 'FAILED']

        if critical_failures:
            overall_status = 'CRITICAL_FAILURE'
            status_message = f"Critical services failed: {', '.join(critical_failures)}"
        elif failures > 0:
            overall_status = 'PARTIAL_SUCCESS'
            status_message = "Some services failed but app can still run with limitations"
        else:
            overall_status = 'SUCCESS'
            status_message = "All authentication tests passed"

        # Generate recommendations
        recommendations = []

        if self.test_results.get('gcloud_auth', {}).get('status') == 'FAILED':
            recommendations.append("🔑 Install Google Cloud SDK and run: gcloud auth login")

        if self.test_results.get('ai_studio', {}).get('status') == 'FAILED':
            recommendations.append("🔑 Get Google AI Studio API key and set GOOGLE_API_KEY")

        if self.test_results.get('vertex_ai', {}).get('status') == 'FAILED':
            recommendations.append("🔑 Enable Vertex AI API and"
                    "check project configuration")

        if self.test_results.get('adc', {}).get('status') == 'FAILED':
            recommendations.append("🔑 Run: gcloud auth application-default login")

        return {
            'overall_status': overall_status,
            'status_message': status_message,
            'total_tests': len(self.test_results) - 1,  # Exclude analysis itself
            'successes': successes,
            'failures': failures,
            'critical_failures': critical_failures,
            'recommendations': recommendations,
            'can_run_app': overall_status != 'CRITICAL_FAILURE'
        }

    def print_auth_report(self):
        """Print a comprehensive authentication report"""

        print("\n" + "="*80)
        print("🔐 GOOGLE CLOUD AUTHENTICATION TEST REPORT")
        print("="*80)

        analysis = self.test_results.get('analysis', {})

        # Overall status
        status_emoji = {
            'SUCCESS': '✅',
            'PARTIAL_SUCCESS': '⚠️',
            'CRITICAL_FAILURE': '❌'
        }

        overall_status = analysis.get('overall_status', 'UNKNOWN')
        emoji = status_emoji.get(overall_status, '❓')

        print(f"\n{emoji} Overall Status: {overall_status}")
        print(
            f"📊 Tests: {analysis.get('successes', 0)} passed,"
            f"{analysis.get('failures', 0)} failed")
        print(f"🚀 Can run app: {'YES' if analysis.get('can_run_app', False) else 'NO'}")

        # Individual test results
        print("\n📋 Individual Test Results:")
        print("-" * 40)

        test_names = {
            'gcloud_auth': 'gcloud CLI Authentication',
            'adc': 'Application Default Credentials',
            'service_account': 'Service Account Authentication',
            'ai_studio': 'Google AI Studio API',
            'vertex_ai': 'Vertex AI API',
            'cloud_tts': 'Cloud Text-to-Speech API',
            'cloud_storage': 'Cloud Storage Access',
            'project_billing': 'Project & Billing'
        }

        for test_key, test_name in test_names.items():
            if test_key in self.test_results:
                result = self.test_results[test_key]
                status = result.get('status', 'UNKNOWN')

                status_symbols = {
                    'SUCCESS': '✅',
                    'FAILED': '❌',
                    'SKIPPED': '⏭️',
                    'ERROR': '🔥',
                    'TIMEOUT': '⏰'
                }

                symbol = status_symbols.get(status, '❓')
                print(f"{symbol} {test_name}: {status}")

                if status in ['FAILED', 'ERROR'] and 'error' in result:
                    print(f"   Error: {result['error']}")
                if 'recommendation' in result:
                    print(f"   💡 {result['recommendation']}")

        # Recommendations
        recommendations = analysis.get('recommendations', [])
        if recommendations:
            print("\n🔧 RECOMMENDED ACTIONS:")
            print("-" * 40)
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec}")

        # Next steps
        print("\n🚀 NEXT STEPS:")
        print("-" * 40)

        if overall_status == 'SUCCESS':
            print("✅ All authentication tests passed!")
            print("🎬 You can now run the video generator:")
            print("   python main.py generate --mission 'your mission here'")
        elif overall_status == 'PARTIAL_SUCCESS':
            print("⚠️ Some services failed but you can still run the app with limitations")
            print("🎬 Try running the generator - it will use fallback methods")
        else:
            print("❌ Critical authentication failures detected")
            print("🔧 Please fix the issues above before running the app")

        print("\n" + "="*80)

def test_gcloud_authentication() -> Dict[str, Any]:
    """
    Main function to test Google Cloud authentication

    Returns:
        Dictionary with complete test results
    """
    tester = GCloudAuthTester()
    results = tester.run_comprehensive_auth_test()
    tester.print_auth_report()
    return results

if __name__ == "__main__":
    # Run authentication tests
    test_gcloud_authentication()
