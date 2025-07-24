#!/bin/bash

# Family Guy style office rules video with continuous generation

python main.py generate \
  --mission "Create Family Guy animated scene: Big muscular brown-haired man in business attire standing in busy office. He explains three important rules to coworkers: 'Rule one: Always lock the office door, FBI agents with guns might raid unexpectedly. Rule two: Never park in someone else's designated spot. Rule three: Do not take brown paper lunch bags that aren't yours.' Office setting with desks, computers, water cooler. Seth MacFarlane animation style." \
  --duration 30 \
  --platform youtube \
  --visual-style "family guy animation" \
  --style comedy \
  --tone humorous \
  --voice "comedic-performer" \
  --session-id "office_rules_family_guy"
  # Note: --hook and --call-to-action are not valid CLI flags in current implementation