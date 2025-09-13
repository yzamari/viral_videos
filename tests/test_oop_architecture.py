"""
Comprehensive test suite for the OOP architecture implementation.

This test suite verifies that the OOP refactoring follows SOLID principles
and maintains proper separation of concerns across all layers.
"""

import pytest
import asyncio
import tempfile
import shutil
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any

# Domain entities
from src.domain.entities.user import User, UserRole, UserStatus
from src.domain.entities.video_session import VideoSession, VideoGenerationConfig, VideoSessionStatus
from src.domain.entities.campaign import Campaign, CampaignStatus, CampaignPriority

# Repositories
from src.repositories.user_repository import UserRepository
from src.repositories.video_session_repository import VideoSessionRepository
from src.repositories.campaign_repository import CampaignRepository

# Services
from src.services.authentication_service import AuthenticationService
from src.services.video_generation_service import VideoGenerationService
from src.services.campaign_service import CampaignService

# Infrastructure
from src.infrastructure.enhanced_di_container import EnhancedDIContainer

# Exceptions
from src.utils.exceptions import (
    AuthenticationError, 
    VideoGenerationError, 
    CampaignError, 
    RepositoryError
)


class TestDomainEntities:
    """Test suite for domain entities following SOLID principles"""
    
    def test_user_entity_creation_and_validation(self):
        """Test User entity creation and business logic encapsulation"""
        # Test valid user creation
        user = User.create_new_user(
            user_id="test-123",
            username="testuser",
            email="test@example.com",
            password="securepassword123",
            organization="Test Org"
        )
        
        assert user.id == "test-123"
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.organization == "Test Org"
        assert user.role == UserRole.TRIAL
        assert user.status == UserStatus.PENDING_VERIFICATION
        
        # Test password verification (encapsulation)
        assert user.verify_password("securepassword123") is True
        assert user.verify_password("wrongpassword") is False
        
        # Test business logic methods
        assert user.can_generate_videos() is False  # Not verified yet
        assert user.is_trial_user() is True
        assert user.get_remaining_trial_days() == 14  # Default trial period
    
    def test_user_entity_validation_errors(self):
        """Test User entity validation following fail-fast principle"""
        # Test invalid username
        with pytest.raises(ValueError, match="Username must be between 3 and 50 characters"):
            User.create_new_user("test", "ab", "test@example.com", "password123")
        
        # Test invalid email
        with pytest.raises(ValueError, match="Invalid email format"):
            User.create_new_user("test", "testuser", "invalid-email", "password123")
        
        # Test weak password
        with pytest.raises(ValueError, match="Password must be at least 8 characters long"):
            User.create_new_user("test", "testuser", "test@example.com", "weak")
    
    def test_user_business_logic_methods(self):
        """Test User entity business logic encapsulation"""
        user = User.create_new_user("test", "testuser", "test@example.com", "password123")
        
        # Test email verification
        user.verify_email()
        assert user.is_email_verified() is True
        assert user.status == UserStatus.ACTIVE
        
        # Test session management
        user.add_session("session-1")
        assert "session-1" in user.active_sessions
        assert user.can_create_new_session() is True  # Trial allows 1 session
        
        user.remove_session("session-1")
        assert "session-1" not in user.active_sessions
    
    def test_video_session_entity_creation(self):
        """Test VideoSession entity creation and state management"""
        config = VideoGenerationConfig(
            mission="Test video generation",
            platform="youtube",
            duration=30,
            discussion_mode="enhanced"
        )
        
        session = VideoSession.create_new_session(
            session_id="session-123",
            user_id="user-456",
            config=config,
            session_name="Test Session"
        )
        
        assert session.id == "session-123"
        assert session.user_id == "user-456"
        assert session.config.mission == "Test video generation"
        assert session.status == VideoSessionStatus.CREATED
    
    def test_video_session_state_transitions(self):
        """Test VideoSession state transitions follow business rules"""
        config = VideoGenerationConfig(mission="Test", platform="youtube")
        session = VideoSession.create_new_session("session", "user", config)
        
        # Test valid state transitions
        session.start_generation()
        assert session.status == VideoSessionStatus.QUEUED
        
        session.begin_processing()
        assert session.status == VideoSessionStatus.GENERATING
        
        session.update_progress("Script Generation", 50.0)
        assert session.current_phase == "Script Generation"
        assert session.progress_percentage == 50.0
        
        # Test completion
        session.complete_successfully("output/video.mp4")
        assert session.status == VideoSessionStatus.COMPLETED
        assert session.output_video_path == "output/video.mp4"
    
    def test_campaign_entity_creation_and_management(self):
        """Test Campaign entity creation and lifecycle management"""
        campaign = Campaign.create_new_campaign(
            campaign_id="campaign-123",
            name="Test Campaign",
            description="A test marketing campaign",
            user_id="user-456",
            target_platforms=["youtube", "tiktok"]
        )
        
        assert campaign.id == "campaign-123"
        assert campaign.name == "Test Campaign"
        assert campaign.user_id == "user-456"
        assert campaign.target_platforms == ["youtube", "tiktok"]
        assert campaign.status == CampaignStatus.DRAFT
        
        # Test adding videos to campaign
        campaign.add_video_session("session-1")
        campaign.add_video_session("session-2")
        assert campaign.total_planned_videos == 2
        
        # Test campaign activation
        campaign.activate_campaign()
        assert campaign.status == CampaignStatus.ACTIVE


class TestRepositoryPattern:
    """Test suite for Repository pattern implementation"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test data"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def user_repository(self, temp_dir):
        """Create UserRepository for testing"""
        return UserRepository(base_path=f"{temp_dir}/users")
    
    @pytest.fixture
    def sample_user(self):
        """Create sample user for testing"""
        return User.create_new_user(
            user_id=str(uuid.uuid4()),
            username="testuser",
            email="test@example.com",
            password="password123"
        )
    
    @pytest.mark.asyncio
    async def test_user_repository_crud_operations(self, user_repository, sample_user):
        """Test UserRepository CRUD operations"""
        # Test save
        await user_repository.save(sample_user)
        
        # Test get_by_id
        retrieved_user = await user_repository.get_by_id(sample_user.id)
        assert retrieved_user is not None
        assert retrieved_user.username == sample_user.username
        assert retrieved_user.email == sample_user.email
        
        # Test get_by_username
        user_by_username = await user_repository.get_by_username(sample_user.username)
        assert user_by_username is not None
        assert user_by_username.id == sample_user.id
        
        # Test get_by_email
        user_by_email = await user_repository.get_by_email(sample_user.email)
        assert user_by_email is not None
        assert user_by_email.id == sample_user.id
        
        # Test exists
        assert await user_repository.exists(sample_user.id) is True
        assert await user_repository.exists("non-existent") is False
        
        # Test delete
        success = await user_repository.delete(sample_user.id)
        assert success is True
        assert await user_repository.exists(sample_user.id) is False
    
    @pytest.mark.asyncio
    async def test_user_repository_query_methods(self, user_repository, temp_dir):
        """Test UserRepository query methods"""
        # Create multiple users
        users = []
        for i in range(5):
            user = User.create_new_user(
                user_id=str(uuid.uuid4()),
                username=f"user{i}",
                email=f"user{i}@example.com",
                password="password123"
            )
            if i < 2:
                user.role = UserRole.PREMIUM
            users.append(user)
            await user_repository.save(user)
        
        # Test list_all
        all_users = await user_repository.list_all()
        assert len(all_users) == 5
        
        # Test find_by_role
        premium_users = await user_repository.find_by_role("premium")
        assert len(premium_users) == 2
        
        # Test count
        count = await user_repository.count()
        assert count == 5
        
        # Test pagination
        page1 = await user_repository.list_all(limit=3, offset=0)
        assert len(page1) == 3
        
        page2 = await user_repository.list_all(limit=3, offset=3)
        assert len(page2) == 2


class TestServiceLayer:
    """Test suite for Service layer implementation"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test data"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def user_repository(self, temp_dir):
        """Create UserRepository for testing"""
        return UserRepository(base_path=f"{temp_dir}/users")
    
    @pytest.fixture
    def video_session_repository(self, temp_dir):
        """Create VideoSessionRepository for testing"""
        return VideoSessionRepository(base_path=f"{temp_dir}/sessions")
    
    @pytest.fixture
    def authentication_service(self, user_repository):
        """Create AuthenticationService for testing"""
        return AuthenticationService(
            user_repository=user_repository,
            secret_key="test-secret-key"
        )
    
    @pytest.fixture
    def video_generation_service(self, user_repository, video_session_repository):
        """Create VideoGenerationService for testing"""
        return VideoGenerationService(
            user_repository=user_repository,
            video_session_repository=video_session_repository
        )
    
    @pytest.mark.asyncio
    async def test_authentication_service_registration(self, authentication_service):
        """Test AuthenticationService user registration"""
        # Test successful registration
        user = await authentication_service.register_user(
            username="newuser",
            email="newuser@example.com",
            password="securepassword123",
            organization="Test Corp"
        )
        
        assert user.username == "newuser"
        assert user.email == "newuser@example.com"
        assert user.organization == "Test Corp"
        assert user.role == UserRole.TRIAL
        
        # Test duplicate username error
        with pytest.raises(AuthenticationError, match="Username already exists"):
            await authentication_service.register_user(
                username="newuser",  # Same username
                email="different@example.com",
                password="password123"
            )
        
        # Test duplicate email error
        with pytest.raises(AuthenticationError, match="Email already registered"):
            await authentication_service.register_user(
                username="differentuser",
                email="newuser@example.com",  # Same email
                password="password123"
            )
    
    @pytest.mark.asyncio
    async def test_authentication_service_login(self, authentication_service):
        """Test AuthenticationService user authentication"""
        # Register user first
        await authentication_service.register_user(
            username="testuser",
            email="test@example.com",
            password="correctpassword"
        )
        
        # Test successful authentication
        user = await authentication_service.authenticate_user(
            username="testuser",
            password="correctpassword"
        )
        assert user is not None
        assert user.username == "testuser"
        
        # Test authentication with email
        user = await authentication_service.authenticate_user(
            username="test@example.com",  # Using email
            password="correctpassword"
        )
        assert user is not None
        assert user.username == "testuser"
        
        # Test failed authentication
        user = await authentication_service.authenticate_user(
            username="testuser",
            password="wrongpassword"
        )
        assert user is None
    
    @pytest.mark.asyncio
    async def test_authentication_service_tokens(self, authentication_service):
        """Test AuthenticationService JWT token management"""
        # Register and authenticate user
        user = await authentication_service.register_user(
            username="tokenuser",
            email="token@example.com",
            password="password123"
        )
        
        # Test token creation
        token = await authentication_service.create_access_token(user)
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Test token verification
        verified_user = await authentication_service.verify_access_token(token)
        assert verified_user is not None
        assert verified_user.id == user.id
        
        # Test token refresh
        new_token = await authentication_service.refresh_access_token(user)
        assert isinstance(new_token, str)
        assert new_token != token  # Should be different
    
    @pytest.mark.asyncio
    async def test_video_generation_service_session_creation(self, video_generation_service, user_repository):
        """Test VideoGenerationService session creation"""
        # Create and save user
        user = User.create_new_user("user1", "user1", "user1@example.com", "password")
        user.verify_email()  # Make user active
        await user_repository.save(user)
        
        # Create video generation config
        config = VideoGenerationConfig(
            mission="Test video generation",
            platform="youtube",
            duration=30
        )
        
        # Test successful session creation
        session = await video_generation_service.create_video_session(user.id, config)
        assert session.user_id == user.id
        assert session.config.mission == "Test video generation"
        assert session.status == VideoSessionStatus.CREATED
    
    @pytest.mark.asyncio
    async def test_video_generation_service_validation(self, video_generation_service, user_repository):
        """Test VideoGenerationService configuration validation"""
        # Create user
        user = User.create_new_user("user1", "user1", "user1@example.com", "password")
        user.verify_email()
        await user_repository.save(user)
        
        # Test valid configuration
        valid_config = VideoGenerationConfig(
            mission="Valid test video generation mission",
            platform="youtube",
            duration=30
        )
        
        validation = await video_generation_service.validate_generation_config(valid_config, user)
        assert validation["valid"] is True
        assert len(validation["errors"]) == 0
        
        # Test invalid configuration
        invalid_config = VideoGenerationConfig(
            mission="Short",  # Too short
            platform="youtube",
            duration=500  # Too long
        )
        
        validation = await video_generation_service.validate_generation_config(invalid_config, user)
        assert validation["valid"] is False
        assert len(validation["errors"]) > 0


class TestDependencyInjection:
    """Test suite for Dependency Injection container"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test data"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_enhanced_di_container_initialization(self, temp_dir):
        """Test EnhancedDIContainer initialization and component resolution"""
        config = {
            "data_path": temp_dir,
            "jwt": {
                "secret_key": "test-key",
                "algorithm": "HS256"
            }
        }
        
        container = EnhancedDIContainer(config)
        
        # Test repository resolution
        user_repo = container.get_user_repository()
        assert user_repo is not None
        assert hasattr(user_repo, 'save')
        assert hasattr(user_repo, 'get_by_id')
        
        video_repo = container.get_video_session_repository()
        assert video_repo is not None
        
        campaign_repo = container.get_campaign_repository()
        assert campaign_repo is not None
        
        # Test service resolution
        auth_service = container.get_authentication_service()
        assert auth_service is not None
        assert hasattr(auth_service, 'register_user')
        assert hasattr(auth_service, 'authenticate_user')
        
        video_service = container.get_video_generation_service()
        assert video_service is not None
        
        campaign_service = container.get_campaign_service()
        assert campaign_service is not None
    
    def test_di_container_health_check(self, temp_dir):
        """Test DI container health check functionality"""
        config = {"data_path": temp_dir}
        container = EnhancedDIContainer(config)
        
        health = container.health_check()
        assert health["status"] == "healthy"
        assert "enhanced_components" in health
        assert "repositories" in health["enhanced_components"]
        assert "services" in health["enhanced_components"]


class TestIntegration:
    """Integration tests for complete OOP architecture"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test data"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def container(self, temp_dir):
        """Create configured DI container"""
        config = {
            "data_path": temp_dir,
            "jwt": {"secret_key": "test-secret-key"},
            "video_generation": {"max_concurrent_generations": 2}
        }
        return EnhancedDIContainer(config)
    
    @pytest.mark.asyncio
    async def test_complete_user_registration_and_video_generation_flow(self, container):
        """Test complete flow from user registration to video generation"""
        auth_service = container.get_authentication_service()
        video_service = container.get_video_generation_service()
        
        # Step 1: Register user
        user = await auth_service.register_user(
            username="flowuser",
            email="flow@example.com",
            password="securepassword"
        )
        assert user is not None
        
        # Step 2: Verify email (simulate)
        success = await auth_service.verify_email(user.id, "verification-token")
        assert success is True
        
        # Step 3: Create access token
        token = await auth_service.create_access_token(user)
        assert token is not None
        
        # Step 4: Verify token
        verified_user = await auth_service.verify_access_token(token)
        assert verified_user.id == user.id
        
        # Step 5: Create video session
        config = VideoGenerationConfig(
            mission="Integration test video generation",
            platform="youtube",
            duration=20
        )
        
        session = await video_service.create_video_session(verified_user.id, config)
        assert session.user_id == verified_user.id
        assert session.status == VideoSessionStatus.CREATED
        
        # Step 6: Start generation
        success = await video_service.start_video_generation(session.id)
        assert success is True
        
        # Step 7: Check progress
        progress = await video_service.get_generation_progress(session.id)
        assert "session_id" in progress
        assert progress["session_id"] == session.id
    
    @pytest.mark.asyncio
    async def test_error_handling_across_layers(self, container):
        """Test error handling propagation across architecture layers"""
        auth_service = container.get_authentication_service()
        video_service = container.get_video_generation_service()
        
        # Test authentication error propagation
        with pytest.raises(AuthenticationError):
            await auth_service.register_user(
                username="ab",  # Too short
                email="invalid-email",
                password="weak"
            )
        
        # Test video generation error for non-existent user
        config = VideoGenerationConfig(
            mission="Test mission",
            platform="youtube"
        )
        
        with pytest.raises(VideoGenerationError):
            await video_service.create_video_session("non-existent-user", config)


class TestSOLIDPrinciples:
    """Test suite verifying SOLID principle adherence"""
    
    def test_single_responsibility_principle(self):
        """Verify each class has a single responsibility"""
        # User entity should only handle user-related logic
        user = User.create_new_user("test", "user", "user@example.com", "password")
        
        # Should have user-specific methods
        assert hasattr(user, 'verify_password')
        assert hasattr(user, 'can_generate_videos')
        assert hasattr(user, 'is_trial_user')
        
        # Should NOT have video generation logic
        assert not hasattr(user, 'generate_video')
        assert not hasattr(user, 'process_video')
    
    def test_open_closed_principle(self):
        """Verify classes are open for extension, closed for modification"""
        # Repository interfaces allow for new implementations
        # without modifying existing code
        from src.repositories.interfaces import IUserRepository
        
        # Can create new repository implementation
        class TestUserRepository(IUserRepository):
            async def save(self, user): pass
            async def get_by_id(self, user_id): pass
            async def delete(self, user_id): pass
            async def exists(self, user_id): pass
            async def list_all(self, limit=None, offset=0): pass
            async def count(self): pass
            async def get_by_username(self, username): pass
            async def get_by_email(self, email): pass
            async def find_by_role(self, role, limit=None): pass
            async def find_trial_users_expiring(self, days=7): pass
            async def find_inactive_users(self, days=30): pass
            async def update_last_login(self, user_id): pass
        
        # This satisfies the interface contract
        test_repo = TestUserRepository()
        assert isinstance(test_repo, IUserRepository)
    
    def test_liskov_substitution_principle(self):
        """Verify derived classes can replace base classes"""
        from src.repositories.interfaces import IUserRepository
        from src.repositories.user_repository import UserRepository
        
        # UserRepository should be substitutable for IUserRepository
        user_repo = UserRepository("test-path")
        assert isinstance(user_repo, IUserRepository)
        
        # All interface methods should be available
        interface_methods = [method for method in dir(IUserRepository) 
                           if not method.startswith('_') and callable(getattr(IUserRepository, method, None))]
        
        for method in interface_methods:
            assert hasattr(user_repo, method)
    
    def test_interface_segregation_principle(self):
        """Verify interfaces are segregated by responsibility"""
        from src.repositories.interfaces import IUserRepository, IVideoSessionRepository
        from src.services.interfaces import IAuthenticationService, IVideoGenerationService
        
        # Repository interfaces should be specific
        user_repo_methods = [m for m in dir(IUserRepository) if not m.startswith('_')]
        video_repo_methods = [m for m in dir(IVideoSessionRepository) if not m.startswith('_')]
        
        # Should not have significant overlap (except common CRUD operations)
        user_specific = set(user_repo_methods) - set(video_repo_methods)
        video_specific = set(video_repo_methods) - set(user_repo_methods)
        
        # Each interface should have specific methods
        assert len(user_specific) > 0
        assert len(video_specific) > 0
    
    def test_dependency_inversion_principle(self):
        """Verify high-level modules don't depend on low-level modules"""
        # Services should depend on repository interfaces, not implementations
        from src.services.authentication_service import AuthenticationService
        from src.repositories.interfaces import IUserRepository
        
        # Service constructor should accept interface, not concrete class
        import inspect
        
        constructor = AuthenticationService.__init__
        signature = inspect.signature(constructor)
        
        # Should have user_repository parameter
        assert 'user_repository' in signature.parameters
        
        # Parameter should be annotated with interface type
        param = signature.parameters['user_repository']
        assert param.annotation == IUserRepository


if __name__ == "__main__":
    """Run the test suite"""
    pytest.main([__file__, "-v", "--tb=short"])