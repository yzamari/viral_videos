"""
Parallel Processing Utilities
Enables concurrent execution of AI operations for faster video generation
"""

import asyncio
import concurrent.futures
from typing import List, Dict, Any, Callable, Optional
from functools import partial
import time

from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class ParallelProcessor:
    """
    Manages parallel execution of AI operations
    Optimizes performance by running independent tasks concurrently
    """
    
    def __init__(self, max_workers: int = 4):
        """Initialize parallel processor"""
        self.max_workers = max_workers
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        logger.info(f"🚀 Parallel Processor initialized with {max_workers} workers")
    
    async def run_parallel_ai_discussions(self, discussion_tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run multiple AI discussions in parallel"""
        logger.info(f"🔄 Running {len(discussion_tasks)} AI discussions in parallel")
        start_time = time.time()
        
        async def run_single_discussion(task_info):
            """Run a single discussion task"""
            discussion_system = task_info['discussion_system']
            topic = task_info['topic']
            participants = task_info['participants']
            
            try:
                result = discussion_system.start_discussion(topic, participants)
                return {
                    'task_id': task_info['task_id'],
                    'status': 'completed',
                    'result': result,
                    'topic': topic.title
                }
            except Exception as e:
                logger.error(f"❌ Discussion failed for {task_info['task_id']}: {e}")
                return {
                    'task_id': task_info['task_id'],
                    'status': 'failed', 
                    'error': str(e),
                    'topic': topic.title
                }
        
        # Run all discussions concurrently
        tasks = [run_single_discussion(task) for task in discussion_tasks]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        discussion_results = {}
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"❌ Discussion task failed: {result}")
                continue
                
            if result['status'] == 'completed':
                discussion_results[result['task_id']] = result['result']
                logger.info(f"✅ Discussion completed: {result['topic']}")
            else:
                logger.warning(f"⚠️ Discussion failed: {result['topic']}")
        
        elapsed_time = time.time() - start_time
        logger.info(f"🚀 Parallel discussions completed in {elapsed_time:.1f}s (vs ~{len(discussion_tasks) * 20}s sequential)")
        
        return discussion_results
    
    async def run_parallel_script_processing(self, script_tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run script generation and processing in parallel"""
        logger.info(f"📝 Running {len(script_tasks)} script tasks in parallel")
        start_time = time.time()
        
        async def run_script_task(task_info):
            """Run a single script processing task"""
            try:
                func = task_info['function']
                args = task_info.get('args', [])
                kwargs = task_info.get('kwargs', {})
                
                # Run in executor for CPU-bound operations
                loop = asyncio.get_event_loop()
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = await loop.run_in_executor(self.executor, partial(func, *args, **kwargs))
                
                return {
                    'task_id': task_info['task_id'],
                    'status': 'completed',
                    'result': result
                }
            except Exception as e:
                logger.error(f"❌ Script task failed for {task_info['task_id']}: {e}")
                return {
                    'task_id': task_info['task_id'],
                    'status': 'failed',
                    'error': str(e)
                }
        
        # Run all script tasks concurrently
        tasks = [run_script_task(task) for task in script_tasks]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        script_results = {}
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"❌ Script task failed: {result}")
                continue
                
            if result['status'] == 'completed':
                script_results[result['task_id']] = result['result']
                logger.info(f"✅ Script task completed: {result['task_id']}")
            else:
                logger.warning(f"⚠️ Script task failed: {result['task_id']}")
        
        elapsed_time = time.time() - start_time
        logger.info(f"📝 Parallel script processing completed in {elapsed_time:.1f}s")
        
        return script_results
    
    async def run_parallel_media_generation(self, media_tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run video and audio generation in parallel"""
        logger.info(f"🎬 Running {len(media_tasks)} media generation tasks in parallel")
        start_time = time.time()
        
        async def run_media_task(task_info):
            """Run a single media generation task"""
            try:
                func = task_info['function']
                args = task_info.get('args', [])
                kwargs = task_info.get('kwargs', {})
                task_type = task_info.get('type', 'unknown')
                
                # Run in executor for I/O-bound operations
                loop = asyncio.get_event_loop()
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = await loop.run_in_executor(self.executor, partial(func, *args, **kwargs))
                
                return {
                    'task_id': task_info['task_id'],
                    'type': task_type,
                    'status': 'completed',
                    'result': result
                }
            except Exception as e:
                logger.error(f"❌ Media task failed for {task_info['task_id']}: {e}")
                return {
                    'task_id': task_info['task_id'],
                    'type': task_info.get('type', 'unknown'),
                    'status': 'failed',
                    'error': str(e)
                }
        
        # Run all media tasks concurrently
        tasks = [run_media_task(task) for task in media_tasks]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results by type
        media_results = {
            'video_clips': [],
            'audio_segments': [],
            'failed_tasks': []
        }
        
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"❌ Media task failed: {result}")
                continue
                
            if result['status'] == 'completed':
                if result['type'] == 'video_clip':
                    media_results['video_clips'].append(result['result'])
                elif result['type'] == 'audio_segment':
                    media_results['audio_segments'].append(result['result'])
                logger.info(f"✅ Media task completed: {result['task_id']} ({result['type']})")
            else:
                media_results['failed_tasks'].append(result)
                logger.warning(f"⚠️ Media task failed: {result['task_id']}")
        
        elapsed_time = time.time() - start_time
        logger.info(f"🎬 Parallel media generation completed in {elapsed_time:.1f}s")
        
        return media_results
    
    async def run_concurrent_batch(self, batch_tasks: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Run multiple different task types concurrently"""
        logger.info(f"🚀 Running concurrent batch with {sum(len(tasks) for tasks in batch_tasks.values())} total tasks")
        start_time = time.time()
        
        concurrent_tasks = []
        task_types = []
        
        # Set up concurrent execution for different task types
        if 'discussions' in batch_tasks:
            concurrent_tasks.append(self.run_parallel_ai_discussions(batch_tasks['discussions']))
            task_types.append('discussions')
        
        if 'scripts' in batch_tasks:
            concurrent_tasks.append(self.run_parallel_script_processing(batch_tasks['scripts']))
            task_types.append('scripts')
            
        if 'media' in batch_tasks:
            concurrent_tasks.append(self.run_parallel_media_generation(batch_tasks['media']))
            task_types.append('media')
        
        # Execute all task types concurrently
        results = await asyncio.gather(*concurrent_tasks, return_exceptions=True)
        
        # Combine results
        combined_results = {}
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"❌ Task type {task_types[i]} failed: {result}")
                continue
            combined_results[task_types[i]] = result
        
        elapsed_time = time.time() - start_time
        logger.info(f"🚀 Concurrent batch completed in {elapsed_time:.1f}s")
        
        return combined_results
    
    def __del__(self):
        """Cleanup executor on deletion"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)