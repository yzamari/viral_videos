#!/bin/bash

# ============================================================================
# Test Script for New Generate-Series Command
# Shows the power of narrative orchestration
# ============================================================================

echo "🎬 Testing Narrative Series Generation System"
echo "============================================="
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# ============================================================================
# TEST 1: DRY RUN - PTSD Education Film
# ============================================================================
echo -e "${MAGENTA}TEST 1: PTSD Education Film (Dry Run)${NC}"
echo -e "${MAGENTA}--------------------------------------${NC}"
echo "This creates a narrative plan without generating videos"
echo ""

python3 main.py generate-series \
    --narrative "2-minute PTSD education film showing 4 IDF soldiers (ages 25-55) with different symptoms: hypervigilance, emotional numbing, panic attacks, and avoidance. Shows their October 7th experience, individual struggles in civilian life, and convergence at therapy for hope." \
    --duration 120 \
    --characters 4 \
    --structure educational \
    --style "Waltz with Bashir rotoscoped animation" \
    --visual-style "muted colors, documentary realism" \
    --platform youtube \
    --session-id ptsd_education_test \
    --dry-run

echo ""
echo -e "${GREEN}✅ Dry run complete - check narrative plan${NC}"
echo ""

# ============================================================================
# TEST 2: SIMPLE NARRATIVE - 30 Second Story
# ============================================================================
echo -e "${MAGENTA}TEST 2: Simple 30-Second Story${NC}"
echo -e "${MAGENTA}-------------------------------${NC}"
echo "Quick test with single character"
echo ""

# Uncomment to run actual generation
# python3 main.py generate-series \
#     --narrative "A day in the life of a startup founder facing challenges and finding success" \
#     --duration 30 \
#     --characters 1 \
#     --structure three_act \
#     --style "modern documentary" \
#     --visual-style "clean minimalist" \
#     --session-id startup_story_test \
#     --no-cheap

echo "Skipped (uncomment to run)"
echo ""

# ============================================================================
# TEST 3: USING EXISTING CHARACTERS
# ============================================================================
echo -e "${MAGENTA}TEST 3: Using Character Database${NC}"
echo -e "${MAGENTA}---------------------------------${NC}"
echo "Using pre-created PTSD characters from database"
echo ""

# First ensure characters exist
echo "Creating characters if needed..."
python3 -c "
from src.characters.character_database import get_character_database
db = get_character_database()
chars = db.list_characters(tags=['ptsd'])
if chars:
    print(f'Found {len(chars)} PTSD characters in database')
    for c in chars[:4]:
        print(f'  - {c.name}: {c.display_name} ({c.age}, {c.profession})')
else:
    print('No PTSD characters found - run create_ptsd_characters.py first')
"

echo ""

# Uncomment to run with existing characters
# python3 main.py generate-series \
#     --narrative "Follow-up therapy session showing progress of PTSD recovery" \
#     --duration 60 \
#     --character-ids "david_ptsd,yael_ptsd,moshe_ptsd,eli_ptsd" \
#     --structure circular \
#     --style "Waltz with Bashir animation" \
#     --therapeutic-mode \
#     --session-id therapy_progress_test

echo "Skipped (uncomment to run with characters)"
echo ""

# ============================================================================
# COMPARISON WITH OLD METHOD
# ============================================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}COMPARISON: Old vs New Method${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${YELLOW}OLD METHOD (Manual Shell Script):${NC}"
echo "  • Write 900+ line shell script"
echo "  • Manually plan 8 scenes"
echo "  • Manually describe each character in every scene"
echo "  • Run 8 separate generation commands"
echo "  • Hope for consistency"
echo "  • Manually combine videos"
echo "  Time: Hours of scripting + generation"
echo ""

echo -e "${GREEN}NEW METHOD (Narrative Orchestrator):${NC}"
echo "  • Single command with narrative description"
echo "  • AI automatically plans scenes"
echo "  • Character database maintains consistency"
echo "  • Parallel generation of all scenes"
echo "  • Automatic narrative coherence"
echo "  • Auto-combines final video"
echo "  Time: One command, automatic execution"
echo ""

# ============================================================================
# AVAILABLE STRUCTURES
# ============================================================================
echo -e "${BLUE}Available Narrative Structures:${NC}"
echo "  • three_act    - Classic beginning, middle, end"
echo "  • five_act     - Shakespearean structure"
echo "  • heros_journey - Campbell's monomyth"
echo "  • parallel     - Multiple parallel stories"
echo "  • circular     - Ends where it begins"
echo "  • educational  - Problem, examples, solution"
echo "  • documentary  - Chronological real events"
echo ""

# ============================================================================
# EXAMPLE COMMANDS
# ============================================================================
echo -e "${BLUE}Example Commands:${NC}"
echo ""

echo "1. Corporate Training Video:"
echo "   python3 main.py generate-series \\"
echo "     --narrative \"Team building workshop showing collaboration\" \\"
echo "     --duration 180 --characters 5 --structure parallel"
echo ""

echo "2. Historical Documentary:"
echo "   python3 main.py generate-series \\"
echo "     --narrative \"The rise of artificial intelligence from 1950-2024\" \\"
echo "     --duration 300 --structure documentary --scenes 10"
echo ""

echo "3. Hero's Journey:"
echo "   python3 main.py generate-series \\"
echo "     --narrative \"Young entrepreneur's journey to unicorn startup\" \\"
echo "     --duration 240 --structure heros_journey"
echo ""

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Narrative Orchestration System Ready!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "The app now intelligently handles:"
echo "  • Multi-scene narratives"
echo "  • Character arcs"
echo "  • Story structure"
echo "  • Automatic decomposition"
echo "  • Parallel generation"
echo "  • Final assembly"
echo ""
echo "What used to require complex scripting is now a single command!"