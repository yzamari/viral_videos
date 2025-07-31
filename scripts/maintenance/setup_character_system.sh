#!/bin/bash

# Setup Character System for ViralAI
# Configures environment and creates initial characters

echo "🎭 Setting up ViralAI Character System"
echo "===================================="
echo ""

# Set environment variable for current session
export GOOGLE_CLOUD_PROJECT=viralgen-464411
echo "✅ Environment variable set: GOOGLE_CLOUD_PROJECT=viralgen-464411"

# Add to shell profile for permanent use
SHELL_RC=""
if [ -f ~/.zshrc ]; then
    SHELL_RC=~/.zshrc
elif [ -f ~/.bashrc ]; then
    SHELL_RC=~/.bashrc
elif [ -f ~/.bash_profile ]; then
    SHELL_RC=~/.bash_profile
fi

if [ -n "$SHELL_RC" ]; then
    if ! grep -q "GOOGLE_CLOUD_PROJECT=viralgen-464411" "$SHELL_RC"; then
        echo "export GOOGLE_CLOUD_PROJECT=viralgen-464411" >> "$SHELL_RC"
        echo "✅ Added to $SHELL_RC for future sessions"
    else
        echo "✅ Already configured in $SHELL_RC"
    fi
fi

echo ""

# Test the system
echo "🔧 Testing character reference system..."
python3 main.py test-character-system

if [ $? -eq 0 ]; then
    echo ""
    echo "🎬 Creating professional news anchor profiles..."
    python3 main.py create-news-anchors
    
    echo ""
    echo "📁 Character Storage Locations:"
    echo "   Directory: $(pwd)/outputs/character_references/"
    echo "   Database: $(pwd)/outputs/character_references/characters.json"
    echo ""
    
    echo "🎭 Available Characters:"
    python3 main.py list-characters
    
    echo ""
    echo "🚀 Character system ready! You can now:"
    echo "   1. Run: ./create_iran_water_crisis_series.sh"
    echo "   2. Or use: ./manage_characters.sh for more options"
    echo "   3. Create custom characters with: python3 main.py store-character photo.jpg --name 'Name'"
    
else
    echo ""
    echo "❌ Character system not ready. Please check the error messages above."
fi