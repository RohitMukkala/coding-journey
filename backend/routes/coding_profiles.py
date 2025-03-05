from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import requests
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from models import CodingProfile
from sqlalchemy import and_
from auth import get_current_user
from models import User as DBUser
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

router = APIRouter()

def save_profile_data(db: Session, user_id: int, platform: str, username: str, data: Dict[str, Any]):
    """Save or update coding profile data in the database."""
    logger.info(f"Attempting to save {platform} data for user {user_id} with username {username}")
    logger.debug(f"Received data: {data}")
    
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
    else:
        logger.info(f"Updating existing {platform} profile for user {user_id}")
    
    # Update common fields
    profile.last_updated = datetime.utcnow()
    
    # Update platform-specific fields
    if platform == "github":
        logger.debug("Updating GitHub fields")
        profile.total_contributions = data.get("contributions", {}).get("total_contributions")
        profile.current_streak = data.get("contributions", {}).get("current_streak")
        profile.longest_streak = data.get("contributions", {}).get("longest_streak")
        profile.total_stars = data.get("stats", {}).get("stars")
        profile.total_forks = data.get("stats", {}).get("forks")
        profile.languages = data.get("languages")
    
    elif platform == "leetcode":
        logger.debug("Updating LeetCode fields")
        profile.total_problems_solved = data.get("totalSolved")
        profile.easy_solved = data.get("easySolved")
        profile.medium_solved = data.get("mediumSolved")
        profile.hard_solved = data.get("hardSolved")
        profile.easy_percentage = data.get("easyPercentage")
        profile.medium_percentage = data.get("mediumPercentage")
        profile.hard_percentage = data.get("hardPercentage")
    
    elif platform == "codechef":
        logger.debug("Updating CodeChef fields")
        profile.current_rating = data.get("currentRating")
        profile.highest_rating = data.get("highestRating")
        profile.global_rank = data.get("globalRank")
        profile.country_rank = data.get("countryRank")
        profile.stars = data.get("stars")
    
    elif platform == "codeforces":
        logger.debug("Updating Codeforces fields")
        profile.codeforces_rating = data.get("current_rating")
        profile.codeforces_max_rating = data.get("max_rating")
        profile.problems_solved_count = data.get("problems_solved")
        profile.contest_rating = data.get("contest_rating")
    
    try:
        db.commit()
        logger.info(f"Successfully saved {platform} profile data for user {user_id}")
        logger.debug(f"Saved profile data: {profile.__dict__}")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to save {platform} profile data for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save profile data: {str(e)}")

def get_leetcode_data(username: str) -> Dict[str, Any]:
    url = "https://leetcode.com/graphql"
    headers = {"Content-Type": "application/json"}
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
    
    try:
        response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        if "data" in data and data["data"]["matchedUser"] is not None:
            user_data = data["data"]["matchedUser"]
            submissions = user_data["submitStatsGlobal"]["acSubmissionNum"]
            
            submission_data = {
                sub["difficulty"].lower(): sub["count"] 
                for sub in submissions
            }
            
            return {
                "totalSolved": submission_data.get("all", 0),
                "easySolved": submission_data.get("easy", 0),
                "mediumSolved": submission_data.get("medium", 0),
                "hardSolved": submission_data.get("hard", 0),
                "easyPercentage": round(submission_data.get("easy", 0) / submission_data.get("all", 1) * 100, 1),
                "mediumPercentage": round(submission_data.get("medium", 0) / submission_data.get("all", 1) * 100, 1),
                "hardPercentage": round(submission_data.get("hard", 0) / submission_data.get("all", 1) * 100, 1)
            }
        else:
            raise HTTPException(status_code=404, detail="LeetCode user not found")
            
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch LeetCode data: {str(e)}")

def get_codeforces_data(username: str) -> Dict[str, Any]:
    user_status_url = f"https://codeforces.com/api/user.status?handle={username}"
    user_rating_url = f"https://codeforces.com/api/user.rating?handle={username}"

    try:
        # Fetch user's submission status
        user_status_response = requests.get(user_status_url)
        user_status_response.raise_for_status()
        user_status_data = user_status_response.json()
        
        if user_status_data.get('status') != 'OK':
            raise HTTPException(status_code=404, detail=user_status_data.get('comment', 'Codeforces user not found'))

        # Process solved problems
        solved_problems = {}
        for submission in user_status_data['result']:
            if submission.get('verdict') == 'OK':
                problem = submission['problem']
                problem_id = f"{problem['contestId']}{problem['index']}"
                if problem_id not in solved_problems:
                    index = problem.get('index', '')
                    name = problem.get('name', 'Unknown')
                    full_name = f"{index}. {name}" if index else name
                    solved_problems[problem_id] = {
                        'name': full_name,
                        'difficulty': problem.get('rating', 'No rating')
                    }

        # Fetch user's rating
        user_rating_response = requests.get(user_rating_url)
        user_rating_response.raise_for_status()
        user_rating_data = user_rating_response.json()
        
        if user_rating_data.get('status') != 'OK':
            raise HTTPException(status_code=404, detail=user_rating_data.get('comment', 'Codeforces user not found'))

        rating_history = user_rating_data['result']
        current_rating = rating_history[-1]['newRating'] if rating_history else None

        return {
            "problems_solved": len(solved_problems),
            "current_rating": current_rating,
            "example_problems": list(solved_problems.values())[:5]
        }
        
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch Codeforces data: {str(e)}")

def get_codechef_data(username: str) -> Dict[str, Any]:
    url = f"https://codechef-api.vercel.app/handle/{username}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
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
        
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch CodeChef data: {str(e)}")

@router.get("/leetcode/{username}")
async def get_leetcode_stats(
    username: str,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user)
):
    data = get_leetcode_data(username)
    if current_user:
        save_profile_data(db, current_user.id, "leetcode", username, data)
    return data

@router.get("/codeforces/{username}")
async def get_codeforces_stats(
    username: str,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user)
):
    try:
        data = get_codeforces_data(username)
        if current_user:
            save_profile_data(db, current_user.id, "codeforces", username, data)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/codechef/{username}")
async def get_codechef_stats(
    username: str,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user)
):
    data = get_codechef_data(username)
    if current_user:
        save_profile_data(db, current_user.id, "codechef", username, data)
    return data 