"""
Automatic Authentication Handler
Integrates with the main application to handle authentication problems automatically
Reads from and updates .env file with proper project configuration
"""

import os
import sys
import subprocess
import json
import time
from typing import Dict, Any, Optional, Tuple, List
from pathlib import Path

from .logging_config import get_logger

logger = get_logger(__name__)


class AutoAuthHandler:
    """Automatic authentication handler for Google Cloud services"""
    
    def __init__(self):
        self.required_apis = [
            "aiplatform.googleapis.com",          # Vertex AI
            "texttospeech.googleapis.com",        # Text-to-Speech
            "storage.googleapis.com",             # Cloud Storage
            "generativelanguage.googleapis.com"  # Generative Language (Gemini)
        ]
        
        # Load configuration from .env file
        self.env_vars = self.load_env_file()
        self.target_project = self.env_vars.get("GOOGLE_CLOUD_PROJECT_ID", "viralgen-464411")
        self.target_location = self.env_vars.get("GOOGLE_CLOUD_LOCATION", "us-central1")
        self.target_bucket = self.env_vars.get("VERTEX_AI_GCS_BUCKET", "viral-veo2-results")
    
    def load_env_file(self) -> Dict[str, str]:
        """Load environment variables from .env file"""
        env_vars = {}
        env_file = Path(".env")
        
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
        
        return env_vars
    
    def save_env_file(self, env_vars: Dict[str, str]):
        """Save environment variables to .env file"""
        env_file = Path(".env")
        
        # Read existing file to preserve comments and structure
        lines = []
        if env_file.exists():
            with open(env_file, 'r') as f:
                lines = f.readlines()
        
        # Update existing variables
        updated_vars = set()
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped and not stripped.startswith('#') and '=' in stripped:
                key = stripped.split('=', 1)[0].strip()
                if key in env_vars:
                    lines[i] = f"{key}={env_vars[key]}\n"
                    updated_vars.add(key)
        
        # Add new variables at the end
        for key, value in env_vars.items():
            if key not in updated_vars:
                lines.append(f"{key}={value}\n")
        
        # Write back to file
        with open(env_file, 'w') as f:
            f.writelines(lines)
    
    def run_command(self, cmd: List[str], capture_output: bool = True, timeout: int = 30) -> Tuple[bool, str, str]:
        """Run a command and return success status, stdout, stderr"""
        try:
            result = subprocess.run(
                cmd, 
                capture_output=capture_output,
                text=True,
                timeout=timeout
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out: {' '.join(cmd)}")
            return False, "", "Command timed out"
        except Exception as e:
            logger.error(f"Command failed: {' '.join(cmd)} - {e}")
            return False, "", str(e)
    
    def check_gcloud_installed(self) -> bool:
        """Check if gcloud CLI is installed"""
        success, _, _ = self.run_command(["which", "gcloud"])
        return success
    
    def install_gcloud_instructions(self) -> str:
        """Get platform-specific gcloud installation instructions"""
        import platform
        system = platform.system().lower()
        
        if system == "darwin":  # macOS
            return """
🔧 Install Google Cloud SDK on macOS:

Option 1 - Homebrew (Recommended):
  brew install google-cloud-sdk

Option 2 - Manual Download:
  https://cloud.google.com/sdk/docs/install-sdk#mac

After installation, restart your terminal and run this script again.
"""
        elif system == "linux":
            return """
🔧 Install Google Cloud SDK on Linux:

# Add the Cloud SDK distribution URI as a package source
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list

# Import the Google Cloud public key
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -

# Update and install the Cloud SDK
sudo apt-get update && sudo apt-get install google-cloud-cli

Or visit: https://cloud.google.com/sdk/docs/install-sdk#linux
"""
        else:
            return """
🔧 Install Google Cloud SDK:
Visit: https://cloud.google.com/sdk/docs/install
"""
    
    def check_gcloud_auth(self) -> Tuple[bool, Optional[str]]:
        """Check if gcloud is authenticated"""
        success, output, _ = self.run_command(["gcloud", "auth", "list", "--format=json"])
        if not success:
            return False, None
        
        try:
            accounts = json.loads(output)
            active_accounts = [acc for acc in accounts if acc.get("status") == "ACTIVE"]
            if active_accounts:
                return True, active_accounts[0]["account"]
            return False, None
        except:
            return False, None
    
    def authenticate_gcloud(self, force: bool = False) -> bool:
        """Authenticate with gcloud interactively"""
        if not force:
            # Check if already authenticated
            is_auth, account = self.check_gcloud_auth()
            if is_auth:
                logger.info(f"Already authenticated as: {account}")
                return True
        
        logger.info("🔐 Opening Google Cloud authentication...")
        print("\n" + "="*60)
        print("🔐 GOOGLE CLOUD AUTHENTICATION REQUIRED")
        print("="*60)
        print("Your browser will open for authentication.")
        print("Please sign in with your Google account that has access to the project.")
        print("="*60 + "\n")
        
        # Run gcloud auth login
        success, _, error = self.run_command(["gcloud", "auth", "login"], capture_output=False, timeout=300)
        if not success:
            logger.error(f"gcloud auth login failed: {error}")
            return False
        
        logger.info("✅ Google Cloud authentication completed!")
        return True
    
    def setup_application_default_credentials(self) -> bool:
        """Setup Application Default Credentials"""
        logger.info("🔑 Setting up Application Default Credentials...")
        
        # Check if already set up
        success, _, _ = self.run_command(["gcloud", "auth", "application-default", "print-access-token"])
        if success:
            logger.info("✅ Application Default Credentials already configured")
            return True
        
        print("\n" + "="*60)
        print("🔑 APPLICATION DEFAULT CREDENTIALS SETUP")
        print("="*60)
        print("Setting up credentials for API access...")
        print("Your browser will open again for additional permissions.")
        print("="*60 + "\n")
        
        success, _, error = self.run_command(
            ["gcloud", "auth", "application-default", "login"], 
            capture_output=False, 
            timeout=300
        )
        if not success:
            logger.error(f"ADC setup failed: {error}")
            return False
        
        logger.info("✅ Application Default Credentials configured!")
        return True
    
    def get_current_project(self) -> Optional[str]:
        """Get current gcloud project"""
        success, output, _ = self.run_command(["gcloud", "config", "get-value", "project"])
        if success and output.strip() and output.strip() != "(unset)":
            return output.strip()
        return None
    
    def check_and_set_project(self) -> bool:
        """Check and set the correct project"""
        # Check current project
        current_project = self.get_current_project()
        
        if current_project == self.target_project:
            logger.info(f"✅ Project already set: {self.target_project}")
            return True
        
        logger.info(f"🔧 Setting project to: {self.target_project}")
        success, _, error = self.run_command(["gcloud", "config", "set", "project", self.target_project])
        if not success:
            logger.error(f"Failed to set project: {error}")
            return False
        
        logger.info(f"✅ Project set to: {self.target_project}")
        return True
    
    def enable_required_apis(self) -> bool:
        """Enable required Google Cloud APIs"""
        logger.info("🔧 Enabling required APIs...")
        
        success_count = 0
        for api in self.required_apis:
            logger.info(f"Enabling {api}...")
            success, _, error = self.run_command(["gcloud", "services", "enable", api], timeout=60)
            if success:
                logger.info(f"✅ Enabled {api}")
                success_count += 1
            else:
                logger.warning(f"⚠️ Failed to enable {api}: {error}")
        
        logger.info(f"✅ Enabled {success_count}/{len(self.required_apis)} APIs")
        return success_count > 0
    
    def update_env_file(self) -> bool:
        """Update .env file with correct project settings"""
        env_file = Path(".env")
        
        if not env_file.exists():
            logger.warning("⚠️ .env file not found, creating one...")
            self.create_basic_env_file()
        
        # Reload env vars
        self.env_vars = self.load_env_file()
        
        # Update project settings
        updates = {
            "GOOGLE_CLOUD_PROJECT_ID": self.target_project,
            "GOOGLE_CLOUD_LOCATION": self.target_location,
            "VEO_PROJECT_ID": self.target_project,
            "VEO_LOCATION": self.target_location,
            "VERTEX_AI_PROJECT_ID": self.target_project,  # Legacy compatibility
            "VERTEX_AI_LOCATION": self.target_location,   # Legacy compatibility
            "VERTEX_AI_GCS_BUCKET": self.target_bucket
        }
        
        self.env_vars.update(updates)
        
        # Ensure API keys don't have quotes
        for key in ["GOOGLE_API_KEY", "GEMINI_API_KEY"]:
            if key in self.env_vars:
                # Remove quotes if present
                value = self.env_vars[key]
                if value.startswith('"') and value.endswith('"'):
                    self.env_vars[key] = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    self.env_vars[key] = value[1:-1]
        
        self.save_env_file(self.env_vars)
        
        logger.info("✅ Updated .env file with project settings")
        return True
    
    def create_basic_env_file(self) -> bool:
        """Create a basic .env file from template or defaults"""
        template_file = Path("config.env.example")
        
        if template_file.exists():
            # Copy template to .env
            import shutil
            shutil.copy(template_file, ".env")
            logger.info("✅ Created .env file from template")
        else:
            # Create basic .env with essential values
            env_content = f"""# Viral AI Video Generator Environment Variables

# Core API Keys
GOOGLE_API_KEY=your_google_ai_studio_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT_ID={self.target_project}
GOOGLE_CLOUD_LOCATION={self.target_location}

# VEO Video Generation
VEO_PROJECT_ID={self.target_project}
VEO_LOCATION={self.target_location}
USE_REAL_VEO2=true
VEO_FALLBACK_ENABLED=true

# Legacy Compatibility
VERTEX_AI_PROJECT_ID={self.target_project}
VERTEX_AI_LOCATION={self.target_location}
VERTEX_AI_GCS_BUCKET={self.target_bucket}

# Application Settings
DEFAULT_PLATFORM=youtube
DEFAULT_CATEGORY=Comedy
OUTPUT_DIRECTORY=outputs
LOGS_DIRECTORY=logs
DEBUG_MODE=false
ENABLE_COMPREHENSIVE_LOGGING=true
"""
            
            with open(".env", 'w') as f:
                f.write(env_content)
            
            logger.info("✅ Created basic .env file")
        
        return True
    
    def check_api_key(self) -> Tuple[bool, str]:
        """Check if API key is configured and valid"""
        # Load from .env file
        api_key = self.env_vars.get('GOOGLE_API_KEY', '')
        
        if not api_key:
            # Also check environment variables
            api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
        
        if not api_key or api_key in ["your_google_ai_studio_api_key_here", "your_gemini_api_key_here"]:
            return False, "API key not configured"
        
        if len(api_key) < 30:
            return False, "API key appears invalid (too short)"
        
        return True, "API key configured"
    
    def handle_authentication_problem(self, error_details: str = "") -> bool:
        """
        Main method to handle authentication problems automatically
        Returns True if authentication was fixed, False otherwise
        """
        logger.info("🔧 Handling authentication problem...")
        
        if error_details:
            logger.info(f"Error details: {error_details}")
        
        # Step 1: Check if gcloud is installed
        if not self.check_gcloud_installed():
            logger.error("❌ Google Cloud SDK not installed")
            print(self.install_gcloud_instructions())
            return False
        
        # Step 2: Authenticate gcloud
        if not self.authenticate_gcloud():
            logger.error("❌ Failed to authenticate gcloud")
            return False
        
        # Step 3: Setup Application Default Credentials
        if not self.setup_application_default_credentials():
            logger.error("❌ Failed to setup Application Default Credentials")
            return False
        
        # Step 4: Set correct project
        if not self.check_and_set_project():
            logger.error("❌ Failed to set project")
            return False
        
        # Step 5: Enable APIs
        self.enable_required_apis()
        
        # Step 6: Update .env file
        self.update_env_file()
        
        # Step 7: Check API key
        has_api_key, api_key_status = self.check_api_key()
        if not has_api_key:
            logger.warning(f"⚠️ {api_key_status}")
            print("\n" + "="*60)
            print("🔑 API KEY REQUIRED")
            print("="*60)
            print("Get your Google AI Studio API key from:")
            print("https://makersuite.google.com/app/apikey")
            print("\nAdd it to your .env file:")
            print("GOOGLE_API_KEY=your_actual_api_key_here")
            print("="*60 + "\n")
        
        logger.info("✅ Authentication setup completed!")
        return True
    
    def quick_auth_check(self) -> Dict[str, Any]:
        """Quick check of authentication status"""
        # Reload env vars to get latest values
        self.env_vars = self.load_env_file()
        
        results = {
            "gcloud_installed": self.check_gcloud_installed(),
            "gcloud_authenticated": False,
            "adc_working": False,
            "project_correct": False,
            "api_key_configured": False,
            "overall_ready": False
        }
        
        if results["gcloud_installed"]:
            is_auth, account = self.check_gcloud_auth()
            results["gcloud_authenticated"] = is_auth
            
            if is_auth:
                # Check ADC
                success, _, _ = self.run_command(["gcloud", "auth", "application-default", "print-access-token"])
                results["adc_working"] = success
                
                # Check project
                current_project = self.get_current_project()
                results["project_correct"] = current_project == self.target_project
        
        # Check API key
        has_api_key, _ = self.check_api_key()
        results["api_key_configured"] = has_api_key
        
        # Overall readiness
        results["overall_ready"] = all([
            results["gcloud_installed"],
            results["gcloud_authenticated"],
            results["adc_working"],
            results["project_correct"]
        ])
        
        return results

    def auto_fix_authentication(self) -> bool:
        """
        Automatically detect and fix authentication problems
        
        Returns:
            True if authentication is working, False otherwise
        """
        logger.info("🔧 Auto-fixing authentication problems...")
        
        # Step 1: Check if gcloud is installed
        if not self.check_gcloud_installed():
            logger.error("❌ gcloud CLI not installed")
            print(self.install_gcloud_instructions())
            return False
        
        # Step 2: Check if authenticated
        is_auth, account = self.check_gcloud_auth()
        if not is_auth:
            logger.info("🔐 gcloud not authenticated, opening authentication...")
            if not self.authenticate_gcloud():
                return False
        
        # Step 3: Setup Application Default Credentials
        if not self.setup_application_default_credentials():
            return False
        
        # Step 4: Set correct project
        current_project = self.get_current_project()
        if current_project != self.target_project:
            logger.info(f"🔧 Setting project to: {self.target_project}")
            success, _, error = self.run_command(["gcloud", "config", "set", "project", self.target_project])
            if not success:
                logger.error(f"❌ Failed to set project: {error}")
                return False
        
        # Step 5: Enable required APIs
        logger.info("🔧 Enabling required APIs...")
        for api in self.required_apis:
            logger.info(f"   Enabling {api}...")
            success, _, error = self.run_command(["gcloud", "services", "enable", api])
            if not success:
                logger.warning(f"⚠️ Failed to enable {api}: {error}")
        
        # Step 6: Check API key
        has_api_key, api_key_status = self.check_api_key()
        if not has_api_key:
            logger.warning(f"⚠️ {api_key_status}")
            print("\n" + "="*60)
            print("🔑 API KEY REQUIRED")
            print("="*60)
            print("Get your Google AI Studio API key from:")
            print("https://makersuite.google.com/app/apikey")
            print("\nAdd it to your .env file:")
            print("GOOGLE_API_KEY=your_actual_api_key_here")
            print("="*60 + "\n")
            # Don't fail here - the app can still work with limited functionality
        
        logger.info("✅ Authentication auto-fix completed!")
        return True
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive authentication test using GCloudAuthTester"""
        try:
            from .gcloud_auth_tester import GCloudAuthTester
            tester = GCloudAuthTester()
            return tester.run_comprehensive_auth_test()
        except Exception as e:
            logger.error(f"❌ Comprehensive test failed: {e}")
            return {"status": "ERROR", "error": str(e)}


# Global instance
auto_auth_handler = AutoAuthHandler() 