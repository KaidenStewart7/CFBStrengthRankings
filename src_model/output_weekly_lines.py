import sqlite3
import os
from sklearn.linear_model import LinearRegression
from fetch_api_data import FetchApiData

# season type
SEASON_TYPE = "regular"
# Week
DB_WEEK = 1

# Base directory of the current script
base_dir = os.path.dirname(os.path.abspath(__file__))

# Rankings path 
RANKINGS_PATH = os.path.join(base_dir, "..", "txt", f"2026_week{2026}_strength_ratings.txt")

# Input data path
INPUT_PATH = os.path.join(base_dir, "..", "db", "Model.db")

def create_model():
    connection = sqlite3.connect(INPUT_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT Neutral_Flag, Home_Rating_Diff, Home_Point_Diff
        FROM model_data
    """)

    data = cursor.fetchall()

    connection.close()

    # X = independent variables
    # y = dependent variable
    X = [[row[0], row[1]] for row in data]
    y = [row[2] for row in data]

    model = LinearRegression()
    model.fit(X, y)
    return model
def get_top_teams():
    teams = []

    with open(RANKINGS_PATH, "r") as file:
        lines = file.readlines()

        for count, line in enumerate(lines):
            if count > 0:
                ranking = line[0:line.index(".")]
                name = line[line.index(".") + 2:line.index(":")]
                rating = line[line.index(":") + 2:line.rfind('(') - 1]
                teams.append({
                    "Name": name,
                    "Rating": '{:.4f}'.format(float(rating))
                })

    return teams

def create_lines():
    # Create regression model
    model = create_model()

    # Get Week 2 games from API
    api_data = FetchApiData()
    games = api_data.fetch_games(1, SEASON_TYPE)

    if games is None:
        print("No games data fetched.")
        return

    # Get team ratings
    teams = get_top_teams()

    # Create dictionary for quick rating lookup
    team_ratings = {}

    for team in teams:
        team_ratings[team["Name"]] = float(team["Rating"])

    # Connect to Model.db
    connection = sqlite3.connect(INPUT_PATH)
    cursor = connection.cursor()

    # Delete existing lines for this week
    cursor.execute("""
        DELETE FROM lines_2025
        WHERE Week = ?
    """, (DB_WEEK,))

    for game in games:

        # Only use FBS vs FBS games
        if (game["homeClassification"] == "fbs" and
                game["awayClassification"] == "fbs"):

            # Get game information
            home_team = game["homeTeam"]
            away_team = game["awayTeam"]
            neutral_flag = game["neutralSite"]

            # Make sure both teams have ratings
            if home_team not in team_ratings:
                print(f"Skipping {home_team}: no rating found.")
                continue

            if away_team not in team_ratings:
                print(f"Skipping {away_team}: no rating found.")
                continue

            # Get ratings
            home_rating = team_ratings[home_team]
            away_rating = team_ratings[away_team]

            # Calculate rating difference
            home_rating_diff = home_rating - away_rating

            # Predict point differential
            prediction = model.predict([
                [neutral_flag, home_rating_diff]
            ])[0]

            # Determine projected winner
            if prediction >= 0:
                projected_winner = home_team
            else:
                projected_winner = away_team

            # Make projected line positive
            projected_line = abs(prediction)

            # Round to nearest 0.5
            projected_line = round(projected_line * 2) / 2

            if SEASON_TYPE == "postseason":
                week = 17
            else:
                week = DB_WEEK

            # Insert into lines_2025
            cursor.execute("""
                INSERT INTO lines_2025 (
                    Week,
                    Home_Team,
                    Away_Team,
                    Neutral_Flag,
                    Projected_Winner,
                    Projected_Line,
                    Home_Rating,
                    Away_Rating
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                week,
                home_team,
                away_team,
                neutral_flag,
                projected_winner,
                projected_line,
                home_rating,
                away_rating
            ))

    connection.commit()
    connection.close()

    print(f"Successfully created lines for Week {DB_WEEK}.")


def main():
    create_lines()
    

if __name__ == "__main__":
    main()