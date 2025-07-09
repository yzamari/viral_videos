#!/usr/bin/env python3
"""Quick quota usage checker"""

import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

try:
    from src.generators.optimized_veo_client import OptimizedVeoClient
    
    print('📊 Daily Quota Usage Check')
    print('=' * 40)
    print(f'Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print()
    
    # Initialize client to check quota
    api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
    if not api_key:
        print('❌ No API key found in environment')
        exit(1)
    
    client = OptimizedVeoClient(api_key, 'outputs')
    
    print('🎯 Current Quota Status:')
    print(f'   {client.quota_tracker.get_status()}')
    print()
    
    # Check if quota is exhausted
    if client.quota_tracker.is_quota_exhausted():
        print('🚫 QUOTA EXHAUSTED: Daily limit reached')
        print(f'   Used: {client.quota_tracker.daily_count} videos today')
    else:
        remaining = 50 - client.quota_tracker.daily_count
        print(f'✅ QUOTA AVAILABLE: {remaining} videos remaining today')
        print(f'   Used: {client.quota_tracker.daily_count} videos today')
    
    print()
    print('📋 Quota Details:')
    print(f'   Daily limit: {client.quota_tracker.daily_limit} videos')
    print(f'   Rate limit: {client.quota_tracker.rpm_limit} videos/minute')  
    print(f'   Min spacing: {client.quota_tracker.min_spacing} seconds')
    print()
    
    # Add clear explanation
    remaining = 50 - client.quota_tracker.daily_count
    spacing = client.quota_tracker.min_spacing
    
    print('💡 What this means:')
    if remaining > 0:
        print(f'   ✅ You can create {remaining} more videos today')
        print(f'   ⏰ You need to wait {spacing} seconds between each video')
        if remaining > 1:
            total_time = (remaining - 1) * spacing
            hours = total_time // 3600
            minutes = (total_time % 3600) // 60
            if hours > 0:
                print(f'   🕐 Creating all {remaining} videos will take ~{hours}h {minutes}m (due to spacing)')
            else:
                print(f'   🕐 Creating all {remaining} videos will take ~{minutes}m (due to spacing)')
    else:
        print('   🚫 No videos remaining today - quota exhausted')
    
    print()
    print('⏰ Reset Time: Midnight (daily quota resets)')
    
except ImportError as e:
    print(f'❌ Import error: {e}')
except Exception as e:
    print(f'❌ Error checking quota: {e}')