"""
Traditional & Print Media Support System
Handles newspapers, magazines, billboards, radio, TV advertising
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
from PIL import Image, ImageDraw, ImageFont
import numpy as np

logger = logging.getLogger(__name__)


class TraditionalMediaType(Enum):
    """Types of traditional media"""
    NEWSPAPER = "newspaper"
    MAGAZINE = "magazine"
    BILLBOARD = "billboard"
    TRANSIT = "transit"
    RADIO = "radio"
    TV = "tv"
    DIRECT_MAIL = "direct_mail"
    BROCHURE = "brochure"
    BUSINESS_CARD = "business_card"
    POSTER = "poster"


class PrintFormat(Enum):
    """Standard print formats"""
    # Newspaper formats
    FULL_PAGE = "full_page"
    HALF_PAGE = "half_page"
    QUARTER_PAGE = "quarter_page"
    EIGHTH_PAGE = "eighth_page"
    CLASSIFIED = "classified"
    
    # Magazine formats
    SPREAD = "spread"
    SINGLE_PAGE = "single_page"
    ISLAND = "island"
    
    # Billboard formats
    BULLETIN = "bulletin_14x48"
    POSTER_30 = "30_sheet"
    POSTER_8 = "8_sheet"
    DIGITAL_BILLBOARD = "digital"
    
    # Business formats
    LETTER = "8.5x11"
    A4 = "210x297mm"
    BUSINESS_CARD_US = "3.5x2"
    BUSINESS_CARD_EU = "85x55mm"


@dataclass
class PrintSpecification:
    """Print media specifications"""
    format_type: PrintFormat
    width_inches: float
    height_inches: float
    dpi: int = 300
    color_mode: str = "CMYK"
    bleed: float = 0.125  # inches
    safe_zone: float = 0.25  # inches
    file_formats: List[str] = field(default_factory=lambda: ["PDF", "EPS", "TIFF"])


@dataclass
class TraditionalCampaign:
    """Traditional media campaign"""
    campaign_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    media_types: List[TraditionalMediaType] = field(default_factory=list)
    target_markets: List[str] = field(default_factory=list)
    budget: float = 0
    start_date: datetime = field(default_factory=datetime.now)
    end_date: Optional[datetime] = None
    creatives: List[Dict[str, Any]] = field(default_factory=list)
    placements: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class TraditionalMediaManager:
    """
    Manages traditional and print media advertising
    Handles creation, specifications, and distribution
    """
    
    def __init__(self):
        """Initialize traditional media manager"""
        self.campaigns: Dict[str, TraditionalCampaign] = {}
        self.specifications = self._load_specifications()
        self.templates = self._load_templates()
        self.vendors = self._load_vendor_database()
        
        logger.info("✅ TraditionalMediaManager initialized")
    
    def _load_specifications(self) -> Dict[str, PrintSpecification]:
        """Load standard print specifications"""
        return {
            # Newspapers
            "newspaper_full": PrintSpecification(
                format_type=PrintFormat.FULL_PAGE,
                width_inches=11.5,
                height_inches=21,
                dpi=200,
                color_mode="CMYK"
            ),
            "newspaper_half": PrintSpecification(
                format_type=PrintFormat.HALF_PAGE,
                width_inches=11.5,
                height_inches=10.5,
                dpi=200,
                color_mode="CMYK"
            ),
            
            # Magazines
            "magazine_spread": PrintSpecification(
                format_type=PrintFormat.SPREAD,
                width_inches=17,
                height_inches=11,
                dpi=300,
                color_mode="CMYK",
                bleed=0.125
            ),
            "magazine_single": PrintSpecification(
                format_type=PrintFormat.SINGLE_PAGE,
                width_inches=8.5,
                height_inches=11,
                dpi=300,
                color_mode="CMYK",
                bleed=0.125
            ),
            
            # Billboards
            "billboard_14x48": PrintSpecification(
                format_type=PrintFormat.BULLETIN,
                width_inches=672,  # 14 feet
                height_inches=252,  # 48 feet
                dpi=15,  # Lower DPI for large format
                color_mode="RGB"
            ),
            "billboard_30sheet": PrintSpecification(
                format_type=PrintFormat.POSTER_30,
                width_inches=144,  # 12 feet
                height_inches=300,  # 25 feet
                dpi=30,
                color_mode="RGB"
            ),
            
            # Business materials
            "business_card": PrintSpecification(
                format_type=PrintFormat.BUSINESS_CARD_US,
                width_inches=3.5,
                height_inches=2,
                dpi=300,
                color_mode="CMYK",
                bleed=0.125
            ),
            "brochure_trifold": PrintSpecification(
                format_type=PrintFormat.LETTER,
                width_inches=11,
                height_inches=8.5,
                dpi=300,
                color_mode="CMYK",
                bleed=0.125
            )
        }
    
    def create_print_campaign(
        self,
        name: str,
        media_types: List[TraditionalMediaType],
        budget: float,
        target_markets: List[str],
        duration_days: int = 30
    ) -> TraditionalCampaign:
        """
        Create a traditional media campaign
        
        Args:
            name: Campaign name
            media_types: Types of traditional media
            budget: Total budget
            target_markets: Geographic markets
            duration_days: Campaign duration
            
        Returns:
            Created campaign
        """
        campaign = TraditionalCampaign(
            name=name,
            media_types=media_types,
            target_markets=target_markets,
            budget=budget,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=duration_days)
        )
        
        # Allocate budget across media types
        budget_per_type = budget / len(media_types)
        
        for media_type in media_types:
            if media_type == TraditionalMediaType.NEWSPAPER:
                self._plan_newspaper_campaign(campaign, budget_per_type)
            elif media_type == TraditionalMediaType.BILLBOARD:
                self._plan_billboard_campaign(campaign, budget_per_type)
            elif media_type == TraditionalMediaType.RADIO:
                self._plan_radio_campaign(campaign, budget_per_type)
            elif media_type == TraditionalMediaType.TV:
                self._plan_tv_campaign(campaign, budget_per_type)
        
        self.campaigns[campaign.campaign_id] = campaign
        
        logger.info(f"✅ Traditional campaign created: {campaign.name}")
        return campaign
    
    def generate_print_creative(
        self,
        campaign_id: str,
        format_name: str,
        content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate print-ready creative
        
        Args:
            campaign_id: Campaign identifier
            format_name: Print format specification name
            content: Creative content (headline, body, images, etc.)
            
        Returns:
            Print-ready creative file information
        """
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")
        
        spec = self.specifications.get(format_name)
        if not spec:
            raise ValueError(f"Unknown format: {format_name}")
        
        # Calculate pixel dimensions
        width_px = int(spec.width_inches * spec.dpi)
        height_px = int(spec.height_inches * spec.dpi)
        
        # Create CMYK image for print
        if spec.color_mode == "CMYK":
            # Create RGB first, then convert
            image = Image.new("RGB", (width_px, height_px), color="white")
        else:
            image = Image.new("RGB", (width_px, height_px), color="white")
        
        draw = ImageDraw.Draw(image)
        
        # Add content
        self._add_print_content(draw, spec, content, width_px, height_px)
        
        # Add bleed and crop marks if needed
        if spec.bleed > 0:
            image = self._add_bleed_and_marks(image, spec)
        
        # Save in multiple formats
        output_files = []
        for file_format in spec.file_formats:
            filename = f"{campaign_id}_{format_name}.{file_format.lower()}"
            filepath = f"/tmp/{filename}"
            
            if file_format == "PDF":
                image.save(filepath, "PDF", resolution=spec.dpi)
            elif file_format == "TIFF":
                image.save(filepath, "TIFF", dpi=(spec.dpi, spec.dpi))
            else:
                image.save(filepath, file_format)
            
            output_files.append({
                "format": file_format,
                "path": filepath,
                "size_mb": os.path.getsize(filepath) / 1024 / 1024
            })
        
        creative = {
            "creative_id": str(uuid.uuid4()),
            "campaign_id": campaign_id,
            "format": format_name,
            "specification": {
                "width": spec.width_inches,
                "height": spec.height_inches,
                "dpi": spec.dpi,
                "color_mode": spec.color_mode
            },
            "files": output_files,
            "created_at": datetime.now().isoformat()
        }
        
        campaign.creatives.append(creative)
        
        logger.info(f"✅ Print creative generated: {format_name}")
        return creative
    
    def _add_print_content(
        self,
        draw: ImageDraw.Draw,
        spec: PrintSpecification,
        content: Dict[str, Any],
        width: int,
        height: int
    ):
        """Add content to print creative"""
        # Calculate safe zone
        safe_margin = int(spec.safe_zone * spec.dpi)
        
        # Try to load font, fallback to default
        try:
            headline_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size=int(spec.dpi * 0.5))
            body_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size=int(spec.dpi * 0.15))
        except:
            headline_font = ImageFont.load_default()
            body_font = ImageFont.load_default()
        
        # Add headline
        if "headline" in content:
            draw.text(
                (safe_margin, safe_margin),
                content["headline"],
                fill="black",
                font=headline_font
            )
        
        # Add body text
        if "body" in content:
            y_offset = safe_margin + int(spec.dpi * 0.7)
            draw.multiline_text(
                (safe_margin, y_offset),
                content["body"],
                fill="black",
                font=body_font,
                spacing=10
            )
        
        # Add logo placeholder
        if "logo" in content:
            logo_size = int(spec.dpi * 0.5)
            logo_position = (width - safe_margin - logo_size, height - safe_margin - logo_size)
            draw.rectangle(
                [logo_position, (logo_position[0] + logo_size, logo_position[1] + logo_size)],
                outline="black",
                width=2
            )
            draw.text(
                (logo_position[0] + 10, logo_position[1] + logo_size // 2),
                "LOGO",
                fill="black"
            )
        
        # Add call-to-action
        if "cta" in content:
            cta_y = height - safe_margin - int(spec.dpi * 0.3)
            draw.text(
                (safe_margin, cta_y),
                content["cta"],
                fill="black",
                font=body_font
            )
    
    def _add_bleed_and_marks(
        self,
        image: Image.Image,
        spec: PrintSpecification
    ) -> Image.Image:
        """Add bleed area and crop marks"""
        bleed_px = int(spec.bleed * spec.dpi)
        
        # Create new image with bleed
        new_width = image.width + (bleed_px * 2)
        new_height = image.height + (bleed_px * 2)
        
        new_image = Image.new("RGB", (new_width, new_height), color="white")
        new_image.paste(image, (bleed_px, bleed_px))
        
        # Add crop marks
        draw = ImageDraw.Draw(new_image)
        mark_length = int(spec.dpi * 0.25)
        
        # Top-left
        draw.line([(0, bleed_px), (mark_length, bleed_px)], fill="black", width=1)
        draw.line([(bleed_px, 0), (bleed_px, mark_length)], fill="black", width=1)
        
        # Top-right
        draw.line([(new_width - mark_length, bleed_px), (new_width, bleed_px)], fill="black", width=1)
        draw.line([(new_width - bleed_px, 0), (new_width - bleed_px, mark_length)], fill="black", width=1)
        
        # Bottom-left
        draw.line([(0, new_height - bleed_px), (mark_length, new_height - bleed_px)], fill="black", width=1)
        draw.line([(bleed_px, new_height - mark_length), (bleed_px, new_height)], fill="black", width=1)
        
        # Bottom-right
        draw.line([(new_width - mark_length, new_height - bleed_px), (new_width, new_height - bleed_px)], fill="black", width=1)
        draw.line([(new_width - bleed_px, new_height - mark_length), (new_width - bleed_px, new_height)], fill="black", width=1)
        
        return new_image
    
    def _plan_newspaper_campaign(
        self,
        campaign: TraditionalCampaign,
        budget: float
    ):
        """Plan newspaper advertising"""
        # Select newspapers based on target markets
        newspapers = self._get_newspapers_for_markets(campaign.target_markets)
        
        # Calculate placements
        budget_per_paper = budget / len(newspapers)
        
        for newspaper in newspapers:
            # Determine ad size based on budget
            if budget_per_paper >= 10000:
                ad_size = "full_page"
            elif budget_per_paper >= 5000:
                ad_size = "half_page"
            else:
                ad_size = "quarter_page"
            
            placement = {
                "media_type": "newspaper",
                "publication": newspaper["name"],
                "circulation": newspaper["circulation"],
                "ad_size": ad_size,
                "frequency": "weekly",
                "cost": budget_per_paper,
                "markets": newspaper["markets"]
            }
            
            campaign.placements.append(placement)
    
    def _plan_billboard_campaign(
        self,
        campaign: TraditionalCampaign,
        budget: float
    ):
        """Plan billboard advertising"""
        # Determine number of billboards based on budget
        cost_per_billboard = 3000  # Average monthly cost
        num_billboards = int(budget / cost_per_billboard)
        
        for i in range(num_billboards):
            placement = {
                "media_type": "billboard",
                "format": "14x48" if budget > 50000 else "30_sheet",
                "location": f"Highway {i+1}",
                "impressions_daily": 50000,
                "cost": cost_per_billboard,
                "duration_weeks": 4
            }
            
            campaign.placements.append(placement)
    
    def _plan_radio_campaign(
        self,
        campaign: TraditionalCampaign,
        budget: float
    ):
        """Plan radio advertising"""
        # Select radio stations
        stations = self._get_radio_stations_for_markets(campaign.target_markets)
        
        budget_per_station = budget / len(stations)
        
        for station in stations:
            # Calculate spots based on budget
            cost_per_spot = 100  # Average 30-second spot
            num_spots = int(budget_per_station / cost_per_spot)
            
            placement = {
                "media_type": "radio",
                "station": station["call_sign"],
                "format": station["format"],
                "audience": station["audience"],
                "spot_length": 30,
                "spots_per_day": num_spots // 30,  # Spread over month
                "dayparts": ["morning_drive", "afternoon_drive"],
                "cost": budget_per_station
            }
            
            campaign.placements.append(placement)
    
    def _plan_tv_campaign(
        self,
        campaign: TraditionalCampaign,
        budget: float
    ):
        """Plan TV advertising"""
        # Determine TV strategy based on budget
        if budget >= 100000:
            # National cable
            placement = {
                "media_type": "tv",
                "type": "national_cable",
                "networks": ["CNN", "ESPN", "HGTV"],
                "spot_length": 30,
                "frequency": "daily",
                "dayparts": ["prime_time"],
                "cost": budget
            }
        else:
            # Local broadcast
            placement = {
                "media_type": "tv",
                "type": "local_broadcast",
                "stations": ["ABC", "CBS", "NBC", "FOX"],
                "spot_length": 30,
                "frequency": "weekly",
                "dayparts": ["early_fringe", "late_fringe"],
                "cost": budget
            }
        
        campaign.placements.append(placement)
    
    def _get_newspapers_for_markets(self, markets: List[str]) -> List[Dict[str, Any]]:
        """Get newspapers for target markets"""
        # Simplified - in production, use real database
        newspapers = [
            {"name": "The New York Times", "circulation": 500000, "markets": ["New York", "National"]},
            {"name": "Los Angeles Times", "circulation": 300000, "markets": ["Los Angeles", "California"]},
            {"name": "Chicago Tribune", "circulation": 250000, "markets": ["Chicago", "Illinois"]},
            {"name": "The Washington Post", "circulation": 350000, "markets": ["Washington DC", "National"]},
            {"name": "USA Today", "circulation": 1000000, "markets": ["National"]}
        ]
        
        # Filter by markets
        relevant = []
        for newspaper in newspapers:
            if any(market in newspaper["markets"] for market in markets):
                relevant.append(newspaper)
        
        return relevant if relevant else newspapers[:3]
    
    def _get_radio_stations_for_markets(self, markets: List[str]) -> List[Dict[str, Any]]:
        """Get radio stations for target markets"""
        # Simplified - in production, use real database
        stations = [
            {"call_sign": "WXYZ-FM", "format": "Top 40", "audience": 500000},
            {"call_sign": "WABC-AM", "format": "Talk", "audience": 300000},
            {"call_sign": "KLOS-FM", "format": "Rock", "audience": 400000},
            {"call_sign": "WBBM-AM", "format": "News", "audience": 250000}
        ]
        
        return stations[:min(len(stations), len(markets))]
    
    def _load_templates(self) -> Dict[str, Any]:
        """Load creative templates"""
        return {
            "newspaper": {
                "retail": {"headline_size": 72, "body_columns": 3},
                "automotive": {"headline_size": 96, "include_photo": True},
                "real_estate": {"layout": "grid", "photos": 6}
            },
            "magazine": {
                "fashion": {"layout": "full_bleed", "minimal_text": True},
                "technology": {"layout": "infographic", "data_viz": True}
            },
            "billboard": {
                "standard": {"max_words": 7, "font_size": "massive"},
                "digital": {"animation": True, "duration": 8}
            }
        }
    
    def _load_vendor_database(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load vendor/publication database"""
        return {
            "printers": [
                {"name": "PrintCo", "capabilities": ["offset", "digital"], "turnaround": 3},
                {"name": "QuickPrint", "capabilities": ["digital"], "turnaround": 1}
            ],
            "media_buyers": [
                {"name": "MediaMax", "specialties": ["newspaper", "magazine"], "commission": 0.15},
                {"name": "OutdoorPro", "specialties": ["billboard", "transit"], "commission": 0.12}
            ],
            "production": [
                {"name": "CreativeStudio", "services": ["design", "copywriting"], "hourly_rate": 150},
                {"name": "VideoWorks", "services": ["tv", "radio"], "hourly_rate": 200}
            ]
        }
    
    def get_campaign_report(self, campaign_id: str) -> Dict[str, Any]:
        """Generate traditional campaign report"""
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")
        
        # Calculate metrics
        total_impressions = 0
        for placement in campaign.placements:
            if "impressions_daily" in placement:
                days = (campaign.end_date - campaign.start_date).days if campaign.end_date else 30
                total_impressions += placement["impressions_daily"] * days
            elif "circulation" in placement:
                total_impressions += placement["circulation"]
            elif "audience" in placement:
                total_impressions += placement["audience"]
        
        report = {
            "campaign_id": campaign_id,
            "name": campaign.name,
            "status": "active" if datetime.now() < campaign.end_date else "completed",
            "budget": campaign.budget,
            "spent": sum(p.get("cost", 0) for p in campaign.placements),
            "media_types": [mt.value for mt in campaign.media_types],
            "markets": campaign.target_markets,
            "total_impressions": total_impressions,
            "cpm": (campaign.budget / total_impressions * 1000) if total_impressions > 0 else 0,
            "placements": len(campaign.placements),
            "creatives": len(campaign.creatives),
            "timeline": {
                "start": campaign.start_date.isoformat(),
                "end": campaign.end_date.isoformat() if campaign.end_date else None
            }
        }
        
        return report
    
    def export_print_package(self, campaign_id: str) -> str:
        """Export complete print package for production"""
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")
        
        # Create package with all creatives and specifications
        package = {
            "campaign": {
                "id": campaign_id,
                "name": campaign.name,
                "client": campaign.metadata.get("client", "Unknown")
            },
            "creatives": campaign.creatives,
            "specifications": [],
            "instructions": {
                "color_profile": "CMYK",
                "file_formats": ["PDF", "EPS"],
                "delivery_method": "FTP",
                "contact": campaign.metadata.get("contact", {})
            }
        }
        
        # Add specifications for each creative
        for creative in campaign.creatives:
            format_name = creative.get("format")
            if format_name in self.specifications:
                spec = self.specifications[format_name]
                package["specifications"].append({
                    "format": format_name,
                    "dimensions": f"{spec.width_inches}x{spec.height_inches} inches",
                    "dpi": spec.dpi,
                    "color_mode": spec.color_mode,
                    "bleed": spec.bleed,
                    "safe_zone": spec.safe_zone
                })
        
        # Save package
        package_path = f"/tmp/print_package_{campaign_id}.json"
        with open(package_path, 'w') as f:
            json.dump(package, f, indent=2)
        
        logger.info(f"✅ Print package exported: {package_path}")
        return package_path