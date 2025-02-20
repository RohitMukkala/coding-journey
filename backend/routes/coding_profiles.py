from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import requests

router = APIRouter()

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
        tagProblemCounts {
          advanced {
            tagName
            problemsSolved
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
            
            # Process submission data
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
async def get_leetcode_stats(username: str):
    return get_leetcode_data(username)

@router.get("/codeforces/{username}")
async def get_codeforces_stats(username: str):
    return get_codeforces_data(username)

@router.get("/codechef/{username}")
async def get_codechef_stats(username: str):
    return get_codechef_data(username) 