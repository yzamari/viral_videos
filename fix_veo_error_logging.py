#!/usr/bin/env python3
"""
Add better VEO error logging and debugging
"""

import os
import shutil

def add_veo_error_logging():
    """Add comprehensive VEO error logging"""
    print("🔧 Adding VEO error logging...")
    
    video_gen_path = "/Users/yahavzamari/viralAi/src/generators/video_generator.py"
    
    with open(video_gen_path, 'r') as f:
        content = f.read()
    
    # Find and enhance VEO error logging
    enhanced_logging = '''                        except Exception as e:
                            logger.error(f"❌ VEO generation failed for clip {i+1} attempt {veo_attempt + 1}:")
                            logger.error(f"   Error type: {type(e).__name__}")
                            logger.error(f"   Error message: {str(e)}")
                            
                            # Check for common VEO failure reasons
                            error_msg = str(e).lower()
                            if 'quota' in error_msg:
                                logger.error("   🚨 QUOTA EXCEEDED - VEO API limit reached")
                                print("⚠️ VEO QUOTA EXCEEDED - Consider using --cheap mode")
                            elif 'invalid' in error_msg and 'prompt' in error_msg:
                                logger.error("   🚨 INVALID PROMPT - VEO rejected the prompt")
                                logger.error(f"   Prompt was: {current_prompt[:200]}...")
                            elif 'timeout' in error_msg:
                                logger.error("   🚨 TIMEOUT - VEO generation took too long")
                            elif 'connection' in error_msg or 'network' in error_msg:
                                logger.error("   🚨 NETWORK ERROR - Check internet connection")
                            else:
                                logger.error("   🚨 UNKNOWN ERROR - Check VEO service status")
                            
                            self._last_veo_error = str(e)  # Store error for next attempt
                            clip_path = None'''
    
    # Replace the existing error handling
    if "except Exception as e:" in content and "VEO generation failed" in content:
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "except Exception as e:" in line and i+1 < len(lines) and "VEO generation failed" in lines[i+1]:
                # Find the end of this except block
                j = i
                current_indent = len(line) - len(line.lstrip())
                while j < len(lines) and (not lines[j].strip() or len(lines[j]) - len(lines[j].lstrip()) > current_indent):
                    j += 1
                # Replace the except block
                lines[i:j] = enhanced_logging.split('\n')
                break
        content = '\n'.join(lines)
    
    with open(video_gen_path, 'w') as f:
        f.write(content)
    
    print("✅ VEO error logging enhanced")

def main():
    print("🚀 Adding VEO error logging\n")
    
    add_veo_error_logging()
    
    print("\n✨ VEO error logging added!")

if __name__ == "__main__":
    main()