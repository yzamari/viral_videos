#!/usr/bin/env python3
"""
Standalone Google Cloud Authentication Checker
Run this script to verify your authentication setup before using the video generator
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.gcloud_auth_tester import test_gcloud_authentication

def main():
    """Main function to run authentication tests"""
    print("🔐 Google Cloud Authentication Checker")
    print("=" * 50)
    
    try:
        # Run comprehensive authentication tests
        results = test_gcloud_authentication()
        
        # Get analysis results
        analysis = results.get('analysis', {})
        
        # Exit with appropriate code
        if analysis.get('can_run_app', False):
            print("\n🎉 SUCCESS: Authentication is properly configured!")
            print("🚀 You can now run the video generator:")
            print("   python main.py generate --mission 'your mission here'")
            sys.exit(0)
        else:
            print("\n❌ FAILURE: Authentication issues detected!")
            print("🔧 Please fix the issues above before running the video generator.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Authentication check cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during authentication check: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 