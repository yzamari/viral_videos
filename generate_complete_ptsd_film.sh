#!/bin/bash

# ============================================================================
# Complete PTSD Educational Film Generator
# Creates characters in database and generates all 8 scenes
# 2-minute film about 4 IDF soldiers with PTSD after October 7th
# ============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ============================================================================
# HEADER
# ============================================================================
clear
echo -e "${MAGENTA}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${MAGENTA}║     🎬 PTSD EDUCATION FILM - COMPLETE GENERATOR 🎬           ║${NC}"
echo -e "${MAGENTA}║                                                              ║${NC}"
echo -e "${MAGENTA}║  Four IDF Soldiers: October 7th Trauma & Recovery Journey   ║${NC}"
echo -e "${MAGENTA}║  Duration: 2 minutes | Style: Waltz with Bashir Animation   ║${NC}"
echo -e "${MAGENTA}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ============================================================================
# STEP 1: CREATE CHARACTERS IN DATABASE
# ============================================================================
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}STEP 1: CHARACTER DATABASE SETUP${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Create the character creation Python script inline
cat > /tmp/create_ptsd_characters_temp.py << 'PYTHON_SCRIPT'
#!/usr/bin/env python3
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, '/Users/yahavzamari/viralAi')

from src.characters.character_database import get_character_database
from src.characters.character_model import Character

def create_ptsd_characters():
    """Create the four PTSD education characters"""
    
    db = get_character_database()
    
    # Character 1: David - Combat Infantry
    david = Character(
        name="david_ptsd",
        display_name="David",
        age=25,
        profession="IDF Combat Infantry (Reserve)",
        personality="Pre-trauma: confident, athletic, social. Post-trauma: hypervigilant, anxious, startles easily",
        visual_description="Young athletic male, short dark hair, clean-shaven, tanned skin. Military: combat vest, infantry insignia. Civilian: white office shirt, jeans",
        voice_style="Young adult male, Hebrew accent, tense when triggered, breathing quickens during flashbacks",
        speaking_style="Short sentences, sometimes trails off mid-thought, avoids war topics",
        tags=["ptsd", "october7", "combat", "hypervigilance", "israeli"],
        expertise_areas=["combat", "office work", "PTSD symptoms"],
        catchphrases=["I'm fine, really", "Just need a moment", "It's nothing"],
        energy_level="high_anxiety",
        language_preferences=["Hebrew", "English"],
        voice_provider="google",
        voice_id="he-IL-Wavenet-D"
    )
    
    # Character 2: Yael - Medical Corps
    yael = Character(
        name="yael_ptsd", 
        display_name="Yael",
        age=30,
        profession="IDF Medical Corps (Reserve)",
        personality="Pre-trauma: caring, empathetic, warm mother. Post-trauma: emotionally numb, disconnected, guilt",
        visual_description="Female, brown hair usually tied back, medical corps insignia. Civilian: casual mom clothes, tired eyes, forced smile",
        voice_style="Female, Hebrew accent, monotone when numb, occasional breaking voice",
        speaking_style="Mechanical responses, delayed reactions, apologizes frequently",
        tags=["ptsd", "october7", "medic", "emotional_numbing", "israeli", "mother"],
        expertise_areas=["medical", "trauma care", "parenting struggles"],
        catchphrases=["I should feel something", "They needed me more", "I'm sorry, what did you say?"],
        energy_level="low",
        language_preferences=["Hebrew", "English"],
        voice_provider="google",
        voice_id="he-IL-Wavenet-A"
    )
    
    # Character 3: Moshe - Tank Commander  
    moshe = Character(
        name="moshe_ptsd",
        display_name="Moshe",
        age=35,
        profession="IDF Armored Corps Tank Commander (Reserve)",
        personality="Pre-trauma: decisive leader, protective, strategic. Post-trauma: panic attacks, loss of control, avoids driving",
        visual_description="Male, beard, stocky build, black tank corps beret. Civilian: polo shirt, visible tension in shoulders",
        voice_style="Male, deeper voice, Hebrew accent, breathing becomes rapid during panic",
        speaking_style="Used to give orders, now uncertain, counts to calm himself",
        tags=["ptsd", "october7", "tank", "panic_attacks", "israeli"],
        expertise_areas=["armored warfare", "leadership", "panic management"],
        catchphrases=["I can't breathe", "Pull over, pull over", "One, two, three, four..."],
        energy_level="volatile",
        language_preferences=["Hebrew", "English"],
        voice_provider="google",
        voice_id="he-IL-Wavenet-B"
    )
    
    # Character 4: Rabbi Eli - Military Rabbinate
    eli = Character(
        name="eli_ptsd",
        display_name="Rabbi Eli",
        age=55,
        profession="IDF Military Rabbinate - Casualty Identification (Reserve)",
        personality="Pre-trauma: spiritual, comforting, wise. Post-trauma: haunted, avoids crowds, questioning faith",
        visual_description="Male, grey beard, kippah, glasses, rabbi insignia. Civilian: black kippah, white shirt, tzitzit visible",
        voice_style="Older male, Hebrew accent, sometimes whispers prayers, voice cracks with emotion",
        speaking_style="Quotes scripture for comfort, long pauses, sometimes can't finish sentences",
        tags=["ptsd", "october7", "rabbi", "nightmares", "israeli", "religious"],
        expertise_areas=["Jewish law", "casualty identification", "spiritual counseling"],
        catchphrases=["Baruch Dayan HaEmet", "Their faces... I see their faces", "HaShem, give me strength"],
        energy_level="subdued",
        language_preferences=["Hebrew", "English", "Aramaic"],
        voice_provider="google",
        voice_id="he-IL-Wavenet-C"
    )
    
    # Create all characters
    characters = [david, yael, moshe, eli]
    created = []
    
    for char in characters:
        try:
            existing = db.get_character(char.name)
            if existing:
                print(f"  ⚠️  {char.display_name} already exists, updating...")
                db.update_character(char.name, char.to_dict())
            else:
                db.create_character(char)
                print(f"  ✅ Created: {char.display_name} ({char.age}, {char.profession})")
            created.append(char.name)
        except Exception as e:
            print(f"  ❌ Error with {char.display_name}: {e}")
    
    # Create group reference
    group_data = {
        "group_name": "ptsd_october7_soldiers",
        "description": "Four IDF soldiers for PTSD education film",
        "characters": created,
        "scene_consistency": {
            "animation_style": "Waltz with Bashir rotoscoped",
            "color_palette": "muted earth tones",
            "setting": "Israel post-October 7th"
        }
    }
    
    group_file = Path("data/characters/groups/ptsd_october7.json")
    group_file.parent.mkdir(parents=True, exist_ok=True)
    with open(group_file, 'w') as f:
        json.dump(group_data, f, indent=2)
    
    return created

if __name__ == "__main__":
    character_ids = create_ptsd_characters()
    print(f"\n  📋 Character IDs ready: {', '.join(character_ids)}")
PYTHON_SCRIPT

# Run character creation
echo -e "${YELLOW}Creating characters in database...${NC}"
python3 /tmp/create_ptsd_characters_temp.py
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to create characters. Exiting.${NC}"
    exit 1
fi

# Verify characters exist
echo -e "\n${YELLOW}Verifying characters...${NC}"
python3 main.py list-characters 2>/dev/null | grep -E "(david_ptsd|yael_ptsd|moshe_ptsd|eli_ptsd)" | head -4
echo ""

# ============================================================================
# STEP 2: GENERATE ALL 8 SCENES
# ============================================================================
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}STEP 2: SCENE GENERATION (8 × 15 seconds = 2 minutes)${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Progress tracking
TOTAL_SCENES=8
CURRENT_SCENE=0

# Function to update progress bar
show_progress() {
    CURRENT_SCENE=$1
    PERCENT=$((CURRENT_SCENE * 100 / TOTAL_SCENES))
    FILLED=$((PERCENT / 5))
    EMPTY=$((20 - FILLED))
    
    printf "\r  Progress: ["
    printf "%${FILLED}s" | tr ' ' '█'
    printf "%${EMPTY}s" | tr ' ' '░'
    printf "] %d%% (%d/8 scenes)" $PERCENT $CURRENT_SCENE
}

# Scene 1: October 7th Combat
echo -e "\n${GREEN}🎬 Scene 1/8: October 7th - The Day${NC}"
show_progress 0
python3 main.py generate \
  --mission "Rotoscoped Waltz with Bashir animation: October 7th combat. Split screen four quadrants showing character:david_ptsd in top-left clearing rooms, character:yael_ptsd in top-right treating wounded, character:moshe_ptsd in bottom-left commanding tank, character:eli_ptsd in bottom-right with casualty identification. Muted colors, documentary style." \
  --duration 15 \
  --no-cheap \
  --character-refs "david_ptsd,yael_ptsd,moshe_ptsd,eli_ptsd" \
  --platform youtube \
  --style "Waltz with Bashir documentary" \
  --visual-style "rotoscoped animation, split screen, muted palette" \
  --veo-model-order veo3 \
  --session-id ptsd_film_sc1_combat \
  --therapeutic-mode \
  2>/dev/null
show_progress 1
echo -e " ✓"

# Scene 2: David's Office
echo -e "\n${GREEN}🎬 Scene 2/8: David - Hypervigilance at Work${NC}"
python3 main.py generate \
  --mission "Rotoscoped: character:david_ptsd at office. Printer BANG triggers hypervigilance. Office morphs to combat zone. Returns gripping desk. Blues shift to desert browns in flashback." \
  --duration 15 \
  --no-cheap \
  --character-refs "david_ptsd" \
  --platform youtube \
  --style "Waltz with Bashir psychological" \
  --visual-style "seamless reality morphing, rotoscoped anxiety" \
  --veo-model-order veo3 \
  --session-id ptsd_film_sc2_david \
  --therapeutic-mode \
  2>/dev/null
show_progress 2
echo -e " ✓"

# Scene 3: Yael's Home
echo -e "\n${GREEN}🎬 Scene 3/8: Yael - Emotional Numbness${NC}"
python3 main.py generate \
  --mission "Rotoscoped: character:yael_ptsd watching children play, emotionally numb. Transparent overlays of wounded. No response to child. Muted colors, silent tears." \
  --duration 15 \
  --no-cheap \
  --character-refs "yael_ptsd" \
  --platform youtube \
  --style "Waltz with Bashir emotional" \
  --visual-style "emotional disconnect, trauma overlays" \
  --veo-model-order veo3 \
  --session-id ptsd_film_sc3_yael \
  --therapeutic-mode \
  2>/dev/null
show_progress 3
echo -e " ✓"

# Scene 4: Moshe's Car
echo -e "\n${GREEN}🎬 Scene 4/8: Moshe - Highway Panic Attack${NC}"
python3 main.py generate \
  --mission "Rotoscoped: character:moshe_ptsd driving. Truck horn triggers panic. Dashboard becomes tank controls. Highway morphs to Gaza. Pulls over breathing heavily." \
  --duration 15 \
  --no-cheap \
  --character-refs "moshe_ptsd" \
  --platform youtube \
  --style "Waltz with Bashir thriller" \
  --visual-style "panic visualization, reality morphing" \
  --veo-model-order veo3 \
  --session-id ptsd_film_sc4_moshe \
  --therapeutic-mode \
  2>/dev/null
show_progress 4
echo -e " ✓"

# Scene 5: Rabbi Eli's Market
echo -e "\n${GREEN}🎬 Scene 5/8: Rabbi Eli - Avoidance${NC}"
python3 main.py generate \
  --mission "Rotoscoped: character:eli_ptsd avoiding crowded market. Sees covered bodies in crowd faces. Takes empty street, touches mezuzah. Muted browns." \
  --duration 15 \
  --no-cheap \
  --character-refs "eli_ptsd" \
  --platform youtube \
  --style "Waltz with Bashir somber" \
  --visual-style "avoidance behavior, ghostly overlays" \
  --veo-model-order veo3 \
  --session-id ptsd_film_sc5_eli \
  --therapeutic-mode \
  2>/dev/null
show_progress 5
echo -e " ✓"

# Scene 6: Interwoven Crisis
echo -e "\n${GREEN}🎬 Scene 6/8: All Four - Peak Crisis${NC}"
python3 main.py generate \
  --mission "Rotoscoped montage: Rapid cuts between all four characters at worst moments. character:david_ptsd hyperventilating, character:yael_ptsd alone dark, character:moshe_ptsd highway shoulder, character:eli_ptsd unable enter synagogue. Synchronized breathing." \
  --duration 15 \
  --no-cheap \
  --character-refs "david_ptsd,yael_ptsd,moshe_ptsd,eli_ptsd" \
  --platform youtube \
  --style "Waltz with Bashir crisis" \
  --visual-style "rapid cutting, synchronized suffering" \
  --veo-model-order veo3 \
  --session-id ptsd_film_sc6_crisis \
  --therapeutic-mode \
  2>/dev/null
show_progress 6
echo -e " ✓"

# Scene 7: Arriving at Therapy
echo -e "\n${GREEN}🎬 Scene 7/8: Convergence - Therapy Center${NC}"
python3 main.py generate \
  --mission "Rotoscoped: All four arriving at Mental Health Center. character:david_ptsd exits car, character:yael_ptsd climbs steps, character:moshe_ptsd in lobby, character:eli_ptsd enters. Recognition nods. Subtle warm yellows appear." \
  --duration 15 \
  --no-cheap \
  --character-refs "david_ptsd,yael_ptsd,moshe_ptsd,eli_ptsd" \
  --platform youtube \
  --style "Waltz with Bashir documentary" \
  --visual-style "convergent paths, warming colors" \
  --veo-model-order veo3 \
  --session-id ptsd_film_sc7_arrival \
  --therapeutic-mode \
  2>/dev/null
show_progress 7
echo -e " ✓"

# Scene 8: Group Therapy
echo -e "\n${GREEN}🎬 Scene 8/8: Group Therapy - Hope${NC}"
python3 main.py generate \
  --mission "Rotoscoped finale: Therapy circle with all four characters. character:eli_ptsd speaks, others listen. character:yael_ptsd softens, character:david_ptsd stops bouncing, character:moshe_ptsd unclenches. Colors gain warmth. Text: 'Healing begins with seeking help'." \
  --duration 15 \
  --no-cheap \
  --character-refs "david_ptsd,yael_ptsd,moshe_ptsd,eli_ptsd" \
  --platform youtube \
  --style "Waltz with Bashir hopeful" \
  --visual-style "circular composition, gradual hope" \
  --veo-model-order veo3 \
  --session-id ptsd_film_sc8_therapy \
  --therapeutic-mode \
  2>/dev/null
show_progress 8
echo -e " ✓"

echo -e "\n"

# ============================================================================
# STEP 3: COMBINE SCENES (OPTIONAL)
# ============================================================================
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}STEP 3: FINAL ASSEMBLY${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if combine script exists
if [ -f "combine_scenes.py" ]; then
    echo -e "${YELLOW}Combining all scenes into final film...${NC}"
    python3 combine_scenes.py \
        --scenes outputs/ptsd_film_sc*/final_output/*.mp4 \
        --output outputs/PTSD_Education_Film_Final.mp4 \
        2>/dev/null
    echo -e "${GREEN}✅ Final film created: outputs/PTSD_Education_Film_Final.mp4${NC}"
else
    echo -e "${YELLOW}⚠️  combine_scenes.py not found. Manual combination required.${NC}"
fi

# ============================================================================
# SUMMARY
# ============================================================================
echo ""
echo -e "${MAGENTA}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${MAGENTA}║                    ✅ GENERATION COMPLETE!                   ║${NC}"
echo -e "${MAGENTA}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📁 Individual Scenes:${NC}"
echo "  • Scene 1 (Combat):      outputs/ptsd_film_sc1_combat/"
echo "  • Scene 2 (David):       outputs/ptsd_film_sc2_david/"
echo "  • Scene 3 (Yael):        outputs/ptsd_film_sc3_yael/"
echo "  • Scene 4 (Moshe):       outputs/ptsd_film_sc4_moshe/"
echo "  • Scene 5 (Eli):         outputs/ptsd_film_sc5_eli/"
echo "  • Scene 6 (Crisis):      outputs/ptsd_film_sc6_crisis/"
echo "  • Scene 7 (Arrival):     outputs/ptsd_film_sc7_arrival/"
echo "  • Scene 8 (Therapy):     outputs/ptsd_film_sc8_therapy/"
echo ""
echo -e "${BLUE}👥 Characters Created:${NC}"
echo "  • David (25) - Combat Infantry - Hypervigilance"
echo "  • Yael (30)  - Medical Corps - Emotional Numbness"
echo "  • Moshe (35) - Tank Commander - Panic Attacks"
echo "  • Eli (55)   - Military Rabbi - Avoidance/Nightmares"
echo ""
echo -e "${BLUE}🎬 Next Steps:${NC}"
echo "  1. Review each scene for quality"
echo "  2. Add Hebrew narration (voices configured in DB)"
echo "  3. Add English subtitles"
echo "  4. Share with mental health professionals for review"
echo ""
echo -e "${YELLOW}⚠️  Important: This content is for educational purposes.${NC}"
echo -e "${YELLOW}   Always use with professional mental health supervision.${NC}"
echo ""
echo -e "${GREEN}Total Generation Time: ~5-10 minutes${NC}"
echo -e "${GREEN}Film Duration: 2 minutes (8 × 15 seconds)${NC}"
echo ""

# Clean up temp file
rm -f /tmp/create_ptsd_characters_temp.py

exit 0