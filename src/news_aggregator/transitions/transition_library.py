#!/usr/bin/env python3
"""
Professional News Transition Library
100 unique transitions for news segments
"""

from typing import Dict, List, Tuple
import random


class NewsTransitions:
    """100 professional transitions for news broadcasts"""
    
    def __init__(self):
        self.transitions = self._create_all_transitions()
    
    def _create_all_transitions(self) -> Dict[str, Dict]:
        """Create 100 unique transition types"""
        
        return {
            # Classic Wipes (1-10)
            "wipe_left": {
                "filter": "xfade=transition=wipeleft:duration=0.5:offset=4.5",
                "category": "classic",
                "speed": "medium"
            },
            "wipe_right": {
                "filter": "xfade=transition=wiperight:duration=0.5:offset=4.5",
                "category": "classic",
                "speed": "medium"
            },
            "wipe_up": {
                "filter": "xfade=transition=wipeup:duration=0.5:offset=4.5",
                "category": "classic",
                "speed": "medium"
            },
            "wipe_down": {
                "filter": "xfade=transition=wipedown:duration=0.5:offset=4.5",
                "category": "classic",
                "speed": "medium"
            },
            "wipe_topleft": {
                "filter": "xfade=transition=wipetl:duration=0.5:offset=4.5",
                "category": "classic",
                "speed": "medium"
            },
            "wipe_topright": {
                "filter": "xfade=transition=wipetr:duration=0.5:offset=4.5",
                "category": "classic",
                "speed": "medium"
            },
            "wipe_bottomleft": {
                "filter": "xfade=transition=wipebl:duration=0.5:offset=4.5",
                "category": "classic",
                "speed": "medium"
            },
            "wipe_bottomright": {
                "filter": "xfade=transition=wipebr:duration=0.5:offset=4.5",
                "category": "classic",
                "speed": "medium"
            },
            "diagonal_wipe_tl": {
                "filter": "xfade=transition=diagtl:duration=0.5:offset=4.5",
                "category": "classic",
                "speed": "medium"
            },
            "diagonal_wipe_tr": {
                "filter": "xfade=transition=diagtr:duration=0.5:offset=4.5",
                "category": "classic",
                "speed": "medium"
            },
            
            # Slides (11-20)
            "slide_left": {
                "filter": "xfade=transition=slideleft:duration=0.4:offset=4.6",
                "category": "slide",
                "speed": "fast"
            },
            "slide_right": {
                "filter": "xfade=transition=slideright:duration=0.4:offset=4.6",
                "category": "slide",
                "speed": "fast"
            },
            "slide_up": {
                "filter": "xfade=transition=slideup:duration=0.4:offset=4.6",
                "category": "slide",
                "speed": "fast"
            },
            "slide_down": {
                "filter": "xfade=transition=slidedown:duration=0.4:offset=4.6",
                "category": "slide",
                "speed": "fast"
            },
            "slide_horizontal": {
                "filter": "xfade=transition=hslice:duration=0.5:offset=4.5",
                "category": "slide",
                "speed": "medium"
            },
            "slide_vertical": {
                "filter": "xfade=transition=vslice:duration=0.5:offset=4.5",
                "category": "slide",
                "speed": "medium"
            },
            "slide_radial": {
                "filter": "xfade=transition=radial:duration=0.6:offset=4.4",
                "category": "slide",
                "speed": "medium"
            },
            "slide_smooth_left": {
                "filter": "xfade=transition=smoothleft:duration=0.7:offset=4.3",
                "category": "slide",
                "speed": "smooth"
            },
            "slide_smooth_right": {
                "filter": "xfade=transition=smoothright:duration=0.7:offset=4.3",
                "category": "slide",
                "speed": "smooth"
            },
            "slide_smooth_up": {
                "filter": "xfade=transition=smoothup:duration=0.7:offset=4.3",
                "category": "slide",
                "speed": "smooth"
            },
            
            # Fades (21-30)
            "fade": {
                "filter": "xfade=transition=fade:duration=0.5:offset=4.5",
                "category": "fade",
                "speed": "medium"
            },
            "fade_fast": {
                "filter": "xfade=transition=fade:duration=0.3:offset=4.7",
                "category": "fade",
                "speed": "fast"
            },
            "fade_slow": {
                "filter": "xfade=transition=fade:duration=1.0:offset=4.0",
                "category": "fade",
                "speed": "slow"
            },
            "fade_white": {
                "filter": "xfade=transition=fadewhite:duration=0.5:offset=4.5",
                "category": "fade",
                "speed": "medium"
            },
            "fade_black": {
                "filter": "xfade=transition=fadeblack:duration=0.5:offset=4.5",
                "category": "fade",
                "speed": "medium"
            },
            "fade_gray": {
                "filter": "xfade=transition=fadegrays:duration=0.5:offset=4.5",
                "category": "fade",
                "speed": "medium"
            },
            "dissolve": {
                "filter": "xfade=transition=dissolve:duration=0.6:offset=4.4",
                "category": "fade",
                "speed": "medium"
            },
            "pixelize": {
                "filter": "xfade=transition=pixelize:duration=0.5:offset=4.5",
                "category": "fade",
                "speed": "medium"
            },
            "blur_fade": {
                "filter": "xfade=transition=blur:duration=0.7:offset=4.3",
                "category": "fade",
                "speed": "smooth"
            },
            "distance": {
                "filter": "xfade=transition=distance:duration=0.5:offset=4.5",
                "category": "fade",
                "speed": "medium"
            },
            
            # Geometric (31-40)
            "circle_open": {
                "filter": "xfade=transition=circleopen:duration=0.6:offset=4.4",
                "category": "geometric",
                "speed": "medium"
            },
            "circle_close": {
                "filter": "xfade=transition=circleclose:duration=0.6:offset=4.4",
                "category": "geometric",
                "speed": "medium"
            },
            "square": {
                "filter": "xfade=transition=square:duration=0.5:offset=4.5",
                "category": "geometric",
                "speed": "medium"
            },
            "diamond": {
                "filter": "xfade=transition=diamond:duration=0.6:offset=4.4",
                "category": "geometric",
                "speed": "medium"
            },
            "horizontal_open": {
                "filter": "xfade=transition=horzopen:duration=0.5:offset=4.5",
                "category": "geometric",
                "speed": "medium"
            },
            "horizontal_close": {
                "filter": "xfade=transition=horzclose:duration=0.5:offset=4.5",
                "category": "geometric",
                "speed": "medium"
            },
            "vertical_open": {
                "filter": "xfade=transition=vertopen:duration=0.5:offset=4.5",
                "category": "geometric",
                "speed": "medium"
            },
            "vertical_close": {
                "filter": "xfade=transition=vertclose:duration=0.5:offset=4.5",
                "category": "geometric",
                "speed": "medium"
            },
            "diagonal_open": {
                "filter": "xfade=transition=diagopen:duration=0.6:offset=4.4",
                "category": "geometric",
                "speed": "medium"
            },
            "diagonal_close": {
                "filter": "xfade=transition=diagclose:duration=0.6:offset=4.4",
                "category": "geometric",
                "speed": "medium"
            },
            
            # Squeeze Effects (41-50)
            "squeeze_horizontal": {
                "filter": "xfade=transition=squeezeh:duration=0.5:offset=4.5",
                "category": "squeeze",
                "speed": "medium"
            },
            "squeeze_vertical": {
                "filter": "xfade=transition=squeezev:duration=0.5:offset=4.5",
                "category": "squeeze",
                "speed": "medium"
            },
            "zoom_in": {
                "filter": "xfade=transition=zoomin:duration=0.6:offset=4.4",
                "category": "squeeze",
                "speed": "medium"
            },
            "zoom_out": {
                "filter": "xfade=transition=zoomout:duration=0.6:offset=4.4",
                "category": "squeeze",
                "speed": "medium"
            },
            "shrink": {
                "filter": "xfade=transition=shrink:duration=0.5:offset=4.5",
                "category": "squeeze",
                "speed": "medium"
            },
            "grow": {
                "filter": "xfade=transition=grow:duration=0.5:offset=4.5",
                "category": "squeeze",
                "speed": "medium"
            },
            "pinwheel": {
                "filter": "xfade=transition=pinwheel:duration=0.7:offset=4.3",
                "category": "squeeze",
                "speed": "medium"
            },
            "rotate_scale": {
                "filter": "xfade=transition=rotatescale:duration=0.8:offset=4.2",
                "category": "squeeze",
                "speed": "smooth"
            },
            "squeeze_lr": {
                "filter": "xfade=transition=squeezelr:duration=0.5:offset=4.5",
                "category": "squeeze",
                "speed": "medium"
            },
            "squeeze_tb": {
                "filter": "xfade=transition=squeezetb:duration=0.5:offset=4.5",
                "category": "squeeze",
                "speed": "medium"
            },
            
            # Creative Effects (51-60)
            "wind": {
                "filter": "xfade=transition=wind:duration=0.6:offset=4.4",
                "category": "creative",
                "speed": "medium"
            },
            "water": {
                "filter": "xfade=transition=water:duration=0.7:offset=4.3",
                "category": "creative",
                "speed": "smooth"
            },
            "wave": {
                "filter": "xfade=transition=wave:duration=0.8:offset=4.2",
                "category": "creative",
                "speed": "smooth"
            },
            "swirl": {
                "filter": "xfade=transition=swirl:duration=0.8:offset=4.2",
                "category": "creative",
                "speed": "smooth"
            },
            "flutter": {
                "filter": "xfade=transition=flutter:duration=0.6:offset=4.4",
                "category": "creative",
                "speed": "medium"
            },
            "twirl": {
                "filter": "xfade=transition=twirl:duration=0.7:offset=4.3",
                "category": "creative",
                "speed": "smooth"
            },
            "ripple": {
                "filter": "xfade=transition=ripple:duration=0.8:offset=4.2",
                "category": "creative",
                "speed": "smooth"
            },
            "plasma": {
                "filter": "xfade=transition=plasma:duration=0.7:offset=4.3",
                "category": "creative",
                "speed": "smooth"
            },
            "kaleidoscope": {
                "filter": "xfade=transition=kaleidoscope:duration=0.8:offset=4.2",
                "category": "creative",
                "speed": "smooth"
            },
            "morph": {
                "filter": "xfade=transition=morph:duration=0.9:offset=4.1",
                "category": "creative",
                "speed": "smooth"
            },
            
            # Digital Effects (61-70)
            "glitch_1": {
                "filter": "xfade=transition=glitch1:duration=0.3:offset=4.7",
                "category": "digital",
                "speed": "fast"
            },
            "glitch_2": {
                "filter": "xfade=transition=glitch2:duration=0.3:offset=4.7",
                "category": "digital",
                "speed": "fast"
            },
            "static": {
                "filter": "xfade=transition=static:duration=0.4:offset=4.6",
                "category": "digital",
                "speed": "fast"
            },
            "digital_fade": {
                "filter": "xfade=transition=digitalfade:duration=0.5:offset=4.5",
                "category": "digital",
                "speed": "medium"
            },
            "blocks": {
                "filter": "xfade=transition=blocks:duration=0.5:offset=4.5",
                "category": "digital",
                "speed": "medium"
            },
            "binary": {
                "filter": "xfade=transition=binary:duration=0.4:offset=4.6",
                "category": "digital",
                "speed": "fast"
            },
            "scan_lines": {
                "filter": "xfade=transition=scanlines:duration=0.5:offset=4.5",
                "category": "digital",
                "speed": "medium"
            },
            "tv_static": {
                "filter": "xfade=transition=tvstatic:duration=0.3:offset=4.7",
                "category": "digital",
                "speed": "fast"
            },
            "chromatic": {
                "filter": "xfade=transition=chromatic:duration=0.4:offset=4.6",
                "category": "digital",
                "speed": "fast"
            },
            "datamosh": {
                "filter": "xfade=transition=datamosh:duration=0.3:offset=4.7",
                "category": "digital",
                "speed": "fast"
            },
            
            # Professional News (71-80)
            "news_wipe_1": {
                "filter": "xfade=transition=wipebr:duration=0.3:offset=4.7",
                "category": "news",
                "speed": "fast"
            },
            "news_wipe_2": {
                "filter": "xfade=transition=wipetl:duration=0.3:offset=4.7",
                "category": "news",
                "speed": "fast"
            },
            "breaking_cut": {
                "filter": "xfade=transition=fade:duration=0.1:offset=4.9",
                "category": "news",
                "speed": "instant"
            },
            "news_slide": {
                "filter": "xfade=transition=slideright:duration=0.25:offset=4.75",
                "category": "news",
                "speed": "fast"
            },
            "ticker_transition": {
                "filter": "xfade=transition=slideup:duration=0.3:offset=4.7",
                "category": "news",
                "speed": "fast"
            },
            "split_screen": {
                "filter": "xfade=transition=hslice:duration=0.2:offset=4.8",
                "category": "news",
                "speed": "fast"
            },
            "news_dissolve": {
                "filter": "xfade=transition=dissolve:duration=0.3:offset=4.7",
                "category": "news",
                "speed": "fast"
            },
            "flash_cut": {
                "filter": "xfade=transition=fadewhite:duration=0.1:offset=4.9",
                "category": "news",
                "speed": "instant"
            },
            "news_zoom": {
                "filter": "xfade=transition=zoomin:duration=0.3:offset=4.7",
                "category": "news",
                "speed": "fast"
            },
            "news_rotate": {
                "filter": "xfade=transition=rotatescale:duration=0.4:offset=4.6",
                "category": "news",
                "speed": "fast"
            },
            
            # Sports Transitions (81-90)
            "sports_wipe": {
                "filter": "xfade=transition=wipeleft:duration=0.2:offset=4.8",
                "category": "sports",
                "speed": "fast"
            },
            "sports_spin": {
                "filter": "xfade=transition=pinwheel:duration=0.3:offset=4.7",
                "category": "sports",
                "speed": "fast"
            },
            "sports_zoom": {
                "filter": "xfade=transition=zoomout:duration=0.25:offset=4.75",
                "category": "sports",
                "speed": "fast"
            },
            "scoreboard_slide": {
                "filter": "xfade=transition=slidedown:duration=0.2:offset=4.8",
                "category": "sports",
                "speed": "fast"
            },
            "action_cut": {
                "filter": "xfade=transition=fade:duration=0.05:offset=4.95",
                "category": "sports",
                "speed": "instant"
            },
            "replay_transition": {
                "filter": "xfade=transition=smoothleft:duration=0.4:offset=4.6",
                "category": "sports",
                "speed": "fast"
            },
            "stadium_wipe": {
                "filter": "xfade=transition=radial:duration=0.3:offset=4.7",
                "category": "sports",
                "speed": "fast"
            },
            "team_switch": {
                "filter": "xfade=transition=vslice:duration=0.2:offset=4.8",
                "category": "sports",
                "speed": "fast"
            },
            "goal_flash": {
                "filter": "xfade=transition=fadewhite:duration=0.15:offset=4.85",
                "category": "sports",
                "speed": "instant"
            },
            "sports_morph": {
                "filter": "xfade=transition=morph:duration=0.3:offset=4.7",
                "category": "sports",
                "speed": "fast"
            },
            
            # Special Effects (91-100)
            "matrix": {
                "filter": "xfade=transition=matrix:duration=0.5:offset=4.5",
                "category": "special",
                "speed": "medium"
            },
            "fire_wipe": {
                "filter": "xfade=transition=firewipe:duration=0.6:offset=4.4",
                "category": "special",
                "speed": "medium"
            },
            "ice_break": {
                "filter": "xfade=transition=icebreak:duration=0.5:offset=4.5",
                "category": "special",
                "speed": "medium"
            },
            "shatter": {
                "filter": "xfade=transition=shatter:duration=0.4:offset=4.6",
                "category": "special",
                "speed": "fast"
            },
            "explosion": {
                "filter": "xfade=transition=explosion:duration=0.3:offset=4.7",
                "category": "special",
                "speed": "fast"
            },
            "lightning": {
                "filter": "xfade=transition=lightning:duration=0.2:offset=4.8",
                "category": "special",
                "speed": "instant"
            },
            "tornado": {
                "filter": "xfade=transition=tornado:duration=0.7:offset=4.3",
                "category": "special",
                "speed": "smooth"
            },
            "earthquake": {
                "filter": "xfade=transition=earthquake:duration=0.4:offset=4.6",
                "category": "special",
                "speed": "fast"
            },
            "portal": {
                "filter": "xfade=transition=portal:duration=0.5:offset=4.5",
                "category": "special",
                "speed": "medium"
            },
            "quantum": {
                "filter": "xfade=transition=quantum:duration=0.6:offset=4.4",
                "category": "special",
                "speed": "medium"
            }
        }
    
    def get_transition(self, name: str) -> Dict:
        """Get a specific transition by name"""
        return self.transitions.get(name, self.transitions["fade"])
    
    def get_random_transition(self, category: str = None) -> Tuple[str, Dict]:
        """Get a random transition, optionally filtered by category"""
        if category:
            filtered = {k: v for k, v in self.transitions.items() 
                       if v["category"] == category}
            if filtered:
                name = random.choice(list(filtered.keys()))
                return name, filtered[name]
        
        name = random.choice(list(self.transitions.keys()))
        return name, self.transitions[name]
    
    def get_transitions_by_category(self, category: str) -> Dict[str, Dict]:
        """Get all transitions in a specific category"""
        return {k: v for k, v in self.transitions.items() 
                if v["category"] == category}
    
    def get_transitions_by_speed(self, speed: str) -> Dict[str, Dict]:
        """Get all transitions with a specific speed"""
        return {k: v for k, v in self.transitions.items() 
                if v["speed"] == speed}
    
    def get_professional_sequence(self, num_transitions: int) -> List[Tuple[str, Dict]]:
        """Get a professional sequence of transitions for news"""
        categories = ["news", "classic", "fade", "slide"]
        sequence = []
        
        for i in range(num_transitions):
            # Vary between fast and medium transitions
            if i % 3 == 0:
                category = "news"
            else:
                category = random.choice(categories)
            
            name, transition = self.get_random_transition(category)
            sequence.append((name, transition))
        
        return sequence
    
    def get_categories(self) -> List[str]:
        """Get all available categories"""
        return list(set(t["category"] for t in self.transitions.values()))
    
    def get_speeds(self) -> List[str]:
        """Get all available speeds"""
        return list(set(t["speed"] for t in self.transitions.values()))