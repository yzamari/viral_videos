"""
FFmpeg utilities for hardware acceleration and optimized video processing
"""
import subprocess
import platform
from typing import List, Optional
from ..utils.logging_config import get_logger

logger = get_logger(__name__)

class FFmpegAcceleration:
    """Manages FFmpeg hardware acceleration options"""
    
    @staticmethod
    def get_hw_accel_flags() -> List[str]:
        """Get hardware acceleration flags based on the platform"""
        system = platform.system().lower()
        
        if system == 'darwin':  # macOS
            # Use VideoToolbox for hardware acceleration on macOS
            return ['-hwaccel', 'videotoolbox']
        elif system == 'linux':
            # Check for NVIDIA GPU
            try:
                result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
                if result.returncode == 0:
                    return ['-hwaccel', 'cuda']
            except:
                pass
            # Fallback to VAAPI
            return ['-hwaccel', 'vaapi']
        elif system == 'windows':
            # Try NVIDIA first, then Intel QuickSync
            try:
                result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
                if result.returncode == 0:
                    return ['-hwaccel', 'cuda']
            except:
                pass
            return ['-hwaccel', 'qsv']
        
        # No hardware acceleration
        return []
    
    @staticmethod
    def get_hw_encoder(codec: str = 'h264') -> Optional[str]:
        """Get hardware encoder based on platform and codec"""
        system = platform.system().lower()
        
        if codec == 'h264':
            if system == 'darwin':
                return 'h264_videotoolbox'
            elif system == 'linux':
                # Check for NVIDIA
                try:
                    result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
                    if result.returncode == 0:
                        return 'h264_nvenc'
                except:
                    pass
                return 'h264_vaapi'
            elif system == 'windows':
                try:
                    result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
                    if result.returncode == 0:
                        return 'h264_nvenc'
                except:
                    pass
                return 'h264_qsv'
        
        # Fallback to software encoder
        return f'lib{codec}'
    
    @staticmethod
    def get_optimized_ffmpeg_base() -> List[str]:
        """Get optimized FFmpeg base command with hardware acceleration"""
        base_cmd = ['ffmpeg', '-y']
        
        # Add hardware acceleration flags
        hw_flags = FFmpegAcceleration.get_hw_accel_flags()
        if hw_flags:
            base_cmd.extend(hw_flags)
            logger.info(f"🚀 Using hardware acceleration: {' '.join(hw_flags)}")
        
        return base_cmd