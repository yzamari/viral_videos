"""Media Downloader - Downloads and manages scraped media assets"""

import os
import aiohttp
import asyncio
import hashlib
import mimetypes
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urlparse, unquote
import aiofiles
import subprocess
import json

from ...utils.logging_config import get_logger
from ..models.content_models import MediaAsset, AssetType

logger = get_logger(__name__)


class MediaDownloader:
    """Downloads and processes media assets from scraped content"""
    
    def __init__(self, cache_dir: str = "outputs/news_media_cache", max_concurrent: int = 5):
        self.cache_dir = cache_dir
        self.max_concurrent = max_concurrent
        os.makedirs(cache_dir, exist_ok=True)
        
        # Track downloaded media
        self.media_registry_path = os.path.join(cache_dir, "media_registry.json")
        self.media_registry = self._load_registry()
        
        # Supported media types
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
        self.video_extensions = {'.mp4', '.webm', '.mov', '.avi', '.mkv', '.m4v'}
        self.audio_extensions = {'.mp3', '.wav', '.m4a', '.aac', '.ogg'}
    
    def _load_registry(self) -> Dict[str, Dict[str, Any]]:
        """Load media registry from disk"""
        if os.path.exists(self.media_registry_path):
            try:
                with open(self.media_registry_path, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_registry(self):
        """Save media registry to disk"""
        with open(self.media_registry_path, 'w') as f:
            json.dump(self.media_registry, f, indent=2)
    
    async def download_media_batch(
        self, 
        media_urls: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Download multiple media files concurrently"""
        
        logger.info(f"Downloading {len(media_urls)} media assets...")
        
        # Create download tasks with semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def download_with_semaphore(url: str, meta: Optional[Dict] = None):
            async with semaphore:
                return await self.download_media(url, meta)
        
        # Process metadata for each URL
        url_metadata = {}
        if metadata:
            for url in media_urls:
                url_metadata[url] = metadata.get(url, {})
        
        # Download all media concurrently
        tasks = [
            download_with_semaphore(url, url_metadata.get(url))
            for url in media_urls
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        downloaded = []
        for url, result in zip(media_urls, results):
            if isinstance(result, Exception):
                logger.error(f"Failed to download {url}: {str(result)}")
            elif result:
                downloaded.append(result)
        
        logger.info(f"Successfully downloaded {len(downloaded)} out of {len(media_urls)} media files")
        
        # Save registry
        self._save_registry()
        
        return downloaded
    
    async def download_media(
        self, 
        url: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Download a single media file"""
        
        # Check if already downloaded
        url_hash = hashlib.md5(url.encode()).hexdigest()
        if url_hash in self.media_registry:
            cached = self.media_registry[url_hash]
            if os.path.exists(cached['local_path']):
                logger.info(f"Using cached media: {cached['local_path']}")
                return cached
        
        try:
            # Determine media type and extension
            media_type, extension = self._detect_media_type(url)
            if not media_type:
                logger.warning(f"Unsupported media type for URL: {url}")
                return {
                    'url': url,
                    'local_path': None,
                    'media_type': None,
                    'error': 'Unsupported media type'
                }
            
            # Generate local filename
            filename = f"{url_hash}{extension}"
            local_path = os.path.join(self.cache_dir, filename)
            
            # Download file with SSL workaround for development
            # Disable SSL for known problematic sites
            ssl_disabled_domains = ['unsplash.com', 'ynet-pic1.yit.co.il', 'img.mako.co.il', 'sport5.co.il', 'cdn-cgi']
            should_disable_ssl = any(domain in url for domain in ssl_disabled_domains)
            connector = aiohttp.TCPConnector(ssl=False) if should_disable_ssl else None
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(url, timeout=60) as response:
                    response.raise_for_status()
                    
                    # Get file size
                    file_size = int(response.headers.get('Content-Length', 0))
                    
                    # Download in chunks
                    async with aiofiles.open(local_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            await f.write(chunk)
            
            # Process media based on type
            media_info = await self._process_media(local_path, media_type)
            
            # Create media record
            media_record = {
                'url': url,
                'local_path': local_path,
                'media_type': media_type,
                'extension': extension,
                'file_size': file_size or os.path.getsize(local_path),
                'metadata': metadata or {},
                **media_info
            }
            
            # Store in registry
            self.media_registry[url_hash] = media_record
            
            logger.info(f"Downloaded {media_type}: {url} -> {local_path}")
            return media_record
            
        except Exception as e:
            logger.error(f"Failed to download {url}: {str(e)}")
            return None
    
    def _detect_media_type(self, url: str) -> Tuple[Optional[str], str]:
        """Detect media type from URL"""
        
        # Parse URL
        parsed = urlparse(url)
        path = unquote(parsed.path.lower())
        
        # Check extension
        for ext in self.image_extensions:
            if path.endswith(ext):
                return 'image', ext
        
        for ext in self.video_extensions:
            if path.endswith(ext):
                return 'video', ext
        
        for ext in self.audio_extensions:
            if path.endswith(ext):
                return 'audio', ext
        
        # Special handling for common image hosting services
        if any(host in parsed.netloc for host in ['unsplash.com', 'pexels.com', 'pixabay.com', 'imgur.com']):
            return 'image', '.jpg'
        
        # Check query parameters for format hints
        if parsed.query:
            query_lower = parsed.query.lower()
            if any(fmt in query_lower for fmt in ['format=jpg', 'format=jpeg', 'format=png', 'fm=jpg', 'fm=jpeg']):
                return 'image', '.jpg'
            elif any(fmt in query_lower for fmt in ['format=mp4', 'format=webm']):
                return 'video', '.mp4'
        
        # Try to guess from mimetype
        mime_type, _ = mimetypes.guess_type(url)
        if mime_type:
            if mime_type.startswith('image/'):
                return 'image', '.jpg'
            elif mime_type.startswith('video/'):
                return 'video', '.mp4'
            elif mime_type.startswith('audio/'):
                return 'audio', '.mp3'
        
        # Default to image for URLs with common image parameters
        if any(param in url.lower() for param in ['w=', 'width=', 'h=', 'height=', 'size=', 'quality=']):
            return 'image', '.jpg'
        
        return None, ''
    
    async def _process_media(self, file_path: str, media_type: str) -> Dict[str, Any]:
        """Process media file and extract metadata"""
        
        info = {}
        
        if media_type == 'image':
            info.update(await self._process_image(file_path))
        elif media_type == 'video':
            info.update(await self._process_video(file_path))
        elif media_type == 'audio':
            info.update(await self._process_audio(file_path))
        
        return info
    
    async def _process_image(self, file_path: str) -> Dict[str, Any]:
        """Process image and extract metadata"""
        
        try:
            # Use ffprobe to get image info
            cmd = [
                'ffprobe', '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=width,height',
                '-of', 'json',
                file_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                if data.get('streams'):
                    stream = data['streams'][0]
                    return {
                        'width': stream.get('width', 0),
                        'height': stream.get('height', 0),
                        'dimensions': (stream.get('width', 0), stream.get('height', 0))
                    }
        except Exception as e:
            logger.warning(f"Failed to process image {file_path}: {str(e)}")
        
        return {}
    
    async def _process_video(self, file_path: str) -> Dict[str, Any]:
        """Process video and extract metadata"""
        
        try:
            # Use ffprobe to get video info
            cmd = [
                'ffprobe', '-v', 'error',
                '-show_entries', 'format=duration',
                '-show_entries', 'stream=width,height,r_frame_rate',
                '-of', 'json',
                file_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                
                info = {}
                
                # Get duration
                if data.get('format'):
                    duration = data['format'].get('duration')
                    if duration:
                        info['duration'] = float(duration)
                
                # Get dimensions and framerate
                if data.get('streams'):
                    stream = data['streams'][0]
                    info['width'] = stream.get('width', 0)
                    info['height'] = stream.get('height', 0)
                    info['dimensions'] = (stream.get('width', 0), stream.get('height', 0))
                    
                    # Parse framerate
                    fps_str = stream.get('r_frame_rate', '0/1')
                    try:
                        num, den = map(int, fps_str.split('/'))
                        if den > 0:
                            info['fps'] = num / den
                    except:
                        pass
                
                # Generate thumbnail
                thumbnail_path = await self._generate_video_thumbnail(file_path)
                if thumbnail_path:
                    info['thumbnail_path'] = thumbnail_path
                
                return info
                
        except Exception as e:
            logger.warning(f"Failed to process video {file_path}: {str(e)}")
        
        return {}
    
    async def _process_audio(self, file_path: str) -> Dict[str, Any]:
        """Process audio and extract metadata"""
        
        try:
            # Use ffprobe to get audio info
            cmd = [
                'ffprobe', '-v', 'error',
                '-show_entries', 'format=duration',
                '-show_entries', 'stream=sample_rate,channels',
                '-of', 'json',
                file_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                
                info = {}
                
                # Get duration
                if data.get('format'):
                    duration = data['format'].get('duration')
                    if duration:
                        info['duration'] = float(duration)
                
                # Get audio properties
                if data.get('streams'):
                    stream = data['streams'][0]
                    info['sample_rate'] = stream.get('sample_rate')
                    info['channels'] = stream.get('channels')
                
                return info
                
        except Exception as e:
            logger.warning(f"Failed to process audio {file_path}: {str(e)}")
        
        return {}
    
    async def _generate_video_thumbnail(self, video_path: str) -> Optional[str]:
        """Generate thumbnail from video"""
        
        try:
            # Generate thumbnail at 2 seconds or 10% of duration
            thumbnail_path = video_path.replace('.mp4', '_thumb.jpg')
            
            cmd = [
                'ffmpeg', '-y',
                '-i', video_path,
                '-ss', '2',  # Seek to 2 seconds
                '-vframes', '1',  # Extract 1 frame
                '-vf', 'scale=640:-1',  # Scale to 640px width
                thumbnail_path
            ]
            
            result = subprocess.run(cmd, capture_output=True)
            if result.returncode == 0 and os.path.exists(thumbnail_path):
                return thumbnail_path
                
        except Exception as e:
            logger.warning(f"Failed to generate thumbnail: {str(e)}")
        
        return None
    
    def get_media_by_type(self, media_type: str) -> List[Dict[str, Any]]:
        """Get all downloaded media of a specific type"""
        
        return [
            media for media in self.media_registry.values()
            if media['media_type'] == media_type
        ]
    
    def clean_cache(self, max_age_days: int = 7):
        """Clean old media from cache"""
        
        import time
        current_time = time.time()
        max_age_seconds = max_age_days * 24 * 60 * 60
        
        removed = 0
        for url_hash, media in list(self.media_registry.items()):
            file_path = media['local_path']
            
            if os.path.exists(file_path):
                file_age = current_time - os.path.getmtime(file_path)
                
                if file_age > max_age_seconds:
                    try:
                        os.remove(file_path)
                        # Remove thumbnail if exists
                        if 'thumbnail_path' in media:
                            if os.path.exists(media['thumbnail_path']):
                                os.remove(media['thumbnail_path'])
                        
                        del self.media_registry[url_hash]
                        removed += 1
                    except Exception as e:
                        logger.error(f"Failed to remove {file_path}: {str(e)}")
        
        if removed > 0:
            self._save_registry()
            logger.info(f"Cleaned {removed} old media files from cache")
    
    async def extract_video_clips(
        self,
        video_path: str,
        segments: List[Tuple[float, float]],
        output_dir: Optional[str] = None
    ) -> List[str]:
        """Extract specific segments from a video"""
        
        if not output_dir:
            output_dir = os.path.join(self.cache_dir, "clips")
        os.makedirs(output_dir, exist_ok=True)
        
        clips = []
        
        for i, (start, end) in enumerate(segments):
            duration = end - start
            output_path = os.path.join(
                output_dir,
                f"{os.path.basename(video_path)}_clip_{i}.mp4"
            )
            
            cmd = [
                'ffmpeg', '-y',
                '-i', video_path,
                '-ss', str(start),
                '-t', str(duration),
                '-c', 'copy',
                output_path
            ]
            
            try:
                result = subprocess.run(cmd, capture_output=True)
                if result.returncode == 0:
                    clips.append(output_path)
                    logger.info(f"Extracted clip: {output_path}")
            except Exception as e:
                logger.error(f"Failed to extract clip: {str(e)}")
        
        return clips