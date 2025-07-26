#!/bin/bash

# Monitor script to check progress of all three running scripts

echo "📊 Video Generation Monitor"
echo "=========================="
echo "Monitoring 3 scripts every 60 seconds"
echo ""

while true; do
    clear
    echo "📊 VIDEO GENERATION MONITOR - $(date)"
    echo "============================================"
    
    # Check Israeli PM Series
    echo -e "\n🦸 ISRAELI PM MARVEL SERIES:"
    pm_pids=$(pgrep -f "run_israeli_pm_multilang.sh")
    if [ -n "$pm_pids" ]; then
        echo "   Status: 🟢 RUNNING (PID: $pm_pids)"
        # Check which episode
        pm_dirs=$(ls -d outputs/pm_marvel_ep* 2>/dev/null | wc -l)
        echo "   Episodes completed: $pm_dirs/3"
        # Check for language files
        for ep in 1 2 3; do
            if [ -d "outputs/pm_marvel_ep${ep}_*/languages" ]; then
                lang_count=$(ls outputs/pm_marvel_ep${ep}_*/languages 2>/dev/null | grep -E "(en_US|he)" | wc -l)
                echo "   Episode $ep languages: $lang_count/2"
            fi
        done
    else
        echo "   Status: ⭕ NOT RUNNING or COMPLETED"
        pm_complete=$(ls -d outputs/pm_marvel_ep* 2>/dev/null | wc -l)
        echo "   Episodes found: $pm_complete/3"
    fi
    
    # Check Nuclear News Series
    echo -e "\n☢️  NUCLEAR NEWS SERIES:"
    nuclear_pids=$(pgrep -f "run_nuclear_news_multilang.sh")
    if [ -n "$nuclear_pids" ]; then
        echo "   Status: 🟢 RUNNING (PID: $nuclear_pids)"
        nuclear_dirs=$(ls -d outputs/nuclear_news_ep* 2>/dev/null | wc -l)
        echo "   Episodes completed: $nuclear_dirs/3"
        # Check for language files
        for ep in 1 2 3; do
            if [ -d "outputs/nuclear_news_ep${ep}/languages" ]; then
                lang_count=$(ls outputs/nuclear_news_ep${ep}/languages 2>/dev/null | grep -E "(en_US|he)" | wc -l)
                echo "   Episode $ep languages: $lang_count/2"
            fi
        done
    else
        echo "   Status: ⭕ NOT RUNNING or COMPLETED"
        nuclear_complete=$(ls -d outputs/nuclear_news_ep* 2>/dev/null | wc -l)
        echo "   Episodes found: $nuclear_complete/3"
    fi
    
    # Check Iranian Water Crisis Series
    echo -e "\n💧 IRANIAN WATER CRISIS SERIES:"
    water_pids=$(pgrep -f "run_iranian_news_multilang.sh")
    if [ -n "$water_pids" ]; then
        echo "   Status: 🟢 RUNNING (PID: $water_pids)"
        water_dirs=$(ls -d outputs/water_crisis_ep* 2>/dev/null | wc -l)
        echo "   Episodes completed: $water_dirs/3"
        # Check for language files
        for ep in 1 2 3; do
            if [ -d "outputs/water_crisis_ep${ep}/languages" ]; then
                lang_count=$(ls outputs/water_crisis_ep${ep}/languages 2>/dev/null | grep -E "(en_US|he)" | wc -l)
                echo "   Episode $ep languages: $lang_count/2"
            fi
        done
    else
        echo "   Status: ⭕ NOT RUNNING or COMPLETED"
        water_complete=$(ls -d outputs/water_crisis_ep* 2>/dev/null | wc -l)
        echo "   Episodes found: $water_complete/3"
    fi
    
    # Check for VEO clips
    echo -e "\n🎬 VEO GENERATION STATUS:"
    veo_count=$(find outputs -name "veo_*.mp4" -mmin -60 2>/dev/null | wc -l)
    echo "   VEO clips generated in last hour: $veo_count"
    
    # Check system resources
    echo -e "\n💻 SYSTEM RESOURCES:"
    echo -n "   CPU Usage: "
    top -l 1 | grep "CPU usage" | awk '{print $3}'
    echo -n "   Memory: "
    top -l 1 | grep "PhysMem" | awk '{print $2, $4}'
    
    # Running python processes
    python_count=$(pgrep -f "python3 main.py" | wc -l)
    echo "   Active video generations: $python_count"
    
    echo -e "\n============================================"
    echo "Next update in 60 seconds... (Press Ctrl+C to stop)"
    
    sleep 60
done