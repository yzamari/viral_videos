#!/usr/bin/env python3
"""Test character extraction from mission text."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.generators.video_generator import VideoGenerator

# Test the character extraction
test_missions = [
    "David Ben-Gurion (with his iconic white Einstein-like hair, round face, and distinctive appearance of the real historical figure) rises from desert",
    "Meeting with Golda Meir - elderly woman with gray hair pulled back, stern expression",
    "Benjamin Netanyahu: man with gray hair and strong jawline speaks at podium",
    "Yitzhak Rabin (middle-aged, receding hairline, serious military look) signs peace accord",
    "Shimon Peres looks distinguished with white hair and warm smile"
]

# Create a minimal video generator instance
vg = VideoGenerator(None, None, None, None, None, None, None)

print("Testing character extraction:\n")
for mission in test_missions:
    print(f"Mission: {mission[:80]}...")
    descriptions = vg._extract_character_descriptions_from_mission(mission)
    print(f"Extracted: {descriptions}")
    print("-" * 80)