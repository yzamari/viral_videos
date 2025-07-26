#!/usr/bin/env python3
"""
Create Marvel-style overlay with Israeli flag for the PM series
"""

import json
from pathlib import Path

# Marvel color scheme
MARVEL_RED = "#ED1D24"
MARVEL_BLUE = "#0476F2"
MARVEL_YELLOW = "#FFD700"
MARVEL_WHITE = "#FFFFFF"
MARVEL_BLACK = "#000000"

def create_marvel_overlay_config():
    """Create Marvel-style overlay configuration"""
    
    overlay_config = {
        "style": "marvel_comics",
        "elements": [
            # Israeli flag in top-left
            {
                "type": "flag",
                "country": "israel",
                "position": {
                    "x": 20,
                    "y": 20
                },
                "size": {
                    "width": 60,
                    "height": 40
                },
                "opacity": 0.9,
                "animation": "fade_in"
            },
            # Marvel-style comic frame
            {
                "type": "frame",
                "style": "comic_book",
                "border_width": 8,
                "colors": {
                    "primary": MARVEL_RED,
                    "secondary": MARVEL_YELLOW,
                    "accent": MARVEL_BLUE
                },
                "effects": [
                    "halftone_dots",
                    "comic_lines"
                ]
            },
            # Episode title banner
            {
                "type": "banner",
                "position": "top",
                "height": 80,
                "background": {
                    "type": "gradient",
                    "colors": [MARVEL_RED, MARVEL_BLACK],
                    "direction": "horizontal"
                },
                "text": {
                    "font": "comic_sans_bold",
                    "size": 36,
                    "color": MARVEL_YELLOW,
                    "outline": {
                        "color": MARVEL_BLACK,
                        "width": 3
                    },
                    "effects": ["comic_shadow", "3d_effect"]
                }
            },
            # Comic speech bubbles for dialogue
            {
                "type": "speech_bubble",
                "style": "marvel",
                "background": MARVEL_WHITE,
                "border": {
                    "color": MARVEL_BLACK,
                    "width": 3
                },
                "tail": {
                    "style": "pointed",
                    "position": "auto"
                },
                "text": {
                    "font": "comic_sans",
                    "color": MARVEL_BLACK,
                    "size": 24,
                    "max_width": 300
                }
            },
            # Action words (POW!, BAM!, etc.)
            {
                "type": "action_text",
                "style": "marvel_impact",
                "colors": {
                    "fill": MARVEL_YELLOW,
                    "outline": MARVEL_RED,
                    "shadow": MARVEL_BLACK
                },
                "effects": [
                    "explosion_burst",
                    "motion_blur",
                    "comic_shake"
                ],
                "font": {
                    "family": "impact_bold",
                    "size": 72,
                    "weight": "black"
                }
            },
            # Character name plates
            {
                "type": "nameplate",
                "position": "bottom_third",
                "style": "marvel_hero",
                "background": {
                    "type": "hexagon",
                    "color": MARVEL_BLUE,
                    "border": MARVEL_YELLOW,
                    "border_width": 4
                },
                "text": {
                    "font": "marvel_font",
                    "color": MARVEL_WHITE,
                    "size": 28,
                    "effects": ["metallic_shine"]
                }
            },
            # Marvel logo watermark
            {
                "type": "watermark",
                "image": "marvel_style_logo",
                "position": {
                    "x": -20,
                    "y": -20
                },
                "anchor": "bottom_right",
                "size": {
                    "width": 100,
                    "height": 40
                },
                "opacity": 0.7
            }
        ],
        "transitions": {
            "page_turn": {
                "duration": 0.5,
                "style": "comic_book_flip"
            },
            "panel_slide": {
                "duration": 0.3,
                "style": "comic_panel_wipe"
            },
            "action_burst": {
                "duration": 0.2,
                "style": "explosion_transition"
            }
        },
        "effects": {
            "global": [
                "comic_book_texture",
                "halftone_background",
                "vintage_paper"
            ],
            "action_scenes": [
                "speed_lines",
                "impact_burst",
                "screen_shake"
            ]
        }
    }
    
    return overlay_config

def save_overlay_config(output_path="marvel_overlay_config.json"):
    """Save the overlay configuration to a JSON file"""
    config = create_marvel_overlay_config()
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Marvel overlay configuration saved to: {output_path}")
    return output_path

if __name__ == "__main__":
    save_overlay_config()