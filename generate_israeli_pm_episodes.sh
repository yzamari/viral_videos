#!/bin/bash

# Helper script to generate specific Israeli PM episodes
# Usage: ./generate_israeli_pm_episodes.sh [episode numbers]
# Example: ./generate_israeli_pm_episodes.sh 4 6 3 8 11 2

# Display usage if no arguments
if [ $# -eq 0 ]; then
    echo "Usage: $0 [episode numbers]"
    echo "Example: $0 4 6 3 8 11 2"
    echo ""
    echo "Available episodes:"
    echo "  1: David Ben-Gurion - The Founding Titan"
    echo "  2: Moshe Sharett - The Forgotten Avenger"
    echo "  3: Levi Eshkol - The Anxious Avenger"
    echo "  4: Golda Meir - The Iron Grandmother"
    echo "  5: Yitzhak Rabin I - The Soldier's Gambit"
    echo "  6: Menachem Begin - The Revolutionary Phoenix"
    echo "  7: Yitzhak Shamir - The Tiny Terrorist Titan"
    echo "  8: Yitzhak Rabin II - The Peace Soldier's Last Stand"
    echo "  9: Shimon Peres - The Eternal Runner-Up"
    echo " 10: Benjamin Netanyahu I - The Rise of the Smooth Operator"
    echo " 11: Ehud Barak - The Commando's Folly"
    echo " 12: Ariel Sharon - The Bulldozer's Last Ride"
    echo " 13: Ehud Olmert - The Accidental Corrupt PM"
    echo " 14: Benjamin Netanyahu II - The Infinity PM"
    echo " 15: Naftali Bennett - The One Year Wonder"
    echo " 16: Yair Lapid - The Caretaker Cameo"
    echo " 17: Benjamin Netanyahu III - Democracy's Endgame"
    exit 0
fi

# Pass all arguments to the main script
./create_israeli_pm_marvel_series.sh "$@"