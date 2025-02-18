import requests

def get_leetcode_data(username):
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
    response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if "data" in data and data["data"]["matchedUser"] is not None:
            return data["data"]["matchedUser"]
        else:
            return "Invalid LeetCode username"
    else:
        return "Failed to fetch LeetCode data"

def get_codeforces_data(username):
    user_status_url = f"https://codeforces.com/api/user.status?handle={username}"
    user_rating_url = f"https://codeforces.com/api/user.rating?handle={username}"

    user_status_response = requests.get(user_status_url)
    if user_status_response.status_code != 200:
        return {"error": f"Failed to fetch user status for {username}"}
    user_status_data = user_status_response.json()
    if user_status_data.get('status') != 'OK':
        return {"error": user_status_data.get('comment', 'Unknown error')}

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
    example_problems = list(solved_problems.values())[:5]

    user_rating_response = requests.get(user_rating_url)
    if user_rating_response.status_code != 200:
        return {"error": f"Failed to fetch user rating for {username}"}
    user_rating_data = user_rating_response.json()
    if user_rating_data.get('status') != 'OK':
        return {"error": user_rating_data.get('comment', 'Unknown error')}

    rating_history = user_rating_data['result']
    current_rating = rating_history[-1]['newRating'] if rating_history else None

    return {
        "problems_solved": len(solved_problems),
        "current_rating": current_rating,
        "example_problems": example_problems
    }

def get_codechef_data(username):
    url = f"https://codechef-api.vercel.app/handle/{username}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        return "Invalid CodeChef username"

def display_user_data(leetcode_username, codeforces_handle, codechef_handle):
    output = ""

    # LeetCode Data
    output += "\nLeetCode Data:\n\n"
    if leetcode_username:
        leetcode_data = get_leetcode_data(leetcode_username)
        if isinstance(leetcode_data, dict):
            submissions = leetcode_data.get('submitStatsGlobal', {}).get('acSubmissionNum', [])
            all_count = next((item['count'] for item in submissions if item['difficulty'] == 'All'), 0)
            easy_count = next((item['count'] for item in submissions if item['difficulty'] == 'Easy'), 0)
            medium_count = next((item['count'] for item in submissions if item['difficulty'] == 'Medium'), 0)
            hard_count = next((item['count'] for item in submissions if item['difficulty'] == 'Hard'), 0)

            output += f"Submissions (All Time):\n"
            output += f"All: {all_count} submissions\n"
            output += f"Easy: {easy_count} submissions\n"
            output += f"Medium: {medium_count} submissions\n"
            output += f"Hard: {hard_count} submissions\n\n"

            tags = leetcode_data.get('tagProblemCounts', {}).get('advanced', [])
            output += "Tag Problem Counts:\n"
            for tag in tags:
                output += f"{tag['tagName']}: {tag['problemsSolved']} problems solved\n"
        else:
            output += f"{leetcode_data}\n"
    else:
        output += "Invalid LeetCode username\n"

    # CodeChef Data
    output += "\nCodeChef Data:\n\n"
    if codechef_handle:
        codechef_data = get_codechef_data(codechef_handle)
        if isinstance(codechef_data, dict) and 'currentRating' in codechef_data:
            output += f"User: {codechef_data.get('name', 'N/A')}\n"
            output += f"Current Rating: {codechef_data.get('currentRating', 'N/A')}\n"
            output += f"Highest Rating: {codechef_data.get('highestRating', 'N/A')}\n"
            output += f"Country: {codechef_data.get('countryName', 'N/A')}\n"
            output += f"Global Rank: {codechef_data.get('globalRank', 'N/A')}\n"
            output += f"Country Rank: {codechef_data.get('countryRank', 'N/A')}\n"
            output += f"Stars: {codechef_data.get('stars', 'N/A')}\n"
        else:
            output += "Invalid CodeChef data format\n"
    else:
        output += "Invalid CodeChef username\n"

    # Codeforces Data
    output += "\nCodeforces Data:\n\n"
    if codeforces_handle:
        codeforces_data = get_codeforces_data(codeforces_handle)
        if isinstance(codeforces_data, dict) and 'problems_solved' in codeforces_data:
            output += f"Number of Problems Solved: {codeforces_data.get('problems_solved', 0)}\n"
            current_rating = codeforces_data.get('current_rating', 'N/A')
            output += f"User Rating: {current_rating if current_rating is not None else 'N/A'}\n\n"
            example_problems = codeforces_data.get('example_problems', [])
            if example_problems:
                output += "Problem Sets:\n"
                for problem in example_problems:
                    output += f"Problem: {problem.get('name', 'Unknown')} - Difficulty: {problem.get('difficulty', 'No rating')}\n"
            else:
                output += "Problem Sets: No solved problems found\n"
        else:
            error_msg = codeforces_data.get('error', 'Failed to fetch Codeforces data')
            output += f"{error_msg}\n"
    else:
        output += "Invalid Codeforces username\n"

    print(output)

# Example usage
leetcode_username = "RohitMukkala"  # Replace with actual LeetCode username
codeforces_handle = "beast264"  # Replace with actual Codeforces handle
codechef_handle = "beast264"  # Replace with actual CodeChef handle

display_user_data(leetcode_username, codeforces_handle, codechef_handle)
