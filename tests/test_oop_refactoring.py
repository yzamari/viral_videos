"""
Comprehensive tests for OOP refactoring
Tests all interfaces, providers, and dependency injection
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ai.interfaces.auth import AuthProvider, AuthType, Credentials
from src.ai.interfaces.storage import StorageProvider, StorageConfig, StorageType, StorageObject
from src.ai.interfaces.video_generation_enhanced import (
    VideoGenerationProvider,
    VideoGenerationConfig,
    EnhancedVideoRequest,
    EnhancedVideoResponse,
    VideoProvider,
    VideoStyle,
    VideoQuality,
    VideoGenerationOrchestrator
)
from src.agents.interfaces import (
    AgentInterface,
    AgentContext,
    AgentResponse,
    AgentRole,
    AgentFactory,
    AgentOrchestrator
)
from src.infrastructure.di_container import DIContainer, ContainerBuilder, get_container

# Test Authentication Providers
class TestAuthProviders:
    """Test authentication provider interface"""
    
    @pytest.mark.asyncio
    async def test_api_key_auth(self):
        """Test API key authentication"""
        from src.ai.providers.auth.api_key_auth import APIKeyAuthProvider
        
        provider = APIKeyAuthProvider(
            api_key="test-key-123",
            header_name="X-API-Key"
        )
        
        credentials = await provider.get_credentials()
        
        assert credentials.auth_type == AuthType.API_KEY
        assert credentials.api_key == "test-key-123"
        assert not credentials.is_expired()
        
        headers = provider.get_headers()
        assert headers["X-API-Key"] == "test-key-123"
    
    @pytest.mark.asyncio
    async def test_google_auth_mock(self):
        """Test Google Cloud authentication with mock"""
        from src.ai.providers.auth.google_auth import GoogleCloudAuthProvider
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = "mock-access-token"
            mock_run.return_value.returncode = 0
            
            provider = GoogleCloudAuthProvider(project_id="test-project")
            credentials = await provider.get_credentials()
            
            assert credentials.auth_type == AuthType.GOOGLE_CLOUD
            assert credentials.access_token == "mock-access-token"
            assert credentials.metadata['project_id'] == "test-project"

# Test Storage Providers
class TestStorageProviders:
    """Test storage provider interface"""
    
    @pytest.mark.asyncio
    async def test_local_storage(self, tmp_path):
        """Test local storage provider"""
        from src.ai.providers.storage.local_storage import LocalStorageProvider
        
        config = StorageConfig(
            storage_type=StorageType.LOCAL,
            base_path=str(tmp_path)
        )
        
        provider = LocalStorageProvider(config)
        
        # Test save
        data = b"Hello, World!"
        obj = await provider.save("test.txt", data, content_type="text/plain")
        
        assert obj.key == "test.txt"
        assert obj.size == len(data)
        assert obj.content_type == "text/plain"
        
        # Test load
        loaded_data = await provider.load("test.txt")
        assert loaded_data == data
        
        # Test exists
        assert await provider.exists("test.txt")
        assert not await provider.exists("nonexistent.txt")
        
        # Test list
        objects = await provider.list()
        assert len(objects) == 1
        assert objects[0].key == "test.txt"
        
        # Test delete
        assert await provider.delete("test.txt")
        assert not await provider.exists("test.txt")
    
    @pytest.mark.asyncio
    async def test_storage_streaming(self, tmp_path):
        """Test storage streaming"""
        from src.ai.providers.storage.local_storage import LocalStorageProvider
        
        config = StorageConfig(
            storage_type=StorageType.LOCAL,
            base_path=str(tmp_path)
        )
        
        provider = LocalStorageProvider(config)
        
        # Save large data
        large_data = b"x" * 10000
        await provider.save("large.bin", large_data)
        
        # Stream data
        chunks = []
        async for chunk in provider.stream("large.bin", chunk_size=1000):
            chunks.append(chunk)
        
        assert len(chunks) == 10
        assert b"".join(chunks) == large_data

# Test Video Generation Providers
class TestVideoProviders:
    """Test video generation provider interface"""
    
    def test_video_provider_capabilities(self):
        """Test video provider capability checking"""
        from src.ai.providers.video.veo3_provider import Veo3VideoProvider
        from src.ai.providers.auth.google_auth import GoogleCloudAuthProvider
        
        auth = GoogleCloudAuthProvider()
        config = VideoGenerationConfig(
            provider=VideoProvider.VEO3,
            auth_provider=auth,
            custom_config={'project_id': 'test', 'location': 'us-central1'}
        )
        
        provider = Veo3VideoProvider(config)
        
        # Test capabilities
        assert provider.supports_audio() == True
        assert provider.supports_style(VideoStyle.CINEMATIC) == True
        assert provider.supports_style(VideoStyle.CARTOON) == False
        assert provider.get_max_duration() == 10.0
        assert "1920x1080" in provider.get_supported_resolutions()
    
    @pytest.mark.asyncio
    async def test_video_generation_mock(self):
        """Test video generation with mock"""
        from src.ai.providers.video.veo3_provider import Veo3VideoProvider
        
        # Create mock auth provider
        mock_auth = Mock(spec=AuthProvider)
        mock_auth.ensure_valid_credentials = AsyncMock(return_value=Credentials(
            auth_type=AuthType.GOOGLE_CLOUD,
            access_token="mock-token"
        ))
        
        config = VideoGenerationConfig(
            provider=VideoProvider.VEO3,
            auth_provider=mock_auth,
            custom_config={'project_id': 'test', 'location': 'us-central1'}
        )
        
        provider = Veo3VideoProvider(config)
        
        # Mock the API call
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                'name': 'operations/job-123'
            })
            
            # Create proper async context manager mock
            mock_post = AsyncMock()
            mock_post.__aenter__ = AsyncMock(return_value=mock_response)
            mock_post.__aexit__ = AsyncMock(return_value=None)
            
            mock_session_instance = AsyncMock()
            mock_session_instance.post = Mock(return_value=mock_post)
            mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
            mock_session_instance.__aexit__ = AsyncMock(return_value=None)
            
            mock_session.return_value = mock_session_instance
            
            request = EnhancedVideoRequest(
                prompt="A beautiful sunset",
                duration=5.0,
                style=VideoStyle.CINEMATIC
            )
            
            response = await provider.generate_video(request)
            
            assert response.success == True
            assert response.job_id == "job-123"
            assert response.provider_used == VideoProvider.VEO3
    
    @pytest.mark.asyncio
    async def test_video_orchestrator(self):
        """Test video generation orchestrator"""
        # Create mock providers
        mock_veo3 = Mock(spec=VideoGenerationProvider)
        mock_veo3.is_available.return_value = True
        mock_veo3.generate_video = AsyncMock(return_value=EnhancedVideoResponse(
            success=False,
            error_message="Veo3 failed"
        ))
        
        mock_runway = Mock(spec=VideoGenerationProvider)
        mock_runway.is_available.return_value = True
        mock_runway.generate_video = AsyncMock(return_value=EnhancedVideoResponse(
            success=True,
            job_id="runway-job-123",
            provider_used=VideoProvider.RUNWAY_ML
        ))
        
        # Create orchestrator
        orchestrator = VideoGenerationOrchestrator({
            VideoProvider.VEO3: mock_veo3,
            VideoProvider.RUNWAY_ML: mock_runway
        })
        
        orchestrator.set_fallback_chain([VideoProvider.VEO3, VideoProvider.RUNWAY_ML])
        
        # Test fallback
        request = EnhancedVideoRequest(
            prompt="Test video",
            duration=5.0
        )
        
        response = await orchestrator.generate_with_fallback(request)
        
        assert response.success == True
        assert response.provider_used == VideoProvider.RUNWAY_ML
        assert mock_veo3.generate_video.called
        assert mock_runway.generate_video.called

# Test Agent System
class TestAgentSystem:
    """Test agent system with dependency injection"""
    
    @pytest.mark.asyncio
    async def test_agent_interface(self):
        """Test agent interface"""
        from src.ai.interfaces.text_generation import TextGenerationService
        
        # Create mock AI service
        mock_ai = Mock(spec=TextGenerationService)
        
        # Create test agent
        class TestAgent(AgentInterface[str]):
            async def execute(self, context: AgentContext) -> AgentResponse[str]:
                return AgentResponse(
                    success=True,
                    data="Test result",
                    confidence=0.9
                )
            
            def get_capabilities(self) -> list:
                return ["test", "mock"]
        
        agent = TestAgent(mock_ai, AgentRole.TREND_ANALYST)
        
        context = AgentContext(
            mission="Test mission",
            session_id="test-123"
        )
        
        response = await agent.execute(context)
        
        assert response.success == True
        assert response.data == "Test result"
        assert response.confidence == 0.9
    
    @pytest.mark.asyncio
    async def test_agent_orchestrator(self):
        """Test agent orchestrator"""
        from src.ai.manager import AIServiceManager
        
        # Create mock AI manager
        mock_ai_manager = Mock(spec=AIServiceManager)
        mock_text_service = Mock()
        mock_ai_manager.get_text_service.return_value = mock_text_service
        
        # Create factory
        factory = AgentFactory(mock_ai_manager)
        
        # Register test agents
        class TestAgent1(AgentInterface[str]):
            async def execute(self, context: AgentContext) -> AgentResponse[str]:
                return AgentResponse(success=True, data="Agent1", confidence=0.8)
            
            def get_capabilities(self): return []
        
        class TestAgent2(AgentInterface[str]):
            async def execute(self, context: AgentContext) -> AgentResponse[str]:
                return AgentResponse(success=True, data="Agent2", confidence=0.9)
            
            def get_capabilities(self): return []
        
        factory.register(AgentRole.TREND_ANALYST, TestAgent1)
        factory.register(AgentRole.SCRIPT_WRITER, TestAgent2)
        
        # Create orchestrator
        orchestrator = AgentOrchestrator(factory)
        
        context = AgentContext(
            mission="Test",
            session_id="test-123"
        )
        
        # Test sequential execution
        responses = await orchestrator.execute_sequential(
            context,
            [AgentRole.TREND_ANALYST, AgentRole.SCRIPT_WRITER]
        )
        
        assert len(responses) == 2
        assert responses[0].data == "Agent1"
        assert responses[1].data == "Agent2"
        
        # Test parallel execution
        responses = await orchestrator.execute_parallel(
            context,
            [AgentRole.TREND_ANALYST, AgentRole.SCRIPT_WRITER]
        )
        
        assert len(responses) == 2
        
        # Test voting
        response = await orchestrator.execute_with_voting(
            context,
            [AgentRole.TREND_ANALYST, AgentRole.SCRIPT_WRITER],
            threshold=0.5
        )
        
        assert response.success == True
        assert response.data == "Agent2"  # Higher confidence

# Test Dependency Injection Container
class TestDIContainer:
    """Test dependency injection container"""
    
    def test_container_registration(self):
        """Test service registration"""
        container = DIContainer()
        
        # Register a simple service
        class IService:
            pass
        
        class ServiceImpl(IService):
            def __init__(self):
                self.value = "test"
        
        container.register(IService, ServiceImpl)
        
        # Resolve service
        service = container.resolve(IService)
        
        assert isinstance(service, ServiceImpl)
        assert service.value == "test"
        
        # Test singleton
        service2 = container.resolve(IService)
        assert service is service2
    
    def test_container_builder(self):
        """Test container builder"""
        builder = ContainerBuilder()
        container = builder.build()
        
        assert container is not None
    
    @patch.dict(os.environ, {'GOOGLE_CLOUD_PROJECT': 'test-project'})
    def test_full_container_with_mocks(self):
        """Test full container with mocked services"""
        from src.ai.manager import AIServiceManager
        
        # Build container
        container = (ContainerBuilder()
            .register_authentication()
            .register_storage()
            .register_ai_services()
            .build())
        
        # Resolve AI manager
        ai_manager = container.resolve(AIServiceManager)
        assert ai_manager is not None

# Integration test
class TestIntegration:
    """Integration tests for the refactored system"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_video_generation(self, tmp_path):
        """Test end-to-end video generation with all components"""
        # This would be a full integration test in production
        # For now, we mock external services
        
        from src.ai.providers.auth.api_key_auth import APIKeyAuthProvider
        from src.ai.providers.storage.local_storage import LocalStorageProvider
        
        # Setup components
        auth = APIKeyAuthProvider("test-key")
        storage_config = StorageConfig(
            storage_type=StorageType.LOCAL,
            base_path=str(tmp_path)
        )
        storage = LocalStorageProvider(storage_config)
        
        # Create mock video provider
        mock_provider = Mock(spec=VideoGenerationProvider)
        mock_provider.is_available.return_value = True
        mock_provider.generate_video = AsyncMock(return_value=EnhancedVideoResponse(
            success=True,
            job_id="test-job",
            provider_used=VideoProvider.VEO3
        ))
        
        # Create orchestrator
        orchestrator = VideoGenerationOrchestrator({
            VideoProvider.VEO3: mock_provider
        })
        
        # Make request
        request = EnhancedVideoRequest(
            prompt="Test video",
            duration=5.0,
            quality=VideoQuality.STANDARD
        )
        
        response = await orchestrator.generate_with_fallback(request)
        
        assert response.success == True
        assert response.job_id == "test-job"

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])