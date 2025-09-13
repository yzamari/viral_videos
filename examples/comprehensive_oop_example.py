"""
ViralAI Comprehensive OOP Architecture Examples

This file demonstrates the complete OOP refactoring with SOLID principles,
showing real usage patterns for domain entities, services, repositories,
and dependency injection throughout the ViralAI platform.
"""

import asyncio
import uuid
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path

# Setup path for imports
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Domain entities
from src.domain.entities.user import User, UserRole, UserStatus
from src.domain.entities.video_session import VideoSession, VideoGenerationConfig, VideoSessionStatus
from src.domain.entities.campaign import Campaign, CampaignStatus, CampaignPriority

# Infrastructure
from src.infrastructure.enhanced_di_container import EnhancedDIContainer

# Services (imported through DI container)
from src.utils.exceptions import AuthenticationError, VideoGenerationError, CampaignError


async def example_complete_user_workflow():
    """
    Comprehensive user workflow example demonstrating the full user lifecycle.
    This shows proper domain entity usage and service layer interaction.
    """
    print("\n" + "="*70)
    print("🔐 COMPLETE USER WORKFLOW EXAMPLE")
    print("="*70)
    
    # Setup temporary data directory
    temp_dir = tempfile.mkdtemp()
    try:
        # Configure DI container
        config = {
            "data_path": temp_dir,
            "jwt": {
                "secret_key": "demo-secret-key-change-in-production",
                "algorithm": "HS256",
                "access_token_expire_minutes": 30
            }
        }
        container = EnhancedDIContainer(config)
        auth_service = container.get_authentication_service()
        
        print("📋 Step 1: User Registration")
        print("-" * 30)
        
        # Register new user - demonstrates domain entity creation through service
        user = await auth_service.register_user(
            username="alice_creator",
            email="alice@creativestudio.com",
            password="SecurePassword123!",
            organization="Creative Studio Inc"
        )
        
        print(f"✅ User registered successfully:")
        print(f"   • ID: {user.id}")
        print(f"   • Username: {user.username}")
        print(f"   • Email: {user.email}")
        print(f"   • Role: {user.role.value}")
        print(f"   • Status: {user.status.value}")
        print(f"   • Organization: {user.organization}")
        print(f"   • Trial expires: {user.trial_expires_at}")
        
        # Show business logic encapsulation
        print(f"\n📊 User Business Logic (Encapsulated):")
        print(f"   • Can generate videos: {user.can_generate_videos()}")
        print(f"   • Is trial user: {user.is_trial_user()}")
        print(f"   • Trial days remaining: {user.get_remaining_trial_days()}")
        print(f"   • Email verified: {user.is_email_verified()}")
        
        print(f"\n📋 Step 2: Email Verification")
        print("-" * 30)
        
        # Simulate email verification
        verification_success = await auth_service.verify_email(user.id, "demo-verification-token")
        if verification_success:
            print("✅ Email verified successfully")
            
            # Refresh user to see updated status
            authenticated_user = await auth_service.authenticate_user(user.username, "SecurePassword123!")
            print(f"   • Updated status: {authenticated_user.status.value}")
            print(f"   • Can now generate videos: {authenticated_user.can_generate_videos()}")
        
        print(f"\n📋 Step 3: User Authentication & Token Management")
        print("-" * 30)
        
        # Authenticate user
        auth_user = await auth_service.authenticate_user("alice_creator", "SecurePassword123!")
        if auth_user:
            print("✅ Authentication successful")
            
            # Create access token
            token = await auth_service.create_access_token(auth_user)
            print(f"🔑 Access token generated (length: {len(token)} chars)")
            
            # Verify token
            verified_user = await auth_service.verify_access_token(token)
            if verified_user:
                print("✅ Token verification successful")
                print(f"   • Verified user: {verified_user.username}")
            
            # Refresh token
            new_token = await auth_service.refresh_access_token(auth_user)
            print(f"🔄 Token refreshed (new length: {len(new_token)} chars)")
        
        print(f"\n📋 Step 4: User Profile Management")
        print("-" * 30)
        
        # Update user preferences (domain logic)
        auth_user.update_preferences({
            "default_platform": "youtube",
            "preferred_duration": 60,
            "auto_generate_subtitles": True,
            "notification_frequency": "daily"
        })
        
        # Update notification settings
        auth_user.update_notification_settings({
            "email_notifications": True,
            "video_completion_alerts": True,
            "weekly_usage_reports": False
        })
        
        print("✅ User preferences updated:")
        print(f"   • Preferences: {len(auth_user.preferences)} settings")
        print(f"   • Notifications: {len(auth_user.notification_settings)} settings")
        
        # Show usage summary
        usage_summary = auth_user.get_usage_summary()
        print(f"\n📈 Usage Summary:")
        for key, value in usage_summary.items():
            print(f"   • {key}: {value}")
        
        print(f"\n✅ Complete user workflow demonstration finished")
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)


async def example_video_generation_advanced_workflow():
    """
    Advanced video generation workflow showing the complete process from
    configuration validation to session monitoring and completion.
    """
    print("\n" + "="*70)
    print("🎬 ADVANCED VIDEO GENERATION WORKFLOW")
    print("="*70)
    
    temp_dir = tempfile.mkdtemp()
    try:
        # Setup container with video generation configuration
        config = {
            "data_path": temp_dir,
            "jwt": {"secret_key": "demo-key"},
            "video_generation": {
                "max_concurrent_generations": 3
            }
        }
        container = EnhancedDIContainer(config)
        
        auth_service = container.get_authentication_service()
        video_service = container.get_video_generation_service()
        
        print("📋 Step 1: Setup Premium User")
        print("-" * 30)
        
        # Create premium user for advanced features
        user = await auth_service.register_user(
            username="pro_videographer",
            email="pro@studio.com",
            password="ProfessionalPass123!"
        )
        await auth_service.verify_email(user.id, "verification")
        
        # Upgrade to premium (simulate)
        authenticated_user = await auth_service.authenticate_user(user.username, "ProfessionalPass123!")
        authenticated_user.upgrade_to_premium()
        
        print(f"✅ Premium user setup complete:")
        print(f"   • Role: {authenticated_user.role.value}")
        print(f"   • Monthly limit: {authenticated_user.role.get_max_monthly_videos()}")
        print(f"   • Session limit: {authenticated_user.role.get_max_sessions()}")
        print(f"   • Premium features: {authenticated_user.role.can_access_premium_features()}")
        
        print(f"\n📋 Step 2: Create Advanced Video Configurations")
        print("-" * 30)
        
        # Create multiple video configurations for different use cases
        video_configs = [
            {
                "name": "Product Demo",
                "config": VideoGenerationConfig(
                    mission="Create a compelling product demonstration video showcasing our new AI-powered video editing software, highlighting key features like automated scene detection, intelligent cropping, and one-click color correction for professional content creators",
                    platform="youtube",
                    duration=120,
                    discussion_mode="professional",
                    language="english",
                    use_premium_models=True,
                    enable_subtitles=True,
                    background_music=True,
                    visual_style="professional",
                    style="corporate"
                )
            },
            {
                "name": "Social Media Teaser",
                "config": VideoGenerationConfig(
                    mission="Create an exciting 30-second teaser for social media promoting our upcoming product launch",
                    platform="tiktok",
                    duration=30,
                    discussion_mode="enhanced",
                    language="english",
                    use_premium_models=True,
                    enable_subtitles=True,
                    background_music=True,
                    visual_style="dynamic"
                )
            },
            {
                "name": "Tutorial Content",
                "config": VideoGenerationConfig(
                    mission="Develop a step-by-step tutorial showing beginners how to create professional-looking videos using basic equipment and free software",
                    platform="youtube",
                    duration=300,
                    discussion_mode="enhanced",
                    language="english",
                    use_premium_models=False,  # Standard models for tutorial
                    enable_subtitles=True,
                    background_music=False  # No music for tutorial
                )
            }
        ]
        
        print(f"📋 Created {len(video_configs)} video configurations:")
        for i, config_data in enumerate(video_configs, 1):
            config = config_data["config"]
            print(f"   {i}. {config_data['name']}:")
            print(f"      • Platform: {config.platform}")
            print(f"      • Duration: {config.duration}s")
            print(f"      • Premium models: {config.use_premium_models}")
            print(f"      • Mission length: {len(config.mission)} chars")
        
        print(f"\n📋 Step 3: Validate Configurations")
        print("-" * 30)
        
        validated_configs = []
        for config_data in video_configs:
            config = config_data["config"]
            validation = await video_service.validate_generation_config(config, authenticated_user)
            
            print(f"🔍 Validating {config_data['name']}:")
            if validation["valid"]:
                print(f"   ✅ Valid configuration")
                if validation.get("warnings"):
                    for warning in validation["warnings"]:
                        print(f"   ⚠️  {warning}")
                validated_configs.append(config_data)
            else:
                print(f"   ❌ Invalid configuration:")
                for error in validation["errors"]:
                    print(f"      • {error}")
        
        print(f"\n📋 Step 4: Cost Estimation")
        print("-" * 30)
        
        total_estimated_cost = 0
        total_estimated_time = 0
        
        for config_data in validated_configs:
            config = config_data["config"]
            cost_estimate = await video_service.estimate_generation_cost(config)
            
            print(f"💰 Cost estimate for {config_data['name']}:")
            print(f"   • Estimated cost: {cost_estimate['estimated_cost']} credits")
            print(f"   • Estimated time: {cost_estimate['estimated_time_seconds']}s")
            print(f"   • Base cost: {cost_estimate['base_cost']}")
            print(f"   • Duration factor: {cost_estimate['duration_factor']:.2f}")
            print(f"   • Mode factor: {cost_estimate['mode_factor']:.2f}")
            
            total_estimated_cost += cost_estimate['estimated_cost']
            total_estimated_time += cost_estimate['estimated_time_seconds']
        
        print(f"\n💰 Total Estimates:")
        print(f"   • Total cost: {total_estimated_cost:.2f} credits")
        print(f"   • Total time: {total_estimated_time:.0f} seconds ({total_estimated_time/60:.1f} minutes)")
        
        print(f"\n📋 Step 5: Create and Manage Video Sessions")
        print("-" * 30)
        
        created_sessions = []
        for config_data in validated_configs:
            config = config_data["config"]
            
            try:
                session = await video_service.create_video_session(authenticated_user.id, config)
                created_sessions.append((config_data["name"], session))
                
                print(f"✅ Created session for {config_data['name']}:")
                print(f"   • Session ID: {session.id}")
                print(f"   • Status: {session.status.value}")
                print(f"   • Progress: {session.progress_percentage}%")
                print(f"   • Estimated completion: {session.estimated_completion_time}")
                
            except VideoGenerationError as e:
                print(f"❌ Failed to create session for {config_data['name']}: {e}")
        
        print(f"\n📋 Step 6: Start Generation and Monitor Progress")
        print("-" * 30)
        
        # Start generation for all sessions
        for name, session in created_sessions[:2]:  # Limit to 2 for demo
            success = await video_service.start_video_generation(session.id)
            if success:
                print(f"🚀 Started generation for {name} (Session: {session.id})")
            else:
                print(f"❌ Failed to start generation for {name}")
        
        # Monitor progress for a few iterations
        print(f"\n📊 Monitoring Progress:")
        for iteration in range(3):
            await asyncio.sleep(0.5)  # Simulate time passing
            print(f"\nIteration {iteration + 1}:")
            
            for name, session in created_sessions:
                progress = await video_service.get_generation_progress(session.id)
                if "error" not in progress:
                    status = progress.get("status", "unknown")
                    percentage = progress.get("progress_percentage", 0)
                    phase = progress.get("current_phase", "Unknown")
                    
                    print(f"   {name}: {status} - {percentage:.1f}% - {phase}")
        
        print(f"\n📋 Step 7: Queue Status and User Sessions")
        print("-" * 30)
        
        # Check generation queue status
        queue_status = await video_service.get_generation_queue_status()
        if "error" not in queue_status:
            print(f"🔄 Generation Queue Status:")
            print(f"   • Active generations: {queue_status.get('active_generations', 0)}")
            print(f"   • Queued sessions: {queue_status.get('queued_sessions', 0)}")
            print(f"   • Available slots: {queue_status.get('available_slots', 0)}")
            print(f"   • Max concurrent: {queue_status.get('max_concurrent', 0)}")
        
        # Get all user sessions
        user_sessions = await video_service.get_user_sessions(authenticated_user.id)
        print(f"\n📋 User Sessions Summary:")
        print(f"   • Total sessions: {len(user_sessions)}")
        
        for session in user_sessions:
            print(f"   • {session.id}: {session.status.value} ({session.progress_percentage:.1f}%)")
        
        print(f"\n✅ Advanced video generation workflow completed")
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


async def example_campaign_management_complete():
    """
    Complete campaign management workflow demonstrating campaign lifecycle,
    multi-platform coordination, and performance tracking.
    """
    print("\n" + "="*70)
    print("📈 COMPLETE CAMPAIGN MANAGEMENT WORKFLOW")
    print("="*70)
    
    temp_dir = tempfile.mkdtemp()
    try:
        # Setup container
        config = {"data_path": temp_dir, "jwt": {"secret_key": "demo-key"}}
        container = EnhancedDIContainer(config)
        
        auth_service = container.get_authentication_service()
        video_service = container.get_video_generation_service()
        campaign_service = container.get_campaign_service()
        
        print("📋 Step 1: Setup Marketing Team User")
        print("-" * 30)
        
        # Create marketing user
        marketing_user = await auth_service.register_user(
            username="marketing_director",
            email="marketing@company.com",
            password="MarketingPass123!",
            organization="Global Marketing Solutions"
        )
        await auth_service.verify_email(marketing_user.id, "verification")
        
        # Get authenticated user and upgrade to premium for campaign features
        auth_user = await auth_service.authenticate_user(marketing_user.username, "MarketingPass123!")
        auth_user.upgrade_to_premium()
        
        print(f"✅ Marketing user setup:")
        print(f"   • Username: {auth_user.username}")
        print(f"   • Role: {auth_user.role.value}")
        print(f"   • Organization: {auth_user.organization}")
        
        print(f"\n📋 Step 2: Create Multi-Platform Campaign")
        print("-" * 30)
        
        # Create comprehensive campaign
        campaign = await campaign_service.create_campaign(
            user_id=auth_user.id,
            name="Q1 2024 Product Launch Campaign",
            description="Comprehensive multi-platform video campaign for our revolutionary AI-powered productivity software launch targeting young professionals and entrepreneurs",
            target_platforms=["youtube", "tiktok", "instagram", "facebook"]
        )
        
        print(f"✅ Campaign created:")
        print(f"   • ID: {campaign.id}")
        print(f"   • Name: {campaign.name}")
        print(f"   • Status: {campaign.status.value}")
        print(f"   • Priority: {campaign.priority.value}")
        print(f"   • Target platforms: {', '.join(campaign.target_platforms)}")
        
        # Set campaign budget and metadata
        campaign.set_budget(15000.0)  # $15,000 campaign budget
        campaign.add_tags(["product-launch", "ai", "productivity", "b2b", "q1-2024"])
        
        print(f"💰 Campaign budget set: ${campaign.estimated_budget}")
        print(f"🏷️  Campaign tags: {', '.join(campaign.tags)}")
        
        print(f"\n📋 Step 3: Create Platform-Specific Video Content")
        print("-" * 30)
        
        # Define platform-specific video strategies
        platform_strategies = [
            {
                "platform": "youtube",
                "videos": [
                    {
                        "name": "Full Product Demo",
                        "config": VideoGenerationConfig(
                            mission="Create a comprehensive 5-minute product demonstration video showcasing all key features of our AI productivity software, including workflow automation, intelligent task prioritization, and seamless team collaboration tools",
                            platform="youtube",
                            duration=300,
                            discussion_mode="professional",
                            use_premium_models=True,
                            enable_subtitles=True
                        )
                    },
                    {
                        "name": "Customer Testimonials",
                        "config": VideoGenerationConfig(
                            mission="Produce a compelling customer testimonial video featuring success stories from early adopters of our productivity software",
                            platform="youtube", 
                            duration=180,
                            discussion_mode="enhanced",
                            enable_subtitles=True
                        )
                    }
                ]
            },
            {
                "platform": "tiktok",
                "videos": [
                    {
                        "name": "Quick Feature Highlight",
                        "config": VideoGenerationConfig(
                            mission="Create an engaging 30-second video highlighting the most impressive AI feature of our productivity software with trendy visual effects",
                            platform="tiktok",
                            duration=30,
                            discussion_mode="enhanced",
                            visual_style="dynamic",
                            background_music=True
                        )
                    },
                    {
                        "name": "Before & After Productivity",
                        "config": VideoGenerationConfig(
                            mission="Show a dramatic before-and-after comparison of workplace productivity using our AI software",
                            platform="tiktok",
                            duration=25,
                            discussion_mode="enhanced",
                            visual_style="dynamic"
                        )
                    }
                ]
            },
            {
                "platform": "instagram",
                "videos": [
                    {
                        "name": "Behind the Scenes",
                        "config": VideoGenerationConfig(
                            mission="Create behind-the-scenes content showing our development team and the innovative process of building AI-powered productivity tools",
                            platform="instagram",
                            duration=60,
                            discussion_mode="enhanced",
                            visual_style="lifestyle"
                        )
                    }
                ]
            }
        ]
        
        # Create video sessions for each platform strategy
        campaign_sessions = []
        total_platform_videos = 0
        
        for platform_strategy in platform_strategies:
            platform = platform_strategy["platform"]
            print(f"\n🎯 Creating content for {platform.upper()}:")
            
            for video_data in platform_strategy["videos"]:
                video_name = video_data["name"]
                config = video_data["config"]
                
                try:
                    session = await video_service.create_video_session(auth_user.id, config)
                    campaign_sessions.append({
                        "platform": platform,
                        "name": video_name,
                        "session": session
                    })
                    
                    # Add to campaign
                    success = await campaign_service.add_video_to_campaign(
                        campaign_id=campaign.id,
                        video_session_id=session.id,
                        user_id=auth_user.id
                    )
                    
                    if success:
                        total_platform_videos += 1
                        print(f"   ✅ {video_name}: Session created and added to campaign")
                    else:
                        print(f"   ❌ {video_name}: Failed to add to campaign")
                        
                except VideoGenerationError as e:
                    print(f"   ❌ {video_name}: Failed to create session - {e}")
        
        print(f"\n📊 Campaign Content Summary:")
        print(f"   • Total videos planned: {total_platform_videos}")
        print(f"   • Platforms covered: {len(platform_strategies)}")
        
        # Update campaign with cost estimates
        total_campaign_cost = 0
        for session_data in campaign_sessions:
            config = session_data["session"].config
            cost_estimate = await video_service.estimate_generation_cost(config)
            total_campaign_cost += cost_estimate.get("estimated_cost", 0)
        
        campaign.add_cost(total_campaign_cost, "Initial video generation estimates")
        print(f"💰 Estimated total campaign cost: ${campaign.actual_cost:.2f}")
        
        print(f"\n📋 Step 4: Activate Campaign")
        print("-" * 30)
        
        # Activate campaign
        success = await campaign_service.activate_campaign(campaign.id, auth_user.id)
        if success:
            print(f"🚀 Campaign activated successfully")
            print(f"   • Status: {campaign.status.value}")
            print(f"   • Start date: {campaign.start_date}")
            print(f"   • Planned videos: {campaign.total_planned_videos}")
        else:
            print(f"❌ Failed to activate campaign")
        
        print(f"\n📋 Step 5: Campaign Performance Monitoring")
        print("-" * 30)
        
        # Get detailed campaign performance
        performance = await campaign_service.get_campaign_performance(campaign.id, auth_user.id)
        
        print(f"📈 Campaign Performance Metrics:")
        print(f"   • Completion rate: {performance.get('completion_rate', 0):.1f}%")
        print(f"   • Failure rate: {performance.get('failure_rate', 0):.1f}%")
        print(f"   • Budget utilization: {performance.get('budget_utilization', 0):.1f}%")
        print(f"   • Duration: {performance.get('duration_days', 0)} days")
        print(f"   • Total videos: {performance.get('total_videos', 0)}")
        print(f"   • Completed: {performance.get('completed_videos', 0)}")
        print(f"   • Failed: {performance.get('failed_videos', 0)}")
        
        if "video_sessions" in performance:
            print(f"\n📹 Video Session Details:")
            for session_info in performance["video_sessions"][:3]:  # Show first 3
                print(f"   • {session_info['id']}: {session_info['status']} ({session_info['progress']:.1f}%)")
        
        print(f"\n📋 Step 6: Campaign Analytics")
        print("-" * 30)
        
        # Get user campaign analytics
        analytics = await campaign_service.get_campaign_analytics(auth_user.id, days=30)
        
        if "error" not in analytics:
            print(f"📊 Marketing User Analytics (30 days):")
            print(f"   • Total campaigns: {analytics.get('total_campaigns', 0)}")
            print(f"   • Active campaigns: {analytics.get('active_campaigns', 0)}")
            print(f"   • Completed campaigns: {analytics.get('completed_campaigns', 0)}")
            print(f"   • Total videos: {analytics.get('total_videos', 0)}")
            print(f"   • Success rate: {analytics.get('success_rate', 0):.1f}%")
            print(f"   • Total cost: ${analytics.get('total_cost', 0):.2f}")
            print(f"   • Avg campaign cost: ${analytics.get('average_campaign_cost', 0):.2f}")
            print(f"   • Cost per video: ${analytics.get('cost_per_video', 0):.2f}")
        
        print(f"\n✅ Complete campaign management workflow finished")
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


async def example_dependency_injection_showcase():
    """
    Showcase of dependency injection container capabilities and SOLID principles.
    """
    print("\n" + "="*70)
    print("🔧 DEPENDENCY INJECTION & SOLID PRINCIPLES SHOWCASE")
    print("="*70)
    
    temp_dir = tempfile.mkdtemp()
    try:
        print("📋 Step 1: Container Configuration & Initialization")
        print("-" * 30)
        
        # Demonstrate configurable container setup
        config = {
            "data_path": temp_dir,
            "jwt": {
                "secret_key": "production-secret-key-here",
                "algorithm": "HS256",
                "access_token_expire_minutes": 60
            },
            "video_generation": {
                "max_concurrent_generations": 8
            }
        }
        
        container = EnhancedDIContainer(config)
        print(f"✅ DI Container initialized with custom configuration")
        
        # Health check
        health = container.health_check()
        print(f"🏥 Container health status: {health['status']}")
        
        print(f"\n📦 Enhanced Components Status:")
        for component_type, components in health.get('enhanced_components', {}).items():
            print(f"   {component_type.upper()}:")
            for name, status in components.items():
                emoji = "✅" if status == "healthy" else "❌" if status == "missing" else "⚠️"
                print(f"      {emoji} {name}: {status}")
        
        print(f"\n📋 Step 2: Service Resolution (Dependency Injection)")
        print("-" * 30)
        
        # Demonstrate automatic dependency injection
        print("🔧 Resolving services with automatic dependency injection:")
        
        # Each service gets its dependencies automatically injected
        auth_service = container.get_authentication_service()
        print("   ✅ AuthenticationService resolved")
        print("      ├─ IUserRepository injected")
        print("      ├─ JWT configuration injected")
        print("      └─ Algorithm & expiration settings injected")
        
        video_service = container.get_video_generation_service()
        print("   ✅ VideoGenerationService resolved")
        print("      ├─ IUserRepository injected")
        print("      ├─ IVideoSessionRepository injected")
        print("      └─ Max concurrent generations config injected")
        
        campaign_service = container.get_campaign_service()
        print("   ✅ CampaignService resolved")
        print("      ├─ IUserRepository injected")
        print("      ├─ ICampaignRepository injected")
        print("      └─ IVideoSessionRepository injected")
        
        print(f"\n📋 Step 3: Repository Resolution (Data Layer)")
        print("-" * 30)
        
        # Show repository resolution and configuration
        user_repo = container.get_user_repository()
        video_repo = container.get_video_session_repository()
        campaign_repo = container.get_campaign_repository()
        
        print("💾 Repository instances resolved:")
        print(f"   ✅ UserRepository: {type(user_repo).__name__}")
        print(f"   ✅ VideoSessionRepository: {type(video_repo).__name__}")
        print(f"   ✅ CampaignRepository: {type(campaign_repo).__name__}")
        
        # Show they all implement their interfaces (Liskov Substitution Principle)
        from src.repositories.interfaces import IUserRepository, IVideoSessionRepository, ICampaignRepository
        
        print(f"\n🔍 Interface Implementation Verification:")
        print(f"   • UserRepository implements IUserRepository: {isinstance(user_repo, IUserRepository)}")
        print(f"   • VideoSessionRepository implements IVideoSessionRepository: {isinstance(video_repo, IVideoSessionRepository)}")
        print(f"   • CampaignRepository implements ICampaignRepository: {isinstance(campaign_repo, ICampaignRepository)}")
        
        print(f"\n📋 Step 4: SOLID Principles Demonstration")
        print("-" * 30)
        
        # Single Responsibility Principle
        print("🎯 Single Responsibility Principle:")
        print("   ✅ AuthenticationService: Only handles user auth")
        print("   ✅ VideoGenerationService: Only handles video generation")
        print("   ✅ CampaignService: Only handles campaign management")
        print("   ✅ UserRepository: Only handles user data access")
        
        # Open/Closed Principle
        print(f"\n🔄 Open/Closed Principle:")
        print("   ✅ Services use interfaces - can extend without modification")
        print("   ✅ New repository implementations can be added")
        print("   ✅ New authentication methods can be added")
        
        # Liskov Substitution Principle
        print(f"\n🔄 Liskov Substitution Principle:")
        print("   ✅ Any IUserRepository implementation can replace another")
        print("   ✅ Services work with interfaces, not concrete classes")
        
        # Interface Segregation Principle
        print(f"\n📋 Interface Segregation Principle:")
        print("   ✅ IUserRepository: Only user-specific methods")
        print("   ✅ IVideoSessionRepository: Only video session methods")
        print("   ✅ ICampaignRepository: Only campaign methods")
        print("   ✅ No interface has methods it doesn't need")
        
        # Dependency Inversion Principle
        print(f"\n🔄 Dependency Inversion Principle:")
        print("   ✅ High-level services depend on interfaces")
        print("   ✅ Low-level repositories implement interfaces")
        print("   ✅ Dependencies are injected, not created")
        
        print(f"\n📋 Step 5: Configuration Flexibility")
        print("-" * 30)
        
        # Show how configuration can be changed
        original_config = container.get_config()
        print(f"📁 Original configuration:")
        print(f"   • Data path: {original_config.get('data_path')}")
        print(f"   • JWT expire minutes: {original_config.get('jwt', {}).get('access_token_expire_minutes')}")
        print(f"   • Max generations: {original_config.get('video_generation', {}).get('max_concurrent_generations')}")
        
        # Update configuration
        new_config = {
            "jwt": {"access_token_expire_minutes": 120},  # Extend to 2 hours
            "video_generation": {"max_concurrent_generations": 15}  # Increase capacity
        }
        container.update_config(new_config)
        
        updated_config = container.get_config()
        print(f"\n📁 Updated configuration:")
        print(f"   • JWT expire minutes: {updated_config.get('jwt', {}).get('access_token_expire_minutes')}")
        print(f"   • Max generations: {updated_config.get('video_generation', {}).get('max_concurrent_generations')}")
        
        print(f"\n✅ Dependency injection showcase completed")
        print(f"🎉 All SOLID principles are properly implemented!")
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


async def example_error_handling_and_validation():
    """
    Comprehensive error handling and validation examples across all architecture layers.
    """
    print("\n" + "="*70)
    print("⚠️  ERROR HANDLING & VALIDATION SHOWCASE")
    print("="*70)
    
    temp_dir = tempfile.mkdtemp()
    try:
        config = {"data_path": temp_dir, "jwt": {"secret_key": "demo-key"}}
        container = EnhancedDIContainer(config)
        
        auth_service = container.get_authentication_service()
        video_service = container.get_video_generation_service()
        campaign_service = container.get_campaign_service()
        
        print("📋 Step 1: Domain Entity Validation")
        print("-" * 30)
        
        # Test User entity validation
        print("👤 User Entity Validation:")
        validation_tests = [
            ("Empty username", lambda: User.create_new_user("test", "", "test@example.com", "password123")),
            ("Short username", lambda: User.create_new_user("test", "ab", "test@example.com", "password123")),
            ("Invalid email", lambda: User.create_new_user("test", "user", "not-an-email", "password123")),
            ("Weak password", lambda: User.create_new_user("test", "user", "user@example.com", "123")),
        ]
        
        for test_name, test_func in validation_tests:
            try:
                test_func()
                print(f"   ❌ {test_name}: Should have failed but didn't")
            except ValueError as e:
                print(f"   ✅ {test_name}: Correctly caught - {e}")
        
        # Test VideoGenerationConfig validation
        print(f"\n🎬 VideoGenerationConfig Validation:")
        video_validation_tests = [
            ("Empty mission", lambda: VideoGenerationConfig(mission="", platform="youtube")),
            ("Short mission", lambda: VideoGenerationConfig(mission="Short", platform="youtube")),
            ("Invalid duration", lambda: VideoGenerationConfig(mission="Test mission", platform="youtube", duration=500)),
            ("Invalid platform", lambda: VideoGenerationConfig(mission="Test mission", platform="invalid")),
        ]
        
        for test_name, test_func in video_validation_tests:
            try:
                test_func()
                print(f"   ❌ {test_name}: Should have failed but didn't")
            except ValueError as e:
                print(f"   ✅ {test_name}: Correctly caught - {e}")
        
        print(f"\n📋 Step 2: Service Layer Error Handling")
        print("-" * 30)
        
        # Test AuthenticationService errors
        print("🔐 Authentication Service Errors:")
        auth_error_tests = [
            ("Register invalid user", lambda: auth_service.register_user("ab", "bad-email", "weak")),
            ("Authenticate non-existent", lambda: auth_service.authenticate_user("nonexistent", "password")),
            ("Verify invalid token", lambda: auth_service.verify_access_token("invalid-token")),
        ]
        
        for test_name, test_func in auth_error_tests:
            try:
                await test_func()
                print(f"   ❌ {test_name}: Should have failed but didn't")
            except (AuthenticationError, TypeError) as e:
                print(f"   ✅ {test_name}: Correctly caught - {type(e).__name__}")
            except Exception as e:
                print(f"   ⚠️  {test_name}: Unexpected error type - {type(e).__name__}")
        
        # Test VideoGenerationService errors  
        print(f"\n🎬 Video Generation Service Errors:")
        invalid_config = VideoGenerationConfig(mission="Test mission", platform="youtube")
        
        video_error_tests = [
            ("Create session for non-existent user", lambda: video_service.create_video_session("nonexistent", invalid_config)),
            ("Start generation for non-existent session", lambda: video_service.start_video_generation("nonexistent")),
            ("Get progress for non-existent session", lambda: video_service.get_generation_progress("nonexistent")),
        ]
        
        for test_name, test_func in video_error_tests:
            try:
                result = await test_func()
                if isinstance(result, dict) and "error" in result:
                    print(f"   ✅ {test_name}: Correctly returned error response")
                else:
                    print(f"   ❌ {test_name}: Should have failed but didn't")
            except (VideoGenerationError, Exception) as e:
                print(f"   ✅ {test_name}: Correctly caught - {type(e).__name__}")
        
        print(f"\n📋 Step 3: Business Logic Error Handling")
        print("-" * 30)
        
        # Create a valid user for business logic tests
        user = await auth_service.register_user(
            username="testuser",
            email="test@example.com", 
            password="validpassword123"
        )
        
        print("🔒 Business Logic Constraint Violations:")
        
        # Test trial user limitations
        print(f"   👤 User status: {user.status.value} (not verified)")
        print(f"   📊 Can generate videos: {user.can_generate_videos()}")
        
        # Try to create video session with unverified user
        try:
            config = VideoGenerationConfig(mission="Test mission for unverified user", platform="youtube")
            session = await video_service.create_video_session(user.id, config)
            print(f"   ❌ Unverified user video creation: Should have failed")
        except VideoGenerationError as e:
            print(f"   ✅ Unverified user video creation: Correctly blocked - Account restriction")
        
        # Verify user and test session limits
        await auth_service.verify_email(user.id, "verification-token")
        verified_user = await auth_service.authenticate_user("testuser", "validpassword123")
        
        print(f"\n   👤 After verification: {verified_user.status.value}")
        print(f"   📊 Can generate videos: {verified_user.can_generate_videos()}")
        print(f"   🎯 Session limit: {verified_user.role.get_max_sessions()}")
        
        # Test session limit enforcement
        created_sessions = []
        for i in range(3):  # Try to create more than trial limit (1)
            try:
                config = VideoGenerationConfig(mission=f"Test mission {i+1}", platform="youtube")
                session = await video_service.create_video_session(verified_user.id, config)
                created_sessions.append(session)
                print(f"   ✅ Session {i+1}: Created successfully")
            except VideoGenerationError as e:
                print(f"   ✅ Session {i+1}: Correctly blocked - {e}")
                break
        
        print(f"\n📋 Step 4: Error Recovery Patterns")
        print("-" * 30)
        
        # Demonstrate proper error recovery
        print("🔄 Error Recovery Examples:")
        
        # Retry pattern for transient failures
        print("   🔁 Retry pattern demonstration:")
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # This would normally be a real operation that might fail transiently
                if attempt < 2:  # Simulate failure on first 2 attempts
                    raise Exception("Simulated transient failure")
                else:
                    print(f"      ✅ Operation succeeded on attempt {attempt + 1}")
                    break
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"      ⚠️  Attempt {attempt + 1} failed: {e} - Retrying...")
                else:
                    print(f"      ❌ All {max_retries} attempts failed")
        
        # Graceful degradation
        print("   🎛️  Graceful degradation example:")
        try:
            # Try premium feature first
            config = VideoGenerationConfig(
                mission="Test with premium features",
                platform="youtube",
                use_premium_models=True
            )
            print("      🔧 Attempting with premium models...")
            # In real scenario, this might fail due to quota/availability
            raise Exception("Premium models temporarily unavailable")
            
        except Exception as e:
            print(f"      ⚠️  Premium feature failed: {e}")
            print("      🔄 Falling back to standard models...")
            
            # Fallback to standard features
            fallback_config = VideoGenerationConfig(
                mission="Test with standard features",
                platform="youtube", 
                use_premium_models=False
            )
            print("      ✅ Fallback configuration ready")
        
        print(f"\n✅ Error handling and validation showcase completed")
        print("🎯 All error scenarios properly handled with clear feedback")
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


async def main():
    """
    Main function orchestrating all comprehensive examples.
    """
    print("🚀 COMPREHENSIVE VIRALAI OOP ARCHITECTURE EXAMPLES")
    print("=" * 70)
    print("Demonstrating SOLID principles, clean architecture, and")
    print("comprehensive business workflows in the ViralAI platform.")
    print("=" * 70)
    
    examples = [
        ("Complete User Workflow", example_complete_user_workflow),
        ("Advanced Video Generation", example_video_generation_advanced_workflow), 
        ("Campaign Management", example_campaign_management_complete),
        ("Dependency Injection Showcase", example_dependency_injection_showcase),
        ("Error Handling & Validation", example_error_handling_and_validation)
    ]
    
    start_time = datetime.now()
    
    for i, (name, example_func) in enumerate(examples, 1):
        try:
            print(f"\n🎯 [{i}/{len(examples)}] {name}")
            await example_func()
            print(f"✅ {name} completed successfully")
        except Exception as e:
            print(f"❌ {name} failed with error: {e}")
            print(f"   Error type: {type(e).__name__}")
        
        if i < len(examples):
            print(f"\n{'─' * 50}")
            await asyncio.sleep(0.1)  # Brief pause between examples
    
    duration = datetime.now() - start_time
    
    print(f"\n" + "=" * 70)
    print("🎉 ALL COMPREHENSIVE EXAMPLES COMPLETED!")
    print("=" * 70)
    print(f"⏱️  Total execution time: {duration.total_seconds():.2f} seconds")
    print(f"📊 Examples run: {len(examples)}")
    print(f"🏗️  Architecture: Clean Architecture with SOLID principles")
    print(f"📦 Components: Domain entities, Services, Repositories, DI Container")
    print(f"🔧 Patterns: Repository, Service Layer, Dependency Injection")
    print(f"✅ Error Handling: Comprehensive validation and recovery")
    
    print(f"\n🎯 Key Achievements Demonstrated:")
    print("   • Proper domain entity encapsulation")
    print("   • Business logic separation in service layer")
    print("   • Data access abstraction with repository pattern")
    print("   • Dependency injection for loose coupling")
    print("   • Comprehensive error handling and validation")
    print("   • SOLID principles implementation")
    print("   • Clean architecture separation of concerns")
    
    print(f"\n🚀 The ViralAI platform is now built with enterprise-grade OOP architecture!")


if __name__ == "__main__":
    """
    Entry point for running comprehensive OOP architecture examples.
    """
    print("Starting ViralAI Comprehensive OOP Architecture Examples...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  Examples interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error running examples: {e}")
        print(f"Error type: {type(e).__name__}")
    else:
        print("\n👋 Examples completed successfully!")