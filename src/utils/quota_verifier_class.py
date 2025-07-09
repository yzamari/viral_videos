"""
QuotaVerifier Class - Simple quota checking interface
"""

from typing import Dict, Any, Tuple
from .logging_config import get_logger
from .quota_verification import (
    get_real_google_quota_info,
    get_real_google_quota_usage,
    get_veo_quota_info,
    get_google_cloud_quota_info
)

logger = get_logger(__name__)


class QuotaVerifier:
    """
    Quota verification class that provides a unified interface for checking
    Google AI quotas across different services.
    """

    def __init__(self, api_key: str):
        """
        Initialize quota verifier with API key

        Args:
            api_key: Google AI Studio API key
        """
        self.api_key = api_key
        self.logger = get_logger(__name__)

    def check_all_quotas(self) -> Dict[str, Any]:
        """
        Check all available quotas and return comprehensive status

        Returns:
            Dictionary with quota status for all services
        """
        results = {}

        # Check Google AI Studio quota
        self.logger.info("🔍 Checking Google AI Studio quota...")
        try:
            google_ai_quota = get_real_google_quota_info(self.api_key)
            results['google_ai_studio'] = google_ai_quota
        except Exception as e:
            results['google_ai_studio'] = {
                'status': 'ERROR',
                'message': f'Error checking Google AI Studio: {e}',
                'available': False
            }

        # Check Google AI usage quota
        self.logger.info("🔍 Checking Google AI usage quota...")
        try:
            usage_quota = get_real_google_quota_usage(self.api_key)
            results['google_ai_usage'] = usage_quota
        except Exception as e:
            results['google_ai_usage'] = {
                'status': 'ERROR',
                'message': f'Error checking usage quota: {e}',
                'can_generate': False
            }

        # Check VEO-specific quota
        self.logger.info("🔍 Checking VEO quota...")
        try:
            veo_quota = get_veo_quota_info(self.api_key)
            results['veo_quota'] = veo_quota
        except Exception as e:
            self.logger.warning(f"Could not check VEO quota: {e}")
            results['veo_quota'] = {
                'status': 'ERROR',
                'message': f'Could not check VEO quota: {e}',
                'available': False
            }

        # Check Google Cloud quota (if available)
        self.logger.info("🔍 Checking Google Cloud quota...")
        try:
            cloud_quota = get_google_cloud_quota_info()
            results['google_cloud'] = cloud_quota
        except Exception as e:
            results['google_cloud'] = {
                'status': 'ERROR',
                'message': f'Error checking Google Cloud: {e}',
                'available': False
            }

        # Determine overall status
        overall_status = self._determine_overall_status(results)
        results['overall_status'] = overall_status

        return results

    def _determine_overall_status(self, results: Dict[str, Any]) -> bool:
        """
        Determine overall quota status based on individual service results

        Args:
            results: Dictionary of individual service results

        Returns:
            True if overall status is good, False if there are issues
        """
        # Check critical services
        google_ai_ok = results.get('google_ai_studio', {}).get('api_accessible', False)
        usage_ok = results.get('google_ai_usage', {}).get('can_generate', False)

        # VEO is optional - don't fail overall status if VEO is not available
        veo_status = results.get('veo_quota', {}).get('status', 'UNKNOWN')
        veo_critical_failure = veo_status in ['FORBIDDEN', 'UNAUTHORIZED']

        # Overall status is good if Google AI is accessible and can generate
        # VEO issues are warnings, not failures
        overall_good = google_ai_ok and usage_ok and not veo_critical_failure

        return overall_good

    def check_veo_quota(self) -> Dict[str, Any]:
        """
        Check VEO-specific quota

        Returns:
            Dictionary with VEO quota status
        """
        try:
            return get_veo_quota_info(self.api_key)
        except Exception as e:
            return {
                'status': 'ERROR',
                'message': f'Error checking VEO quota: {e}',
                'available': False
            }

    def check_google_ai_quota(self) -> Dict[str, Any]:
        """
        Check Google AI Studio quota

        Returns:
            Dictionary with Google AI Studio quota status
        """
        try:
            return get_real_google_quota_info(self.api_key)
        except Exception as e:
            return {
                'status': 'ERROR',
                'message': f'Error checking Google AI Studio: {e}',
                'available': False
            }

    def check_usage_quota(self) -> Dict[str, Any]:
        """
        Check Google AI usage quota

        Returns:
            Dictionary with usage quota status
        """
        try:
            return get_real_google_quota_usage(self.api_key)
        except Exception as e:
            return {
                'status': 'ERROR',
                'message': f'Error checking usage quota: {e}',
                'can_generate': False
            }

    def is_generation_possible(self) -> Tuple[bool, str]:
        """
        Check if video generation is currently possible

        Returns:
            Tuple of (is_possible, reason)
        """
        quota_status = self.check_all_quotas()

        if quota_status['overall_status']:
            return True, "All quotas available for generation"

        # Determine specific reason
        google_ai = quota_status.get('google_ai_studio', {})
        usage = quota_status.get('google_ai_usage', {})
        veo = quota_status.get('veo_quota', {})

        if not google_ai.get('api_accessible', False):
            return False, f"Google AI Studio API not accessible: {google_ai.get('message', 'Unknown error')}"

        if not usage.get('can_generate', False):
            return False, f"Google AI quota exhausted: {usage.get('message', 'Unknown error')}"

        if veo.get('status') in ['FORBIDDEN', 'UNAUTHORIZED']:
            return False, f"VEO access denied: {veo.get('message', 'Unknown error')}"

        return True, "Generation possible with potential limitations"

