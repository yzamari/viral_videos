"""
Dynamic Media Transitions
Creates engaging transitions between media (split-screen, mosaic, swipe, etc.)
"""

import os
import cv2
import numpy as np
from typing import List, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class DynamicTransitions:
    """Creates dynamic transitions between media segments"""
    
    def __init__(self, dimensions: Tuple[int, int]):
        self.width, self.height = dimensions
    
    def create_split_screen(
        self,
        media1_path: str,
        media2_path: str,
        duration: float,
        output_path: str,
        orientation: str = "vertical"
    ) -> str:
        """
        Create split-screen effect with two media sources
        
        Args:
            media1_path: First media file
            media2_path: Second media file
            duration: Duration of the segment
            output_path: Output file path
            orientation: 'vertical' or 'horizontal' split
        """
        import subprocess
        
        if orientation == "vertical":
            # Side by side
            filter_complex = f"""
            [0:v]scale={self.width//2}:{self.height}[left];
            [1:v]scale={self.width//2}:{self.height}[right];
            [left][right]hstack=inputs=2[v]
            """
        else:
            # Top and bottom
            filter_complex = f"""
            [0:v]scale={self.width}:{self.height//2}[top];
            [1:v]scale={self.width}:{self.height//2}[bottom];
            [top][bottom]vstack=inputs=2[v]
            """
        
        cmd = [
            'ffmpeg', '-y',
            '-i', media1_path,
            '-i', media2_path,
            '-filter_complex', filter_complex,
            '-map', '[v]',
            '-t', str(duration),
            '-c:v', 'libx264',
            '-preset', 'fast',
            output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return output_path
        except Exception as e:
            logger.error(f"Split screen creation failed: {e}")
            return media1_path
    
    def create_mosaic(
        self,
        media_paths: List[str],
        duration: float,
        output_path: str,
        grid: Tuple[int, int] = (2, 2)
    ) -> str:
        """
        Create mosaic effect with multiple media sources
        
        Args:
            media_paths: List of media files (up to 4)
            duration: Duration of the segment
            output_path: Output file path
            grid: Grid dimensions (rows, cols)
        """
        import subprocess
        
        if len(media_paths) < 4:
            # Duplicate media to fill grid
            while len(media_paths) < 4:
                media_paths.append(media_paths[0])
        
        cell_w = self.width // 2
        cell_h = self.height // 2
        
        filter_complex = f"""
        [0:v]scale={cell_w}:{cell_h}[v0];
        [1:v]scale={cell_w}:{cell_h}[v1];
        [2:v]scale={cell_w}:{cell_h}[v2];
        [3:v]scale={cell_w}:{cell_h}[v3];
        [v0][v1]hstack=inputs=2[top];
        [v2][v3]hstack=inputs=2[bottom];
        [top][bottom]vstack=inputs=2[v]
        """
        
        cmd = ['ffmpeg', '-y']
        for path in media_paths[:4]:
            cmd.extend(['-i', path])
        cmd.extend([
            '-filter_complex', filter_complex,
            '-map', '[v]',
            '-t', str(duration),
            '-c:v', 'libx264',
            '-preset', 'fast',
            output_path
        ])
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return output_path
        except Exception as e:
            logger.error(f"Mosaic creation failed: {e}")
            return media_paths[0]
    
    def create_swipe_transition(
        self,
        media1_path: str,
        media2_path: str,
        duration: float,
        output_path: str,
        direction: str = "left"
    ) -> str:
        """
        Create swipe transition between two media sources
        
        Args:
            media1_path: First media file
            media2_path: Second media file
            duration: Duration of transition
            output_path: Output file path
            direction: Swipe direction (left/right/up/down)
        """
        import subprocess
        
        # Xfade filter for smooth transition
        filter_map = {
            "left": "slideleft",
            "right": "slideright",
            "up": "slideup",
            "down": "slidedown"
        }
        
        transition = filter_map.get(direction, "fade")
        
        cmd = [
            'ffmpeg', '-y',
            '-i', media1_path,
            '-i', media2_path,
            '-filter_complex',
            f"[0:v][1:v]xfade=transition={transition}:duration=0.5:offset={duration-0.5}[v]",
            '-map', '[v]',
            '-t', str(duration),
            '-c:v', 'libx264',
            '-preset', 'fast',
            output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return output_path
        except Exception as e:
            logger.error(f"Swipe transition failed: {e}")
            return media1_path
    
    def create_zoom_pan(
        self,
        media_path: str,
        duration: float,
        output_path: str,
        zoom_factor: float = 1.3
    ) -> str:
        """
        Create zoom and pan effect (Ken Burns effect)
        
        Args:
            media_path: Media file
            duration: Duration of effect
            output_path: Output file path
            zoom_factor: Zoom multiplication factor
        """
        import subprocess
        
        # Zoom in from center with slight pan
        filter_complex = f"""
        scale=-2:{int(self.height * zoom_factor)},
        zoompan=z='min(zoom+0.0015,{zoom_factor})':
        x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':
        d={int(duration * 25)}:s={self.width}x{self.height}
        """
        
        cmd = [
            'ffmpeg', '-y',
            '-i', media_path,
            '-vf', filter_complex,
            '-t', str(duration),
            '-c:v', 'libx264',
            '-preset', 'fast',
            output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return output_path
        except Exception as e:
            logger.error(f"Zoom pan effect failed: {e}")
            return media_path
    
    def apply_dynamic_sequence(
        self,
        media_files: List[str],
        segment_duration: float,
        transitions: List[str],
        output_path: str
    ) -> str:
        """
        Apply a sequence of dynamic transitions to create engaging segment
        
        Args:
            media_files: List of media files to use
            segment_duration: Total duration of the segment
            transitions: List of transition types to apply
            output_path: Output file path
        """
        if not media_files:
            return None
        
        # Calculate time per transition
        num_transitions = min(len(transitions), len(media_files) - 1)
        if num_transitions == 0:
            # Single media, apply zoom/pan
            return self.create_zoom_pan(
                media_files[0],
                segment_duration,
                output_path
            )
        
        time_per_segment = segment_duration / (num_transitions + 1)
        
        # Create temporary segments with transitions
        temp_segments = []
        
        for i in range(num_transitions):
            transition = transitions[i % len(transitions)]
            temp_output = f"{output_path}_segment_{i}.mp4"
            
            if transition == "split-screen":
                result = self.create_split_screen(
                    media_files[i],
                    media_files[i + 1],
                    time_per_segment * 2,
                    temp_output
                )
            elif transition == "mosaic":
                result = self.create_mosaic(
                    media_files[i:i+4],
                    time_per_segment,
                    temp_output
                )
            elif transition in ["swipe", "slide"]:
                result = self.create_swipe_transition(
                    media_files[i],
                    media_files[i + 1],
                    time_per_segment * 2,
                    temp_output,
                    direction="left"
                )
            else:
                # Default to zoom/pan
                result = self.create_zoom_pan(
                    media_files[i],
                    time_per_segment,
                    temp_output
                )
            
            temp_segments.append(result)
        
        # Concatenate all segments
        if len(temp_segments) > 1:
            concat_list = output_path + "_concat.txt"
            with open(concat_list, 'w') as f:
                for segment in temp_segments:
                    f.write(f"file '{os.path.abspath(segment)}'\n")
            
            import subprocess
            cmd = [
                'ffmpeg', '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_list,
                '-c', 'copy',
                output_path
            ]
            
            try:
                subprocess.run(cmd, check=True, capture_output=True)
                
                # Clean up temp files
                for segment in temp_segments:
                    try:
                        os.remove(segment)
                    except:
                        pass
                os.remove(concat_list)
                
                return output_path
            except Exception as e:
                logger.error(f"Concatenation failed: {e}")
                return temp_segments[0] if temp_segments else None
        
        return temp_segments[0] if temp_segments else None