#!/bin/bash

# ============================================================================
# PTSD Educational Film: Four IDF Soldiers - October 7th Aftermath
# 2-minute animation in Waltz with Bashir style
# ============================================================================

echo "🎬 PTSD Education Film: Four Soldiers, Eight Scenes"
echo "===================================================="
echo "Duration: 120 seconds (8 scenes × 15 seconds)"
echo "Style: Waltz with Bashir rotoscoped animation"
echo ""

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ============================================================================
# CHARACTER DEFINITIONS (for consistency across all scenes)
# ============================================================================
# David: 25, combat infantry, short dark hair, athletic, clean-shaven
# Yael: 30, female medic, brown hair tied back, medical insignia
# Moshe: 35, tank commander, beard, stocky, black beret
# Eli: 55, military rabbi, grey beard, kippah, glasses
# ============================================================================

echo -e "${YELLOW}Starting scene generation...${NC}\n"

# ============================================================================
# SCENE 1: October 7th - The Day That Changed Everything
# ============================================================================
echo -e "${GREEN}[1/8] Generating Scene 1: October 7th Combat${NC}"
python main.py generate \
  --mission "Rotoscoped animation, Waltz with Bashir style: Split screen showing four IDF soldiers during October 7th combat. Top-left: David, 25-year-old combat infantry soldier with short dark hair and athletic build, moving through smoke-filled kibbutz. Top-right: Yael, 30-year-old female medic with tied brown hair, treating wounded under fire. Bottom-left: Moshe, 35-year-old bearded tank commander in black beret, inside tank turret scanning horizon. Bottom-right: Rabbi Eli, 55-year-old military chaplain with grey beard and kippah, kneeling beside covered bodies. Muted colors, documentary realism, sounds of distant explosions." \
  --duration 15 \
  --no-cheap \
  --platform youtube \
  --category Educational \
  --style "Waltz with Bashir rotoscoped war documentary" \
  --visual-style "muted earth tones, rotoscoped animation, split-screen quadrants, realistic military uniforms, documentary cinematography" \
  --veo-model-order veo3 \
  --session-id ptsd_4soldiers_scene1_oct7 \
  --therapeutic-mode

sleep 2

# ============================================================================
# SCENE 2: David's Office - Hypervigilance at Work
# ============================================================================
echo -e "${GREEN}[2/8] Generating Scene 2: David's Office Flashback${NC}"
python main.py generate \
  --mission "Rotoscoped animation continuation: David (same 25-year-old from scene 1, short dark hair, now in civilian clothes - white shirt and jeans) sits at modern office desk typing. Sudden printer jam BANG sound. His eyes dilate, shoulders tense. Seamless transition - the office walls dissolve into smoke, computer screen becomes rifle scope view, coworkers blur into combat soldiers. His breathing accelerates, hands shake over keyboard. Muted blue-grey office colors shift to desert browns during flashback. Return to office as he grips desk edge." \
  --duration 15 \
  --no-cheap \
  --platform youtube \
  --category Educational \
  --style "Waltz with Bashir psychological animation" \
  --visual-style "seamless morphing between office and battlefield, hypervigilant eye movements, rotoscoped realistic motion, muted color transitions" \
  --veo-model-order veo3 \
  --session-id ptsd_4soldiers_scene2_david_office \
  --therapeutic-mode

sleep 2

# ============================================================================
# SCENE 3: Yael's Home - Emotional Numbness with Children
# ============================================================================
echo -e "${GREEN}[3/8] Generating Scene 3: Yael's Emotional Numbness${NC}"
python main.py generate \
  --mission "Rotoscoped animation continuation: Yael (same 30-year-old from scene 1, brown hair now loose, wearing casual clothes) sits on living room couch watching her two young children play with toys on carpet. Her face is expressionless, eyes vacant. Children laugh and show her drawings but she stares through them. Flashback overlay - transparent images of wounded soldiers she treated fade in and out over the domestic scene. Her hands rest limply, no response to child tugging her sleeve. Muted home colors, warm yellows dampened to greys. Silent tears without emotion." \
  --duration 15 \
  --no-cheap \
  --platform youtube \
  --category Educational \
  --style "Waltz with Bashir emotional documentary" \
  --visual-style "emotional disconnect visualization, transparent trauma overlays, rotoscoped children movements, desaturated domestic colors" \
  --veo-model-order veo3 \
  --session-id ptsd_4soldiers_scene3_yael_home \
  --therapeutic-mode

sleep 2

# ============================================================================
# SCENE 4: Moshe's Car - Panic Attack While Driving
# ============================================================================
echo -e "${GREEN}[4/8] Generating Scene 4: Moshe's Highway Panic${NC}"
python main.py generate \
  --mission "Rotoscoped animation continuation: Moshe (same 35-year-old from scene 1, beard, stocky build, now in civilian clothes) driving on busy highway. Hands grip steering wheel, knuckles white. Truck passes with loud honk - trigger. His vision tunnels, dashboard morphs into tank controls. Highway becomes Gaza corridor, cars transform into military vehicles. Breathing rapid, chest heaving. Pulls over to highway shoulder, head on steering wheel. Other cars pass by normally while his reality fractures. Muted colors with red warning flashes during panic peak." \
  --duration 15 \
  --no-cheap \
  --platform youtube \
  --category Educational \
  --style "Waltz with Bashir psychological thriller animation" \
  --visual-style "tunnel vision effect, morphing reality and memory, rotoscoped heavy breathing, shifting between highway and combat zone" \
  --veo-model-order veo3 \
  --session-id ptsd_4soldiers_scene4_moshe_driving \
  --therapeutic-mode

sleep 2

# ============================================================================
# SCENE 5: Eli's Market - Avoidance and Nightmares
# ============================================================================
echo -e "${GREEN}[5/8] Generating Scene 5: Rabbi Eli's Avoidance${NC}"
python main.py generate \
  --mission "Rotoscoped animation continuation: Rabbi Eli (same 55-year-old from scene 1, grey beard, kippah, glasses, civilian clothes with small religious symbols) approaches crowded outdoor market. Sees crowd, stops abruptly. Flash of memory - rows of covered bodies he identified. Crowd faces momentarily become those of the deceased. He turns away, walks empty side street instead. Brief nightmare flash - sorting personal effects, dog tags, prayer over remains. Returns to present, alone on quiet street, touching mezuzah on doorpost for comfort. Muted browns and greys, market colors drain during flashback." \
  --duration 15 \
  --no-cheap \
  --platform youtube \
  --category Educational \
  --style "Waltz with Bashir somber documentary animation" \
  --visual-style "crowd avoidance visualization, ghostly memory overlays, rotoscoped religious gestures, isolation in frame composition" \
  --veo-model-order veo3 \
  --session-id ptsd_4soldiers_scene5_eli_market \
  --therapeutic-mode

sleep 2

# ============================================================================
# SCENE 6: Interwoven Struggles - Peak Symptoms
# ============================================================================
echo -e "${GREEN}[6/8] Generating Scene 6: Interwoven Struggles${NC}"
python main.py generate \
  --mission "Rotoscoped animation montage: Rapid intercuts between all four soldiers at their worst moments. David hyperventilating at office desk. Yael sitting alone in dark while children sleep. Moshe parked on highway shoulder, hazard lights blinking. Eli standing at synagogue entrance, unable to enter. Each shot 2-3 seconds, increasingly rapid cuts. Their breathing synchronizes despite being in different locations. All four check phones showing same time: 3:00 PM. Muted colors at maximum desaturation, documentary style, handheld camera feel." \
  --duration 15 \
  --no-cheap \
  --platform youtube \
  --category Educational \
  --style "Waltz with Bashir crisis montage animation" \
  --visual-style "rapid cutting rhythm, synchronized breathing animation, rotoscoped isolation, darkest color palette moment" \
  --veo-model-order veo3 \
  --session-id ptsd_4soldiers_scene6_interweave \
  --therapeutic-mode

sleep 2

# ============================================================================
# SCENE 7: Convergence - Arriving at Therapy
# ============================================================================
echo -e "${GREEN}[7/8] Generating Scene 7: Convergence at Therapy Center${NC}"
python main.py generate \
  --mission "Rotoscoped animation: Four separate shots converging. David exits his car at medical building parking lot. Yael walks up steps holding appointment card. Moshe sits in lobby checking in at reception. Eli enters through glass doors with Hebrew sign 'Mental Health Center'. Each recognizes others from service - subtle nods of acknowledgment. No words needed, shared understanding in their eyes. Building is modern, clean lines, plants in lobby. First hints of warmer colors beginning to appear - subtle yellows in lighting. Documentary framing, respectful distance." \
  --duration 15 \
  --no-cheap \
  --platform youtube \
  --category Educational \
  --style "Waltz with Bashir documentary realism" \
  --visual-style "convergent paths visualization, recognition moments, rotoscoped subtle gestures, gradually warming color palette" \
  --veo-model-order veo3 \
  --session-id ptsd_4soldiers_scene7_convergence \
  --therapeutic-mode

sleep 2

# ============================================================================
# SCENE 8: Group Therapy - First Steps to Healing
# ============================================================================
echo -e "${GREEN}[8/8] Generating Scene 8: Group Therapy Session${NC}"
python main.py generate \
  --mission "Rotoscoped animation finale: Therapy room with circle of chairs. David, Yael, Moshe, and Eli sit with therapist and two other veterans. Warm but still muted lighting, plants by window, tissues on side table. Eli speaks first, others listen with understanding nods. Yael's rigid posture slightly softens. David's leg stops bouncing. Moshe unclenches his hands. Not cured but beginning. Final shot pulls back through window showing therapy building with subtitle 'Healing begins with seeking help'. Colors gain 20% more saturation, hope without false promises." \
  --duration 15 \
  --no-cheap \
  --platform youtube \
  --category Educational \
  --style "Waltz with Bashir hopeful documentary" \
  --visual-style "circular composition, gradual body language relaxation, rotoscoped therapeutic environment, subtle color restoration" \
  --veo-model-order veo3 \
  --session-id ptsd_4soldiers_scene8_therapy \
  --therapeutic-mode

echo ""
echo -e "${GREEN}✅ All 8 scenes generated successfully!${NC}"
echo ""
echo "📁 Output locations:"
echo "  Scene 1 (Oct 7):     outputs/ptsd_4soldiers_scene1_oct7/"
echo "  Scene 2 (David):     outputs/ptsd_4soldiers_scene2_david_office/"
echo "  Scene 3 (Yael):      outputs/ptsd_4soldiers_scene3_yael_home/"
echo "  Scene 4 (Moshe):     outputs/ptsd_4soldiers_scene4_moshe_driving/"
echo "  Scene 5 (Eli):       outputs/ptsd_4soldiers_scene5_eli_market/"
echo "  Scene 6 (Interweave):outputs/ptsd_4soldiers_scene6_interweave/"
echo "  Scene 7 (Converge):  outputs/ptsd_4soldiers_scene7_convergence/"
echo "  Scene 8 (Therapy):   outputs/ptsd_4soldiers_scene8_therapy/"
echo ""
echo "🎬 Next steps:"
echo "1. Review each scene for character consistency"
echo "2. Generate Hebrew narration for each character"
echo "3. Combine all scenes into final 2-minute film"
echo "4. Add Hebrew narration with English subtitles"
echo ""
echo -e "${YELLOW}Note: Each scene explicitly describes the characters to maintain visual consistency${NC}"