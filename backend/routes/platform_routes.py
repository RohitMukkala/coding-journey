from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from database import get_db, SessionLocal
from models import CodingProfile, User as DBUser
from auth import get_current_user
from datetime import datetime, timedelta
from sqlalchemy import and_
import asyncio
import logging
from typing import Dict, Any, Optional
import httpx
import os

router = APIRouter()
logger = logging.getLogger(__name__)

# Cache settings
CACHE_EXPIRY = timedelta(minutes=30)  # Update data every 30 minutes

def get_cached_profile(db: Session, user_id: int, platform: str) -> Optional[CodingProfile]:
    """Get cached profile data from database."""
    profile = db.query(CodingProfile).filter(
        and_(
            CodingProfile.user_id == user_id,
            CodingProfile.platform == platform
        )
    ).first()
    
    if profile and datetime.utcnow() - profile.last_updated < CACHE_EXPIRY:
        logger.info(f"Using cached {platform} data for user {user_id}")
        return profile
    
    return None

def update_profile_in_db(
    user_id: int,
    platform: str,
    username: str,
    data: Dict[str, Any]
):
    """Update profile data in the database."""
    try:
        # Create new database session for background task
        db = SessionLocal()
        try:
            logger.info(f"Updating {platform} data for user {user_id}")
            profile = db.query(CodingProfile).filter(
                and_(
                    CodingProfile.user_id == user_id,
                    CodingProfile.platform == platform
                )
            ).first()

            if not profile:
                logger.info(f"Creating new {platform} profile for user {user_id}")
                profile = CodingProfile(
                    user_id=user_id,
                    platform=platform,
                    username=username
                )
                db.add(profile)

            # Update common fields
            profile.last_updated = datetime.utcnow()

            # Update platform-specific fields
            if platform == "leetcode":
                profile.total_problems_solved = data.get("totalSolved")
                profile.easy_solved = data.get("easySolved")
                profile.medium_solved = data.get("mediumSolved")
                profile.hard_solved = data.get("hardSolved")
                profile.easy_percentage = data.get("easyPercentage")
                profile.medium_percentage = data.get("mediumPercentage")
                profile.hard_percentage = data.get("hardPercentage")
            
            elif platform == "codechef":
                profile.current_rating = data.get("currentRating")
                profile.highest_rating = data.get("highestRating")
                profile.global_rank = data.get("globalRank")
                profile.country_rank = data.get("countryRank")
                profile.stars = data.get("stars")
            
            elif platform == "codeforces":
                profile.codeforces_rating = data.get("current_rating")
                profile.codeforces_max_rating = data.get("max_rating")
                profile.problems_solved_count = data.get("problems_solved")
                profile.contest_rating = data.get("contest_rating")

            db.commit()
            logger.info(f"Successfully updated {platform} profile for user {user_id}")

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error updating {platform} profile: {str(e)}")

@router.get("/leetcode/{username}")
async def get_leetcode_stats(
    username: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user)
):
    # First, try to get cached data
    cached_profile = get_cached_profile(db, current_user.id, "leetcode")
    if cached_profile:
        # Start background update if cache is about to expire
        if datetime.utcnow() - cached_profile.last_updated > CACHE_EXPIRY - timedelta(minutes=5):
            data = await fetch_leetcode_data(username)
            background_tasks.add_task(
                update_profile_in_db,
                current_user.id,
                "leetcode",
                username,
                data
            )
        return {
            "totalSolved": cached_profile.total_problems_solved,
            "easySolved": cached_profile.easy_solved,
            "mediumSolved": cached_profile.medium_solved,
            "hardSolved": cached_profile.hard_solved,
            "easyPercentage": cached_profile.easy_percentage,
            "mediumPercentage": cached_profile.medium_percentage,
            "hardPercentage": cached_profile.hard_percentage,
        }

    # If no cached data, fetch new data
    data = await fetch_leetcode_data(username)
    background_tasks.add_task(
        update_profile_in_db,
        current_user.id,
        "leetcode",
        username,
        data
    )
    return data

@router.get("/codechef/{username}")
async def get_codechef_stats(
    username: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user)
):
    cached_profile = get_cached_profile(db, current_user.id, "codechef")
    if cached_profile:
        if datetime.utcnow() - cached_profile.last_updated > CACHE_EXPIRY - timedelta(minutes=5):
            data = await fetch_codechef_data(username)
            background_tasks.add_task(
                update_profile_in_db,
                current_user.id,
                "codechef",
                username,
                data
            )
        return {
            "currentRating": cached_profile.current_rating,
            "highestRating": cached_profile.highest_rating,
            "globalRank": cached_profile.global_rank,
            "countryRank": cached_profile.country_rank,
            "stars": cached_profile.stars,
        }

    data = await fetch_codechef_data(username)
    background_tasks.add_task(
        update_profile_in_db,
        current_user.id,
        "codechef",
        username,
        data
    )
    return data

@router.get("/codeforces/{username}")
async def get_codeforces_stats(
    username: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user)
):
    cached_profile = get_cached_profile(db, current_user.id, "codeforces")
    if cached_profile:
        if datetime.utcnow() - cached_profile.last_updated > CACHE_EXPIRY - timedelta(minutes=5):
            data = await fetch_codeforces_data(username)
            background_tasks.add_task(
                update_profile_in_db,
                current_user.id,
                "codeforces",
                username,
                data
            )
        return {
            "current_rating": cached_profile.codeforces_rating,
            "max_rating": cached_profile.codeforces_max_rating,
            "problems_solved": cached_profile.problems_solved_count,
            "contest_rating": cached_profile.contest_rating,
        }

    data = await fetch_codeforces_data(username)
    background_tasks.add_task(
        update_profile_in_db,
        current_user.id,
        "codeforces",
        username,
        data
    )
    return data

async def fetch_leetcode_data(username: str) -> Dict[str, Any]:
    """Fetch LeetCode data from API."""
    async with httpx.AsyncClient() as client:
        url = "https://leetcode.com/graphql"
        query = """
        query getUserProfile($username: String!) {
          matchedUser(username: $username) {
            submitStatsGlobal {
              acSubmissionNum {
                difficulty
                count
              }
            }
          }
        }
        """
        variables = {"username": username}
        
        response = await client.post(url, json={"query": query, "variables": variables})
        data = response.json()
        
        if "data" in data and data["data"]["matchedUser"]:
            submissions = data["data"]["matchedUser"]["submitStatsGlobal"]["acSubmissionNum"]
            submission_data = {sub["difficulty"].lower(): sub["count"] for sub in submissions}
            total = submission_data.get("all", 0)
            
            return {
                "totalSolved": total,
                "easySolved": submission_data.get("easy", 0),
                "mediumSolved": submission_data.get("medium", 0),
                "hardSolved": submission_data.get("hard", 0),
                "easyPercentage": round(submission_data.get("easy", 0) / total * 100, 1) if total else 0,
                "mediumPercentage": round(submission_data.get("medium", 0) / total * 100, 1) if total else 0,
                "hardPercentage": round(submission_data.get("hard", 0) / total * 100, 1) if total else 0,
            }
        raise HTTPException(status_code=404, detail="LeetCode user not found")

async def fetch_codechef_data(username: str) -> Dict[str, Any]:
    """Fetch CodeChef data from API."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://codechef-api.vercel.app/handle/{username}")
        data = response.json()
        
        if not data:
            raise HTTPException(status_code=404, detail="CodeChef user not found")
            
        return {
            "currentRating": data.get("currentRating"),
            "highestRating": data.get("highestRating"),
            "globalRank": data.get("globalRank"),
            "countryRank": data.get("countryRank"),
            "stars": data.get("stars")
        }

async def fetch_codeforces_data(username: str) -> Dict[str, Any]:
    """Fetch CodeForces data from API."""
    async with httpx.AsyncClient() as client:
        [status_response, rating_response] = await asyncio.gather(
            client.get(f"https://codeforces.com/api/user.status?handle={username}"),
            client.get(f"https://codeforces.com/api/user.rating?handle={username}")
        )
        
        status_data = status_response.json()
        rating_data = rating_response.json()
        
        if status_data.get('status') != 'OK':
            raise HTTPException(status_code=404, detail="CodeForces user not found")
            
        solved_problems = set()
        for submission in status_data['result']:
            if submission.get('verdict') == 'OK':
                problem = submission['problem']
                problem_id = f"{problem['contestId']}{problem['index']}"
                solved_problems.add(problem_id)
                
        rating_history = rating_data.get('result', [])
        current_rating = rating_history[-1]['newRating'] if rating_history else None
        
        return {
            "problems_solved": len(solved_problems),
            "current_rating": current_rating,
            "max_rating": max((r['newRating'] for r in rating_history), default=None) if rating_history else None,
            "contest_rating": current_rating
        }

async def fetch_github_data(username: str) -> Dict[str, Any]:
    """Fetch GitHub data from API."""
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"}
        
        # Fetch basic profile
        profile_response = await client.get(f"https://api.github.com/users/{username}", headers=headers)
        profile_data = profile_response.json()
        
        # Fetch contributions via GraphQL
        query = """
        query ($username: String!) {
            user(login: $username) {
                contributionsCollection {
                    contributionCalendar {
                        totalContributions
                        weeks {
                            contributionDays {
                                date
                                contributionCount
                            }
                        }
                    }
                }
            }
        }
        """
        contributions_response = await client.post(
            "https://api.github.com/graphql",
            json={"query": query, "variables": {"username": username}},
            headers=headers
        )
        contributions_data = contributions_response.json()
        
        # Process contributions
        calendar = contributions_data.get('data', {}).get('user', {}).get('contributionsCollection', {}).get('contributionCalendar', {})
        contribution_days = [
            day for week in calendar.get('weeks', [])
            for day in week.get('contributionDays', [])
        ]
        
        # Calculate streaks
        current_streak = 0
        longest_streak = 0
        current_consecutive = 0
        
        for day in sorted(contribution_days, key=lambda x: x['date']):
            if day['contributionCount'] > 0:
                current_consecutive += 1
                longest_streak = max(longest_streak, current_consecutive)
            else:
                current_consecutive = 0
        
        current_streak = current_consecutive
        
        # Fetch repositories for stars and forks
        repos_response = await client.get(f"https://api.github.com/users/{username}/repos?per_page=100", headers=headers)
        repos = repos_response.json()
        
        total_stars = sum(repo.get('stargazers_count', 0) for repo in repos)
        total_forks = sum(repo.get('forks_count', 0) for repo in repos)
        
        # Fetch languages
        languages = {}
        for repo in repos:
            lang_response = await client.get(repo['languages_url'], headers=headers)
            lang_data = lang_response.json()
            for lang, bytes in lang_data.items():
                languages[lang] = languages.get(lang, 0) + bytes
        
        if languages:
            total = sum(languages.values())
            languages = {lang: round((count / total) * 100, 2) for lang, count in languages.items()}
        
        return {
            "profile": profile_data,
            "contributions": {
                "total_contributions": calendar.get('totalContributions', 0),
                "current_streak": current_streak,
                "longest_streak": longest_streak
            },
            "stats": {
                "stars": total_stars,
                "forks": total_forks
            },
            "languages": languages
        }

@router.get("/github/{username}")
async def get_github_stats(
    username: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user)
):
    """Get GitHub stats with caching."""
    cached_profile = get_cached_profile(db, current_user.id, "github")
    if cached_profile:
        # If cache is about to expire, fetch fresh data in background
        if datetime.utcnow() - cached_profile.last_updated > CACHE_EXPIRY - timedelta(minutes=5):
            data = await fetch_github_data(username)
            background_tasks.add_task(
                update_profile_in_db,
                current_user.id,
                "github",
                username,
                data
            )
        
        # Return cached data
        return {
            "profile": None,  # We don't store basic profile data
            "contributions": {
                "total_contributions": cached_profile.total_contributions,
                "current_streak": cached_profile.current_streak,
                "longest_streak": cached_profile.longest_streak
            },
            "stats": {
                "stars": cached_profile.total_stars,
                "forks": cached_profile.total_forks
            },
            "languages": cached_profile.languages
        }

    # No cache available, fetch fresh data
    data = await fetch_github_data(username)
    background_tasks.add_task(
        update_profile_in_db,
        current_user.id,
        "github",
        username,
        data
    )
    return data 