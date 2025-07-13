#!/usr/bin/env python3
"""
Comprehensive Environment Setup with Automatic Authentication
Handles Google Cloud authentication, API keys, and environment variables
Reads from and updates .env file with proper project configuration
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

def print_status(message: str, status: str = "info"):
    """Print colored status messages"""
    colors = {
        "info": "\033[94m",      # Blue
        "success": "\033[92m",   # Green
        "warning": "\033[93m",   # Yellow
        "error": "\033[91m",     # Red
        "reset": "\033[0m"       # Reset
    }
    
    icons = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️", 
        "error": "❌"
    }
    
    color = colors.get(status, colors["info"])
    icon = icons.get(status, "•")
    reset = colors["reset"]
    
    print(f"{color}{icon} {message}{reset}")

def run_command(cmd: list, capture_output: bool = True, timeout: int = 30) -> Tuple[bool, str, str]:
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
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def load_env_file() -> Dict[str, str]:
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

def save_env_file(env_vars: Dict[str, str]):
    """Save environment variables to .env file"""
    env_file = Path(".env")
    
    # Read existing file to preserve comments and structure
    lines = []
    if env_file.exists():
        with open(env_file, 'r') as f:
            lines = f.readlines()
    
    # Ensure all lines end with newline
    for i, line in enumerate(lines):
        if not line.endswith('\n'):
            lines[i] = line + '\n'
    
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

def create_env_from_template() -> Dict[str, str]:
    """Create .env file from template and return default values"""
    template_file = Path("config.env.example")
    env_file = Path(".env")
    
    if template_file.exists():
        # Copy template to .env
        import shutil
        shutil.copy(template_file, env_file)
        print_status("Created .env file from template", "success")
        
        # Fix the copied file to comment out GOOGLE_APPLICATION_CREDENTIALS
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Comment out GOOGLE_APPLICATION_CREDENTIALS line
        content = content.replace(
            'GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account-key.json',
            '# GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account-key.json'
        )
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print_status("Commented out GOOGLE_APPLICATION_CREDENTIALS for ADC usage", "info")
        
        # Load the template values
        return load_env_file()
    else:
        # Create basic .env with essential values
        default_env = {
            "GOOGLE_API_KEY": "your_google_ai_studio_api_key_here",
            "GEMINI_API_KEY": "your_gemini_api_key_here",
            "GOOGLE_CLOUD_PROJECT_ID": "viralgen-464411",
            "GOOGLE_CLOUD_LOCATION": "us-central1",
            "VEO_PROJECT_ID": "viralgen-464411",
            "VEO_LOCATION": "us-central1",
            "DEFAULT_PLATFORM": "youtube",
            "DEFAULT_CATEGORY": "Comedy",
            "OUTPUT_DIRECTORY": "outputs",
            "LOGS_DIRECTORY": "logs",
            "DEBUG_MODE": "false",
            "ENABLE_COMPREHENSIVE_LOGGING": "true"
        }
        
        save_env_file(default_env)
        print_status("Created basic .env file", "success")
        return default_env

def check_gcloud_installed() -> bool:
    """Check if gcloud CLI is installed"""
    success, _, _ = run_command(["which", "gcloud"])
    return success

def install_gcloud():
    """Install Google Cloud SDK"""
    print_status("Google Cloud SDK not found. Installing...", "warning")
    
    # Detect OS and provide installation instructions
    import platform
    system = platform.system().lower()
    
    if system == "darwin":  # macOS
        print_status("Installing Google Cloud SDK via Homebrew...", "info")
        success, _, error = run_command(["brew", "install", "google-cloud-sdk"], timeout=300)
        if not success:
            print_status(f"Homebrew installation failed: {error}", "error")
            print_status("Please install manually: https://cloud.google.com/sdk/docs/install", "warning")
            return False
    else:
        print_status("Please install Google Cloud SDK manually:", "warning")
        print_status("https://cloud.google.com/sdk/docs/install", "info")
        return False
    
    return True

def check_gcloud_auth() -> Tuple[bool, Optional[str]]:
    """Check if gcloud is authenticated"""
    success, output, _ = run_command(["gcloud", "auth", "list", "--format=json"])
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

def authenticate_gcloud() -> bool:
    """Authenticate with gcloud"""
    print_status("Opening Google Cloud authentication...", "info")
    
    # Run gcloud auth login
    success, _, error = run_command(["gcloud", "auth", "login"], capture_output=False, timeout=300)
    if not success:
        print_status(f"gcloud auth login failed: {error}", "error")
        return False
    
    print_status("Google Cloud authentication completed!", "success")
    return True

def setup_application_default_credentials() -> bool:
    """Setup Application Default Credentials"""
    print_status("Setting up Application Default Credentials...", "info")
    
    success, _, error = run_command(["gcloud", "auth", "application-default", "login"], capture_output=False, timeout=300)
    if not success:
        print_status(f"ADC setup failed: {error}", "error")
        return False
    
    print_status("Application Default Credentials configured!", "success")
    return True

def get_current_project() -> Optional[str]:
    """Get current gcloud project"""
    success, output, _ = run_command(["gcloud", "config", "get-value", "project"])
    if success and output.strip() and output.strip() != "(unset)":
        return output.strip()
    return None

def set_project(project_id: str) -> bool:
    """Set the gcloud project"""
    print_status(f"Setting project to: {project_id}", "info")
    
    success, _, error = run_command(["gcloud", "config", "set", "project", project_id])
    if not success:
        print_status(f"Failed to set project: {error}", "error")
        return False
    
    print_status(f"Project set to: {project_id}", "success")
    return True

def enable_required_apis(project_id: str) -> bool:
    """Enable required Google Cloud APIs"""
    apis = [
        "aiplatform.googleapis.com",          # Vertex AI
        "texttospeech.googleapis.com",        # Text-to-Speech
        "storage.googleapis.com",             # Cloud Storage
        "generativelanguage.googleapis.com"  # Generative Language (Gemini)
    ]
    
    print_status("Enabling required APIs...", "info")
    
    for api in apis:
        print_status(f"Enabling {api}...", "info")
        success, _, error = run_command(["gcloud", "services", "enable", api], timeout=60)
        if not success:
            print_status(f"Failed to enable {api}: {error}", "warning")
        else:
            print_status(f"Enabled {api}", "success")
    
    return True

def check_api_key_validity(api_key: str) -> bool:
    """Check if Google API key is valid"""
    if not api_key or api_key in ["your_google_ai_studio_api_key_here", "your_gemini_api_key_here"]:
        return False
    
    # Simple validation - should be around 39 characters for Google API keys
    return len(api_key) > 30

def prompt_for_api_key() -> Optional[str]:
    """Prompt user for Google API key"""
    print_status("Google API key needed for AI services", "warning")
    print_status("Get your API key from: https://makersuite.google.com/app/apikey", "info")
    
    api_key = input("Enter your Google API key (or press Enter to skip): ").strip()
    if api_key and check_api_key_validity(api_key):
        return api_key
    return None

def update_env_with_project_settings(env_vars: Dict[str, str], project_id: str, location: str) -> Dict[str, str]:
    """Update environment variables with project settings"""
    updates = {
        "GOOGLE_CLOUD_PROJECT_ID": project_id,
        "GOOGLE_CLOUD_LOCATION": location,
        "VEO_PROJECT_ID": project_id,
        "VEO_LOCATION": location,
        "VERTEX_AI_PROJECT_ID": project_id,  # Legacy compatibility
        "VERTEX_AI_LOCATION": location,      # Legacy compatibility
        "VERTEX_AI_GCS_BUCKET": f"viral-veo2-results"
    }
    
    env_vars.update(updates)
    
    # Ensure API keys don't have quotes
    for key in ["GOOGLE_API_KEY", "GEMINI_API_KEY"]:
        if key in env_vars:
            # Remove quotes if present
            value = env_vars[key]
            if value.startswith('"') and value.endswith('"'):
                env_vars[key] = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                env_vars[key] = value[1:-1]
    
    return env_vars

def test_authentication() -> Dict[str, Any]:
    """Test all authentication components"""
    results = {
        "gcloud_cli": False,
        "application_default": False,
        "project_set": False,
        "api_key_valid": False,
        "overall_success": False
    }
    
    print_status("Testing authentication setup...", "info")
    
    # Test gcloud CLI
    is_auth, account = check_gcloud_auth()
    results["gcloud_cli"] = is_auth
    if is_auth:
        print_status(f"gcloud CLI authenticated as: {account}", "success")
    else:
        print_status("gcloud CLI not authenticated", "error")
    
    # Test Application Default Credentials
    success, _, _ = run_command(["gcloud", "auth", "application-default", "print-access-token"])
    results["application_default"] = success
    if success:
        print_status("Application Default Credentials working", "success")
    else:
        print_status("Application Default Credentials not working", "error")
    
    # Test project configuration
    current_project = get_current_project()
    results["project_set"] = current_project is not None
    if current_project:
        print_status(f"Project configured: {current_project}", "success")
    else:
        print_status("No project configured", "error")
    
    # Test API key from .env
    env_vars = load_env_file()
    api_key = env_vars.get("GOOGLE_API_KEY", "")
    results["api_key_valid"] = check_api_key_validity(api_key)
    if results["api_key_valid"]:
        print_status("Google API key configured", "success")
    else:
        print_status("Google API key missing or invalid", "error")
    
    # Overall success
    results["overall_success"] = all([
        results["gcloud_cli"],
        results["application_default"], 
        results["project_set"],
        results["api_key_valid"]
    ])
    
    return results

def main():
    """Main setup function"""
    print_status("🚀 Viral AI Video Generator - Environment Setup", "info")
    print("=" * 60)
    
    # Step 1: Load or create .env file
    env_vars = {}
    if not Path(".env").exists():
        print_status("Creating .env file from template...", "info")
        env_vars = create_env_from_template()
    else:
        print_status("Loading existing .env file...", "info")
        env_vars = load_env_file()
    
    # Get project settings from .env or use defaults
    target_project = env_vars.get("GOOGLE_CLOUD_PROJECT_ID", "viralgen-464411")
    target_location = env_vars.get("GOOGLE_CLOUD_LOCATION", "us-central1")
    
    print_status(f"Using project: {target_project}", "info")
    print_status(f"Using location: {target_location}", "info")
    
    # Step 2: Check if gcloud is installed
    if not check_gcloud_installed():
        if not install_gcloud():
            print_status("Please install Google Cloud SDK manually and run this script again", "error")
            sys.exit(1)
    
    print_status("Google Cloud SDK found", "success")
    
    # Step 3: Check/setup authentication
    is_authenticated, account = check_gcloud_auth()
    if not is_authenticated:
        print_status("Google Cloud authentication required", "warning")
        if not authenticate_gcloud():
            print_status("Authentication failed", "error")
            sys.exit(1)
    else:
        print_status(f"Already authenticated as: {account}", "success")
    
    # Step 4: Setup Application Default Credentials
    success, _, _ = run_command(["gcloud", "auth", "application-default", "print-access-token"])
    if not success:
        print_status("Setting up Application Default Credentials...", "info")
        if not setup_application_default_credentials():
            print_status("Failed to setup Application Default Credentials", "error")
            sys.exit(1)
    else:
        print_status("Application Default Credentials already configured", "success")
    
    # Step 5: Check/set project
    current_project = get_current_project()
    
    if not current_project or current_project != target_project:
        if not set_project(target_project):
            print_status("Failed to set project", "error")
            sys.exit(1)
    else:
        print_status(f"Project already set: {current_project}", "success")
    
    # Step 6: Enable required APIs
    enable_required_apis(target_project)
    
    # Step 7: Update .env file with project settings
    env_vars = update_env_with_project_settings(env_vars, target_project, target_location)
    
    # Step 8: Check/update API key
    api_key = env_vars.get("GOOGLE_API_KEY", "")
    if not check_api_key_validity(api_key):
        print_status("Google API key needed for full functionality", "warning")
        new_api_key = prompt_for_api_key()
        if new_api_key:
            env_vars["GOOGLE_API_KEY"] = new_api_key
            env_vars["GEMINI_API_KEY"] = new_api_key
            print_status("API key updated in .env file", "success")
        else:
            print_status("Skipping API key setup - some features may not work", "warning")
    
    # Step 9: Save updated .env file
    save_env_file(env_vars)
    print_status("Updated .env file with authentication settings", "success")
    
    # Step 10: Final authentication test
    print_status("Running final authentication test...", "info")
    results = test_authentication()
    
    print("\n" + "=" * 60)
    if results["overall_success"]:
        print_status("🎉 Environment setup completed successfully!", "success")
        print_status("You can now run: python main.py generate --help", "info")
    else:
        print_status("⚠️ Setup completed with some issues", "warning")
        print_status("Check the errors above and run the script again if needed", "info")
    
    # Step 11: Display current .env settings
    print("\n" + "=" * 60)
    print_status("Current .env Configuration:", "info")
    print("=" * 60)
    
    key_display = {
        "GOOGLE_CLOUD_PROJECT_ID": "Google Cloud Project",
        "GOOGLE_CLOUD_LOCATION": "Google Cloud Location", 
        "VEO_PROJECT_ID": "VEO Project ID",
        "VEO_LOCATION": "VEO Location",
        "GOOGLE_API_KEY": "Google AI Studio API Key",
        "DEFAULT_PLATFORM": "Default Platform",
        "DEFAULT_CATEGORY": "Default Category",
        "OUTPUT_DIRECTORY": "Output Directory",
        "ENABLE_COMPREHENSIVE_LOGGING": "Comprehensive Logging"
    }
    
    for key, description in key_display.items():
        value = env_vars.get(key, "Not set")
        if "API_KEY" in key and value not in ["Not set", "your_google_ai_studio_api_key_here"]:
            # Mask API key for security
            value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
        print(f"  {description}: {value}")
    
    print("=" * 60)

if __name__ == "__main__":
    main() 