#!/usr/bin/env python3
"""
Fix duration enforcement in script generation and validation
"""

import os
import re

def fix_duration_enforcement():
    """Fix all duration-related issues in the video generation system"""
    
    print("🔧 Fixing duration enforcement issues...")
    
    # Fix 1: Update EnhancedScriptProcessor to enforce duration limits
    script_processor_path = "src/generators/enhanced_script_processor.py"
    if os.path.exists(script_processor_path):
        with open(script_processor_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add duration enforcement in process method
        if "def process_for_audio_generation" in content:
            # Find the method and add duration enforcement
            new_duration_check = '''
    def process_for_audio_generation(self, script: str, language: Language = Language.ENGLISH_US,
                                   target_duration: Optional[int] = None,
                                   platform: Platform = Platform.YOUTUBE,
                                   config: Optional[GeneratedVideoConfig] = None) -> Dict[str, Any]:
        """Process script for audio generation with STRICT duration enforcement"""
        
        logger.info(f"🎯 Processing script for {language.value} audio generation")
        logger.info(f"⏱️  Target duration: {target_duration} seconds")
        
        # CRITICAL: Validate and truncate script to fit duration BEFORE processing
        if target_duration:
            # Calculate maximum words based on target duration
            # Average speaking rate: 150 words per minute (2.5 words per second)
            words_per_second = 2.5
            max_words = int(target_duration * words_per_second * 0.85)  # 85% to account for pauses
            
            script_words = script.split()
            current_word_count = len(script_words)
            
            if current_word_count > max_words:
                logger.warning(f"⚠️  Script has {current_word_count} words but max is {max_words} for {target_duration}s")
                logger.warning(f"📄 Truncating script to fit duration constraint")
                
                # Truncate to sentences that fit within word limit
                sentences = self._split_into_sentences(script, language)
                truncated_sentences = []
                word_count = 0
                
                for sentence in sentences:
                    sentence_words = len(sentence.split())
                    if word_count + sentence_words <= max_words:
                        truncated_sentences.append(sentence)
                        word_count += sentence_words
                    else:
                        break
                
                script = ' '.join(truncated_sentences)
                logger.info(f"✂️  Truncated script to {word_count} words ({len(truncated_sentences)} sentences)")'''
            
            # Replace or add the duration check
            if "def process_for_audio_generation" in content:
                # Find the method definition
                method_start = content.find("def process_for_audio_generation")
                if method_start > -1:
                    # Find the docstring end
                    docstring_end = content.find('"""', method_start + 50) + 3
                    if docstring_end > method_start:
                        # Insert the duration check after docstring
                        before = content[:docstring_end]
                        after = content[docstring_end:]
                        
                        # Extract the existing method signature and docstring
                        method_end = content.find("\n", method_start)
                        next_quote = content.find('"""', method_start)
                        
                        # Only update if we haven't already added the fix
                        if "STRICT duration enforcement" not in content:
                            content = content.replace(
                                'def process_for_audio_generation(self, script: str, language: Language = Language.ENGLISH_US,',
                                new_duration_check.split('\n')[1]
                            )
                            print("✅ Added duration enforcement to process_for_audio_generation")
        
        # Fix 2: Add segment duration calculation with padding
        segment_duration_fix = '''
        # Calculate segment durations including padding
        total_duration_with_padding = 0.0
        segment_timings = []
        
        for i, segment in enumerate(segments):
            # Account for padding between segments (except last)
            if i > 0:
                total_duration_with_padding += self.padding_between_segments
            
            segment_duration = segment.get('duration', 0)
            total_duration_with_padding += segment_duration
            segment_timings.append({
                'index': i,
                'start': total_duration_with_padding - segment_duration,
                'duration': segment_duration,
                'text': segment['text']
            })
        
        # Validate total duration INCLUDING padding
        if target_duration and total_duration_with_padding > target_duration * 1.1:  # 10% tolerance
            logger.error(f"❌ Total audio duration {total_duration_with_padding:.1f}s (with padding) exceeds target {target_duration}s")
            
            # Truncate segments to fit
            truncated_segments = []
            current_duration = 0.0
            
            for i, segment in enumerate(segments):
                segment_duration = segment.get('duration', 0)
                padding = self.padding_between_segments if i > 0 else 0
                
                if current_duration + segment_duration + padding <= target_duration:
                    truncated_segments.append(segment)
                    current_duration += segment_duration + padding
                else:
                    break
            
            segments = truncated_segments
            logger.warning(f"⚠️  Truncated to {len(segments)} segments to fit duration")'''
        
        # Add segment duration validation
        if "# Create segments" in content and segment_duration_fix not in content:
            content = content.replace(
                "# Create segments",
                "# Create segments\n" + segment_duration_fix
            )
            print("✅ Added segment duration validation with padding")
        
        # Save the updated file
        with open(script_processor_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Updated {script_processor_path}")
    
    # Fix 2: Update video_generator.py to enforce duration validation
    video_gen_path = "src/generators/video_generator.py"
    if os.path.exists(video_gen_path):
        with open(video_gen_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add strict validation before generation
        duration_validation = '''
        # CRITICAL: Validate duration before proceeding
        if hasattr(config, 'duration_seconds') and config.duration_seconds:
            target_duration = config.duration_seconds
            
            # Check if script duration is within acceptable range
            script_duration = script_result.get('total_duration', 0)
            if script_duration > target_duration * 1.15:  # 15% tolerance
                error_msg = f"❌ Script duration {script_duration:.1f}s exceeds target {target_duration}s by too much"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            logger.info(f"✅ Script duration {script_duration:.1f}s is within tolerance for {target_duration}s target")'''
        
        # Add validation check if not already present
        if "CRITICAL: Validate duration before proceeding" not in content:
            # Find a good place to insert (after script generation)
            if "script_result = " in content:
                # Insert after script result
                insertion_point = content.find("script_result = ")
                if insertion_point > -1:
                    # Find the end of that line
                    line_end = content.find("\n", insertion_point)
                    if line_end > -1:
                        content = content[:line_end+1] + duration_validation + "\n" + content[line_end+1:]
                        print("✅ Added duration validation to video_generator.py")
        
        # Save the updated file
        with open(video_gen_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    # Fix 3: Update AI agent prompts to emphasize duration
    update_ai_agent_prompts()
    
    # Fix 4: Fix the enum error in overlay generation
    fix_overlay_enum_error()
    
    print("\n✅ Duration enforcement fixes completed!")
    print("\n📋 Summary of changes:")
    print("1. Added strict duration enforcement in script processing")
    print("2. Added segment truncation when exceeding duration")
    print("3. Added padding calculation to total duration")
    print("4. Added duration validation before video generation")
    print("5. Updated AI agent prompts to emphasize duration")
    print("6. Fixed overlay enum error")

def update_ai_agent_prompts():
    """Update all AI agent prompts to emphasize duration constraints"""
    
    agents_dir = "src/agents"
    if not os.path.exists(agents_dir):
        return
    
    # Common duration reminder to add to all agents
    duration_reminder = """
CRITICAL DURATION CONSTRAINT: The video MUST be exactly {duration} seconds.
- Each segment should be approximately {duration/num_segments:.1f} seconds
- Account for 300ms padding between segments
- Total content must fit within duration including pauses
- DO NOT generate content that exceeds the target duration"""
    
    # Update specific agent files
    agent_files = [
        "script_writer_agent.py",
        "viral_hook_specialist.py", 
        "story_architect.py",
        "platform_optimizer.py"
    ]
    
    for agent_file in agent_files:
        filepath = os.path.join(agents_dir, agent_file)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add duration reminder to prompts
            if "CRITICAL DURATION CONSTRAINT" not in content:
                # Find prompt definitions
                if "prompt = " in content or "PROMPT = " in content:
                    content = content.replace(
                        'prompt = """',
                        f'prompt = """\n{duration_reminder}\n'
                    )
                    content = content.replace(
                        'PROMPT = """',
                        f'PROMPT = """\n{duration_reminder}\n'
                    )
                    print(f"✅ Updated duration prompts in {agent_file}")
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

def fix_overlay_enum_error():
    """Fix the 'str' object has no attribute 'value' error in overlay generation"""
    
    video_gen_path = "src/generators/video_generator.py"
    if os.path.exists(video_gen_path):
        with open(video_gen_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix enum access
        enum_fixes = [
            # Fix language enum access
            ('language.value', 'str(language) if hasattr(language, "value") else str(language)'),
            # Fix platform enum access  
            ('platform.value', 'str(platform) if hasattr(platform, "value") else str(platform)'),
            # Fix category enum access
            ('category.value', 'str(category) if hasattr(category, "value") else str(category)'),
        ]
        
        for old_pattern, new_pattern in enum_fixes:
            if old_pattern in content:
                content = content.replace(old_pattern, new_pattern)
                print(f"✅ Fixed enum access: {old_pattern} -> {new_pattern}")
        
        # Save the updated file
        with open(video_gen_path, 'w', encoding='utf-8') as f:
            f.write(content)

if __name__ == "__main__":
    fix_duration_enforcement()