"""
MoviePy configuration for text rendering without ImageMagick
"""
import os
from moviepy.config import IMAGEMAGICK_BINARY

# Disable ImageMagick for text rendering
IMAGEMAGICK_BINARY = None

# Set environment variable to disable ImageMagick
os.environ['IMAGEMAGICK_BINARY'] = ''
