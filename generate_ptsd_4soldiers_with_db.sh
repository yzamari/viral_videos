#!/bin/bash

# ============================================================================
# PTSD Educational Film with Character Database
# Uses persistent character definitions for consistency
# ============================================================================

echo "🎬 PTSD Education Film: Database-Driven Character Generation"
echo "=========================================================="
echo ""

# Step 1: Create/Update characters in database
echo "📝 Step 1: Setting up characters in database..."
python3 create_ptsd_characters.py
if [ $? -ne 0 ]; then
    echo "❌ Failed to create characters. Exiting."
    exit 1
fi
echo ""

# Step 2: List available characters
echo "📋 Step 2: Verifying characters in database..."
python3 main.py list-characters | grep ptsd
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Starting scene generation with character database...${NC}\n"

# ============================================================================
# SCENE GENERATION WITH CHARACTER REFERENCES
# ============================================================================

# Scene 1: October 7th - All Four in Combat
echo -e "${GREEN}[1/8] Scene 1: October 7th Combat - All Characters${NC}"
python3 main.py generate \
  --mission "Rotoscoped Waltz with Bashir animation: October 7th combat. Split screen four quadrants showing character:david_ptsd in top-left clearing rooms, character:yael_ptsd in top-right treating wounded, character:moshe_ptsd in bottom-left commanding tank, character:eli_ptsd in bottom-right with casualty identification. Muted colors, documentary style, authentic IDF uniforms and equipment." \
  --duration 15 \
  --no-cheap \
  --character-refs "david_ptsd,yael_ptsd,moshe_ptsd,eli_ptsd" \
  --platform youtube \
  --style "Waltz with Bashir documentary" \
  --visual-style "rotoscoped animation, split screen, muted palette" \
  --veo-model-order veo3 \
  --session-id ptsd_education_sc1_combat \
  --therapeutic-mode

sleep 3

# Scene 2: David's Hypervigilance
echo -e "${GREEN}[2/8] Scene 2: David's Office Hypervigilance${NC}"
python3 main.py generate \
  --mission "Rotoscoped animation: character:david_ptsd at office desk. Printer suddenly jams with BANG. His hypervigilance triggers - eyes dilate, shoulders tense. Office morphs into combat zone, computer becomes rifle scope. Returns to reality gripping desk. Muted office blues shift to desert browns during flashback." \
  --duration 15 \
  --no-cheap \
  --character-refs "david_ptsd" \
  --platform youtube \
  --style "Waltz with Bashir psychological" \
  --visual-style "seamless reality morphing, rotoscoped anxiety" \
  --veo-model-order veo3 \
  --session-id ptsd_education_sc2_david \
  --therapeutic-mode

sleep 3

# Scene 3: Yael's Emotional Numbness  
echo -e "${GREEN}[3/8] Scene 3: Yael's Emotional Disconnect${NC}"
python3 main.py generate \
  --mission "Rotoscoped animation: character:yael_ptsd on home couch watching her children play. Her face expressionless, emotionally numb. Children show drawings but she stares through them. Transparent overlays of wounded soldiers she treated. No response to child tugging sleeve. Muted home colors, silent tears without emotion." \
  --duration 15 \
  --no-cheap \
  --character-refs "yael_ptsd" \
  --platform youtube \
  --style "Waltz with Bashir emotional documentary" \
  --visual-style "emotional numbness visualization, trauma overlays" \
  --veo-model-order veo3 \
  --session-id ptsd_education_sc3_yael \
  --therapeutic-mode

sleep 3

# Scene 4: Moshe's Panic Attack
echo -e "${GREEN}[4/8] Scene 4: Moshe's Highway Panic${NC}"
python3 main.py generate \
  --mission "Rotoscoped animation: character:moshe_ptsd driving highway. Truck horn triggers panic attack. White knuckles on wheel, tunnel vision, dashboard morphs to tank controls. Highway becomes Gaza corridor. Pulls over, head on wheel, breathing heavily. Muted colors with red panic flashes." \
  --duration 15 \
  --no-cheap \
  --character-refs "moshe_ptsd" \
  --platform youtube \
  --style "Waltz with Bashir psychological thriller" \
  --visual-style "panic visualization, reality morphing, heavy breathing" \
  --veo-model-order veo3 \
  --session-id ptsd_education_sc4_moshe \
  --therapeutic-mode

sleep 3

# Scene 5: Rabbi Eli's Avoidance
echo -e "${GREEN}[5/8] Scene 5: Rabbi Eli's Market Avoidance${NC}"
python3 main.py generate \
  --mission "Rotoscoped animation: character:eli_ptsd approaching crowded market. Stops seeing crowd. Flash of covered bodies he identified. Crowd faces become the deceased. Turns to empty side street. Touches mezuzah for comfort. Muted browns, colors drain during flashback." \
  --duration 15 \
  --no-cheap \
  --character-refs "eli_ptsd" \
  --platform youtube \
  --style "Waltz with Bashir somber documentary" \
  --visual-style "avoidance behavior, ghostly overlays, religious comfort" \
  --veo-model-order veo3 \
  --session-id ptsd_education_sc5_eli \
  --therapeutic-mode

sleep 3

# Scene 6: Interwoven Struggles
echo -e "${GREEN}[6/8] Scene 6: All Four at Breaking Point${NC}"
python3 main.py generate \
  --mission "Rotoscoped montage: Rapid cuts between character:david_ptsd hyperventilating at desk, character:yael_ptsd alone in dark, character:moshe_ptsd on highway shoulder, character:eli_ptsd unable to enter synagogue. 2-3 second cuts, synchronized breathing. All check phones: 3:00 PM. Maximum color desaturation." \
  --duration 15 \
  --no-cheap \
  --character-refs "david_ptsd,yael_ptsd,moshe_ptsd,eli_ptsd" \
  --platform youtube \
  --style "Waltz with Bashir crisis montage" \
  --visual-style "rapid cutting, synchronized suffering, darkest palette" \
  --veo-model-order veo3 \
  --session-id ptsd_education_sc6_interweave \
  --therapeutic-mode

sleep 3

# Scene 7: Convergence at Therapy
echo -e "${GREEN}[7/8] Scene 7: Meeting at Therapy Center${NC}"
python3 main.py generate \
  --mission "Rotoscoped animation: character:david_ptsd exits car at medical building. character:yael_ptsd walks up steps. character:moshe_ptsd in lobby. character:eli_ptsd enters through doors with Hebrew 'Mental Health Center' sign. Recognition nods between them. Subtle warm yellows appearing in lighting." \
  --duration 15 \
  --no-cheap \
  --character-refs "david_ptsd,yael_ptsd,moshe_ptsd,eli_ptsd" \
  --platform youtube \
  --style "Waltz with Bashir documentary" \
  --visual-style "convergent paths, recognition, warming colors" \
  --veo-model-order veo3 \
  --session-id ptsd_education_sc7_convergence \
  --therapeutic-mode

sleep 3

# Scene 8: Group Therapy Hope
echo -e "${GREEN}[8/8] Scene 8: Group Therapy Session${NC}"
python3 main.py generate \
  --mission "Rotoscoped finale: Therapy room circle with character:david_ptsd, character:yael_ptsd, character:moshe_ptsd, character:eli_ptsd plus therapist and two other veterans. Warm muted lighting. Eli speaks first, others listen. Yael softens slightly. David's leg stops bouncing. Moshe unclenches hands. Not cured but beginning. Colors gain 20% saturation. End text: 'Healing begins with seeking help'." \
  --duration 15 \
  --no-cheap \
  --character-refs "david_ptsd,yael_ptsd,moshe_ptsd,eli_ptsd" \
  --platform youtube \
  --style "Waltz with Bashir hopeful documentary" \
  --visual-style "circular composition, gradual relaxation, subtle hope" \
  --veo-model-order veo3 \
  --session-id ptsd_education_sc8_therapy \
  --therapeutic-mode

echo ""
echo -e "${GREEN}✅ All 8 scenes generated with consistent characters!${NC}"
echo ""
echo "📁 Output Locations:"
echo "  Scene 1: outputs/ptsd_education_sc1_combat/"
echo "  Scene 2: outputs/ptsd_education_sc2_david/"
echo "  Scene 3: outputs/ptsd_education_sc3_yael/"
echo "  Scene 4: outputs/ptsd_education_sc4_moshe/"
echo "  Scene 5: outputs/ptsd_education_sc5_eli/"
echo "  Scene 6: outputs/ptsd_education_sc6_interweave/"
echo "  Scene 7: outputs/ptsd_education_sc7_convergence/"
echo "  Scene 8: outputs/ptsd_education_sc8_therapy/"
echo ""
echo "🎬 Next Steps:"
echo "1. Combine all scenes: python3 combine_scenes.py"
echo "2. Add Hebrew narration with character voices"
echo "3. Add English subtitles"
echo "4. Final color grading and export"
echo ""
echo -e "${YELLOW}Character database ensures visual consistency across all scenes!${NC}"