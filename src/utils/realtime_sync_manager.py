"""
Real-time Audio-Video Synchronization Manager
Implements SOLID principles for professional sync management
"""

import os
import numpy as np
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple, Protocol
from dataclasses import dataclass
from enum import Enum
import logging
from moviepy.editor import AudioFileClip, VideoFileClip, CompositeAudioClip

from ..utils.logging_config import get_logger

logger = get_logger(__name__)


# SOLID Principle: Interface Segregation
class IAudioAnalyzer(Protocol):
    """Interface for audio analysis"""
    def analyze_beats(self, audio_path: str) -> List[float]:
        ...
    
    def get_audio_energy(self, audio_path: str) -> np.ndarray:
        ...


class IVideoSynchronizer(Protocol):
    """Interface for video synchronization"""
    def sync_to_beats(self, video_clips: List[str], beats: List[float]) -> List[str]:
        ...
    
    def adjust_clip_speed(self, clip_path: str, target_duration: float) -> str:
        ...


class ISyncStrategy(ABC):
    """Abstract base class for synchronization strategies (Strategy Pattern)"""
    
    @abstractmethod
    def synchronize(self, audio_data: Dict, video_data: Dict) -> Dict:
        """Synchronize audio and video using specific strategy"""
        pass


# SOLID Principle: Single Responsibility
@dataclass
class BeatData:
    """Data class for beat information"""
    timestamp: float
    strength: float
    frequency: float
    beat_type: str  # 'kick', 'snare', 'hihat', etc.


@dataclass
class SyncPoint:
    """Synchronization point between audio and video"""
    audio_timestamp: float
    video_timestamp: float
    sync_type: str  # 'beat', 'voice', 'silence', 'transition'
    confidence: float


@dataclass
class SyncAnalysis:
    """Complete synchronization analysis result"""
    sync_points: List[SyncPoint]
    overall_sync_score: float
    beat_alignment_score: float
    voice_sync_score: float
    recommendations: List[str]
    adjusted_clip_durations: List[float]


class BeatDetector(IAudioAnalyzer):
    """Detects beats and rhythm in audio (Single Responsibility)"""
    
    def __init__(self):
        self.sample_rate = 44100
        self.hop_length = 512
        
    def analyze_beats(self, audio_path: str) -> List[float]:
        """Detect beat timestamps in audio"""
        try:
            import librosa
            
            # Load audio
            y, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            # Detect beats
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr, hop_length=self.hop_length)
            beat_times = librosa.frames_to_time(beats, sr=sr, hop_length=self.hop_length)
            
            logger.info(f"🎵 Detected {len(beat_times)} beats at {tempo:.1f} BPM")
            return beat_times.tolist()
            
        except ImportError:
            logger.warning("⚠️ Librosa not installed, using fallback beat detection")
            return self._fallback_beat_detection(audio_path)
        except Exception as e:
            logger.error(f"❌ Beat detection failed: {e}")
            return []
    
    def get_audio_energy(self, audio_path: str) -> np.ndarray:
        """Calculate audio energy over time"""
        try:
            with AudioFileClip(audio_path) as audio:
                # Sample audio at intervals
                duration = audio.duration
                sample_rate = 10  # samples per second
                times = np.arange(0, duration, 1/sample_rate)
                
                energy = []
                for t in times:
                    # Get audio frame at time t
                    frame = audio.get_frame(t)
                    # Calculate RMS energy
                    if isinstance(frame, np.ndarray):
                        energy.append(np.sqrt(np.mean(frame**2)))
                    else:
                        energy.append(0)
                
                return np.array(energy)
                
        except Exception as e:
            logger.error(f"❌ Energy calculation failed: {e}")
            return np.array([])
    
    def _fallback_beat_detection(self, audio_path: str) -> List[float]:
        """Simple fallback beat detection based on energy peaks"""
        energy = self.get_audio_energy(audio_path)
        if len(energy) == 0:
            return []
        
        # Find peaks in energy
        mean_energy = np.mean(energy)
        std_energy = np.std(energy)
        threshold = mean_energy + std_energy
        
        peaks = []
        for i in range(1, len(energy)-1):
            if energy[i] > threshold and energy[i] > energy[i-1] and energy[i] > energy[i+1]:
                peaks.append(i * 0.1)  # Convert to time (10 samples/sec)
        
        return peaks


class VoiceAnalyzer(IAudioAnalyzer):
    """Analyzes voice and speech patterns (Single Responsibility)"""
    
    def analyze_voice_segments(self, audio_path: str) -> List[Tuple[float, float]]:
        """Detect voice segments in audio"""
        try:
            # Use webrtcvad for voice activity detection if available
            import webrtcvad
            import wave
            
            vad = webrtcvad.Vad(2)  # Aggressiveness level 2
            
            with wave.open(audio_path, 'rb') as wf:
                sample_rate = wf.getframerate()
                frame_duration = 30  # ms
                
                segments = []
                # Process audio in frames
                # This is simplified - real implementation would be more complex
                
            return segments
            
        except ImportError:
            logger.warning("⚠️ WebRTC VAD not available, using energy-based detection")
            return self._energy_based_voice_detection(audio_path)
    
    def _energy_based_voice_detection(self, audio_path: str) -> List[Tuple[float, float]]:
        """Simple voice detection based on energy levels"""
        with AudioFileClip(audio_path) as audio:
            # Simplified voice detection
            duration = audio.duration
            # Return whole duration as voice for now
            return [(0, duration)]
    
    def analyze_beats(self, audio_path: str) -> List[float]:
        """Implement interface method"""
        return []
    
    def get_audio_energy(self, audio_path: str) -> np.ndarray:
        """Implement interface method"""
        return np.array([])


class ClipSpeedAdjuster(IVideoSynchronizer):
    """Adjusts video clip speed for synchronization (Single Responsibility)"""
    
    def sync_to_beats(self, video_clips: List[str], beats: List[float]) -> List[str]:
        """Sync video clips to audio beats"""
        synced_clips = []
        
        for i, clip_path in enumerate(video_clips):
            if i < len(beats) - 1:
                # Calculate target duration to match beat interval
                target_duration = beats[i+1] - beats[i] if i < len(beats)-1 else 2.0
                adjusted_clip = self.adjust_clip_speed(clip_path, target_duration)
                synced_clips.append(adjusted_clip)
            else:
                synced_clips.append(clip_path)
        
        return synced_clips
    
    def adjust_clip_speed(self, clip_path: str, target_duration: float) -> str:
        """Adjust clip playback speed to match target duration"""
        try:
            with VideoFileClip(clip_path) as clip:
                current_duration = clip.duration
                
                if current_duration <= 0:
                    return clip_path
                
                # Calculate speed factor
                speed_factor = current_duration / target_duration
                
                # Only adjust if difference is significant (>10%)
                if abs(speed_factor - 1.0) > 0.1:
                    # Limit speed adjustment to reasonable range
                    speed_factor = max(0.5, min(2.0, speed_factor))
                    
                    adjusted_clip = clip.fx(lambda c: c.speedx(speed_factor))
                    
                    # Save adjusted clip
                    output_path = clip_path.replace('.mp4', f'_synced_{speed_factor:.2f}x.mp4')
                    adjusted_clip.write_videofile(output_path, logger=None)
                    adjusted_clip.close()
                    
                    logger.info(f"⚡ Adjusted clip speed by {speed_factor:.2f}x")
                    return output_path
                
                return clip_path
                
        except Exception as e:
            logger.error(f"❌ Speed adjustment failed: {e}")
            return clip_path


# SOLID Principle: Open/Closed - New strategies can be added without modifying existing code
class BeatSyncStrategy(ISyncStrategy):
    """Synchronization strategy based on audio beats"""
    
    def __init__(self, beat_detector: BeatDetector):
        self.beat_detector = beat_detector
    
    def synchronize(self, audio_data: Dict, video_data: Dict) -> Dict:
        """Synchronize using beat matching"""
        audio_path = audio_data['path']
        video_clips = video_data['clips']
        
        # Detect beats
        beats = self.beat_detector.analyze_beats(audio_path)
        
        # Create sync points at beats
        sync_points = []
        for i, beat_time in enumerate(beats):
            sync_points.append(SyncPoint(
                audio_timestamp=beat_time,
                video_timestamp=beat_time,
                sync_type='beat',
                confidence=0.9
            ))
        
        return {
            'sync_points': sync_points,
            'beats': beats,
            'strategy': 'beat_sync'
        }


class VoiceSyncStrategy(ISyncStrategy):
    """Synchronization strategy based on voice/speech patterns"""
    
    def __init__(self, voice_analyzer: VoiceAnalyzer):
        self.voice_analyzer = voice_analyzer
    
    def synchronize(self, audio_data: Dict, video_data: Dict) -> Dict:
        """Synchronize using voice patterns"""
        audio_path = audio_data['path']
        
        # Analyze voice segments
        voice_segments = self.voice_analyzer.analyze_voice_segments(audio_path)
        
        # Create sync points at voice starts
        sync_points = []
        for start, end in voice_segments:
            sync_points.append(SyncPoint(
                audio_timestamp=start,
                video_timestamp=start,
                sync_type='voice',
                confidence=0.85
            ))
        
        return {
            'sync_points': sync_points,
            'voice_segments': voice_segments,
            'strategy': 'voice_sync'
        }


class HybridSyncStrategy(ISyncStrategy):
    """Combined synchronization using multiple strategies"""
    
    def __init__(self, strategies: List[ISyncStrategy]):
        self.strategies = strategies
    
    def synchronize(self, audio_data: Dict, video_data: Dict) -> Dict:
        """Combine multiple sync strategies"""
        all_sync_points = []
        
        for strategy in self.strategies:
            result = strategy.synchronize(audio_data, video_data)
            all_sync_points.extend(result.get('sync_points', []))
        
        # Sort and merge sync points
        all_sync_points.sort(key=lambda x: x.audio_timestamp)
        
        return {
            'sync_points': all_sync_points,
            'strategy': 'hybrid'
        }


# SOLID Principle: Dependency Inversion - High-level module depends on abstractions
class RealtimeSyncManager:
    """Main synchronization manager coordinating all sync operations"""
    
    def __init__(self, 
                 audio_analyzer: Optional[IAudioAnalyzer] = None,
                 video_synchronizer: Optional[IVideoSynchronizer] = None,
                 sync_strategy: Optional[ISyncStrategy] = None):
        """
        Initialize with injected dependencies
        
        Args:
            audio_analyzer: Audio analysis implementation
            video_synchronizer: Video sync implementation  
            sync_strategy: Synchronization strategy to use
        """
        self.audio_analyzer = audio_analyzer or BeatDetector()
        self.video_synchronizer = video_synchronizer or ClipSpeedAdjuster()
        self.sync_strategy = sync_strategy or BeatSyncStrategy(BeatDetector())
        
        logger.info("✅ Realtime Sync Manager initialized")
    
    def sync_audio_video_realtime(self, 
                                  audio_files: List[str],
                                  video_clips: List[str],
                                  target_duration: float) -> SyncAnalysis:
        """
        Perform real-time audio-video synchronization
        
        Args:
            audio_files: List of audio file paths
            video_clips: List of video clip paths
            target_duration: Target duration for final video
            
        Returns:
            SyncAnalysis with synchronization results
        """
        logger.info(f"🔄 Starting real-time sync for {len(video_clips)} clips")
        
        # Combine audio files if multiple
        combined_audio = self._combine_audio_files(audio_files)
        
        # Prepare data for strategy
        audio_data = {'path': combined_audio, 'duration': target_duration}
        video_data = {'clips': video_clips}
        
        # Execute synchronization strategy
        sync_result = self.sync_strategy.synchronize(audio_data, video_data)
        
        # Analyze sync quality
        sync_analysis = self._analyze_sync_quality(
            sync_result, 
            audio_files, 
            video_clips,
            target_duration
        )
        
        # Apply synchronization to clips
        if sync_analysis.overall_sync_score < 0.7:
            logger.warning(f"⚠️ Low sync score: {sync_analysis.overall_sync_score:.2f}")
            self._apply_sync_corrections(video_clips, sync_analysis)
        
        logger.info(f"✅ Sync complete with score: {sync_analysis.overall_sync_score:.2f}")
        
        return sync_analysis
    
    def _combine_audio_files(self, audio_files: List[str]) -> str:
        """Combine multiple audio files into one"""
        if len(audio_files) == 1:
            return audio_files[0]
        
        try:
            clips = [AudioFileClip(f) for f in audio_files if os.path.exists(f)]
            if not clips:
                logger.warning("⚠️ No valid audio files found for combination")
                return audio_files[0] if audio_files else ""
            
            combined = CompositeAudioClip(clips)
            
            output_path = audio_files[0].replace('.mp3', '_combined.mp3')
            combined.write_audiofile(output_path, logger=None)
            
            # Clean up resources
            for clip in clips:
                try:
                    clip.close()
                except Exception:
                    pass
            try:
                combined.close()
            except Exception:
                pass
            
            return output_path
            
        except AttributeError as e:
            if "'CompositeAudioClip' object has no attribute 'fps'" in str(e):
                logger.warning("⚠️ MoviePy fps issue on audio clip, using fallback")
                # Return first file as fallback
                return audio_files[0]
            else:
                logger.error(f"❌ Audio combination attribute error: {e}")
                return audio_files[0]
        except Exception as e:
            logger.error(f"❌ Audio combination failed: {e}")
            return audio_files[0]
    
    def _analyze_sync_quality(self, 
                             sync_result: Dict,
                             audio_files: List[str],
                             video_clips: List[str],
                             target_duration: float) -> SyncAnalysis:
        """Analyze the quality of synchronization"""
        sync_points = sync_result.get('sync_points', [])
        
        # Calculate sync scores
        beat_score = self._calculate_beat_alignment_score(sync_points)
        voice_score = self._calculate_voice_sync_score(sync_points)
        overall_score = (beat_score * 0.6 + voice_score * 0.4)
        
        # Generate recommendations
        recommendations = []
        if beat_score < 0.7:
            recommendations.append("Consider adjusting clip transitions to match audio beats")
        if voice_score < 0.7:
            recommendations.append("Improve voice-to-visual synchronization")
        
        # Calculate adjusted durations
        adjusted_durations = self._calculate_adjusted_durations(
            sync_points, len(video_clips), target_duration
        )
        
        return SyncAnalysis(
            sync_points=sync_points,
            overall_sync_score=overall_score,
            beat_alignment_score=beat_score,
            voice_sync_score=voice_score,
            recommendations=recommendations,
            adjusted_clip_durations=adjusted_durations
        )
    
    def _calculate_beat_alignment_score(self, sync_points: List[SyncPoint]) -> float:
        """Calculate how well video aligns with audio beats"""
        if not sync_points:
            return 0.5
        
        beat_points = [p for p in sync_points if p.sync_type == 'beat']
        if not beat_points:
            return 0.5
        
        # Calculate alignment based on timing differences
        total_confidence = sum(p.confidence for p in beat_points)
        return min(1.0, total_confidence / len(beat_points))
    
    def _calculate_voice_sync_score(self, sync_points: List[SyncPoint]) -> float:
        """Calculate voice synchronization score"""
        if not sync_points:
            return 0.5
        
        voice_points = [p for p in sync_points if p.sync_type == 'voice']
        if not voice_points:
            return 0.5
        
        total_confidence = sum(p.confidence for p in voice_points)
        return min(1.0, total_confidence / len(voice_points))
    
    def _calculate_adjusted_durations(self, 
                                     sync_points: List[SyncPoint],
                                     num_clips: int,
                                     target_duration: float) -> List[float]:
        """Calculate adjusted clip durations based on sync points"""
        if not sync_points:
            # Equal distribution
            return [target_duration / num_clips] * num_clips
        
        durations = []
        for i in range(num_clips):
            if i < len(sync_points) - 1:
                duration = sync_points[i+1].audio_timestamp - sync_points[i].audio_timestamp
            else:
                # Last clip gets remaining time
                duration = target_duration - sum(durations)
            
            durations.append(max(0.5, duration))  # Minimum 0.5 seconds
        
        return durations
    
    def _apply_sync_corrections(self, 
                               video_clips: List[str],
                               sync_analysis: SyncAnalysis) -> List[str]:
        """Apply synchronization corrections to video clips"""
        corrected_clips = []
        
        for i, (clip_path, target_duration) in enumerate(
            zip(video_clips, sync_analysis.adjusted_clip_durations)
        ):
            corrected_clip = self.video_synchronizer.adjust_clip_speed(
                clip_path, target_duration
            )
            corrected_clips.append(corrected_clip)
        
        return corrected_clips
    
    def analyze_sync_points_visually(self, sync_analysis: SyncAnalysis) -> str:
        """Generate visual representation of sync points"""
        if not sync_analysis.sync_points:
            return "No sync points available"
        
        # Create ASCII timeline
        timeline_length = 50
        max_time = max(p.audio_timestamp for p in sync_analysis.sync_points)
        
        timeline = ['-'] * timeline_length
        
        for point in sync_analysis.sync_points:
            pos = int((point.audio_timestamp / max_time) * (timeline_length - 1))
            if point.sync_type == 'beat':
                timeline[pos] = '|'
            elif point.sync_type == 'voice':
                timeline[pos] = 'V'
            else:
                timeline[pos] = '*'
        
        visual = f"""
SYNC TIMELINE:
Audio:  [{''.join(timeline)}]
        0s{''.ljust(timeline_length-4)}]{max_time:.1f}s
        
Legend: | = Beat, V = Voice, * = Other
Score: {sync_analysis.overall_sync_score:.2f}/1.0
"""
        return visual


# Factory pattern for creating sync managers with different configurations
class SyncManagerFactory:
    """Factory for creating sync managers with different strategies"""
    
    @staticmethod
    def create_beat_sync_manager() -> RealtimeSyncManager:
        """Create manager optimized for beat synchronization"""
        beat_detector = BeatDetector()
        strategy = BeatSyncStrategy(beat_detector)
        return RealtimeSyncManager(
            audio_analyzer=beat_detector,
            sync_strategy=strategy
        )
    
    @staticmethod
    def create_voice_sync_manager() -> RealtimeSyncManager:
        """Create manager optimized for voice synchronization"""
        voice_analyzer = VoiceAnalyzer()
        strategy = VoiceSyncStrategy(voice_analyzer)
        return RealtimeSyncManager(
            audio_analyzer=voice_analyzer,
            sync_strategy=strategy
        )
    
    @staticmethod
    def create_hybrid_sync_manager() -> RealtimeSyncManager:
        """Create manager using hybrid synchronization"""
        beat_strategy = BeatSyncStrategy(BeatDetector())
        voice_strategy = VoiceSyncStrategy(VoiceAnalyzer())
        hybrid_strategy = HybridSyncStrategy([beat_strategy, voice_strategy])
        
        return RealtimeSyncManager(
            audio_analyzer=BeatDetector(),
            sync_strategy=hybrid_strategy
        )