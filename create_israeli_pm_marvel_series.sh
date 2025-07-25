#!/bin/bash

# Israeli Prime Ministers - Marvel Comics Style Dark Comedy Series
# Educational entertainment about Israel's leaders
# Marvel Comics style with dark humor

# Check if specific episodes were requested
SPECIFIC_EPISODES=""
if [ $# -gt 0 ]; then
    SPECIFIC_EPISODES="$@"
    echo "🎯 Generating specific episodes: $SPECIFIC_EPISODES"
fi

echo "🦸 Israeli Prime Ministers: The Marvel Comics Chronicles"
echo "====================================================="
echo "💥 Marvel Comics Style - POW! BAM! BOOM!"
echo "😈 Dark Comedy & Historical Facts"
echo "🇮🇱 Educational Entertainment"
echo ""

# Function to check if we should generate this episode
should_generate_episode() {
    local episode_num=$1
    # If no specific episodes requested, generate all
    if [ -z "$SPECIFIC_EPISODES" ]; then
        return 0
    fi
    # Check if this episode number is in the requested list
    for ep in $SPECIFIC_EPISODES; do
        if [ "$ep" = "$episode_num" ]; then
            return 0
        fi
    done
    return 1
}

# Episode 1: David Ben-Gurion (1948-1954, 1955-1963)
if should_generate_episode 1; then
    echo "📺 Episode 1: Ben-Gurion - The Founding Titan"
    echo "----------------------------------------------"

    python3 main.py generate \
  --mission "Marvel Comics opening: Comic panels explode! BOOM! David Ben-Gurion bursts from desert sands, speech bubbles everywhere. 'I am... INEVITABLE!' SNAP! British Mandate vanishes in comic smoke. Action panels montage: KA-POW! Declaring independence while others have sweat drops. WHOOSH! Yoga headstands with motion lines during cabinet meetings. Tech panels: Building kibbutzim with Kirby Dots energy. Plot twist panel: Retired to desert cabin, thought bubble: 'Finally, peace.' Final panel teaser: 'Ben-Gurion will return... in 1955!' Editor's note box: 'True Believer Achievement: Created Entire Country!'" \
  --character "David Ben-Gurion - with his iconic white Einstein-like hair, round face, and distinctive appearance of the real historical figure" \
  --platform instagram \
  --duration 65 \
  --visual-style "marvel comics" \
  --tone darkly_humorous \
  --style cinematic \
  --no-cheap \
  --session-id "israeli_pm_ep1_bengurion"

    if [ $? -eq 0 ]; then
        echo "✅ Episode 1 complete!"
        sleep 10
    else
        echo "❌ Episode 1 failed!"
        if [ -n "$SPECIFIC_EPISODES" ]; then
            echo "Continuing with other episodes..."
        else
            exit 1
        fi
    fi
fi

# Episode 2: Moshe Sharett (1954-1955)
if should_generate_episode 2; then
    echo ""
    echo "📺 Episode 2: Sharett - The Forgotten Avenger"
    echo "----------------------------------------------"
    
    python3 main.py generate \
      --mission "Marvel intro: Moshe Sharett materializes between Ben-Gurion appearances like Ant-Man - 'Did anyone notice I was here?' Montage of being overshadowed, papers flying past him in slow-mo. Spider-Man style inner monologue: 'With great responsibility comes... being ignored by history.' Shows diplomatic skills like Doctor Strange's hand movements creating peace treaties. Villain reveal: Ben-Gurion's shadow literally consuming screen. Post-credit: Still in office, checking watch, 'Is it 1955 yet?' Stan Lee cameo as confused citizen: 'Who's the Prime Minister again?'" \
      --character "Moshe Sharett - with his distinctive bald head, round glasses, and thoughtful diplomatic demeanor like the real historical figure" \
      --platform instagram \
      --duration 65 \
      --visual-style "marvel comics" \
      --tone darkly_humorous \
      --style cinematic \
      --no-cheap \
      --session-id "israeli_pm_ep2_sharett"
    if [ $? -eq 0 ]; then
        echo "✅ Episode 2 complete!"
        sleep 10
    else
        echo "❌ Episode 2 failed!"
        if [ -n "$SPECIFIC_EPISODES" ]; then
            echo "Continuing with other episodes..."
        else
            exit 1
        fi
    fi
fi

# Episode 3: Levi Eshkol (1963-1969)
if should_generate_episode 3; then
    echo ""
    echo "📺 Episode 3: Eshkol - The Anxious Avenger"
    echo "------------------------------------------"
    
    python3 main.py generate \
      --mission "Marvel Comics: War room panel, countdown timer bubbles! '6 DAYS!' Generals in action poses: 'Attack NOW!' Eshkol with sweat drops, thought bubble: 'What would Ben-Gurion do?' TRANSFORMATION PANEL: Mild PM becomes WAR HERO! Table SMASH! 'ESHKOL DECIDES!' Victory montage panels: Territory TRIPLES! Map expanding with motion lines. Spider-Man pointing meme panel: 'We have Sinai?!' Death panel: Speech bubble weakening... 'Jerusalem... united...' Final panel: Golda's smoke forms next episode teaser. Editor's note: 'The Anxious Avenger Falls!'" \
      --character "Levi Eshkol - with his tall stature, receding hairline, gentle face, and kind eyes like the real historical figure" \
      --platform instagram \
      --duration 65 \
      --visual-style "marvel comics" \
      --tone darkly_humorous \
      --style cinematic \
      --no-cheap \
      --session-id "israeli_pm_ep3_eshkol"
    
    if [ $? -eq 0 ]; then
        echo "✅ Episode 3 complete!"
        sleep 10
    else
        echo "❌ Episode 3 failed!"
        if [ -n "$SPECIFIC_EPISODES" ]; then
            echo "Continuing with other episodes..."
        else
            exit 1
        fi
    fi
fi

    # Episode 4: Golda Meir (1969-1974)
if should_generate_episode 4; then
    echo ""
    echo "📺 Episode 4: Golda - The Iron Grandmother"
    echo "------------------------------------------"
    
    python3 main.py generate \
      --mission "Marvel Comics: SMOKE PANEL! Golda emerges, cigarette glowing with power! Speech bubble: 'I'm the only MAN in the cabinet!' TRANSFORMATION: Cabinet members become kindergarteners! Action panels: YOM KIPPUR WAR! Coffee pot in one hand, tank radio in other! KABOOM! SNAP! Intelligence failure panel - files scatter! TIME REWIND PANELS showing ignored warnings. Kitchen diplomacy: World leaders SHRINK in her presence! Resignation panel: Mushroom cloud of smoke. Final panel: 'There's no Palestine' - Internet EXPLODES in background! POW!" \
      --character "Golda Meir - with her iconic grey bun hairstyle, strong jawline, and ever-present cigarette like the real historical figure" \
      --platform instagram \
      --duration 65 \
      --visual-style "marvel comics" \
      --tone darkly_humorous \
      --style cinematic \
      --no-cheap \
      --session-id "israeli_pm_ep4_golda"
    if [ $? -eq 0 ]; then
        echo "✅ Episode 4 complete!"
        sleep 10
    else
        echo "❌ Episode 4 failed!"
        if [ -n "$SPECIFIC_EPISODES" ]; then
            echo "Continuing with other episodes..."
        else
            exit 1
        fi
    fi
fi

# Episode 5: Yitzhak Rabin - First Term (1974-1977)
if should_generate_episode 5; then
    echo ""
    echo "📺 Episode 5: Rabin I - The Soldier's Gambit"
    echo "--------------------------------------------"
    
    python3 main.py generate \
      --mission "Marvel Comics: HERO PANEL! Young Rabin with Star of David shield! Transformation sequence: Soldier panels morph to PM! ENTEBBE RESCUE: 'COMMANDOS ASSEMBLE!' Sky-drop action lines! WHOOSH! Economic crisis panel: SNAP! Half the economy dusts away! SCANDAL REVEAL: Bank account papers with SHOCK effects! 'BETRAYAL!' Resignation panel: Shield CLANGS to ground. Speech bubble: 'I'll be back!' Post-credit panel: Begin rising with evil grin. Timeline SPLIT panel: 'What If...?' Future assassination shadow. Editor's box: 'To be continued... tragically.'" \
      --character "Young Yitzhak Rabin - with his distinctive wavy hair, square jaw, and military bearing like the real historical figure" \
      --platform instagram \
      --duration 65 \
      --visual-style "marvel comics" \
      --tone darkly_humorous \
      --style cinematic \
      --no-cheap \
      --session-id "israeli_pm_ep5_rabin1"
    if [ $? -eq 0 ]; then
        echo "✅ Episode 5 complete!"
        sleep 10
    else
        echo "❌ Episode 5 failed!"
        if [ -n "$SPECIFIC_EPISODES" ]; then
            echo "Continuing with other episodes..."
        else
            exit 1
        fi
    fi
fi

# Episode 6: Menachem Begin (1977-1983)
if should_generate_episode 6; then
    echo ""
    echo "📺 Episode 6: Begin - The Revolutionary Phoenix"
    echo "-----------------------------------------------"
    
    python3 main.py generate \
      --mission "Marvel Comics epic: UNDERGROUND PANEL! Begin rises, British 'WANTED' posters swirl! Thought bubble: 'First they ignore you...' CAMP DAVID SUMMIT: Wakanda-style meeting! Sadat and Carter in council poses. PEACE SIGNING: Slow-mo panels, doves with pyramid/star wings! FLUTTER! Dark turn panel: LEBANON WAR CHAOS! Powers out of control! Depression spiral panels: Thor-like breakdown sequence. Nobel Prize MELTS in hands! Cave hermit panel: Alone in darkness. Caption: 'From terrorist to peacemaker to...' Post-credit: Map panel shows settlements spreading like symbiote! CREEP!" \
      --character "Menachem Begin - with his trademark thick-rimmed glasses, receding white hair, and Polish-accented intensity like the real historical figure" \
      --platform instagram \
      --duration 65 \
      --visual-style "marvel comics" \
      --tone darkly_humorous \
      --style cinematic \
      --no-cheap \
      --session-id "israeli_pm_ep6_begin"
    if [ $? -eq 0 ]; then
        echo "✅ Episode 6 complete!"
        sleep 10
    else
        echo "❌ Episode 6 failed!"
        if [ -n "$SPECIFIC_EPISODES" ]; then
            echo "Continuing with other episodes..."
        else
            exit 1
        fi
    fi
fi

# Episode 7: Yitzhak Shamir (1983-1984, 1986-1992)
if should_generate_episode 7; then
    echo ""
    echo "📺 Episode 7: Shamir - The Tiny Terrorist Titan"
    echo "-----------------------------------------------"
    
    python3 main.py generate \
      --mission "Marvel Comics: TINY TITAN PANEL! Shamir ant-sized, speech bubble: 'Size matters NOT!' FLASHBACK PANELS: Underground fighter memories, Winter Soldier style! Musical chairs sequence: PM throne SWITCHING with Peres! SWAP! INTIFADA PANELS: Stones vs Tanks! David vs GOLIATH action! CLANG! Madrid Conference: Being DRAGGED to peace talks! 'NOOOO!' Bush Sr. looms as MEGA-THREAT! 'Your loans... GONE!' Immovable object panel: 'NOT ONE INCH!' meets unstoppable force! CRASH! Defeat panel: Votes scatter like dust. Final panel: 'Terror? I INVENTED it!' MIC DROP! BOOM!" \
      --character "Yitzhak Shamir - with his short stature, bald head with white hair on sides, and stern expression like the real historical figure" \
      --platform instagram \
      --duration 65 \
      --visual-style "marvel comics" \
      --tone darkly_humorous \
      --style cinematic \
      --no-cheap \
      --session-id "israeli_pm_ep7_shamir"
    if [ $? -eq 0 ]; then
        echo "✅ Episode 7 complete!"
        sleep 10
    else
        echo "❌ Episode 7 failed!"
        if [ -n "$SPECIFIC_EPISODES" ]; then
            echo "Continuing with other episodes..."
        else
            exit 1
        fi
    fi
fi

# Episode 8: Yitzhak Rabin - Second Term (1992-1995)
if should_generate_episode 8; then
    echo ""
    echo "📺 Episode 8: Rabin II - The Peace Soldier's Last Stand"
    echo "-------------------------------------------------------"
    
    python3 main.py generate \
      --mission "Marvel Comics return: ICE THAW PANEL! Rabin returns! 'PEACE AVENGERS ASSEMBLE!' Oslo Accords panel: HISTORIC HANDSHAKE with Arafat! Discomfort lines visible. Building peace panels: Constructing while wrenches fly! CLANG! BANG! 'TRAITOR!' chants spread like symbiote across panels! BLACK OOZE! Rally panel: November 4, 1995, peace song notes float. ASSASSINATION NOIR: Three shots! BANG! BANG! BANG! Shield falls. 'Et tu, Yigal?' Hospital panel: Fading... 'I am... Peace Man.' Nation SPLITS down middle! Empty suit ceremony panel. Caption: 'Legacy: It's Complicated.'" \
      --character "Yitzhak Rabin - now older with grey hair, deeper lines on his face, but same military bearing like the real historical figure" \
      --platform instagram \
      --duration 65 \
      --visual-style "marvel comics" \
      --tone darkly_humorous \
      --style cinematic \
      --no-cheap \
      --session-id "israeli_pm_ep8_rabin2"
    if [ $? -eq 0 ]; then
        echo "✅ Episode 8 complete!"
        sleep 10
    else
        echo "❌ Episode 8 failed!"
        if [ -n "$SPECIFIC_EPISODES" ]; then
            echo "Continuing with other episodes..."
        else
            exit 1
        fi
    fi
fi

# Episode 9: Shimon Peres (1995-1996)
if should_generate_episode 9; then
    echo ""
    echo "📺 Episode 9: Peres - The Eternal Runner-Up"
    echo "-------------------------------------------"
    
    python3 main.py generate \
      --mission "Marvel Comics tragedy: THRONE PANEL! Peres finally sits, but 'ACTING PM' floats mockingly above! Tries lifting peace hammer - ALMOST worthy! STRAIN LINES! Operation Grapes panels: MISSILES EVERYWHERE! 'What have I done?!' Qana disaster: SCARLET WITCH-level accident! HORROR! Election battle: BIBI vs PERES! Epic clash panels! '1% MARGIN!' So close! CRUSHING DEFEAT! Lifetime montage panels: Always the bridesmaid. 'MR. PEACE' becomes 'President of... Nothing.' Final panel: Age 93, arc reactor dims... still dreaming. Editor's note: 'The Eternal Runner-Up Rests.'" \
      --character "Shimon Peres - with his distinctive hawk nose, white swept-back hair, and intellectual demeanor like the real historical figure" \
      --platform instagram \
      --duration 65 \
      --visual-style "marvel comics" \
      --tone darkly_humorous \
      --style cinematic \
      --no-cheap \
      --session-id "israeli_pm_ep9_peres"
    if [ $? -eq 0 ]; then
        echo "✅ Episode 9 complete!"
        sleep 10
    else
        echo "❌ Episode 9 failed!"
        if [ -n "$SPECIFIC_EPISODES" ]; then
            echo "Continuing with other episodes..."
        else
            exit 1
        fi
    fi
fi

# Episode 10: Benjamin Netanyahu - First Term (1996-1999)
if should_generate_episode 10; then
    echo ""
    echo "📺 Episode 10: Bibi I - The Rise of the Smooth Operator"
    echo "-------------------------------------------------------"
    
    python3 main.py generate \
      --mission "Marvel Comics origin: MIT GRADUATION PANEL! Young Bibi emerges, perfect English speech bubble! American swagger lines! 'MR. SECURITY' glows like arc reactor! CHEST BEAM! Election panel: Defeats Peres by 1%! 'NARROW VICTORY!' Western Wall tunnel opening: PORTAL TO CHAOS! Spirits escape! WHOOSH! Peace process DISSOLVES like Spider-Man! Particle effects! Scandal montage panels: Cigars! Champagne! Sara RAGE MODE! 'HULK SARA SMASH!' Coalition collapse: Heroes scatter! DISBANDING! Landslide loss panel: 'I'LL BE BACK!' Mirror practice panel: 'One day... LONGEST SERVING!' Post-credit tease!" \
      --character "Young Benjamin Netanyahu - with his distinctive silver hair, sharp features, and charismatic presence like the real historical figure" \
      --platform instagram \
      --duration 65 \
      --visual-style "marvel comics" \
      --tone darkly_humorous \
      --style cinematic \
      --no-cheap \
      --session-id "israeli_pm_ep10_netanyahu1"
    if [ $? -eq 0 ]; then
        echo "✅ Episode 10 complete!"
        sleep 10
    else
        echo "❌ Episode 10 failed!"
        if [ -n "$SPECIFIC_EPISODES" ]; then
            echo "Continuing with other episodes..."
        else
            exit 1
        fi
    fi
fi

# Episode 11: Ehud Barak (1999-2001)
if should_generate_episode 11; then
    echo ""
    echo "📺 Episode 11: Barak - The Commando's Folly"
    echo "-------------------------------------------"
    
    python3 main.py generate \
      --mission "Marvel entrance: Ehud Barak most decorated soldier ever, medals like Infinity Stones. 'Israel's smartest PM' brain glows like Mind Stone. Camp David 2: Offers everything like Doctor Strange seeing all futures. Arafat says no to every timeline. Second Intifada explodes like Hulk rampage. Dressed as woman in operation flashback - 'I understood gender fluidity before it was cool.' Coalition crumbles faster than Thanos snap. Loses to Sharon in biggest landslide ever. Later: Epstein's island cameo, 'I kept my underwear on!' Apartment in luxury tower: 'I'm watching you... from above.'" \
      --character "Ehud Barak - with his compact build, receding hairline, analytical eyes, and military precision like the real historical figure" \
      --platform instagram \
      --duration 65 \
      --visual-style "marvel comics" \
      --tone darkly_humorous \
      --style cinematic \
      --no-cheap \
      --session-id "israeli_pm_ep11_barak"
    if [ $? -eq 0 ]; then
        echo "✅ Episode 11 complete!"
        sleep 10
    else
        echo "❌ Episode 11 failed!"
        if [ -n "$SPECIFIC_EPISODES" ]; then
            echo "Continuing with other episodes..."
        else
            exit 1
        fi
    fi
fi

# Episode 12: Ariel Sharon (2001-2006)
if should_generate_episode 12; then
    echo ""
    echo "📺 Episode 12: Sharon - The Bulldozer's Last Ride"
    echo "-------------------------------------------------"
    
    python3 main.py generate \
      --mission "Marvel epic: Ariel Sharon enters like Juggernaut, 'Nothing stops the Bulldozer!' Sabra-Shatila ghosts swirl like Mysterio illusions. Temple Mount visit: 'I'm just taking a walk' - explosion like stepping on landmine. Second Intifada: goes full Punisher mode. Plot twist: Gaza disengagement, removes settlers like Thanos with Reality Stone. Own party rebels: 'Fine, I'll do it myself,' creates Kadima. Stroke hits like Thor's hammer: eight years in coma, body kept alive like Winter Soldier. Dies with Gaza still unsolved. 'Legacy: It's complicated' in every language." \
      --character "Ariel Sharon - with his massive frame, white hair, and bulldozer-like presence like the real historical figure" \
      --platform instagram \
      --duration 65 \
      --visual-style "marvel comics" \
      --tone darkly_humorous \
      --style cinematic \
      --no-cheap \
      --session-id "israeli_pm_ep12_sharon"
    if [ $? -eq 0 ]; then
        echo "✅ Episode 12 complete!"
        sleep 10
    else
        echo "❌ Episode 12 failed!"
        if [ -n "$SPECIFIC_EPISODES" ]; then
            echo "Continuing with other episodes..."
        else
            exit 1
        fi
    fi
fi

# Episode 13: Ehud Olmert (2006-2009)
if should_generate_episode 13; then
    echo ""
    echo "📺 Episode 13: Olmert - The Accidental Corrupt PM"
    echo "-------------------------------------------------"
    
    python3 main.py generate \
      --mission "Marvel Comics accident: SURPRISE PM PANEL! Olmert: 'I didn't ASK for this!' Spider-bite style! Lebanon War 2 panels: LAUNCHING ATTACK! Everything goes WRONG! BOOM! CRASH! Winograd investigation: SHIELD-style interrogation panels! Secret talks panel: Offers Jerusalem! 'Take the INFINITY GAUNTLET!' CORRUPTION PANELS: Hydra heads multiply! Cash envelopes RAIN DOWN! Prison fitting: Iron Man armor REMOVAL sequence! CLANK! Prison stripes panel: First PM behind bars! Cell echo: 'I almost made PEACE!' Memoir writing panel: 'If only they knew...' Thought bubble despair." \
      --character "Ehud Olmert - with his slicked-back hair, smooth features, and polished appearance like the real historical figure" \
      --platform instagram \
      --duration 65 \
      --visual-style "marvel comics" \
      --tone darkly_humorous \
      --style cinematic \
      --no-cheap \
      --session-id "israeli_pm_ep13_olmert"
    if [ $? -eq 0 ]; then
        echo "✅ Episode 13 complete!"
        sleep 10
    else
        echo "❌ Episode 13 failed!"
        if [ -n "$SPECIFIC_EPISODES" ]; then
            echo "Continuing with other episodes..."
        else
            exit 1
        fi
    fi
fi

# Episode 14: Benjamin Netanyahu - The Return (2009-2021)
if should_generate_episode 14; then
    echo ""
    echo "📺 Episode 14: Bibi Forever - The Infinity PM"
    echo "---------------------------------------------"
    
    python3 main.py generate \
      --mission "Marvel Comics mega-episode: RETURN PANEL! Netanyahu: 'I am INEVITABLE!' SNAP! 12-year montage: Election panels blur in TIME LOOP! Strange-style! UN cartoon bomb panel: KINDERGARTEN THANOS draws! 'THIS IS IRAN!' Trump bromance panels: Hearts float! 'Love you 3000!' Corruption trial: Collecting scandal stones! CIGARS! CHAMPAGNE! MEDIA! COVID panels: 'I SAVED Israel!' Protests RAGE outside! Abraham Accords: PLOT TWIST! Unexpected peace signatures! Coalition JUGGLING - balls drop! CRASH! 'Back in 2022!' WINK! Crown to ash panel: 'KING BIBI' crumbles! Post-credit: Plotting in shadows..." \
      --character "Benjamin Netanyahu - now older, heavier, but still with silver hair and commanding presence like the real historical figure" \
      --platform instagram \
      --duration 65 \
      --visual-style "marvel comics" \
      --tone darkly_humorous \
      --style cinematic \
      --no-cheap \
      --session-id "israeli_pm_ep14_netanyahu_return"
    if [ $? -eq 0 ]; then
        echo "✅ Episode 14 complete!"
        sleep 10
    else
        echo "❌ Episode 14 failed!"
        if [ -n "$SPECIFIC_EPISODES" ]; then
            echo "Continuing with other episodes..."
        else
            exit 1
        fi
    fi
fi

# Episode 15: Naftali Bennett (2021-2022)
if should_generate_episode 15; then
    echo ""
    echo "📺 Episode 15: Bennett - The One Year Wonder"
    echo "--------------------------------------------"
    
    python3 main.py generate \
      --mission "Marvel Comics shortest: ANT-MAN PANEL! Bennett shrinks in! 'Size doesn't MATTER!' Betrayal panel: RIGHT-WING SHOCK! Loki-style side switch! Coalition panel: ENEMIES TOGETHER! Hate lines between all! Yamina DISSOLVES: Spider-Man dusting effect! PARTICLES! COVID surf panels: Silver Surfer on variant waves! SWOOSH! Putin meeting: BABY CHAIR! Instant meme panel! 'HUMILIATION!' Iran panels: Watching bad futures helplessly. Strange-style despair! One year COLLAPSE: 'At least I WAS PM!' Tech world vanish panel! POOF! Post-credit: Bibi's evil laugh! 'TOLD YOU SO!' HA HA HA!" \
      --character "Naftali Bennett - with his bald head, trimmed beard, and tech-bro energy like the real historical figure" \
      --platform instagram \
      --duration 65 \
      --visual-style "marvel comics" \
      --tone darkly_humorous \
      --style cinematic \
      --no-cheap \
      --session-id "israeli_pm_ep15_bennett"
    if [ $? -eq 0 ]; then
        echo "✅ Episode 15 complete!"
        sleep 10
    else
        echo "❌ Episode 15 failed!"
        if [ -n "$SPECIFIC_EPISODES" ]; then
            echo "Continuing with other episodes..."
        else
            exit 1
        fi
    fi
fi

# Episode 16: Yair Lapid (2022)
if should_generate_episode 16; then
    echo ""
    echo "📺 Episode 16: Lapid - The Caretaker Cameo"
    echo "------------------------------------------"
    
    python3 main.py generate \
      --mission "Marvel Comics cameo: SPIDER-MAN ARRIVAL! Lapid: 'Just happy to be HERE!' Web-swinging panels! Five-month SPEEDRUN: PM achievements BLUR by! ZOOM! UN speech panel: 'TWO STATES!' Right-wing heads EXPLODE! SCANNER-STYLE! TV host panels: Mirror admiration! 'HANDSOME PM!' Heart eyes everywhere! Campaign battle: DAVID vs GOLIATH #47! Slingshot ready! Election loss: SURPRISED PIKACHU FACE panel! 'Five minutes of fame!' Clock shows 5:00! Opposition return: 'Maybe next DECADE?' Shrug panel. Post-credit: Instagram THIRST TRAP poses! Caption: 'Democracy dies in darkness... but with RING LIGHT!' CLICK!" \
      --character "Yair Lapid - with his TV anchor good looks, silver fox hair, and media polish like the real historical figure" \
      --platform instagram \
      --duration 65 \
      --visual-style "marvel comics" \
      --tone darkly_humorous \
      --style cinematic \
      --no-cheap \
      --session-id "israeli_pm_ep16_lapid"
    if [ $? -eq 0 ]; then
        echo "✅ Episode 16 complete!"
        sleep 10
    else
        echo "❌ Episode 16 failed!"
        if [ -n "$SPECIFIC_EPISODES" ]; then
            echo "Continuing with other episodes..."
        else
            exit 1
        fi
    fi
fi

# Episode 17: Benjamin Netanyahu - The Final Form (2022-Present)
if should_generate_episode 17; then
    echo ""
    echo "📺 Episode 17: Bibi Eternal - Democracy's Endgame"
    echo "-------------------------------------------------"
    
    python3 main.py generate \
      --mission "Marvel Comics finale: ULTIMATE RETURN! 'Somehow, Netanyahu RETURNED!' Lightning effects! Most right-wing panel: EXTREMISM STONES assembled! GLOW! Judicial reform: SNAP attempt at Supreme Court! RESISTANCE! Protest panels: Half of Israel DISSOLVING! Dust effects! October 7th: DARKEST DAY! Security shield SHATTERS! Vibranium cracks! Gaza war panels: 'TOTAL VICTORY!' Empty speech bubbles for hostages. ICC warrant: INTERNATIONAL VILLAIN status! Wanted posters! Polls diving panel: Coalition held by SCOTCH TAPE! Literally! 'After me, the FLOOD!' Noah vibes. Universe ending panel: Still in power! Post-credit: 'Democracy will return...?' Question mark HUGE! THE END... OR IS IT?!" \
      --character "Benjamin Netanyahu (final form) - greyer, tired, but still defiant like the real historical figure in 2024" \
      --platform instagram \
      --duration 65 \
      --visual-style "marvel comics" \
      --tone darkly_humorous \
      --style cinematic \
      --no-cheap \
      --session-id "israeli_pm_ep17_netanyahu_final"
    if [ $? -eq 0 ]; then
        echo "✅ Episode 17 complete!"
        sleep 10
    else
        echo "❌ Episode 17 failed!"
        if [ -n "$SPECIFIC_EPISODES" ]; then
            echo "Continuing with other episodes..."
        else
            exit 1
        fi
    fi
fi

echo ""
echo "🎬 Series Complete!"
echo "==================="
echo ""
echo "📁 All episodes saved in outputs/israeli_pm_ep*/"
echo ""
echo "🦸 'With great power comes great corruption' - Every Israeli PM, probably"
echo ""
echo "⚠️ Disclaimer: This series contains dark humor about real political figures."
echo "Educational purposes only. Mileage may vary. Democracy not included."