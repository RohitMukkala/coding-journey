from dotenv import load_dotenv
import os
import json
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests

# Load environment variables from .env
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
print(f"GITHUB_TOKEN: {GITHUB_TOKEN}")  # Debugging line

if not GITHUB_TOKEN:
    raise RuntimeError("GitHub API token is missing. Set GITHUB_TOKEN in a .env file.")

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"}

def parse_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").date()

def calculate_streaks(contribution_days):
    current_streak = 0
    longest_streak = 0
    current_consecutive = 0
    last_contribution_date = None
    
    sorted_days = sorted(contribution_days, key=lambda x: x['date'])
    
    for day in sorted_days:
        if day['contributionCount'] > 0:
            current_consecutive += 1
            longest_streak = max(longest_streak, current_consecutive)
            last_contribution_date = parse_date(day['date'])
        else:
            current_consecutive = 0
    
    if last_contribution_date:
        today = datetime.utcnow().date()
        current_date = last_contribution_date
        
        while any(d['date'] == current_date.isoformat() and d['contributionCount'] > 0 for d in sorted_days):
            current_streak += 1
            current_date -= timedelta(days=1)
    
    return current_streak, longest_streak

def process_contributions(data, username):
    try:
        user_data = data.get('data', {}).get('user')
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")
        
        calendar = user_data['contributionsCollection']['contributionCalendar']
        weeks = calendar['weeks']
        
        contribution_days = [day for week in weeks for day in week['contributionDays']]
        current_streak, longest_streak = calculate_streaks(contribution_days)
        
        return {
            "total_contributions": calendar['totalContributions'],
            "current_streak": current_streak,
            "longest_streak": longest_streak
        }
    except KeyError as e:
        raise HTTPException(status_code=500, detail=f"Error processing contributions data: {str(e)}")

@app.get("/{username}")
async def get_profile(username: str):
    try:
        url = f"https://api.github.com/users/{username}"
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        raise HTTPException(status_code=500, detail=f"GitHub API error: {err}")

@app.get("/{username}/contributions")
async def get_contributions(username: str):
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
    try:
        response = requests.post(
            "https://api.github.com/graphql",
            json={"query": query, "variables": {"username": username}},
            headers=HEADERS
        )
        response.raise_for_status()
        return process_contributions(response.json(), username)
    except requests.exceptions.RequestException as err:
        raise HTTPException(status_code=500, detail=f"GitHub API request error: {err}")

@app.get("/{username}/stats")
async def get_stats(username: str):
    try:
        repos_url = f"https://api.github.com/users/{username}/repos?per_page=100"
        response = requests.get(repos_url, headers=HEADERS)
        response.raise_for_status()
        repos = response.json()

        total_stars = sum(repo.get('stargazers_count', 0) for repo in repos)
        total_forks = sum(repo.get('forks_count', 0) for repo in repos)

        return {"stars": total_stars, "forks": total_forks}
    except requests.exceptions.RequestException as err:
        raise HTTPException(status_code=500, detail=f"GitHub API error: {err}")

@app.get("/{username}/languages")
async def get_languages(username: str):
    try:
        languages = {}
        page = 1
        while True:
            url = f"https://api.github.com/users/{username}/repos?page={page}&per_page=100"
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
            repos = response.json()
            if not repos:
                break
            
            for repo in repos:
                lang_url = repo['languages_url']
                lang_response = requests.get(lang_url, headers=HEADERS)
                lang_response.raise_for_status()
                lang_data = lang_response.json()
                for lang, bytes in lang_data.items():
                    languages[lang] = languages.get(lang, 0) + bytes
            
            page += 1

        if not languages:
            return {}

        total = sum(languages.values())
        return {lang: round((count / total) * 100, 2) for lang, count in languages.items()}
    
    except requests.exceptions.RequestException as err:
        raise HTTPException(status_code=500, detail=f"GitHub API error: {err}")

@app.get("/{username}/all")
async def get_all_github_data(username: str):
    """Get all GitHub data for a user in a single request."""
    try:
        # Fetch basic profile data
        profile = await get_profile(username)
        
        # Fetch contributions data
        contributions = await get_contributions(username)
        
        # Fetch stats data
        stats = await get_stats(username)
        
        # Fetch languages data
        languages = await get_languages(username)
        
        # Combine all data
        return {
            "profile": profile,
            "contributions": contributions,
            "stats": stats,
            "languages": languages
        }
    except HTTPException as err:
        raise err
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Error fetching GitHub data: {str(err)}")
