#!/usr/bin/env python3
"""Test the news aggregator concatenation fix"""

import sys
import os
import asyncio

# Add project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def main():
    from src.news_aggregator.cli_integration import main as cli_main
    
    # Test with simple parameters
    test_args = [
        "test",  # program name
        "--mode", "enhanced",
        "--platform", "tiktok", 
        "--duration", "30",
        "--max-stories", "3",
        "--language", "he",
        "--channel-name", "CONCAT_TEST",
        "--aggregate-source", "ynet"
    ]
    
    # Temporarily replace sys.argv
    original_argv = sys.argv
    sys.argv = test_args
    
    try:
        await cli_main()
    finally:
        sys.argv = original_argv

if __name__ == "__main__":
    asyncio.run(main())