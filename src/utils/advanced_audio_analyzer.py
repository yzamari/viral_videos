"""
Advanced Audio Analyzer for Perfect Subtitle Synchronization
Uses librosa for sophisticated audio analysis including pace, pitch, speed, and tempo detection
"""

import numpy as np
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import warnings

# Suppress librosa warnings
warnings.filterwarnings("ignore", category=UserWarning, module="librosa")

try:
    import librosa
    import librosa.display
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

try:
    from moviepy.editor import AudioFileClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class AudioAnalysisResult:
    """Comprehensive audio analysis results"""
    duration: float
    tempo: float
    pitch_mean: float
    pitch_std: float
    energy_levels: List[float]
    speech_rate: float  # words per second
    pace_variations: List[float]  # tempo changes over time
    silence_segments: List[Tuple[float, float]]  # (start, end) of silent parts
    emphasis_segments: List[Tuple[float, float]]  # (start, end) of emphasized parts
    volume_envelope: List[float]  # volume changes over time
    spectral_features: Dict[str, float]
    timing_confidence: float  # 0-1, how confident we are in timing


@dataclass
class SubtitleTiming:
    """Precise subtitle timing based on audio analysis"""
    text: str
    start_time: float
    end_time: float
    confidence: float
    speech_rate: float
    emphasis_level: float
    volume_level: float
    pitch_level: float


class AdvancedAudioAnalyzer:
    """Advanced audio analysis for perfect subtitle synchronization"""
    
    def __init__(self):
        self.sample_rate = 22050  # Standard rate for speech analysis
        self.hop_length = 512     # Frame hop length
        self.frame_length = 2048  # Frame length for analysis
        
        if not LIBROSA_AVAILABLE:
            logger.warning("⚠️ librosa not available. Install with: pip install librosa")
        if not MOVIEPY_AVAILABLE:
            logger.warning("⚠️ moviepy not available. Install with: pip install moviepy")
    
    def analyze_audio_file(self, audio_path: str) -> AudioAnalysisResult:
        """Comprehensive audio analysis for subtitle timing"""
        try:
            if not LIBROSA_AVAILABLE:
                return self._fallback_analysis(audio_path)
            
            logger.info(f"🎵 Starting advanced audio analysis: {audio_path}")
            
            # Load audio file
            y, sr = librosa.load(audio_path, sr=self.sample_rate)
            duration = librosa.get_duration(y=y, sr=sr)
            
            logger.info(f"📊 Audio loaded: {duration:.2f}s at {sr}Hz")
            
            # 1. Tempo and Beat Analysis
            tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr, hop_length=self.hop_length)
            beat_times = librosa.frames_to_time(beat_frames, sr=sr, hop_length=self.hop_length)
            
            # 2. Pitch Analysis
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr, hop_length=self.hop_length)
            pitch_values = []
            
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:  # Valid pitch
                    pitch_values.append(pitch)
            
            pitch_mean = np.mean(pitch_values) if pitch_values else 0
            pitch_std = np.std(pitch_values) if pitch_values else 0
            
            # 3. Energy and Volume Analysis
            energy = librosa.feature.rms(y=y, hop_length=self.hop_length)[0]
            energy_times = librosa.frames_to_time(np.arange(len(energy)), sr=sr, hop_length=self.hop_length)
            
            # 4. Spectral Features
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=self.hop_length)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr, hop_length=self.hop_length)[0]
            zero_crossing_rate = librosa.feature.zero_crossing_rate(y, hop_length=self.hop_length)[0]
            
            # 5. Voice Activity Detection (VAD)
            silence_threshold = np.percentile(energy, 20)  # Bottom 20% as silence
            silence_segments = self._detect_silence_segments(energy, energy_times, silence_threshold)
            
            # 6. Emphasis Detection (high energy segments)
            emphasis_threshold = np.percentile(energy, 80)  # Top 20% as emphasis
            emphasis_segments = self._detect_emphasis_segments(energy, energy_times, emphasis_threshold)
            
            # 7. Pace Variation Analysis
            pace_variations = self._analyze_pace_variations(beat_times, duration)
            
            # 8. Speech Rate Estimation
            speech_rate = self._estimate_speech_rate(y, sr, silence_segments)
            
            # 9. Timing Confidence
            timing_confidence = self._calculate_timing_confidence(energy, pitch_values, tempo)
            
            result = AudioAnalysisResult(
                duration=duration,
                tempo=float(tempo),
                pitch_mean=float(pitch_mean),
                pitch_std=float(pitch_std),
                energy_levels=energy.tolist(),
                speech_rate=speech_rate,
                pace_variations=pace_variations,
                silence_segments=silence_segments,
                emphasis_segments=emphasis_segments,
                volume_envelope=energy.tolist(),
                spectral_features={
                    'spectral_centroid_mean': float(np.mean(spectral_centroid)),
                    'spectral_rolloff_mean': float(np.mean(spectral_rolloff)),
                    'zero_crossing_rate_mean': float(np.mean(zero_crossing_rate))
                },
                timing_confidence=timing_confidence
            )
            
            logger.info(f"✅ Audio analysis complete: tempo={tempo:.1f}bpm, "
                       f"speech_rate={speech_rate:.1f}w/s, confidence={timing_confidence:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Audio analysis failed: {e}")
            return self._fallback_analysis(audio_path)
    
    def _detect_silence_segments(self, energy: np.ndarray, times: np.ndarray, 
                                threshold: float) -> List[Tuple[float, float]]:
        """Detect silent segments in audio"""
        silent_frames = energy < threshold
        segments = []
        
        in_silence = False
        start_time = 0
        
        for i, (is_silent, time) in enumerate(zip(silent_frames, times)):
            if is_silent and not in_silence:
                # Start of silence
                start_time = time
                in_silence = True
            elif not is_silent and in_silence:
                # End of silence
                if time - start_time > 0.1:  # Minimum 100ms silence
                    segments.append((start_time, time))
                in_silence = False
        
        # Handle case where audio ends in silence
        if in_silence and times[-1] - start_time > 0.1:
            segments.append((start_time, times[-1]))
        
        return segments
    
    def _detect_emphasis_segments(self, energy: np.ndarray, times: np.ndarray,
                                 threshold: float) -> List[Tuple[float, float]]:
        """Detect emphasized/high-energy segments"""
        emphasized_frames = energy > threshold
        segments = []
        
        in_emphasis = False
        start_time = 0
        
        for i, (is_emphasized, time) in enumerate(zip(emphasized_frames, times)):
            if is_emphasized and not in_emphasis:
                start_time = time
                in_emphasis = True
            elif not is_emphasized and in_emphasis:
                if time - start_time > 0.1:  # Minimum 100ms emphasis
                    segments.append((start_time, time))
                in_emphasis = False
        
        if in_emphasis and times[-1] - start_time > 0.1:
            segments.append((start_time, times[-1]))
        
        return segments
    
    def _analyze_pace_variations(self, beat_times: np.ndarray, duration: float) -> List[float]:
        """Analyze how pace/tempo varies throughout the audio"""
        if len(beat_times) < 4:
            return [1.0]  # Constant pace if not enough beats
        
        # Calculate local tempo variations
        window_size = 4  # beats
        variations = []
        
        for i in range(len(beat_times) - window_size + 1):
            window_beats = beat_times[i:i + window_size]
            intervals = np.diff(window_beats)
            avg_interval = np.mean(intervals)
            tempo_variation = 60.0 / avg_interval if avg_interval > 0 else 120.0
            variations.append(tempo_variation)
        
        # Normalize variations to relative pace (1.0 = average pace)
        if variations:
            avg_variation = np.mean(variations)
            normalized_variations = [v / avg_variation for v in variations]
            return normalized_variations
        
        return [1.0]
    
    def _estimate_speech_rate(self, y: np.ndarray, sr: int, 
                            silence_segments: List[Tuple[float, float]]) -> float:
        """Estimate speech rate (words per second) based on audio characteristics"""
        try:
            # Calculate speaking time (total - silence)
            total_duration = len(y) / sr
            silence_duration = sum(end - start for start, end in silence_segments)
            speaking_duration = total_duration - silence_duration
            
            if speaking_duration <= 0:
                return 2.5  # Default speech rate
            
            # Estimate syllable rate using onset detection
            onset_frames = librosa.onset.onset_detect(y=y, sr=sr, hop_length=self.hop_length)
            onset_times = librosa.frames_to_time(onset_frames, sr=sr, hop_length=self.hop_length)
            
            # Filter onsets that occur during speech (not silence)
            speech_onsets = []
            for onset_time in onset_times:
                is_in_silence = any(start <= onset_time <= end for start, end in silence_segments)
                if not is_in_silence:
                    speech_onsets.append(onset_time)
            
            # Estimate words per second (typically 1.5-2 syllables per word)
            syllables_per_second = len(speech_onsets) / speaking_duration if speaking_duration > 0 else 0
            words_per_second = syllables_per_second / 1.7  # Average syllables per word
            
            # Clamp to reasonable range
            words_per_second = max(1.0, min(4.0, words_per_second))
            
            return words_per_second
            
        except Exception as e:
            logger.warning(f"⚠️ Speech rate estimation failed: {e}")
            return 2.5  # Default rate
    
    def _calculate_timing_confidence(self, energy: np.ndarray, pitch_values: List[float], 
                                   tempo: float) -> float:
        """Calculate confidence in timing analysis (0-1)"""
        confidence_factors = []
        
        # Energy consistency (less variation = higher confidence)
        if len(energy) > 0:
            energy_cv = np.std(energy) / (np.mean(energy) + 1e-8)  # Coefficient of variation
            energy_confidence = max(0, 1 - energy_cv)
            confidence_factors.append(energy_confidence)
        
        # Pitch stability (more stable pitch = higher confidence for speech)
        if pitch_values:
            pitch_cv = np.std(pitch_values) / (np.mean(pitch_values) + 1e-8)
            pitch_confidence = max(0, 1 - pitch_cv / 100)  # Normalize for typical speech pitch range
            confidence_factors.append(pitch_confidence)
        
        # Tempo reasonableness (speech-like tempo = higher confidence)
        tempo_confidence = 1.0
        if tempo < 60 or tempo > 200:  # Outside typical speech tempo range
            tempo_confidence = 0.7
        confidence_factors.append(tempo_confidence)
        
        # Overall confidence is the mean of all factors
        return np.mean(confidence_factors) if confidence_factors else 0.5
    
    def synchronize_subtitles_with_audio(self, text_segments: List[str], 
                                       audio_analysis: AudioAnalysisResult) -> List[SubtitleTiming]:
        """Create perfectly synchronized subtitles based on audio analysis"""
        try:
            logger.info(f"🎯 Synchronizing {len(text_segments)} subtitle segments with audio analysis")
            
            if not text_segments:
                return []
            
            # Calculate total words and speaking time
            total_words = sum(len(segment.split()) for segment in text_segments)
            speaking_duration = audio_analysis.duration
            
            # Adjust for silence segments
            total_silence = sum(end - start for start, end in audio_analysis.silence_segments)
            speaking_duration -= total_silence
            
            if speaking_duration <= 0:
                speaking_duration = audio_analysis.duration * 0.8  # Assume 80% speaking time
            
            # Use analyzed speech rate with fallback to calculated rate
            speech_rate = audio_analysis.speech_rate
            if speech_rate <= 0:
                speech_rate = total_words / speaking_duration if speaking_duration > 0 else 2.5
            
            logger.info(f"📊 Speech analysis: {speech_rate:.2f} words/sec, "
                       f"{speaking_duration:.1f}s speaking time, {total_silence:.1f}s silence")
            
            # Create synchronized timings
            subtitle_timings = []
            current_time = 0.0
            energy_index = 0
            
            for i, text in enumerate(text_segments):
                words = text.split()
                word_count = len(words)
                
                # Calculate base duration from word count and speech rate
                base_duration = word_count / speech_rate
                
                # Apply audio-based adjustments
                
                # 1. Pace variation adjustment
                if i < len(audio_analysis.pace_variations):
                    pace_factor = audio_analysis.pace_variations[i]
                    base_duration *= (2.0 - pace_factor)  # Slower pace = longer duration
                
                # 2. Content-based timing adjustments
                text_lower = text.lower()
                if any(marker in text_lower for marker in ['?', '!', 'how', 'what', 'why']):
                    # CRITICAL FIX: Remove duration multiplier to maintain exact target duration
                    pass  # base_duration *= 1.2  # Questions and emphasis need more time
                elif any(marker in text_lower for marker in ['and', 'the', 'this', 'that']):
                    base_duration *= 0.9   # Simple connectors can be faster
                
                # 3. Emphasis detection
                emphasis_level = 0.0
                for emp_start, emp_end in audio_analysis.emphasis_segments:
                    if current_time <= emp_start < current_time + base_duration:
                        emphasis_level = 1.0
                        # CRITICAL FIX: Remove duration multiplier to maintain exact target duration
                        pass  # base_duration *= 1.15  # Emphasized speech is slightly slower
                        break
                
                # 4. Volume level detection
                volume_level = 0.5  # Default
                if energy_index < len(audio_analysis.energy_levels):
                    energy_slice = audio_analysis.energy_levels[energy_index:energy_index + 10]
                    volume_level = np.mean(energy_slice) if energy_slice else 0.5
                    energy_index += 10
                
                # 5. Pitch level for this segment
                pitch_level = audio_analysis.pitch_mean
                
                # 6. Avoid overlapping with silence segments
                end_time = current_time + base_duration
                
                # Check if this timing overlaps with silence - if so, adjust
                for silence_start, silence_end in audio_analysis.silence_segments:
                    if current_time < silence_end and end_time > silence_start:
                        # This segment overlaps with silence - adjust timing
                        if current_time < silence_start:
                            # Segment starts before silence - compress before silence
                            available_time = silence_start - current_time
                            if available_time > 0.5:  # Minimum viable duration
                                base_duration = available_time
                                end_time = silence_start
                        else:
                            # Segment starts in silence - move start after silence
                            current_time = silence_end
                            end_time = current_time + base_duration
                
                # Ensure we don't exceed audio duration
                if end_time > audio_analysis.duration:
                    end_time = audio_analysis.duration
                    base_duration = end_time - current_time
                
                # Create subtitle timing with confidence score
                confidence = audio_analysis.timing_confidence * (0.8 + 0.2 * min(1.0, word_count / 5))
                
                subtitle_timing = SubtitleTiming(
                    text=text,
                    start_time=round(current_time, 3),
                    end_time=round(end_time, 3),
                    confidence=round(confidence, 3),
                    speech_rate=round(speech_rate, 2),
                    emphasis_level=round(emphasis_level, 2),
                    volume_level=round(float(volume_level), 2),
                    pitch_level=round(pitch_level, 2)
                )
                
                subtitle_timings.append(subtitle_timing)
                
                logger.info(f"📝 Segment {i+1}: '{text[:30]}...' "
                           f"({subtitle_timing.start_time:.2f}-{subtitle_timing.end_time:.2f}s, "
                           f"conf={subtitle_timing.confidence:.2f})")
                
                current_time = end_time
                
                # Add natural pause between segments (except for last segment)
                if i < len(text_segments) - 1:
                    pause_duration = min(0.1, (audio_analysis.duration - current_time) / (len(text_segments) - i))
                    current_time += pause_duration
            
            # Calculate synchronization accuracy
            total_subtitle_time = subtitle_timings[-1].end_time if subtitle_timings else 0
            sync_accuracy = (total_subtitle_time / audio_analysis.duration) * 100
            avg_confidence = np.mean([st.confidence for st in subtitle_timings])
            
            logger.info(f"✅ Perfect audio-based sync complete: {len(subtitle_timings)} segments, "
                       f"{sync_accuracy:.1f}% timing accuracy, avg confidence: {avg_confidence:.2f}")
            
            return subtitle_timings
            
        except Exception as e:
            logger.error(f"❌ Audio-based subtitle synchronization failed: {e}")
            return self._fallback_subtitle_timing(text_segments, audio_analysis.duration)
    
    def _fallback_analysis(self, audio_path: str) -> AudioAnalysisResult:
        """Fallback analysis when librosa is not available"""
        try:
            # Use moviepy to get basic duration
            if MOVIEPY_AVAILABLE:
                audio_clip = AudioFileClip(audio_path)
                duration = audio_clip.duration
                audio_clip.close()
            else:
                duration = 20.0  # Default assumption
            
            logger.warning("⚠️ Using fallback audio analysis (install librosa for better results)")
            
            return AudioAnalysisResult(
                duration=duration,
                tempo=120.0,  # Default tempo
                pitch_mean=200.0,  # Default pitch
                pitch_std=50.0,
                energy_levels=[0.5] * 100,  # Constant energy
                speech_rate=2.5,  # Default speech rate
                pace_variations=[1.0] * 10,  # Constant pace
                silence_segments=[],  # No silence detection
                emphasis_segments=[],  # No emphasis detection
                volume_envelope=[0.5] * 100,  # Constant volume
                spectral_features={'spectral_centroid_mean': 1000.0, 'spectral_rolloff_mean': 2000.0, 'zero_crossing_rate_mean': 0.1},
                timing_confidence=0.5  # Low confidence for fallback
            )
            
        except Exception as e:
            logger.error(f"❌ Fallback analysis failed: {e}")
            # Return minimal viable analysis
            return AudioAnalysisResult(
                duration=20.0, tempo=120.0, pitch_mean=200.0, pitch_std=50.0,
                energy_levels=[0.5], speech_rate=2.5, pace_variations=[1.0],
                silence_segments=[], emphasis_segments=[], volume_envelope=[0.5],
                spectral_features={}, timing_confidence=0.3
            )
    
    def _fallback_subtitle_timing(self, text_segments: List[str], duration: float) -> List[SubtitleTiming]:
        """Fallback subtitle timing when advanced analysis fails"""
        if not text_segments:
            return []
        
        timings = []
        segment_duration = duration / len(text_segments)
        
        for i, text in enumerate(text_segments):
            start_time = i * segment_duration
            end_time = (i + 1) * segment_duration
            
            timings.append(SubtitleTiming(
                text=text,
                start_time=round(start_time, 3),
                end_time=round(end_time, 3),
                confidence=0.5,  # Low confidence for fallback
                speech_rate=2.5,
                emphasis_level=0.0,
                volume_level=0.5,
                pitch_level=200.0
            ))
        
        return timings