#!/bin/bash
echo "📊 Monitoring PizzaIDF cinematic generation (PID: 58975)..."
echo "=================================================="

while true; do
    # Check if process is still running
    if ! ps -p 58975 > /dev/null; then
        echo "✅ Process completed!"
        break
    fi
    
    # Show latest log entries
    echo -e "\n📄 Latest activity ($(date '+%H:%M:%S')):"
    tail -n 5 pizzaidf_cinematic_output.log 2>/dev/null | grep -E "🎬|✅|⚠️|❌|🎯|📊|⏱️" || echo "Waiting for output..."
    
    # Check for session directory
    SESSION_DIR=$(ls -td outputs/session_* 2>/dev/null | head -1)
    if [ -n "$SESSION_DIR" ]; then
        echo -e "\n📁 Session: $SESSION_DIR"
        
        # Check for final video
        if [ -f "$SESSION_DIR/final_video/"*_final.mp4 ]; then
            echo "🎥 Final video created!"
            ls -lh "$SESSION_DIR/final_video/"*_final.mp4
        fi
    fi
    
    sleep 10
done

echo -e "\n🏁 Generation complete! Check the output log for details."