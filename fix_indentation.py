#!/usr/bin/env python3
"""Fix indentation issue in quota_verification.py"""

# Read the file
with open('src/utils/quota_verification.py', 'r') as f:
    lines = f.readlines()

# Find line 527 (0-indexed would be 526)
# The issue is that line 527 has "except Exception as e:" with wrong indentation
# It should have 8 spaces (2 levels) instead of whatever it has

if len(lines) > 526:
    # Fix line 527
    lines[526] = '        except Exception as e:\n'
    
    # Write back
    with open('src/utils/quota_verification.py', 'w') as f:
        f.writelines(lines)
    
    print("✅ Fixed indentation on line 527")
else:
    print("❌ File doesn't have enough lines") 