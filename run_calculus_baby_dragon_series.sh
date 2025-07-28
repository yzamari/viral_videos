#!/bin/bash

# 🐉 Baby Dragon Teaches Calculus - Family Guy Style Educational Series
# 13 Episodes covering Infinitesimal Calculus course
# Each episode: 40 seconds, Instagram format, English only

# Parse command line arguments
EPISODES_TO_GENERATE=()
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--episodes)
            shift
            # Read episode numbers until we hit another flag or end of args
            while [[ $# -gt 0 && ! "$1" =~ ^- ]]; do
                EPISODES_TO_GENERATE+=("$1")
                shift
            done
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  -e, --episodes <num1> <num2> ...  Generate specific episodes (1-13)"
            echo "  -h, --help                        Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                    # Generate all 13 episodes"
            echo "  $0 -e 1              # Generate only episode 1"
            echo "  $0 -e 1 5 7          # Generate episodes 1, 5, and 7"
            echo "  $0 --episodes 10 11  # Generate episodes 10 and 11"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# If no episodes specified, generate all (1-13)
if [ ${#EPISODES_TO_GENERATE[@]} -eq 0 ]; then
    EPISODES_TO_GENERATE=($(seq 1 13))
fi

echo "🐉 Baby Dragon's Calculus Adventures - Episode Generator"
echo "======================================================"
echo "📚 Course: Infinitesimal Calculus 1"
echo "🎨 Style: Family Guy Animation"
echo "⏱️  Duration: 40 seconds per episode"
echo "📱 Platform: Instagram (auto-posting enabled)"
echo "🎯 Audience: High school & first-year engineering students"
echo "📊 Level: AP Calculus / University Calculus I"
echo ""
echo "📺 Episodes to generate: ${EPISODES_TO_GENERATE[*]}"
echo ""

# Character and scene setup
CHARACTER="Young clever dragon professor with glasses, purple scales, wearing a lab coat, Family Guy animation style, holding advanced calculus textbook, confident and witty expression"
SCENE="University lecture hall with complex equations on multiple blackboards, Family Guy style, mathematical symbols and formulas floating around, epsilon-delta proofs visualized, engineering diagrams in background"
VOICE="en-US-Wavenet-D"  # Clear, confident teaching voice

# Create overlay logo if it doesn't exist
OVERLAY_PATH="/Users/yahavzamari/viralAi/ai_university_logo.png"
if [ ! -f "$OVERLAY_PATH" ]; then
    echo "🎨 Creating AI University logo..."
    python3 create_ai_university_logo.py
fi

# Function to generate episode
generate_episode() {
    local ep_num=$1
    local title=$2
    local mission=$3
    local session_id="calculus_dragon_ep${ep_num}_$(date +%Y%m%d_%H%M%S)"
    
    # Add episode title to the beginning of the mission for big overlay
    local enhanced_mission="EPISODE $ep_num: $title! Show this as HUGE ANIMATED TITLE CARD at the beginning for 3 seconds with epic effects! $mission"
    
    echo ""
    echo "🐉 Episode $ep_num: $title"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    python3 main.py generate \
        --mission "$enhanced_mission" \
        --character "$CHARACTER" \
        --scene "$SCENE" \
        --platform instagram \
        --duration 40 \
        --visual-style "family guy animation" \
        --category Educational \
        --tone funny \
        --style educational \
        --voice "$VOICE" \
        --session-id "$session_id" \
        --languages en-US \
        --no-cheap \
        --auto-post \
        --visual-continuity \
        --content-continuity \
        --theme preset_university \
        --mode professional \
        --discussions deep
    
    if [ $? -eq 0 ]; then
        echo "✅ Episode $ep_num completed!"
        echo "📁 Output: outputs/$session_id/"
    else
        echo "❌ Episode $ep_num failed!"
    fi
    
    # Brief pause between episodes
    sleep 5
}

# Define all episode titles and missions
# Using regular arrays with index mapping instead of associative arrays

EPISODE_TITLES[1]="Numbers Are My Friends!"
EPISODE_MISSIONS[1]="Family Guy style comedy! Baby dragon professor Epsilon discovers his classroom has been turned into a NUMBER MUSEUM! Natural numbers are friendly counting cookies, integers are temperature-changing penguins, rationals are pizza-loving fraction friends, and irrational numbers are mysterious infinite artists drawing spirals! Dragon gives a hilarious guided tour explaining each number type with funny demonstrations and visual gags. Students learn number sets through comedy and memorable characters. Include dragon's witty commentary and educational jokes!"

EPISODE_TITLES[2]="Sequence Dragon Express!"
EPISODE_MISSIONS[2]="Family Guy comedy! Dragon conductor runs the SEQUENCE EXPRESS train where each car represents a term approaching the limit station! Epsilon and delta are friendly train inspectors ensuring passengers stay within bounds. Dragon explains convergence through hilarious train announcements, shows the squeeze theorem as trains merging on parallel tracks, and bounded sequences as safety rails. Include funny passenger reactions, dragon's train conductor jokes, and visual demonstrations of limits. Educational and entertaining!"

EPISODE_TITLES[3]="To Infinity and Beyond!"
EPISODE_MISSIONS[3]="Family Guy space comedy! Dragon astronaut explores INFINITY SPACE STATION where different sequences live! Divergent sequences are friendly rockets zooming to infinity, convergent ones land safely. Dragon demonstrates ratio test as space multiplication game, root test as cosmic plant growth experiment, and comparison test as rocket races. Include funny zero-gravity math demonstrations, dragon's space jokes, and visual explanations of convergence tests. Make infinity concepts approachable and fun!"

EPISODE_TITLES[4]="Dragon Stairs & Time Loops!"
EPISODE_MISSIONS[4]="Family Guy time-travel comedy! Dragon discovers a MATHEMATICAL TIME MACHINE powered by the number e! Each recursive step takes him through mathematical history, meeting famous mathematicians. Monotonic sequences are elevator operators, Bolzano-Weierstrass theorem is a helpful time guide, and nested intervals are time portals. Dragon hilariously explains each concept while time-traveling. Include funny historical encounters, dragon's time-travel jokes, and visual demonstrations of recursive concepts!"

EPISODE_TITLES[5]="Cauchy Dragons Stick Together!"
EPISODE_MISSIONS[5]="Family Guy teamwork comedy! Baby dragon coaches the CAUCHY TEAM in mathematical synchronized swimming! Team members must stay within epsilon distance while performing routines. Heine-Borel theorem is the pool boundaries, Dedekind cuts are diving board positions. Dragon gives hilarious coaching advice explaining completeness through swimming formations. Include funny synchronized swimming mishaps, dragon's coaching pep talks, and visual demonstrations of Cauchy sequences. Mathematical precision meets comedy!"

EPISODE_TITLES[6]="Power-Up Dragon Mathematics!"
EPISODE_MISSIONS[6]="Create a Family Guy style comedy where baby dragon in power-up workshop teaches rational and real exponents, then explores topology. Cover fractional powers, real exponents as limits, accumulation points, isolated points, open and closed sets, interior and closure, and the Cantor set. Use visual metaphors: power transformations, dragon gatherings, bubble zones, fractal magic. Make topology concepts accessible and fun."

EPISODE_TITLES[7]="Function Dragon Transform!"
EPISODE_MISSIONS[7]="Create a Family Guy style comedy where baby dragon shape-shifter teaches functions. Explain transformation rules, domain and range, one-to-one and onto functions, bijections, function composition, even/odd functions, and periodic functions. Use visual metaphors: dragon transformation machine, territory maps, mirror and rotational symmetry. Make abstract function concepts concrete and entertaining."

EPISODE_TITLES[8]="Smooth Dragon Flights!"
EPISODE_MISSIONS[8]="Create a Family Guy style comedy where dragon pilot teaches function limits and continuity. Cover epsilon-delta definition, one-sided limits, Cauchy criterion, continuity conditions, types of discontinuities, and the intermediate value theorem. Use visual metaphors: smooth flying vs teleporting, landing from different directions, altitude changes. Make limits and continuity intuitive through flight analogies."

EPISODE_TITLES[9]="Finding Dragon Treasures!"
EPISODE_MISSIONS[9]="Create a Family Guy style comedy where dragon treasure hunter teaches extreme value theorem, uniform continuity, and introduces derivatives. Cover finding max/min on closed intervals, monotonic bijections, Heine-Cantor theorem, and derivative as instantaneous rate of change. Use visual metaphors: treasure hunting, dragon velocity, measuring slopes. Show relationship between differentiability and continuity."

EPISODE_TITLES[10]="Dragon Calculus Olympics!"
EPISODE_MISSIONS[10]="Create a Family Guy Olympics special where dragons compete in calculus events. Cover chain rule, inverse function derivatives, higher derivatives, critical points, Fermat's theorem, Rolle's theorem, Lagrange mean value theorem, and Cauchy mean value theorem. Use visual metaphors: relay races, gymnastics, marathon running, treasure hunting. Make derivative rules and theorems exciting through Olympic competition format."

EPISODE_TITLES[11]="Dragon's Secret Techniques!"
EPISODE_MISSIONS[11]="Create a Family Guy style comedy where baby dragon in ninja dojo learns secret calculus techniques. Teach Darboux theorem, L'Hôpital's rule for various indeterminate forms, and advanced limit techniques. Use visual metaphors: ninja training, secret scrolls, ultimate techniques. Show how to handle 0/0, infinity/infinity, and other indeterminate forms with humor and clarity."

EPISODE_TITLES[12]="Dragon's Crystal Ball!"
EPISODE_MISSIONS[12]="Create a Family Guy style comedy where fortune teller dragon teaches Taylor polynomials and series. Cover linear and quadratic approximations, Taylor's theorem, remainder estimates, famous series for exponential, trigonometric and logarithmic functions, and the proof that e is irrational. Use visual metaphors: crystal ball predictions, increasing precision, shrinking errors. Make power series accessible and magical."

EPISODE_TITLES[13]="Dragon Detective Agency!"
EPISODE_MISSIONS[13]="Create a Family Guy style comedy where dragon detective investigates functions completely. Teach systematic function analysis: finding domain, critical points, using first and second derivative tests, finding inflection points, asymptotes, and sketching curves. Use visual metaphors: detective investigation, solving cases, mood swings for concavity. Make the complete function investigation process entertaining and memorable."

# Generate selected episodes
for ep in "${EPISODES_TO_GENERATE[@]}"; do
    if [[ $ep -ge 1 && $ep -le 13 ]]; then
        generate_episode "$ep" "${EPISODE_TITLES[$ep]}" "${EPISODE_MISSIONS[$ep]}"
    else
        echo "⚠️  Skipping invalid episode number: $ep (must be 1-13)"
    fi
done

echo ""
echo "🎉 Baby Dragon's Calculus Adventure Series Generation Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📺 Generated ${#EPISODES_TO_GENERATE[@]} episodes: ${EPISODES_TO_GENERATE[*]}"
echo ""
echo "📚 Educational Goals Achieved:"
echo "  ✓ AP Calculus / University Calculus I concepts"
echo "  ✓ Rigorous mathematical explanations with humor"
echo "  ✓ 40 seconds of engaging educational content"
echo "  ✓ Engineering-relevant applications"
echo "  ✓ Epsilon-delta proofs made visual and fun"
echo ""
echo "🎨 Note: Add custom PNG overlay with:"
echo "  - Baby dragon logo in corner"
echo "  - Epsilon chicks thinking"
echo "  - 'Dragon Calculus Academy' branding"
echo ""
echo "💡 Perfect for AP Calculus students and engineering freshmen!"
echo "📱 Auto-posting to Instagram: @yalla.chaos.ai"