#!/bin/bash

# 🐉 Baby Dragon Teaches Calculus - Family Guy Style Educational Series
# 13 Episodes covering Infinitesimal Calculus course
# Each episode: 63-64 seconds, Instagram format, English only

echo "🐉 Baby Dragon's Calculus Adventures - Episode Generator"
echo "======================================================"
echo "📚 Course: Infinitesimal Calculus 1"
echo "🎨 Style: Family Guy Animation"
echo "⏱️  Duration: 63-64 seconds per episode"
echo "📱 Platform: Instagram"
echo "🎯 Goal: Understand concepts in 50 seconds + fun!"
echo ""

# Character and scene setup
CHARACTER="Baby dragon with big cute eyes, chubby cheeks, tiny wings, purple scales, wearing tiny glasses, Family Guy animation style, holding a tiny calculus book"
SCENE="Animated classroom with chalkboard, Family Guy style, colorful math symbols floating around, epsilon chicks (ε) thinking in the background"
VOICE="en-US-Wavenet-C"  # Friendly, youthful voice

# Function to generate episode
generate_episode() {
    local ep_num=$1
    local title=$2
    local mission=$3
    local session_id="calculus_dragon_ep${ep_num}_$(date +%Y%m%d_%H%M%S)"
    
    echo ""
    echo "🐉 Episode $ep_num: $title"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    python3 main.py generate \
        --mission "$mission" \
        --character "$CHARACTER" \
        --scene "$SCENE" \
        --platform instagram \
        --duration 63 \
        --visual-style "family guy animation" \
        --category Educational \
        --tone funny \
        --style educational \
        --voice "$VOICE" \
        --session-id "$session_id" \
        --languages en-US \
        --no-cheap
    
    if [ $? -eq 0 ]; then
        echo "✅ Episode $ep_num completed!"
        echo "📁 Output: outputs/$session_id/"
    else
        echo "❌ Episode $ep_num failed!"
    fi
    
    # Brief pause between episodes
    sleep 5
}

# Episode 1: Introduction to Numbers
generate_episode 1 \
    "Numbers Are My Friends!" \
    "Family Guy cutaway: Baby dragon discovers number sets! 'Hey kids, I'm Epsilon the Dragon!' POOF! Natural numbers appear as counting cookies. 'But wait!' Integers show up with negative temperatures. WHOOSH! Rational numbers as pizza slices. 'Mind blown!' Irrational numbers as infinite dragons. Real numbers form a beautiful number line. Absolute value is like dragon hugs - always positive! Intervals are dragon nap zones. Bounded sets are like dragon cages. Supremum is the tallest dragon! Completeness means no gaps in our number line! Epsilon chicks chirp: 'ε > 0!'"

# Episode 2: Sequences - The Dragon Train
generate_episode 2 \
    "Sequence Dragon Express!" \
    "Family Guy style: Baby dragon conductor on number train! 'All aboard the Sequence Express!' Each car is a term: a₁, a₂, a₃... CHOO CHOO! 'Where we going?' TO THE LIMIT! Train approaches station L. 'Convergence means getting closer!' Epsilon tunnel - we get within ε of L! Unique limit theorem: 'Only ONE destination!' Bounded sequences stay on track. Arithmetic of limits: 'Add, multiply, it all works!' Sandwich theorem: Dragon sandwich with sequences! Epsilon chicks form convergent sequence!"

# Episode 3: More Limits & Infinity
generate_episode 3 \
    "To Infinity and Beyond!" \
    "Baby dragon with rocket pack! 'Let's explore crazy limits!' nth root of constant: Dragon shrinking spell! nth root of n approaches 1: 'Magic stabilization!' ZOOM to infinity! 'Some sequences go FOREVER!' Divergence in extended sense. Ratio test: 'Compare neighbors!' Root test with dragon plants growing. 'If ratio < 1, we converge!' Epsilon chicks multiply rapidly showing divergence. 'Remember: limits help us understand the infinite!'"

# Episode 4: Monotonic Sequences & Recursion
generate_episode 4 \
    "Dragon Stairs & Time Loops!" \
    "Family Guy cutaway: Baby dragon climbing infinite staircase! 'Monotonic means always up or always down!' Bounded + monotonic = convergent! 'No falling off!' Recursive sequences: Dragon caught in time loop! 'Next term depends on previous!' Finding limits of recursive sequences. The number e appears: 'Natural dragon growth!' Cantor's lemma: Nested dragon boxes! Subsequences are dragon cousins. Bolzano-Weierstrass: 'Every bounded sequence has a convergent cousin!'"

# Episode 5: Cauchy & Advanced Concepts
generate_episode 5 \
    "Cauchy Dragons Stick Together!" \
    "Baby dragon army marching! 'Cauchy sequences get closer to EACH OTHER!' Not just to a limit - to themselves! Upper and lower limits: 'Highest and lowest dragon flights!' Heine-Borel: Dragon blanket covers everything! 'Finite covers for compact sets!' Building real numbers: Dragon construction site! Dedekind cuts slice number line. Cauchy completion fills all gaps. Epsilon chicks form Cauchy sequence, getting closer!"

# Episode 6: Powers & Topology Treats
generate_episode 6 \
    "Power-Up Dragon Mathematics!" \
    "Family Guy style: Baby dragon discovers power-ups! 'Rational powers are like partial transformations!' 2^(1/2) is half-dragon mode! Real powers: 'Any number can be an exponent!' Topology adventure begins! Accumulation points where dragons gather. Isolated points are lonely dragons. Open sets: Dragon playgrounds! Closed sets: Dragon fortresses! Interior is inside the castle. Cantor set: Dragon fractal magic! Epsilon chicks demonstrate open balls!"

# Episode 7: Functions - Dragon Transformations
generate_episode 7 \
    "Function Dragon Transform!" \
    "Baby dragon shape-shifter! 'Functions transform inputs to outputs!' Domain is where dragon lives. Range is where dragon can go! One-to-one: 'Each input gets unique output!' Onto: 'Hit every target!' Composition: Dragon combos! 'f∘g means g first, then f!' Even/odd functions: Dragon symmetry! Periodic: Dragon on repeat! Limits at infinity match sequence limits. Epsilon chicks show function mapping!"

# Episode 8: Function Limits & Continuity
generate_episode 8 \
    "Smooth Dragon Flights!" \
    "Family Guy cutaway: Dragon learning to fly smoothly! 'Limits at points - approaching carefully!' One-sided limits: Left and right dragon approaches! Cauchy criterion for functions. CONTINUITY: 'No teleporting!' Small input change = small output change. Continuous functions are smooth flights! Arithmetic preserves continuity. Composition too! Discontinuities: Dragon hiccups! Removable, jump, or essential. Intermediate Value: 'Hit every height while flying!'"

# Episode 9: Extreme Dragon Values
generate_episode 9 \
    "Finding Dragon Treasures!" \
    "Baby dragon treasure hunter! 'Weierstrass says: Continuous on closed interval finds max treasure!' Monotonic + continuous = bijection! Uniform continuity: 'Same ε works everywhere!' Cantor-Heine theorem proves it! Derivatives: Dragon velocity! 'Instantaneous rate of change!' Physical: speed; Geometric: slope! Differentiable implies continuous. 'Smooth flying needs continuity!' Chain rule: Dragon relay race! Epsilon chicks measure rates!"

# Episode 10: Derivative Dragon Olympics
generate_episode 10 \
    "Dragon Calculus Olympics!" \
    "Family Guy sports special! Chain rule relay: 'Pass the derivative!' Inverse function gymnastics: 'Flip and derive!' Higher derivatives: Dragon acceleration, jerk, snap! Critical points: Dragon rest stops! Fermat: 'Local extrema have zero derivative!' Rolle's theorem: Dragon roller coaster! Lagrange MVT: 'Average speed achieved somewhere!' Cauchy's race between functions! Epsilon chicks judge the competition!"

# Episode 11: Advanced Dragon Techniques
generate_episode 11 \
    "Dragon's Secret Techniques!" \
    "Baby dragon ninja training! 'Darboux: Derivatives hit intermediate values!' Even without continuity! L'Hôpital's rule: 'Undefined? Try derivatives!' 0/0 or ∞/∞ battles resolved! Dragon uses secret technique! 'When in doubt, differentiate!' Hospital's rule saves the day repeatedly. Advanced dragon mathematics! Epsilon chicks practice L'Hôpital moves. 'Remember: Calculus has tools for every problem!'"

# Episode 12: Taylor Dragon Approximation
generate_episode 12 \
    "Dragon's Crystal Ball!" \
    "Family Guy fortune teller dragon! 'Taylor polynomials predict function future!' Linear approximation: Baby dragon's first guess. Quadratic: Better dragon prediction! Taylor's theorem: 'nth degree polynomial approximation!' Remainder shrinks as n grows. Little-o notation: 'Faster than dragon sneeze!' Error vanishes near the point. 'e is irrational!' Dragon proof! Epsilon chicks approximate functions!"

# Episode 13: Dragon Function Investigation
generate_episode 13 \
    "Dragon Detective Agency!" \
    "Baby dragon detective with magnifying glass! 'Time to investigate functions!' First derivative test: Going up or down? Second derivative: Dragon smile or frown? Concave up = happy dragon! Concave down = sad dragon. Inflection points: Dragon mood swings! Asymptotes: Dragon cannot reach! Vertical: Wall of infinity! Slant: Dragon slide! 'Every function tells a story!' Epsilon chicks draw function portraits!"

echo ""
echo "🎉 Baby Dragon's Calculus Adventure Series Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📚 Educational Goals Achieved:"
echo "  ✓ 13 weeks of calculus concepts"
echo "  ✓ Family Guy style humor"
echo "  ✓ 50-second concept explanations"
echo "  ✓ Consistent baby dragon character"
echo "  ✓ Epsilon chicks for visual continuity"
echo ""
echo "🎨 Note: Add custom PNG overlay with:"
echo "  - Baby dragon logo in corner"
echo "  - Epsilon chicks thinking"
echo "  - 'Dragon Calculus Academy' branding"
echo ""
echo "💡 Students will love learning calculus with Epsilon the Dragon!"