import requests
import os
from dotenv import load_dotenv

# Current Year
CURRENT_YEAR = 2024

#Load variables from .env file
load_dotenv()

api_token = os.getenv("CFP_API_TOKEN")
headers = {
    "Authorization": f"Bearer {api_token}"
}

# Class to fetch data from the College Football Data API
class FetchApiData:
    # Fetches cfb teams from the College Football Data API 
    # Returns the JSON of the response
    def fetch_cfb_teams(self):
        url = f"https://api.collegefootballdata.com/teams?year={CURRENT_YEAR}&week=1&classification=fbs"
        try: 
            response = requests.get(url, headers=headers)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from {url}: {e}")

    # Fetches all the games for the given week from the College Football Data API
    # Returns the JSON of the response
    def fetch_games(self, week, season_type):
        url = f"https://api.collegefootballdata.com/games?year={CURRENT_YEAR}&week=" + str(week) + "&seasonType=" + season_type
        try: 
            response = requests.get(url, headers=headers)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from {url}: {e}")



