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
    "Family Guy cutaway: Baby dragon in magical number land! 'Hey kids, I'm Epsilon the Dragon! Let's explore NUMBER SETS!' POOF! Natural numbers 1,2,3 appear as counting cookies. 'These are for counting dragon treats!' But wait - Zero appears! 'I'm special!' Then negative numbers show up as ice cubes: -1,-2,-3. 'Together we're INTEGERS!' WHOOSH! Fractions fly in as pizza slices: 1/2, 3/4. 'We're RATIONAL numbers - any fraction!' Suddenly, √2 appears as an infinite spiral dragon. 'I'm IRRATIONAL - my decimal never repeats!' Pi flies by leaving infinite trail. Together they form the REAL NUMBER LINE - a beautiful rainbow path! 'ABSOLUTE VALUE |x| measures distance from zero - like dragon hugs, always positive!' Example: |-5| = 5. INTERVALS are dragon territories: [1,3] includes endpoints, (1,3) doesn't! BOUNDED sets have limits - like dragon playpen with walls. SUPREMUM is the smallest upper bound - the ceiling dragons can't pass! Epsilon chicks demonstrate: 'For any ε>0, we can get closer than ε to any real number!'"

# Episode 2: Sequences - The Dragon Train
generate_episode 2 \
    "Sequence Dragon Express!" \
    "Family Guy style: Baby dragon conductor on magical number train! 'All aboard the SEQUENCE EXPRESS!' Each train car shows a term: a₁=1, a₂=1/2, a₃=1/3... CHOO CHOO! 'Watch the pattern - each term follows a rule!' The train heads toward LIMIT STATION at L=0. 'CONVERGENCE means we get closer and closer to L!' Dragon demonstrates: 'Pick ANY tiny distance ε>0.' Magic epsilon tunnel appears! 'After some point N, ALL terms stay within ε of L!' Shows |aₙ-L|<ε visually. 'The UNIQUE LIMIT THEOREM says only ONE destination possible!' Two tracks can't lead to different stations! BOUNDED sequences have safety rails - can't go to infinity. 'If -M ≤ aₙ ≤ M for all n, we're bounded!' ARITHMETIC OF LIMITS: Two trains approaching L and M. 'Their sum approaches L+M!' Product approaches L×M! Dragon makes sequence sandwich: If aₙ ≤ bₙ ≤ cₙ and outer sequences → L, then bₙ → L too! 'SQUEEZE THEOREM!' Epsilon chicks line up showing 1, 1/2, 1/3, 1/4... converging to 0!"

# Episode 3: More Limits & Infinity
generate_episode 3 \
    "To Infinity and Beyond!" \
    "Baby dragon with rocket pack exploring limit mysteries! 'Let's discover SPECIAL LIMITS!' First: ⁿ√c where c>0. Dragon shrinking spell shows c^(1/n) → 1 as n→∞. 'Any positive number's nth root approaches 1!' Next: ⁿ√n seems huge but... 'SURPRISE! It also approaches 1!' Dragon demonstrates with examples: ¹⁰√10 ≈ 1.26, ¹⁰⁰√100 ≈ 1.047. ZOOM! Some sequences blast off to infinity! 'If aₙ → ∞, we say it DIVERGES to infinity!' Not a real limit, but extended sense. RATIO TEST: Dragon compares consecutive terms. 'If |aₙ₊₁/aₙ| → L < 1, sequence → 0!' Example: 2ⁿ/n! has ratio 2/(n+1) → 0. ROOT TEST with growing dragon plants: 'If ⁿ√|aₙ| → L < 1, we converge!' Example: (1/2)ⁿ has root 1/2 < 1. Epsilon chicks demonstrate geometric sequence: 1, 2, 4, 8, 16... 'Ratio = 2 > 1, so we DIVERGE!' Counter-example: 1, 1/2, 1/4, 1/8... 'Ratio = 1/2 < 1, CONVERGES to 0!' Key insight: 'These tests reveal sequence behavior by examining growth rates!'"

# Episode 4: Monotonic Sequences & Recursion
generate_episode 4 \
    "Dragon Stairs & Time Loops!" \
    "Family Guy cutaway: Baby dragon on infinite staircase! 'MONOTONIC sequences go one direction only!' Climbing stairs: a₁ ≤ a₂ ≤ a₃... is INCREASING. Going down: a₁ ≥ a₂ ≥ a₃... is DECREASING. 'The MONOTONIC CONVERGENCE THEOREM is magical!' If stairs go up (increasing) but have a ceiling (bounded above), you MUST stop somewhere! That's the limit! Example: aₙ = 1 - 1/n starts at 0 and climbs toward 1. TIME LOOP! Dragon in RECURSIVE sequence: a₁ = 2, aₙ₊₁ = (aₙ + 4/aₙ)/2. 'Each term uses the previous one!' To find limit L: If aₙ → L, then aₙ₊₁ → L too. So L = (L + 4/L)/2, giving L = 2! The magical number e appears: (1 + 1/n)ⁿ → e ≈ 2.718... 'It's NATURAL GROWTH!' Dragon demonstrates compound interest. NESTED INTERVALS: Dragon boxes getting smaller: [0,1] ⊃ [0.4,0.6] ⊃ [0.49,0.51]... 'They shrink to a single point!' SUBSEQUENCES: Taking every other term, every third... 'They're sequence cousins!' BOLZANO-WEIERSTRASS: 'Any bounded sequence has a convergent subsequence!' Like finding a pattern in chaos! Epsilon chicks show: even in jumpy sequence 1,0,1,0,1,0... the subsequence 0,0,0... converges!"

# Episode 5: Cauchy & Advanced Concepts
generate_episode 5 \
    "Cauchy Dragons Stick Together!" \
    "Baby dragon army in formation! 'CAUCHY sequences are teams that stick together!' After stage N, ALL dragons stay within ε of each other: |aₘ - aₙ| < ε for all m,n > N. 'We don't need to know the limit - just that they cluster!' Example: 1, 1.4, 1.41, 1.414... (approaching √2). Dragons get closer to each other! FUNDAMENTAL THEOREM: In real numbers, Cauchy = Convergent! 'Complete spaces have no holes!' UPPER/LOWER LIMITS: Dragon flight records! lim sup is the highest accumulation point - where dragons keep returning high. lim inf is the lowest. For oscillating sequence 1,-1,1,-1... lim sup = 1, lim inf = -1. HEINE-BOREL magic: Dragon needs to cover interval [0,1] with blankets. 'From ANY infinite collection, we need only FINITELY many!' Compactness! REAL NUMBER CONSTRUCTION: Dragon builds missing numbers! DEDEKIND CUTS: Split rationals into two sets. The gap between is a real number! Like √2 splits rationals into 'less than √2' and 'greater than √2'. CAUCHY COMPLETION: Fill all gaps where Cauchy sequences should converge! Epsilon chicks demonstrate: 1.4, 1.41, 1.414, 1.4142... 'We're Cauchy, creating √2!'"

# Episode 6: Powers & Topology Treats
generate_episode 6 \
    "Power-Up Dragon Mathematics!" \
    "Family Guy style: Baby dragon in power-up workshop! 'RATIONAL EXPONENTS are fractional powers!' 2^(1/2) = √2 is half-transformation! 8^(1/3) = ∛8 = 2. 'The rule: a^(m/n) = ⁿ√(aᵐ)!' Dragon demonstrates: 4^(3/2) = √(4³) = √64 = 8. REAL EXPONENTS unlock infinite possibilities! 'For any real r, define aʳ = limit of a^(rational approaching r)!' Example: 2^π uses rationals approaching π. TOPOLOGY ADVENTURE! Dragon explores point neighborhoods. ACCUMULATION POINT: 'Where infinitely many dragons gather!' For sequence 1/n, zero is accumulation point. ISOLATED POINTS stand alone - no neighbors nearby! OPEN SETS are bubble zones: 'For each point, there's a whole neighborhood inside!' (0,1) is open. CLOSED SETS include all their boundary dragons! [0,1] is closed. INTERIOR points have breathing room - open ball fits around them. CLOSURE adds all limit points. CANTOR SET: Dragon's fractal magic! Remove middle third repeatedly: [0,1] → [0,1/3]∪[2/3,1] → ... 'Infinitely many points, but no intervals!' Epsilon chicks form ε-balls: 'Every point in open set has ε-neighborhood inside!'"

# Episode 7: Functions - Dragon Transformations
generate_episode 7 \
    "Function Dragon Transform!" \
    "Baby dragon shape-shifting master! 'FUNCTIONS are transformation rules: f(x) takes input x, gives output f(x)!' Dragon machine: Put in 3, get out 9 for f(x)=x². DOMAIN is dragon's territory - all allowed inputs. For f(x)=√x, domain is [0,∞). RANGE is all possible outputs - where dragon can transform to! For f(x)=x², range is [0,∞). ONE-TO-ONE (injective): 'Each input gets UNIQUE output!' f(x)=2x is one-to-one. f(x)=x² is NOT (both 2 and -2 give 4). ONTO (surjective): 'Hit EVERY target in codomain!' f:ℝ→ℝ with f(x)=x³ is onto. BIJECTION = both = perfect pairing! COMPOSITION is combo transformation! '(f∘g)(x) = f(g(x))' - apply g first, then f! Example: f(x)=x², g(x)=x+1. Then (f∘g)(x)=f(x+1)=(x+1)². EVEN functions have mirror symmetry: f(-x)=f(x). Like x² or cos(x). ODD functions have rotational symmetry: f(-x)=-f(x). Like x³ or sin(x). PERIODIC functions repeat: f(x+T)=f(x). Sin and cos have period 2π. 'Functions at infinity: lim f(x) as x→∞ matches sequence limits!' Epsilon chicks map domain to range: 1→1, 2→4, 3→9 for f(x)=x²!"

# Episode 8: Function Limits & Continuity
generate_episode 8 \
    "Smooth Dragon Flights!" \
    "Family Guy cutaway: Dragon pilot learning smooth flying! 'FUNCTION LIMITS: What happens as we approach point c?' lim f(x) as x→c = L means: get close to c, f(x) gets close to L! Precise: For any ε>0, exists δ>0 where |x-c|<δ implies |f(x)-L|<ε. ONE-SIDED LIMITS: Left approach x→c⁻ vs right approach x→c⁺. 'Like landing from different directions!' For f(x)=|x|/x: left limit at 0 is -1, right limit is +1. CAUCHY CRITERION: f has limit at c if for any ε>0, exists δ>0 where |x-y|<δ near c implies |f(x)-f(y)|<ε. CONTINUITY = NO TELEPORTING! 'Three conditions: 1) f(c) exists, 2) lim f(x) as x→c exists, 3) They're EQUAL!' Continuous means smooth flight - small turbulence causes small deviation. ε-δ definition: |x-c|<δ implies |f(x)-f(c)|<ε. ARITHMETIC: Sum, product, quotient (denominator≠0) of continuous functions are continuous! COMPOSITION: If f continuous at c, g continuous at f(c), then g∘f continuous at c! DISCONTINUITIES: REMOVABLE (hole): lim exists but ≠ f(c). JUMP: left and right limits differ. ESSENTIAL: limit doesn't exist (like sin(1/x) at 0). INTERMEDIATE VALUE THEOREM: 'Continuous on [a,b] means hit EVERY altitude between f(a) and f(b)!' No teleporting! Epsilon chicks show smooth vs jumpy paths!"

# Episode 9: Extreme Dragon Values
generate_episode 9 \
    "Finding Dragon Treasures!" \
    "Baby dragon treasure hunter with map! 'WEIERSTRASS EXTREME VALUE THEOREM: Continuous function on closed interval [a,b] MUST achieve maximum and minimum!' No treasure escapes! Dragon searches [0,1] with f(x)=x²-2x+2. Finds MIN at x=1 (value 1) and MAX at x=0 (value 2). MONOTONIC + CONTINUOUS = BIJECTION on interval! 'Always increasing/decreasing means one-to-one and onto!' Example: f(x)=x³ on ℝ. UNIFORM CONTINUITY: 'One δ works for ALL points!' Regular continuity: each point needs its own δ. Uniform: ∀ε>0, ∃δ>0 such that |x-y|<δ implies |f(x)-f(y)|<ε for ALL x,y! HEINE-CANTOR: 'Continuous on closed interval [a,b] is AUTOMATICALLY uniformly continuous!' Closed and bounded = compact = uniform! DERIVATIVE introduction: Dragon velocity! 'f'(x) = lim[h→0] (f(x+h)-f(x))/h' Instantaneous rate of change! Physical meaning: velocity from position. Geometric: slope of tangent line. Example: f(x)=x² has f'(x)=2x. At x=3, slope is 6! DIFFERENTIABLE ⟹ CONTINUOUS: 'Smooth flying requires no jumps!' But continuous doesn't imply differentiable - think |x| at 0. CHAIN RULE preview: (f∘g)'(x) = f'(g(x))·g'(x). 'Multiply the rates!' Epsilon chicks measure slopes at different points!"

# Episode 10: Derivative Dragon Olympics
generate_episode 10 \
    "Dragon Calculus Olympics!" \
    "Family Guy Olympics special! Event 1 - CHAIN RULE RELAY: Dragons pass derivatives! 'For h(x)=f(g(x)), we get h'(x)=f'(g(x))·g'(x)!' Example: h(x)=sin(x²). Inner: g(x)=x², g'(x)=2x. Outer: f(u)=sin(u), f'(u)=cos(u). Result: h'(x)=cos(x²)·2x! Event 2 - INVERSE FUNCTION GYMNASTICS: 'If f and f⁻¹ are inverses, then (f⁻¹)'(y) = 1/f'(f⁻¹(y))!' Flip the derivative! Example: f(x)=x³, f⁻¹(y)=∛y. Then (f⁻¹)'(y) = 1/(3(∛y)²). Event 3 - HIGHER DERIVATIVE MARATHON: f'(x)=velocity, f''(x)=acceleration, f'''(x)=jerk, f⁽⁴⁾(x)=snap! 'Each measures rate of change of previous!' For f(x)=x⁴: f'=4x³, f''=12x², f'''=24x, f⁽⁴⁾=24. Event 4 - CRITICAL POINT TREASURE HUNT: 'Where f'(x)=0 or doesn't exist!' These are potential max/min locations. FERMAT'S THEOREM: Local extrema have f'(c)=0 (if derivative exists). Event 5 - THEOREM RACES: ROLLE: If f continuous on [a,b], differentiable on (a,b), and f(a)=f(b), then ∃c where f'(c)=0! 'Roller coaster must have flat point!' LAGRANGE MVT: Average velocity achieved at some instant! [f(b)-f(a)]/(b-a) = f'(c) for some c∈(a,b). CAUCHY MVT: Racing functions! [f(b)-f(a)]/[g(b)-g(a)] = f'(c)/g'(c). Epsilon chicks score each event!"

# Episode 11: Advanced Dragon Techniques
generate_episode 11 \
    "Dragon's Secret Techniques!" \
    "Baby dragon in ninja dojo learning secret techniques! 'DARBOUX THEOREM: Derivatives satisfy intermediate value property!' Even if f' not continuous! If f'(a)=1 and f'(b)=3, then f' hits every value between 1 and 3! 'Derivatives can't jump over values!' L'HÔPITAL'S RULE - Ultimate technique for 0/0 or ∞/∞! 'When lim f(x)/g(x) gives 0/0 or ∞/∞, use lim f'(x)/g'(x) instead!' Example: lim[x→0] sin(x)/x = 0/0. Apply L'Hôpital: lim cos(x)/1 = 1! Works for ∞/∞ too: lim[x→∞] x/eˣ = lim 1/eˣ = 0. 'Can apply MULTIPLE times!' Example: lim[x→0] (1-cos(x))/x² = lim sin(x)/(2x) = lim cos(x)/2 = 1/2. Other indeterminate forms: 0·∞ (convert to 0/0 or ∞/∞), ∞-∞ (algebraic manipulation), 0⁰, 1^∞, ∞⁰ (use logarithms)! ADVANCED EXAMPLES: lim[x→0⁺] x·ln(x) = 0·(-∞). Rewrite as ln(x)/(1/x) = -∞/∞. L'Hôpital: (1/x)/(-1/x²) = -x → 0! Dragon demonstrates each technique. 'These tools handle ANY limiting challenge!' Epsilon chicks practice: ε^ε as ε→0⁺. Use y=ε^ε, ln(y)=ε·ln(ε), find lim ln(y)=0, so y→1!"

# Episode 12: Taylor Dragon Approximation
generate_episode 12 \
    "Dragon's Crystal Ball!" \
    "Family Guy fortune teller dragon with crystal ball! 'TAYLOR POLYNOMIALS approximate functions near point a!' Start simple: LINEAR approximation f(x) ≈ f(a) + f'(a)(x-a). 'Tangent line prediction!' For f(x)=eˣ at a=0: f(x) ≈ 1 + x. QUADRATIC improves: f(x) ≈ f(a) + f'(a)(x-a) + f''(a)(x-a)²/2!. For eˣ: f(x) ≈ 1 + x + x²/2. TAYLOR'S THEOREM: nth degree polynomial! Pₙ(x) = Σ[k=0 to n] f⁽ᵏ⁾(a)(x-a)ᵏ/k!. 'Each derivative adds precision!' For eˣ: 1 + x + x²/2! + x³/3! + ... REMAINDER Rₙ(x) = f(x) - Pₙ(x) satisfies |Rₙ(x)| ≤ M|x-a|ⁿ⁺¹/(n+1)! where M bounds (n+1)th derivative. 'Error shrinks FAST!' LITTLE-O NOTATION: Rₙ(x) = o((x-a)ⁿ) means Rₙ(x)/(x-a)ⁿ → 0. 'Remainder vanishes faster than (x-a)ⁿ!' FAMOUS SERIES: sin(x) = x - x³/3! + x⁵/5! - ... cos(x) = 1 - x²/2! + x⁴/4! - ... ln(1+x) = x - x²/2 + x³/3 - ... (for |x|<1). PROOF e IS IRRATIONAL: Assume e = p/q. Use Taylor series for e¹. Multiply by q!. Left side isn't integer, right side is. Contradiction! Epsilon chicks approximate sin(0.1) using Taylor: 0.1 - 0.001/6 ≈ 0.0998!"

# Episode 13: Dragon Function Investigation
generate_episode 13 \
    "Dragon Detective Agency!" \
    "Baby dragon detective with magnifying glass and notebook! 'COMPLETE FUNCTION INVESTIGATION - Let's solve the case!' Step 1 - DOMAIN: 'Where does function live?' Check denominators≠0, square roots≥0, logarithms>0. Step 2 - CRITICAL POINTS: Solve f'(x)=0. 'Potential extrema locations!' Step 3 - FIRST DERIVATIVE TEST: Check f' sign changes. (+) to (-) = LOCAL MAX! (-) to (+) = LOCAL MIN! No change = neither! Example: f(x)=x³-3x has f'(x)=3x²-3=0 at x=±1. Step 4 - SECOND DERIVATIVE: f''(x)>0 means CONCAVE UP (happy dragon smile ∪). f''(x)<0 means CONCAVE DOWN (sad dragon frown ∩). At critical point: f''(c)>0 ⟹ local min, f''(c)<0 ⟹ local max. Step 5 - INFLECTION POINTS: Where f'' changes sign. 'Dragon mood swings!' Concavity flips! Step 6 - ASYMPTOTES: VERTICAL at domain boundaries (denominator→0). HORIZONTAL: lim[x→±∞] f(x) = L gives y=L. SLANT: If lim f(x)/x = m≠0, do polynomial division! Example: f(x)=(x²+1)/x has vertical at x=0, slant y=x. Step 7 - SKETCH: Plot critical points, inflections, asymptotes. Connect smoothly using derivative info! COMPLETE EXAMPLE: f(x)=x³/(x²-1). Domain: x≠±1. Vertical asymptotes at x=±1. Critical points, concavity analysis, full sketch! Epsilon chicks create function portrait gallery!"

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