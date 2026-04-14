"""
Database Initialization Script

Creates all database tables and optionally seeds sample data.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import engine, Base
from app.models import base  # Import all models
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random

from app.models.user import User
from app.models.match import Match, MatchStatus, TournamentStage
from app.core.security import hash_password


def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created successfully")


def seed_sample_data():
    """Seed database with sample data for development"""
    print("\nSeeding sample data...")
    
    session = Session(bind=engine)
    
    try:
        # Create sample users
        print("Creating sample users...")
        users = [
            User(
                username="john_predictor",
                email="john@example.com",
                password_hash=hash_password("password123"),
                total_points=150,
                predictions_count=25,
                correct_results=15,
                exact_scores=3
            ),
            User(
                username="sarah_analyst",
                email="sarah@example.com",
                password_hash=hash_password("password123"),
                total_points=200,
                predictions_count=30,
                correct_results=20,
                exact_scores=5
            ),
            User(
                username="mike_fan",
                email="mike@example.com",
                password_hash=hash_password("password123"),
                total_points=100,
                predictions_count=20,
                correct_results=10,
                exact_scores=2
            )
        ]
        session.add_all(users)
        session.commit()
        print(f"✓ Created {len(users)} sample users")
        
        # Create sample matches
        print("Creating sample matches...")
        
        teams = [
            'Argentina', 'Brazil', 'France', 'England', 
            'Spain', 'Germany', 'Netherlands', 'Portugal',
            'Belgium', 'Italy', 'Uruguay', 'Croatia',
            'Denmark', 'Mexico', 'USA', 'Switzerland'
        ]
        
        matches = []
        base_date = datetime.utcnow() + timedelta(days=7)
        
        # Group stage matches
        for i in range(12):
            home_team = random.choice(teams)
            away_team = random.choice([t for t in teams if t != home_team])
            
            match = Match(
                home_team=home_team,
                away_team=away_team,
                match_date=base_date + timedelta(days=i),
                venue=f"Stadium {i+1}",
                stage=TournamentStage.GROUP,
                group_name=f"Group {chr(65 + i % 8)}",
                status=MatchStatus.SCHEDULED
            )
            matches.append(match)
        
        # Add some finished matches
        for i in range(5):
            home_team = random.choice(teams)
            away_team = random.choice([t for t in teams if t != home_team])
            
            match = Match(
                home_team=home_team,
                away_team=away_team,
                match_date=datetime.utcnow() - timedelta(days=i+1),
                venue=f"Stadium {i+1}",
                stage=TournamentStage.GROUP,
                group_name=f"Group {chr(65 + i % 8)}",
                status=MatchStatus.FINISHED,
                home_score=random.randint(0, 3),
                away_score=random.randint(0, 3)
            )
            matches.append(match)
        
        # Knockout stage matches
        knockout_matches = [
            Match(
                home_team='Argentina',
                away_team='France',
                match_date=base_date + timedelta(days=20),
                venue='Main Stadium',
                stage=TournamentStage.FINAL,
                status=MatchStatus.SCHEDULED
            ),
            Match(
                home_team='Brazil',
                away_team='England',
                match_date=base_date + timedelta(days=18),
                venue='Stadium A',
                stage=TournamentStage.SEMI,
                status=MatchStatus.SCHEDULED
            ),
            Match(
                home_team='Spain',
                away_team='Germany',
                match_date=base_date + timedelta(days=18),
                venue='Stadium B',
                stage=TournamentStage.SEMI,
                status=MatchStatus.SCHEDULED
            )
        ]
        
        matches.extend(knockout_matches)
        session.add_all(matches)
        session.commit()
        print(f"✓ Created {len(matches)} sample matches")
        
        print("\n✅ Sample data seeded successfully!")
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        session.rollback()
    finally:
        session.close()


def main():
    """Main initialization function"""
    print("=" * 50)
    print("WC26 Database Initialization")
    print("=" * 50)
    
    # Create tables
    create_tables()
    
    # Ask if user wants to seed sample data
    response = input("\nDo you want to seed sample data? (y/n): ").lower()
    if response == 'y':
        seed_sample_data()
    
    print("\n✅ Database initialization complete!")
    print("\nYou can now start the application with:")
    print("  uvicorn app.main:app --reload")


if __name__ == "__main__":
    main()
