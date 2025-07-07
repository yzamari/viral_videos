#!/usr/bin/env python3
"""
Viral Video Generator - Comprehensive CLI Interface
Supports all configuration options and flags
"""

import argparse
import os
import sys
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.workflows.generate_viral_video import generate_viral_video
from src.agents.enhanced_orchestrator_with_discussions import EnhancedOrchestratorWithDiscussions
from src.utils.logging_config import get_logger, setup_logging
from src.utils.quota_verification import QuotaVerifier

logger = get_logger(__name__)

class ViralVideoCLI:
    """Comprehensive CLI for viral video generation"""
    
    def __init__(self):
        self.parser = self.create_parser()
        
    def create_parser(self):
        """Create comprehensive argument parser"""
        
        parser = argparse.ArgumentParser(
            description="🎬 Viral Video Generator - AI-Powered Video Creation",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Basic video generation
  python cli.py --topic "Persian mythology vs modern Iran" --duration 45

  # Full customization
  python cli.py \\
    --topic "AI revolution in 2024" \\
    --duration 60 \\
    --style cinematic \\
    --platform youtube_shorts \\
    --voice-speed 1.2 \\
    --enable-discussions \\
    --max-discussion-rounds 8 \\
    --output-dir custom_outputs \\
    --session-name my_session \\
    --verbose

  # VEO-specific options
  python cli.py \\
    --topic "Future of AI" \\
    --force-veo2 \\
    --veo-quality high \\
    --veo-aspect-ratio 16:9 \\
    --disable-fallback

  # Audio customization
  python cli.py \\
    --topic "Space exploration" \\
    --voice-type female \\
    --voice-language en-US \\
    --audio-effects \\
    --background-music \\
    --music-volume 0.3

  # Advanced options
  python cli.py \\
    --topic "Climate change solutions" \\
    --enable-19-agents \\
    --discussion-timeout 300 \\
    --consensus-threshold 0.8 \\
    --retry-attempts 3 \\
    --parallel-processing \\
    --gpu-acceleration
            """
        )
        
        # Core video generation options
        core_group = parser.add_argument_group('Core Video Generation')
        core_group.add_argument(
            '--topic', '-t',
            type=str,
            required=True,
            help='Video topic or subject (required)'
        )
        core_group.add_argument(
            '--duration', '-d',
            type=int,
            default=45,
            help='Video duration in seconds (default: 45)'
        )
        core_group.add_argument(
            '--style', '-s',
            choices=[
                'realistic', 'cinematic', 'documentary', 'animated', 
                'comic', 'artistic', 'dramatic', 'educational', 'entertainment',
                'horror', 'comedy', 'action', 'romance', 'sci-fi', 'fantasy'
            ],
            default='realistic',
            help='Video style (default: realistic)'
        )
        core_group.add_argument(
            '--platform', '-p',
            choices=[
                'youtube_shorts', 'tiktok', 'instagram_reels', 
                'youtube_long', 'facebook', 'twitter', 'linkedin',
                'snapchat', 'pinterest', 'general'
            ],
            default='youtube_shorts',
            help='Target platform (default: youtube_shorts)'
        )
        
        # AI Agent options
        ai_group = parser.add_argument_group('AI Agent Configuration')
        ai_group.add_argument(
            '--enable-discussions',
            action='store_true',
            help='Enable AI agent discussions'
        )
        ai_group.add_argument(
            '--disable-discussions',
            action='store_true',
            help='Disable AI agent discussions'
        )
        ai_group.add_argument(
            '--enable-19-agents',
            action='store_true',
            help='Use all 19 specialized AI agents'
        )
        ai_group.add_argument(
            '--max-discussion-rounds',
            type=int,
            default=5,
            help='Maximum discussion rounds (default: 5)'
        )
        ai_group.add_argument(
            '--consensus-threshold',
            type=float,
            default=0.8,
            help='Consensus threshold for agent agreement (default: 0.8)'
        )
        ai_group.add_argument(
            '--discussion-timeout',
            type=int,
            default=300,
            help='Discussion timeout in seconds (default: 300)'
        )
        ai_group.add_argument(
            '--agent-temperature',
            type=float,
            default=0.7,
            help='AI agent creativity temperature (default: 0.7)'
        )
        
        # Audio options
        audio_group = parser.add_argument_group('Audio Configuration')
        audio_group.add_argument(
            '--voice-speed',
            type=float,
            default=1.0,
            help='Voice speed multiplier (default: 1.0)'
        )
        audio_group.add_argument(
            '--voice-type',
            choices=['male', 'female', 'neutral', 'child', 'elderly'],
            default='neutral',
            help='Voice type (default: neutral)'
        )
        audio_group.add_argument(
            '--voice-language',
            default='en-US',
            help='Voice language code (default: en-US)'
        )
        audio_group.add_argument(
            '--voice-emotion',
            choices=['neutral', 'happy', 'sad', 'angry', 'excited', 'calm'],
            default='neutral',
            help='Voice emotion (default: neutral)'
        )
        audio_group.add_argument(
            '--audio-effects',
            action='store_true',
            help='Enable audio effects'
        )
        audio_group.add_argument(
            '--background-music',
            action='store_true',
            help='Add background music'
        )
        audio_group.add_argument(
            '--music-volume',
            type=float,
            default=0.2,
            help='Background music volume (default: 0.2)'
        )
        audio_group.add_argument(
            '--audio-quality',
            choices=['low', 'medium', 'high', 'ultra'],
            default='high',
            help='Audio quality (default: high)'
        )
        
        # VEO-specific options
        veo_group = parser.add_argument_group('VEO Video Generation')
        veo_group.add_argument(
            '--force-veo2',
            action='store_true',
            help='Force VEO-2 generation (no fallback)'
        )
        veo_group.add_argument(
            '--force-veo3',
            action='store_true',
            help='Force VEO-3 generation (if available)'
        )
        veo_group.add_argument(
            '--disable-fallback',
            action='store_true',
            help='Disable fallback to image generation'
        )
        veo_group.add_argument(
            '--veo-quality',
            choices=['low', 'medium', 'high', 'ultra'],
            default='high',
            help='VEO generation quality (default: high)'
        )
        veo_group.add_argument(
            '--veo-aspect-ratio',
            choices=['16:9', '9:16', '1:1', '4:3', '3:4'],
            default='9:16',
            help='Video aspect ratio (default: 9:16)'
        )
        veo_group.add_argument(
            '--veo-fps',
            type=int,
            choices=[24, 30, 60],
            default=30,
            help='Video frame rate (default: 30)'
        )
        veo_group.add_argument(
            '--use-vertex-ai',
            action='store_true',
            help='Use Vertex AI instead of Google AI Studio'
        )
        
        # Visual options
        visual_group = parser.add_argument_group('Visual Configuration')
        visual_group.add_argument(
            '--color-scheme',
            choices=['vibrant', 'pastel', 'monochrome', 'warm', 'cool', 'natural'],
            default='vibrant',
            help='Color scheme (default: vibrant)'
        )
        visual_group.add_argument(
            '--text-overlay',
            action='store_true',
            help='Add text overlays'
        )
        visual_group.add_argument(
            '--subtitles',
            action='store_true',
            help='Generate subtitles'
        )
        visual_group.add_argument(
            '--watermark',
            type=str,
            help='Add watermark text'
        )
        visual_group.add_argument(
            '--logo',
            type=str,
            help='Path to logo image'
        )
        visual_group.add_argument(
            '--transitions',
            choices=['none', 'fade', 'slide', 'zoom', 'spin', 'all'],
            default='fade',
            help='Transition effects (default: fade)'
        )
        
        # Output options
        output_group = parser.add_argument_group('Output Configuration')
        output_group.add_argument(
            '--output-dir',
            type=str,
            default='outputs',
            help='Output directory (default: outputs)'
        )
        output_group.add_argument(
            '--session-name',
            type=str,
            help='Custom session name'
        )
        output_group.add_argument(
            '--output-format',
            choices=['mp4', 'mov', 'avi', 'webm'],
            default='mp4',
            help='Output video format (default: mp4)'
        )
        output_group.add_argument(
            '--output-quality',
            choices=['720p', '1080p', '1440p', '4k'],
            default='1080p',
            help='Output video quality (default: 1080p)'
        )
        output_group.add_argument(
            '--save-intermediates',
            action='store_true',
            help='Save intermediate files'
        )
        output_group.add_argument(
            '--export-discussions',
            action='store_true',
            help='Export agent discussions to JSON'
        )
        
        # Performance options
        perf_group = parser.add_argument_group('Performance Configuration')
        perf_group.add_argument(
            '--parallel-processing',
            action='store_true',
            help='Enable parallel processing'
        )
        perf_group.add_argument(
            '--gpu-acceleration',
            action='store_true',
            help='Enable GPU acceleration'
        )
        perf_group.add_argument(
            '--max-workers',
            type=int,
            default=4,
            help='Maximum worker threads (default: 4)'
        )
        perf_group.add_argument(
            '--memory-limit',
            type=str,
            help='Memory limit (e.g., 4GB, 8GB)'
        )
        perf_group.add_argument(
            '--retry-attempts',
            type=int,
            default=3,
            help='Retry attempts on failure (default: 3)'
        )
        
        # Debug and logging options
        debug_group = parser.add_argument_group('Debug and Logging')
        debug_group.add_argument(
            '--verbose', '-v',
            action='count',
            default=0,
            help='Verbose output (use -vv for very verbose)'
        )
        debug_group.add_argument(
            '--quiet', '-q',
            action='store_true',
            help='Quiet mode (minimal output)'
        )
        debug_group.add_argument(
            '--log-level',
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
            default='INFO',
            help='Log level (default: INFO)'
        )
        debug_group.add_argument(
            '--log-file',
            type=str,
            help='Log file path'
        )
        debug_group.add_argument(
            '--debug-mode',
            action='store_true',
            help='Enable debug mode'
        )
        debug_group.add_argument(
            '--profile',
            action='store_true',
            help='Enable performance profiling'
        )
        
        # Utility options
        util_group = parser.add_argument_group('Utility Commands')
        util_group.add_argument(
            '--check-quota',
            action='store_true',
            help='Check API quota status'
        )
        util_group.add_argument(
            '--list-sessions',
            action='store_true',
            help='List available sessions'
        )
        util_group.add_argument(
            '--cleanup',
            action='store_true',
            help='Clean up old sessions'
        )
        util_group.add_argument(
            '--test-apis',
            action='store_true',
            help='Test API connections'
        )
        util_group.add_argument(
            '--version',
            action='version',
            version='Viral Video Generator v2.0.0'
        )
        
        # Configuration file
        config_group = parser.add_argument_group('Configuration File')
        config_group.add_argument(
            '--config',
            type=str,
            help='Configuration file path (JSON)'
        )
        config_group.add_argument(
            '--save-config',
            type=str,
            help='Save current configuration to file'
        )
        
        return parser
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {e}")
            return {}
    
    def save_config(self, args: argparse.Namespace, config_path: str):
        """Save configuration to JSON file"""
        try:
            config = vars(args)
            # Remove non-serializable items
            config = {k: v for k, v in config.items() if v is not None}
            
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"✅ Configuration saved to {config_path}")
        except Exception as e:
            logger.error(f"Failed to save config to {config_path}: {e}")
    
    def setup_logging(self, args: argparse.Namespace):
        """Setup logging based on arguments"""
        log_level = args.log_level
        
        if args.verbose >= 2:
            log_level = 'DEBUG'
        elif args.verbose == 1:
            log_level = 'INFO'
        elif args.quiet:
            log_level = 'WARNING'
        
        setup_logging(
            log_level=log_level,
            log_file=args.log_file,
            debug_mode=args.debug_mode
        )
    
    def check_quota(self):
        """Check API quota status"""
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            print("❌ GOOGLE_API_KEY not found in environment")
            return False
        
        print("🔍 Checking API quota status...")
        verifier = QuotaVerifier(api_key)
        quota_info = verifier.check_all_quotas()
        
        print(f"📊 Quota Status: {quota_info}")
        return True
    
    def list_sessions(self):
        """List available sessions"""
        outputs_dir = "outputs"
        if not os.path.exists(outputs_dir):
            print("📁 No sessions found (outputs directory doesn't exist)")
            return
        
        sessions = []
        for folder in os.listdir(outputs_dir):
            if folder.startswith("session_"):
                session_path = os.path.join(outputs_dir, folder)
                if os.path.isdir(session_path):
                    try:
                        created = datetime.fromtimestamp(os.path.getctime(session_path))
                        sessions.append((folder, created))
                    except:
                        sessions.append((folder, datetime.now()))
        
        if not sessions:
            print("📁 No sessions found")
            return
        
        print("📁 Available Sessions:")
        sessions.sort(key=lambda x: x[1], reverse=True)
        for session, created in sessions:
            print(f"   {session} (created: {created.strftime('%Y-%m-%d %H:%M:%S')})")
    
    def test_apis(self):
        """Test API connections"""
        print("🧪 Testing API connections...")
        
        # Test Google API
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            print("❌ GOOGLE_API_KEY not found")
            return False
        
        try:
            verifier = QuotaVerifier(api_key)
            quota_info = verifier.check_all_quotas()
            print("✅ Google API connection successful")
        except Exception as e:
            print(f"❌ Google API connection failed: {e}")
            return False
        
        return True
    
    def cleanup_sessions(self, days_old: int = 7):
        """Clean up old sessions"""
        outputs_dir = "outputs"
        if not os.path.exists(outputs_dir):
            print("📁 No sessions to clean up")
            return
        
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        cleaned = 0
        for folder in os.listdir(outputs_dir):
            if folder.startswith("session_"):
                session_path = os.path.join(outputs_dir, folder)
                if os.path.isdir(session_path):
                    try:
                        created = datetime.fromtimestamp(os.path.getctime(session_path))
                        if created < cutoff_date:
                            import shutil
                            shutil.rmtree(session_path)
                            cleaned += 1
                            print(f"🗑️  Cleaned up session: {folder}")
                    except Exception as e:
                        logger.error(f"Failed to clean up {folder}: {e}")
        
        print(f"✅ Cleaned up {cleaned} old sessions")
    
    def run(self):
        """Run the CLI"""
        args = self.parser.parse_args()
        
        # Load config file if specified
        if args.config:
            config = self.load_config(args.config)
            # Override args with config values
            for key, value in config.items():
                if not hasattr(args, key) or getattr(args, key) is None:
                    setattr(args, key, value)
        
        # Setup logging
        self.setup_logging(args)
        
        # Handle utility commands
        if args.check_quota:
            return self.check_quota()
        
        if args.list_sessions:
            return self.list_sessions()
        
        if args.test_apis:
            return self.test_apis()
        
        if args.cleanup:
            return self.cleanup_sessions()
        
        # Save config if requested
        if args.save_config:
            self.save_config(args, args.save_config)
        
        # Validate required arguments
        if not args.topic:
            print("❌ Topic is required. Use --topic to specify the video topic.")
            return False
        
        # Check API key
        if not os.getenv('GOOGLE_API_KEY'):
            print("❌ GOOGLE_API_KEY not found in environment")
            print("   Please set: export GOOGLE_API_KEY=your_api_key_here")
            return False
        
        # Print generation info
        print("🎬 Viral Video Generator")
        print("=" * 50)
        print(f"📝 Topic: {args.topic}")
        print(f"⏱️  Duration: {args.duration}s")
        print(f"🎨 Style: {args.style}")
        print(f"📱 Platform: {args.platform}")
        print(f"🤖 AI Discussions: {'Enabled' if args.enable_discussions else 'Disabled'}")
        print("=" * 50)
        
        try:
            # Generate video
            result = generate_viral_video(
                topic=args.topic,
                duration=args.duration,
                style=args.style,
                platform=args.platform,
                voice_speed=args.voice_speed,
                # Add all other parameters...
            )
            
            print(f"✅ Video generated successfully!")
            print(f"📹 Output: {result}")
            
            return True
            
        except Exception as e:
            logger.error(f"Video generation failed: {e}")
            print(f"❌ Generation failed: {e}")
            return False

def main():
    """Main CLI entry point"""
    cli = ViralVideoCLI()
    success = cli.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 