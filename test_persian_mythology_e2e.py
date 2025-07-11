#!/usr/bin/env python3
"""
End-to-End Test: Persian Mythology Characters - VEO2 Continuous Generation
Tests the complete video generation pipeline with 5 random Persian mythology missions
"""

import os
import sys
import random
import time
import logging
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.agents.working_orchestrator import create_working_orchestrator
from src.utils.comprehensive_logger import ComprehensiveLogger
from config.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PersianMythologyE2ETest:
    """End-to-End test for Persian mythology video generation"""
    
    def __init__(self):
        self.config = settings
        self.results = []
        self.start_time = time.time()
        
        # Persian mythology characters and their stories
        self.persian_mythology_missions = [
            {
                "character": "Rostam",
                "mission": "Create a viral video about Rostam, the legendary Persian hero from Shahnameh, showcasing his incredible strength, his battles with demons, and his tragic relationship with his son Sohrab. Focus on his seven labors and epic adventures.",
                "target_audience": "mythology enthusiasts and Persian culture lovers",
                "hook": "The strongest hero in Persian mythology"
            },
            {
                "character": "Simurgh",
                "mission": "Generate an engaging video about the Simurgh, the benevolent mythical bird in Persian mythology. Show its wisdom, healing powers, and role as a guide for heroes. Highlight its connection to the Tree of Life.",
                "target_audience": "fantasy lovers and spiritual seekers",
                "hook": "The mystical bird that grants wisdom"
            },
            {
                "character": "Ahriman",
                "mission": "Create a dramatic video about Ahriman, the destructive spirit of evil in Zoroastrian mythology. Showcase the eternal battle between light and darkness, good and evil, with Ahura Mazda.",
                "target_audience": "mythology and philosophy enthusiasts",
                "hook": "The ancient force of darkness and chaos"
            },
            {
                "character": "Fereydun",
                "mission": "Produce a heroic video about Fereydun, the legendary king who defeated the tyrant Zahhak. Show his rise to power, his magical mace, and how he brought peace to the Persian empire.",
                "target_audience": "history buffs and mythology fans",
                "hook": "The king who defeated the serpent tyrant"
            },
            {
                "character": "Jamshid",
                "mission": "Create an epic video about Jamshid, the fourth king of the world in Persian mythology. Showcase his golden age, his magical throne that could fly, and his tragic fall from grace due to pride.",
                "target_audience": "mythology enthusiasts and history lovers",
                "hook": "The king with a flying throne who ruled the golden age"
            },
            {
                "character": "Zahhak",
                "mission": "Generate a dark and mysterious video about Zahhak, the tyrant king with serpents growing from his shoulders. Show his pact with Ahriman, his thousand-year reign of terror, and his ultimate defeat.",
                "target_audience": "dark fantasy and mythology fans",
                "hook": "The serpent-shouldered tyrant who ruled through fear"
            },
            {
                "character": "Kaveh",
                "mission": "Create an inspiring video about Kaveh the Blacksmith, the folk hero who led the rebellion against Zahhak. Show his leather apron becoming the royal banner and his fight for justice.",
                "target_audience": "social justice advocates and mythology fans",
                "hook": "The blacksmith who became a revolutionary hero"
            },
            {
                "character": "Manuchehr",
                "mission": "Produce a royal video about Manuchehr, the wise and just king of Persia. Showcase his diplomatic skills, his establishment of laws, and his role in bringing civilization to the ancient world.",
                "target_audience": "leadership enthusiasts and history buffs",
                "hook": "The wise king who established the laws of civilization"
            },
            {
                "character": "Tahmineh",
                "mission": "Create a powerful video about Tahmineh, the warrior princess and mother of Sohrab. Show her strength, her love story with Rostam, and her role in the tragic tale of father and son.",
                "target_audience": "feminist mythology enthusiasts",
                "hook": "The warrior princess who loved the greatest hero"
            },
            {
                "character": "Arash",
                "mission": "Generate an epic video about Arash the Archer, who shot an arrow to determine the border between Iran and Turan. Show his ultimate sacrifice and how his arrow flew for three days.",
                "target_audience": "archery enthusiasts and mythology fans",
                "hook": "The archer whose arrow flew for three days"
            }
        ]
    
    def select_random_missions(self, count=5):
        """Select random missions for testing"""
        selected = random.sample(self.persian_mythology_missions, count)
        logger.info(f"🎯 Selected {count} random Persian mythology missions:")
        for i, mission in enumerate(selected, 1):
            logger.info(f"  {i}. {mission['character']}: {mission['hook']}")
        return selected
    
    def run_single_mission(self, mission_data, mission_num):
        """Run a single video generation mission"""
        character = mission_data['character']
        mission = mission_data['mission']
        
        logger.info(f"\n🎬 MISSION {mission_num}: {character}")
        logger.info(f"📝 Mission: {mission}")
        
        mission_start = time.time()
        
        try:
            # Create orchestrator for this mission
            from src.models.video_models import Platform, VideoCategory
            
            orchestrator = create_working_orchestrator(
                api_key=self.config.google_api_key,
                topic=mission,
                platform='youtube',
                category='education',
                duration=30
            )
            
            # Generate video with enhanced parameters
            result = orchestrator.generate_video({
                'style': 'cinematic',
                'target_audience': mission_data['target_audience'],
                'force_generation': 'images_and_video',
                'frame_continuity': 'on',
                'language': 'en-US'
            })
            
            mission_time = time.time() - mission_start
            
            if result and result.get('success') and result.get('final_video_path'):
                video_path = result['final_video_path']
                file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
                
                result_data = {
                    'mission_num': mission_num,
                    'character': character,
                    'status': 'SUCCESS',
                    'video_path': video_path,
                    'duration': mission_time,
                    'file_size_mb': round(file_size, 2),
                    'error': None
                }
                
                logger.info(f"✅ Mission {mission_num} SUCCESS: {character}")
                logger.info(f"   📹 Video: {video_path}")
                logger.info(f"   ⏱️  Time: {mission_time:.1f}s")
                logger.info(f"   📊 Size: {file_size:.1f}MB")
                
            else:
                result_data = {
                    'mission_num': mission_num,
                    'character': character,
                    'status': 'FAILED',
                    'video_path': None,
                    'duration': mission_time,
                    'file_size_mb': 0,
                    'error': 'No video generated'
                }
                
                logger.error(f"❌ Mission {mission_num} FAILED: {character}")
                
        except Exception as e:
            mission_time = time.time() - mission_start
            result_data = {
                'mission_num': mission_num,
                'character': character,
                'status': 'ERROR',
                'video_path': None,
                'duration': mission_time,
                'file_size_mb': 0,
                'error': str(e)
            }
            
            logger.error(f"💥 Mission {mission_num} ERROR: {character}")
            logger.error(f"   Error: {str(e)}")
        
        self.results.append(result_data)
        return result_data
    
    def run_all_missions(self):
        """Run all 5 random missions"""
        logger.info("🚀 Starting Persian Mythology E2E Test")
        logger.info("=" * 60)
        
        # Select 5 random missions
        selected_missions = self.select_random_missions(5)
        
        # Run each mission
        for i, mission_data in enumerate(selected_missions, 1):
            self.run_single_mission(mission_data, i)
            
            # Brief pause between missions
            if i < len(selected_missions):
                logger.info(f"⏸️  Pausing 10 seconds before next mission...")
                time.sleep(10)
    
    def generate_final_report(self):
        """Generate comprehensive test report"""
        total_time = time.time() - self.start_time
        
        successful = [r for r in self.results if r['status'] == 'SUCCESS']
        failed = [r for r in self.results if r['status'] in ['FAILED', 'ERROR']]
        
        success_rate = len(successful) / len(self.results) * 100
        total_size = sum(r['file_size_mb'] for r in successful)
        avg_time = sum(r['duration'] for r in self.results) / len(self.results)
        
        logger.info("\n" + "=" * 80)
        logger.info("🏆 PERSIAN MYTHOLOGY E2E TEST FINAL REPORT")
        logger.info("=" * 80)
        
        logger.info(f"📊 OVERALL STATISTICS:")
        logger.info(f"   Total Missions: {len(self.results)}")
        logger.info(f"   Successful: {len(successful)}")
        logger.info(f"   Failed: {len(failed)}")
        logger.info(f"   Success Rate: {success_rate:.1f}%")
        logger.info(f"   Total Time: {total_time:.1f}s ({total_time/60:.1f} minutes)")
        logger.info(f"   Average Time per Mission: {avg_time:.1f}s")
        logger.info(f"   Total Video Size: {total_size:.1f}MB")
        
        logger.info(f"\n🎯 MISSION DETAILS:")
        for result in self.results:
            status_icon = "✅" if result['status'] == 'SUCCESS' else "❌"
            logger.info(f"   {status_icon} Mission {result['mission_num']}: {result['character']}")
            logger.info(f"      Status: {result['status']}")
            logger.info(f"      Time: {result['duration']:.1f}s")
            if result['video_path']:
                logger.info(f"      Video: {result['video_path']}")
                logger.info(f"      Size: {result['file_size_mb']}MB")
            if result['error']:
                logger.info(f"      Error: {result['error']}")
        
        if successful:
            logger.info(f"\n🎬 GENERATED VIDEOS:")
            for result in successful:
                logger.info(f"   📹 {result['character']}: {result['video_path']}")
        
        # Test assessment
        if success_rate >= 80:
            logger.info(f"\n🏆 TEST ASSESSMENT: EXCELLENT ({success_rate:.1f}% success rate)")
        elif success_rate >= 60:
            logger.info(f"\n👍 TEST ASSESSMENT: GOOD ({success_rate:.1f}% success rate)")
        elif success_rate >= 40:
            logger.info(f"\n⚠️  TEST ASSESSMENT: NEEDS IMPROVEMENT ({success_rate:.1f}% success rate)")
        else:
            logger.info(f"\n❌ TEST ASSESSMENT: POOR ({success_rate:.1f}% success rate)")
        
        logger.info("=" * 80)
        
        return {
            'total_missions': len(self.results),
            'successful': len(successful),
            'failed': len(failed),
            'success_rate': success_rate,
            'total_time': total_time,
            'results': self.results
        }

def main():
    """Main test execution"""
    print("🏛️  Persian Mythology VEO2 E2E Test Suite")
    print("Testing continuous video generation with 5 random mythology characters")
    print("=" * 80)
    
    # Initialize and run test
    test = PersianMythologyE2ETest()
    
    try:
        # Run all missions
        test.run_all_missions()
        
        # Generate final report
        final_report = test.generate_final_report()
        
        # Return appropriate exit code
        if final_report['success_rate'] >= 80:
            print("\n🎉 Test completed successfully!")
            sys.exit(0)
        else:
            print("\n⚠️  Test completed with issues.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("\n🛑 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n💥 Test failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 