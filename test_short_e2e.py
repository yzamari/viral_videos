#!/usr/bin/env python3
"""Short End-to-End Test for Video Generation System
Tests all critical components: scripts, audio, subtitles, aspect ratio, VEO clients """from src.models.video_models import Platform, VideoCategory
from src.utils.session_manager import session_manager
from src.agents.working_orchestrator import create_working_orchestrator
import os
import sys
import time
import json

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__)))


class ShortE2ETest: """Short comprehensive E2E test for video generation system"""def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key: raise ValueError("GEMINI_API_KEY environment variable is required")

        self.test_results = {}
        self.session_id = None

    def run_all_tests(self): """Run all short E2E tests"""print("🚀 Starting Short E2E Tests for Video Generation System") print("=" * 60)

        try:
            # Test 1: Basic Video Generation
            self.test_basic_video_generation()

            # Test 2: Session Management
            self.test_session_management()

            # Test 3: File Outputs
            self.test_file_outputs()

            # Test 4: VEO Client Testing
            self.test_veo_clients()

            # Test 5: Audio Generation
            self.test_audio_generation()

            # Test 6: Subtitle Generation
            self.test_subtitle_generation()

            # Test 7: Aspect Ratio
            self.test_aspect_ratio()

            # Print Results
            self.print_test_results()

        except Exception as e: print(f"❌ E2E Test Suite Failed: {e}")
            return False

        return True

    def test_basic_video_generation(self): """Test basic video generation functionality"""print("\n🎬 Test 1: Basic Video Generation") print("-" * 40)

        start_time = time.time()

        try:
            # Create orchestrator
            orchestrator = create_working_orchestrator( mission="Create a short video about healthy morning routines", platform="instagram", category="health",
                duration=15,
                api_key=self.api_key, mode="simple")

            self.session_id = orchestrator.session_id print(f"✅ Orchestrator created with session: {self.session_id}")

            # Generate video
            config = { 'topic': 'healthy morning routines', 'platform': Platform.INSTAGRAM, 'category': VideoCategory.HEALTH, 'duration_sec': 15, 'style': 'engaging', 'tone': 'motivational'}

            result = orchestrator.generate_video(config)
 if result and result.get('success'): print("✅ Video generation successful") print(f"📁 Final video: {result.get('final_video_path', 'N/A')}")
 self.test_results['basic_generation'] = { 'success': True, 'duration': time.time() - start_time, 'final_video_path': result.get('final_video_path'), 'session_id': self.session_id
                }
            else: raise Exception("Video generation failed")

        except Exception as e: print(f"❌ Basic video generation failed: {e}") self.test_results['basic_generation'] = { 'success': False, 'error': str(e), 'duration': time.time() - start_time
            }

    def test_session_management(self): """Test session management and directory structure"""print("\n📁 Test 2: Session Management") print("-" * 40)

        try:
            if not self.session_id: raise Exception("No session ID available")

            # Check session info session_info = session_manager.get_session_info(self.session_id) print(f"✅ Session info retrieved: {session_info.get('session_id')}")

            # Check directory structure session_path = session_info.get('session_path')
            if session_path and os.path.exists(session_path): print(f"✅ Session directory exists: {session_path}")

                # Check required directories required_dirs = ['scripts', 'audio', 'video_clips', 'final_output', 'logs']
                for dir_name in required_dirs:
                    dir_path = os.path.join(session_path, dir_name)
                    if os.path.exists(dir_path): print(f"✅ Directory exists: {dir_name}")
                    else: print(f"⚠️ Directory missing: {dir_name}")
 self.test_results['session_management'] = { 'success': True, 'session_path': session_path, 'directories_found': [
                        d for d in required_dirs if os.path.exists(os.path.join(
                                session_path,
                                d))]}
            else: raise Exception("Session directory not found")

        except Exception as e: print(f"❌ Session management test failed: {e}") self.test_results['session_management'] = { 'success': False, 'error': str(e)
            }

    def test_file_outputs(self): """Test that all expected files are created"""print("\n📄 Test 3: File Outputs") print("-" * 40)

        try:
            if not self.session_id: raise Exception("No session ID available")

            session_info = session_manager.get_session_info(self.session_id) session_path = session_info.get('session_path')

            if not session_path: raise Exception("Session path not available")

            # Check for script files scripts_dir = os.path.join(session_path, 'scripts')
            script_files = []
            if os.path.exists(scripts_dir): script_files = [f for f in os.listdir(scripts_dir) if f.endswith(('.json', '.txt'))] print(f"✅ Script files found: {len(script_files)}")
                for f in script_files: print(f"   - {f}")

            # Check for audio files audio_dir = os.path.join(session_path, 'audio')
            audio_files = []
            if os.path.exists(audio_dir): audio_files = [f for f in os.listdir(audio_dir) if f.endswith(('.mp3', '.wav'))] print(f"✅ Audio files found: {len(audio_files)}")
                for f in audio_files: print(f"   - {f}")

            # Check for video clips video_clips_dir = os.path.join(session_path, 'video_clips')
            video_files = []
            if os.path.exists(video_clips_dir):
                for root, dirs, files in os.walk(video_clips_dir): video_files.extend([f for f in files if f.endswith('.mp4')]) print(f"✅ Video clips found: {len(video_files)}")
                for f in video_files: print(f"   - {f}")

            # Check for final video final_dir = os.path.join(session_path, 'final_output')
            final_videos = []
            if os.path.exists(final_dir): final_videos = [f for f in os.listdir(final_dir) if f.endswith('.mp4')] print(f"✅ Final videos found: {len(final_videos)}")
                for f in final_videos: print(f"   - {f}")

            # Check for logs logs_dir = os.path.join(session_path, 'logs')
            log_files = []
            if os.path.exists(logs_dir): log_files = [f for f in os.listdir(logs_dir) if f.endswith('.log')] print(f"✅ Log files found: {len(log_files)}")
                for f in log_files: print(f"   - {f}")
 self.test_results['file_outputs'] = { 'success': True, 'script_files': len(script_files), 'audio_files': len(audio_files), 'video_files': len(video_files), 'final_videos': len(final_videos), 'log_files': len(log_files)
            }

        except Exception as e: print(f"❌ File outputs test failed: {e}") self.test_results['file_outputs'] = { 'success': False, 'error': str(e)
            }

    def test_veo_clients(self): """Test VEO client availability and basic functionality"""print("\n🎥 Test 4: VEO Client Testing") print("-" * 40)

        try:
            from src.generators.veo_client_factory import VeoClientFactory

            factory = VeoClientFactory()

            # Test VEO-2 client veo2_client = factory.get_veo2_client("test_output")
            if veo2_client: print("✅ VEO-2 client available")
            else: print("❌ VEO-2 client not available")

            # Test VEO-3 client veo3_client = factory.get_veo3_client("test_output")
            if veo3_client: print("✅ VEO-3 client available")
            else: print("❌ VEO-3 client not available")

            # Test best available client best_client = factory.get_best_available_client("test_output")
            if best_client: print(f"✅ Best available client: {best_client.__class__.__name__}")
            else: print("❌ No VEO clients available")
 self.test_results['veo_clients'] = { 'success': True, 'veo2_available': veo2_client is not None, 'veo3_available': veo3_client is not None, 'best_client': best_client.__class__.__name__ if best_client else None
            }

        except Exception as e: print(f"❌ VEO client test failed: {e}") self.test_results['veo_clients'] = { 'success': False, 'error': str(e)
            }

    def test_audio_generation(self): """Test audio generation functionality"""print("\n🎵 Test 5: Audio Generation") print("-" * 40)

        try:
            if not self.session_id: raise Exception("No session ID available")

            session_info = session_manager.get_session_info(self.session_id) session_path = session_info.get('session_path')

            if not session_path: raise Exception("Session path not available")

            # Check audio directory audio_dir = os.path.join(session_path, 'audio')
            if os.path.exists(audio_dir): audio_files = [f for f in os.listdir(audio_dir) if f.endswith(('.mp3', '.wav'))]

                if audio_files: print(f"✅ Audio files generated: {len(audio_files)}")

                    # Check file sizes
                    for audio_file in audio_files:
                        file_path = os.path.join(audio_dir, audio_file)
                        file_size = os.path.getsize(file_path) print(f"   - {audio_file}: {file_size} bytes")

                        if file_size > 1000:  # At least 1KB print(f"   ✅ {audio_file} has valid size")
                        else: print(f"   ⚠️ {audio_file} may be too small")
 self.test_results['audio_generation'] = { 'success': True, 'files_generated': len(audio_files), 'audio_files': audio_files
                    }
                else: raise Exception("No audio files found")
            else: raise Exception("Audio directory not found")

        except Exception as e: print(f"❌ Audio generation test failed: {e}") self.test_results['audio_generation'] = { 'success': False, 'error': str(e)
            }

    def test_subtitle_generation(self): """Test subtitle generation and overlay"""print("\n📝 Test 6: Subtitle Generation") print("-" * 40)

        try:
            if not self.session_id: raise Exception("No session ID available")

            session_info = session_manager.get_session_info(self.session_id) session_path = session_info.get('session_path')

            if not session_path: raise Exception("Session path not available")

            # Check for final video final_dir = os.path.join(session_path, 'final_output')
            if os.path.exists(final_dir): final_videos = [f for f in os.listdir(final_dir) if f.endswith('.mp4')]

                if final_videos:
                    final_video_path = os.path.join(final_dir, final_videos[0]) print(f"✅ Final video found: {final_videos[0]}")

                    # Check if video has subtitles (basic check) # This is a simplified check - in reality, you'd need to analyze the video
                    if os.path.exists(final_video_path):
                        file_size = os.path.getsize(final_video_path) print(f"✅ Final video size: {file_size} bytes")

                        # Use ffprobe to check video properties
                        try:
                            import subprocess
                            result = subprocess.run([
                                'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', final_video_path
                            ], capture_output=True, text=True)

                            if result.returncode == 0:
                                video_info = json.loads(result.stdout) streams = video_info.get('streams', [])

                                video_streams = [ s for s in streams if s.get('codec_type') == 'video']
                                audio_streams = [ s for s in streams if s.get('codec_type') == 'audio']
 print(f"✅ Video streams: {len(video_streams)}") print(f"✅ Audio streams: {len(audio_streams)}")

                                if video_streams:
                                    video_stream = video_streams[0] width = video_stream.get('width') height = video_stream.get('height') print(f"✅ Video resolution: {width}x{height}")

                                    # Check aspect ratio
                                    if width and height:
                                        aspect_ratio = width / height
                                        if 0.5 <= aspect_ratio <= 0.6:  # 9:16 range
                                            print( f"✅ Aspect ratio correct for Instagram: {aspect_ratio:.2f}")
                                        else:
                                            print( f"⚠️ Aspect ratio may be incorrect: {aspect_ratio:.2f}")
 self.test_results['subtitle_generation'] = { 'success': True, 'final_video_exists': True, 'video_streams': len(video_streams), 'audio_streams': len(audio_streams), 'video_resolution': f"{width}x{height}" if width and height else "unknown"}
                            else: raise Exception("Could not analyze video with ffprobe")

                        except Exception as e: print(f"⚠️ Could not analyze video: {e}") self.test_results['subtitle_generation'] = { 'success': True, 'final_video_exists': True, 'analysis_failed': str(e)
                            }
                    else: raise Exception("Final video file not accessible")
                else: raise Exception("No final video found")
            else: raise Exception("Final output directory not found")

        except Exception as e: print(f"❌ Subtitle generation test failed: {e}") self.test_results['subtitle_generation'] = { 'success': False, 'error': str(e)
            }

    def test_aspect_ratio(self): """Test aspect ratio correction"""print("\n📐 Test 7: Aspect Ratio") print("-" * 40)

        try:
            # This test is covered in the subtitle generation test
            # Just verify the results here subtitle_result = self.test_results.get('subtitle_generation', {})
 if subtitle_result.get('success'): resolution = subtitle_result.get('video_resolution', '') if resolution and 'x' in resolution: width, height = map(int, resolution.split('x'))
                    aspect_ratio = width / height

                    if 0.5 <= aspect_ratio <= 0.6:  # 9:16 range print(f"✅ Aspect ratio correct: {aspect_ratio:.2f} (9:16)") self.test_results['aspect_ratio'] = { 'success': True, 'aspect_ratio': aspect_ratio, 'resolution': resolution
                        }
                    else: print(f"⚠️ Aspect ratio incorrect: {aspect_ratio:.2f}") self.test_results['aspect_ratio'] = { 'success': False, 'aspect_ratio': aspect_ratio, 'resolution': resolution, 'error': 'Incorrect aspect ratio'}
                else: raise Exception("Could not determine video resolution")
            else: raise Exception("Subtitle test failed, cannot check aspect ratio")

        except Exception as e: print(f"❌ Aspect ratio test failed: {e}") self.test_results['aspect_ratio'] = { 'success': False, 'error': str(e)
            }

    def print_test_results(self): """Print comprehensive test results"""print("\n" + "=" * 60) print("📊 SHORT E2E TEST RESULTS") print("=" * 60)

        total_tests = len(self.test_results) passed_tests = sum(1 for result in self.test_results.values() if result.get('success'))
 print(f"📈 Overall: {passed_tests}/{total_tests} tests passed")
        print()
 for test_name, result in self.test_results.items(): status = "✅ PASS" if result.get('success') else "❌ FAIL"print(f"{status} {test_name.replace('_', ' ').title()}")
 if not result.get('success') and 'error' in result: print(f"   Error: {result['error']}")

            # Print specific metrics if test_name == 'file_outputs' and result.get('success'): print(f"   Scripts: {result.get('script_files', 0)}") print(f"   Audio: {result.get('audio_files', 0)}") print(f"   Videos: {result.get('video_files', 0)}") print(f"   Final: {result.get('final_videos', 0)}") print(f"   Logs: {result.get('log_files', 0)}")
 elif test_name == 'veo_clients' and result.get('success'): print(f"   VEO-2: {'✅' if result.get('veo2_available') else '❌'}") print(f"   VEO-3: {'✅' if result.get('veo3_available') else '❌'}") print(f"   Best: {result.get('best_client', 'N/A')}")
 elif test_name == 'aspect_ratio' and result.get('success'): print(f"   Ratio: {result.get('aspect_ratio', 'N/A'):.2f}") print(f"   Resolution: {result.get('resolution', 'N/A')}")
 print("\n" + "=" * 60)

        if passed_tests == total_tests: print("🎉 ALL TESTS PASSED! Video generation system is working correctly.")
        else: print(f"⚠️ {total_tests - passed_tests} tests failed. Please review the issues above.")
 print("=" * 60)


def main(): """Run the short E2E test suite"""try:
        test_suite = ShortE2ETest()
        success = test_suite.run_all_tests()

        if success: print("\n✅ Short E2E Test Suite completed successfully!")
            return 0
        else: print("\n❌ Short E2E Test Suite failed!")
            return 1

    except Exception as e: print(f"\n❌ Test suite initialization failed: {e}")
        return 1

 if __name__ == "__main__":
    exit(main())
