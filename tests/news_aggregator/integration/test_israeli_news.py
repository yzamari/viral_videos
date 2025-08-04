"""Integration tests for Israeli news generation"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from src.news_aggregator.israeli_news_generator import IsraeliNewsChannel
from src.news_aggregator.models.content_models import ContentItem, NewsSource, SourceType


class TestIsraeliNewsGeneration:
    """Test Israeli news video generation"""
    
    @pytest.fixture
    def mock_articles(self):
        """Create mock Israeli news articles"""
        return [
            ContentItem(
                id="1",
                source=NewsSource(
                    id="ynet",
                    name="Ynet",
                    source_type=SourceType.WEB,
                    url="https://ynet.co.il"
                ),
                title="שר החינוך נתפס אוכל פלאפל בשיעור מתמטיקה",
                content="במהלך ביקור פתע בבית ספר, השר הופתע עם פלאפל ביד",
                language="he",
                metadata={
                    "humor_score": 0.8,
                    "interest_score": 0.7,
                    "is_bizarre": True
                }
            ),
            ContentItem(
                id="2",
                source=NewsSource(
                    id="rotter",
                    name="Rotter",
                    source_type=SourceType.WEB,
                    url="https://rotter.net"
                ),
                title="בלעדי: ראש העיר מכחיש שהוא חייזר",
                content="לאחר שמועות ברשת, ראש העיר יצא בהכחשה נמרצת",
                language="he",
                metadata={
                    "humor_score": 0.9,
                    "interest_score": 0.8,
                    "is_bizarre": True
                }
            ),
            ContentItem(
                id="3",
                source=NewsSource(
                    id="ynet",
                    name="Ynet", 
                    source_type=SourceType.WEB,
                    url="https://ynet.co.il"
                ),
                title="מחקר: 87% מהישראלים לא קוראים מחקרים",
                content="מחקר חדש חושף נתונים מדאיגים על הרגלי הקריאה",
                language="he",
                metadata={
                    "humor_score": 0.7,
                    "interest_score": 0.6
                }
            )
        ]
    
    @pytest.mark.asyncio
    async def test_content_selection(self, mock_articles):
        """Test that top 5 most interesting articles are selected"""
        channel = IsraeliNewsChannel()
        
        # Mock scrapers to return our test articles
        with patch.object(channel.ynet_scraper, 'scrape_ynet_homepage', 
                         return_value=mock_articles[:2]):
            with patch.object(channel.rotter_scraper, 'scrape_rotter_scoops',
                             return_value=[mock_articles[2]]):
                
                # Process content
                video_structure = channel.content_processor.process_for_news_video(
                    mock_articles,
                    target_style="dark_humor"
                )
                
                # Check that articles are selected and ordered correctly
                assert len(video_structure["segments"]) <= 5
                assert video_structure["segments"][0]["title"] == mock_articles[1].title  # Highest score
                assert video_structure["presenter"]["commentary_style"] == "dark_humor"
    
    @pytest.mark.asyncio
    async def test_alien_commentary_generation(self, mock_articles):
        """Test alien commentary for different article types"""
        channel = IsraeliNewsChannel()
        
        # Test political scandal commentary
        political_article = mock_articles[0]
        political_article.categories = ["פוליטיקה"]
        
        commentary = channel.alien._generate_dark_commentary(
            {"title": political_article.title, "content": political_article.content},
            "political_scandal"
        )
        
        assert commentary is not None
        assert len(commentary) > 0
        assert any(word in commentary for word in ["פוליטיקה", "אצלכם", "כוכב"])
    
    @pytest.mark.asyncio
    async def test_ynet_theme_creation(self):
        """Test Ynet theme is created correctly"""
        channel = IsraeliNewsChannel()
        theme = channel._create_ynet_theme()
        
        assert theme["name"] == "Ynet Israeli News"
        assert theme["style"]["colors"]["primary"] == "#D40000"  # Ynet red
        assert theme["metadata"]["rtl"] == True
        assert theme["layout"]["alien_position"]["x"] == 1720  # Bottom right
    
    @pytest.mark.asyncio
    async def test_mission_string_generation(self, mock_articles):
        """Test mission string for existing infrastructure"""
        channel = IsraeliNewsChannel()
        
        video_structure = {
            "segments": [
                {"title": article.title, "summary": article.content[:100]}
                for article in mock_articles[:2]
            ]
        }
        
        mission = channel._create_mission_string(video_structure, "dark_humor")
        
        assert "הומור שחור" in mission
        assert "חייזר" in mission
        assert mock_articles[0].title[:50] in mission
    
    def test_dark_humor_style_mapping(self):
        """Test that dark humor maps to correct existing styles"""
        channel = IsraeliNewsChannel()
        processor = channel.content_processor
        
        # Political scandal with dark humor
        style_config = processor.content_style_mapping["political_scandal"].copy()
        assert style_config["tone"] == "sarcastic"
        
        # Bizarre news  
        style_config = processor.content_style_mapping["bizarre_news"]
        assert style_config["style"] == "humorous"
        assert style_config["visual_style"] == "dynamic"