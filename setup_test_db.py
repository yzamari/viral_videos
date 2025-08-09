#!/usr/bin/env python3
"""
Quick database setup script for testing
Creates SQLite database with basic schema
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, Column, String, Float, DateTime, Integer, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

# Basic models for testing
class User(Base):
    __tablename__ = 'users'
    
    id = Column(String, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Campaign(Base):
    __tablename__ = 'campaigns'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    objective = Column(String)
    platforms = Column(JSON)
    budget = Column(Float)
    status = Column(String)
    user_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class Analytics(Base):
    __tablename__ = 'analytics'
    
    id = Column(String, primary_key=True)
    campaign_id = Column(String)
    metric_type = Column(String)
    value = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    dimensions = Column(JSON)

def setup_database():
    """Create test database with schema"""
    # Remove existing test db
    db_path = 'test.db'
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed existing {db_path}")
    
    # Create new database
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    
    print(f"✅ Created test database: {db_path}")
    print("✅ Tables created: users, campaigns, analytics")
    
    # Create test user
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Add test user
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        test_user = User(
            id="test-user-1",
            username="testuser",
            email="test@example.com",
            hashed_password=pwd_context.hash("testpass123")
        )
        session.add(test_user)
        
        # Add test campaign
        test_campaign = Campaign(
            id="test-campaign-1",
            name="Test Campaign",
            objective="brand_awareness",
            platforms=["youtube", "tiktok"],
            budget=1000.0,
            status="active",
            user_id="test-user-1"
        )
        session.add(test_campaign)
        
        session.commit()
        print("✅ Added test data")
        
    except ImportError:
        print("⚠️ passlib not installed - skipping test data creation")
        print("Run: pip install passlib")
    except Exception as e:
        print(f"Error adding test data: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    setup_database()