"""
Test Configuration and Utilities
"""

import os
import sys
import tempfile
import shutil
from typing import Dict, Any, Optional

# Test settings
TEST_SETTINGS = {
    'api_key': os.getenv('GOOGLE_API_KEY', 'test_key_placeholder'),
    'test_timeout': 30,  # seconds
    'mock_api_calls': True,  # Mock API calls by default
    'create_temp_files': True,
    'cleanup_after_tests': True,
    'verbose_output': True
}

# Test directories
TEST_DIRS = {
    'temp': tempfile.gettempdir(),
    'outputs': 'test_outputs',
    'fixtures': os.path.join(os.path.dirname(__file__), 'fixtures')
}


class TestEnvironment:
    """Test environment manager"""
    
    def __init__(self):
        self.temp_dirs = []
        self.created_files = []
    
    def create_temp_dir(self) -> str:
        """Create a temporary directory for tests"""
        temp_dir = tempfile.mkdtemp(prefix='ai_video_test_')
        self.temp_dirs.append(temp_dir)
        return temp_dir
    
    def create_temp_file(self, content: bytes = b'test content', suffix: str = '.mp4') -> str:
        """Create a temporary file for tests"""
        fd, path = tempfile.mkstemp(suffix=suffix, prefix='test_video_')
        os.write(fd, content)
        os.close(fd)
        self.created_files.append(path)
        return path
    
    def cleanup(self):
        """Clean up test environment"""
        # Remove temporary directories
        for temp_dir in self.temp_dirs:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        
        # Remove temporary files
        for file_path in self.created_files:
            if os.path.exists(file_path):
                os.remove(file_path)
        
        self.temp_dirs.clear()
        self.created_files.clear()


def skip_if_no_api_key(test_func):
    """Decorator to skip tests if no API key is available"""
    import unittest
    
    def wrapper(*args, **kwargs):
        if not TEST_SETTINGS['api_key'] or TEST_SETTINGS['api_key'] == 'test_key_placeholder':
            raise unittest.SkipTest("No valid API key available")
        return test_func(*args, **kwargs)
    
    return wrapper


def skip_if_component_missing(component_path: str):
    """Decorator to skip tests if a component is missing"""
    import unittest
    
    def decorator(test_func):
        def wrapper(*args, **kwargs):
            try:
                __import__(component_path, fromlist=[''])
                return test_func(*args, **kwargs)
            except ImportError:
                raise unittest.SkipTest(f"Component {component_path} not available")
        return wrapper
    return decorator


def mock_api_response(response_data: Dict[str, Any]):
    """Create a mock API response"""
    from unittest.mock import Mock
    
    mock_response = Mock()
    mock_response.text = str(response_data)
    return mock_response


# Global test environment instance
test_env = TestEnvironment() 