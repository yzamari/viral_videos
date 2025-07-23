#!/bin/bash

# Character Management Script
# Create, list, and manage characters for consistent video series

echo "🎭 ViralAI Character Management"
echo "=============================="
echo ""

# Function to show character storage location
show_storage() {
    echo "📁 Character Storage Location:"
    echo "   Directory: outputs/character_references/"
    echo "   Database: outputs/character_references/characters.json"
    echo ""
    
    if [ -d "outputs/character_references" ]; then
        echo "✅ Character storage exists"
        echo "📊 Storage contents:"
        ls -la outputs/character_references/ 2>/dev/null || echo "   (empty)"
    else
        echo "📝 Character storage will be created when first character is added"
    fi
    echo ""
}

# Function to test system
test_system() {
    echo "🔧 Testing character reference system..."
    python main.py test-character-system
    echo ""
}

# Function to create professional anchors
create_anchors() {
    echo "👥 Creating professional news anchor profiles..."
    python main.py create-news-anchors
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ News anchors created!"
        list_characters
    else
        echo ""
        echo "❌ Failed to create anchors. Check the system status above."
    fi
}

# Function to list all characters
list_characters() {
    echo "🎭 Available Characters:"
    python main.py list-characters
    echo ""
}

# Function to create custom character
create_custom() {
    echo "📸 Create Custom Character"
    echo "------------------------"
    echo "To create a custom character, you need:"
    echo "1. A clear photo of the person (preferably headshot)"
    echo "2. A name for the character"
    echo "3. Optional description"
    echo ""
    echo "Example usage:"
    echo "python main.py store-character /path/to/photo.jpg --name 'John Smith' --description 'Male news anchor, professional attire'"
    echo ""
    read -p "Do you have a photo ready to add? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter photo path: " photo_path
        read -p "Enter character name: " char_name
        read -p "Enter description (optional): " description
        
        if [ -n "$description" ]; then
            python main.py store-character "$photo_path" --name "$char_name" --description "$description"
        else
            python main.py store-character "$photo_path" --name "$char_name"
        fi
    fi
    echo ""
}

# Main menu
while true; do
    echo "🎭 Character Management Options:"
    echo "1. Show character storage location"
    echo "2. Test character reference system"
    echo "3. Create professional news anchors (automatic)"
    echo "4. List all characters"
    echo "5. Create custom character (manual)"
    echo "6. Generate test video with character"
    echo "7. Exit"
    echo ""
    
    read -p "Choose an option (1-7): " choice
    echo ""
    
    case $choice in
        1)
            show_storage
            ;;
        2)
            test_system
            ;;
        3)
            create_anchors
            ;;
        4)
            list_characters
            ;;
        5)
            create_custom
            ;;
        6)
            echo "🎬 Generate Test Video with Character"
            echo "-----------------------------------"
            list_characters
            read -p "Enter character ID to use: " char_id
            read -p "Enter scene description: " scene_desc
            echo ""
            echo "Generating test video..."
            python main.py generate \
              --mission "Test video featuring $char_id in $scene_desc setting" \
              --character "$char_id" \
              --scene "$scene_desc" \
              --platform youtube \
              --duration 30 \
              --theme preset_news_edition \
              --no-cheap \
              --session-id "test_character_${char_id}"
            ;;
        7)
            echo "👋 Goodbye!"
            exit 0
            ;;
        *)
            echo "❌ Invalid option. Please choose 1-7."
            ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
    echo ""
done