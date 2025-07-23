"""Weather Graphics Generator for custom weather maps and overlays."""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import Dict, List, Tuple, Optional
import os
from pathlib import Path

class WeatherGraphicsGenerator:
    """Generate custom weather graphics for video overlays."""
    
    def __init__(self, output_dir: str = "assets/weather_graphics"):
        """Initialize weather graphics generator.
        
        Args:
            output_dir: Directory to save generated graphics
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Iran major cities coordinates (normalized 0-1)
        self.iran_cities = {
            "Tehran": (0.51, 0.35),
            "Isfahan": (0.52, 0.47),
            "Shiraz": (0.53, 0.65),
            "Tabriz": (0.46, 0.28),
            "Mashhad": (0.70, 0.34),
            "Ahvaz": (0.49, 0.58),
            "Kerman": (0.62, 0.62)
        }
        
    def create_heat_map(
        self,
        temperatures: Dict[str, float],
        title: str = "Iran Temperature Map",
        output_name: str = "heat_map.png",
        style: str = "normal"  # normal, nuclear, comedy
    ) -> str:
        """Create a heat map showing temperatures.
        
        Args:
            temperatures: City -> temperature mapping
            title: Map title
            output_name: Output filename
            style: Visual style (normal, nuclear, comedy)
            
        Returns:
            Path to created graphic
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Set background color based on style
        if style == "nuclear":
            fig.patch.set_facecolor('#1A1A1A')
            ax.set_facecolor('#2B2B2B')
            text_color = '#FFD700'
            cmap = 'hot'
        elif style == "comedy":
            fig.patch.set_facecolor('#FFE6E6')
            ax.set_facecolor('#FFF0F0')
            text_color = '#FF1493'
            cmap = 'plasma'
        else:
            fig.patch.set_facecolor('white')
            ax.set_facecolor('#E8F4FF')
            text_color = 'black'
            cmap = 'RdYlBu_r'
        
        # Create map outline (simplified Iran shape)
        iran_shape = patches.Polygon([
            (0.3, 0.2), (0.7, 0.2), (0.8, 0.3),
            (0.8, 0.6), (0.7, 0.7), (0.5, 0.8),
            (0.3, 0.7), (0.2, 0.5), (0.2, 0.3)
        ], closed=True, facecolor='lightgray', edgecolor='black', linewidth=2)
        ax.add_patch(iran_shape)
        
        # Plot cities with temperatures
        for city, (x, y) in self.iran_cities.items():
            if city in temperatures:
                temp = temperatures[city]
                
                # Color based on temperature
                if style == "nuclear":
                    color = '#FF0000' if temp > 45 else '#FF6600'
                    marker = '☢' if temp > 50 else 'o'
                elif style == "comedy":
                    color = '#FF69B4' if temp > 45 else '#FF1493'
                    marker = '🔥' if temp > 50 else 'o'
                else:
                    color = plt.cm.RdYlBu_r(1 - (temp - 20) / 40)
                    marker = 'o'
                
                # Plot city
                ax.plot(x, y, marker, markersize=20, color=color)
                ax.text(x, y + 0.03, city, ha='center', va='bottom',
                       fontsize=12, color=text_color, weight='bold')
                ax.text(x, y - 0.03, f'{temp}°C', ha='center', va='top',
                       fontsize=10, color=text_color)
        
        # Add title
        ax.set_title(title, fontsize=20, color=text_color, weight='bold', pad=20)
        
        # Remove axes
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        # Save
        output_path = self.output_dir / output_name
        plt.savefig(output_path, dpi=150, bbox_inches='tight',
                   facecolor=fig.get_facecolor(), edgecolor='none')
        plt.close()
        
        return str(output_path)
    
    def create_water_crisis_map(
        self,
        water_levels: Dict[str, str],  # City -> "critical", "low", "dry"
        output_name: str = "water_crisis_map.png"
    ) -> str:
        """Create water crisis visualization.
        
        Args:
            water_levels: City -> water level status
            output_name: Output filename
            
        Returns:
            Path to created graphic
        """
        # Create image
        img = Image.new('RGBA', (1920, 1080), (26, 26, 26, 255))
        draw = ImageDraw.Draw(img)
        
        # Title
        title = "Iran Water Crisis Status"
        draw.text((960, 50), title, fill=(200, 16, 46), 
                 font=None, anchor='mt')
        
        # Legend
        legend_items = [
            ("🚱 Critical", (255, 0, 0)),
            ("💧 Low", (255, 165, 0)),
            ("🏜️ Dry", (139, 69, 19))
        ]
        
        y_offset = 150
        for item, color in legend_items:
            draw.text((100, y_offset), item, fill=color, font=None)
            y_offset += 40
        
        # Draw cities with water status
        for city, (x, y) in self.iran_cities.items():
            if city in water_levels:
                status = water_levels[city]
                
                # Convert normalized coordinates to pixels
                px = int(x * 1920)
                py = int(y * 1080)
                
                # Draw status
                if status == "critical":
                    symbol = "🚱"
                    color = (255, 0, 0)
                elif status == "low":
                    symbol = "💧"
                    color = (255, 165, 0)
                else:  # dry
                    symbol = "🏜️"
                    color = (139, 69, 19)
                
                # Draw circle background
                draw.ellipse([px-30, py-30, px+30, py+30], 
                           fill=color, outline=(255, 255, 255), width=3)
                
                # Draw city name
                draw.text((px, py+50), city, fill=(255, 255, 255),
                         font=None, anchor='mt')
        
        # Save
        output_path = self.output_dir / output_name
        img.save(output_path)
        
        return str(output_path)
    
    def create_comedy_weather_overlay(
        self,
        jokes: Dict[str, str],  # City -> joke text
        output_name: str = "comedy_weather.png"
    ) -> str:
        """Create comedy weather overlay with jokes.
        
        Args:
            jokes: City -> joke text
            output_name: Output filename
            
        Returns:
            Path to created graphic
        """
        # Create transparent overlay
        img = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Add speech bubbles for each city
        for city, (x, y) in self.iran_cities.items():
            if city in jokes:
                joke = jokes[city]
                
                # Convert coordinates
                px = int(x * 1920)
                py = int(y * 1080)
                
                # Draw speech bubble
                bubble_width = 300
                bubble_height = 80
                
                # Bubble background
                draw.rounded_rectangle(
                    [px - bubble_width//2, py - bubble_height//2,
                     px + bubble_width//2, py + bubble_height//2],
                    radius=20, fill=(255, 255, 255, 230),
                    outline=(0, 0, 0), width=3
                )
                
                # Bubble tail
                points = [
                    (px - 20, py + bubble_height//2),
                    (px, py + bubble_height//2 + 30),
                    (px + 20, py + bubble_height//2)
                ]
                draw.polygon(points, fill=(255, 255, 255, 230),
                           outline=(0, 0, 0))
                
                # Draw joke text (simplified - would need text wrapping)
                draw.text((px, py), joke[:30] + "...", 
                         fill=(0, 0, 0), font=None, anchor='mm')
        
        # Save
        output_path = self.output_dir / output_name
        img.save(output_path)
        
        return str(output_path)
    
    def create_nuclear_weather_animation_frames(
        self,
        num_frames: int = 30,
        output_prefix: str = "nuclear_frame"
    ) -> List[str]:
        """Create animation frames for nuclear weather.
        
        Args:
            num_frames: Number of frames to generate
            output_prefix: Prefix for frame files
            
        Returns:
            List of paths to frame files
        """
        frames = []
        
        for i in range(num_frames):
            img = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Pulsing nuclear symbols
            for city, (x, y) in list(self.iran_cities.items())[:3]:  # Top 3 cities
                px = int(x * 1920)
                py = int(y * 1080)
                
                # Pulsing effect
                size = 50 + int(20 * np.sin(i * 0.2))
                opacity = int(180 + 75 * np.sin(i * 0.2))
                
                # Draw nuclear symbol circle
                draw.ellipse([px-size, py-size, px+size, py+size],
                           fill=(255, 215, 0, opacity),
                           outline=(255, 0, 0), width=5)
                
                # Draw radiation symbol (simplified)
                draw.text((px, py), "☢", fill=(255, 0, 0),
                         font=None, anchor='mm')
            
            # Save frame
            frame_path = self.output_dir / f"{output_prefix}_{i:04d}.png"
            img.save(frame_path)
            frames.append(str(frame_path))
        
        return frames


# Example usage
if __name__ == "__main__":
    generator = WeatherGraphicsGenerator()
    
    # Create nuclear heat map
    temps = {
        "Tehran": 52,  # Nuclear hot!
        "Isfahan": 48,
        "Shiraz": 45,
        "Mashhad": 47
    }
    generator.create_heat_map(temps, "Nuclear Summer Forecast", 
                            "nuclear_heat.png", style="nuclear")
    
    # Create water crisis map
    water = {
        "Tehran": "critical",
        "Isfahan": "dry",
        "Shiraz": "low",
        "Ahvaz": "dry"
    }
    generator.create_water_crisis_map(water, "water_crisis.png")
    
    # Create comedy overlay
    jokes = {
        "Tehran": "So hot, we're cooking kebab on sidewalks!",
        "Isfahan": "Water? What's that?",
        "Shiraz": "Even our poems are dry now!"
    }
    generator.create_comedy_weather_overlay(jokes, "comedy_weather.png")