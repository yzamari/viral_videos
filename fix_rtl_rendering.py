#!/usr/bin/env python3
"""
Fix RTL text rendering in video generation
"""

import sys
import subprocess

def install_rtl_packages():
    """Install required packages for RTL text support"""
    packages = [
        'arabic-reshaper',
        'python-bidi'
    ]
    
    for package in packages:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
    print("✅ RTL support packages installed")

if __name__ == "__main__":
    install_rtl_packages()