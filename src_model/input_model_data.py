import os
import sqlite3

# Currrent Year
DB_YEAR = 2026
# Current Week
DB_WEEK = 0
# Current Rankings Path 
base_dir = os.path.dirname(os.path.abspath(__file__))
RANKINGS_PATH = os.path.join(base_dir, "..", "txt", f"2026_week{DB_WEEK}_strength_ratings.txt")
# Input data path
INPUT_PATH = os.path.join(base_dir, "..", "db", f"{DB_YEAR}_cfb_game_results.db")
# Output data path
OUTPUT_PATH = os.path.join(base_dir, "..", "db", "Model.db")

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

def get_game_results():
    connection = sqlite3.connect(INPUT_PATH)
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM GAME WHERE Week = ?", (DB_WEEK,))
    game_results = cursor.fetchall()

    connection.close()
    return game_results

def input_model_data():
    games = get_game_results()
    teams = get_top_teams()

    # Create a dictionary so we can quickly find a team's rating
    team_ratings = {}

    for team in teams:
        team_ratings[team["Name"]] = float(team["Rating"])

    # Connect to Model.db
    connection = sqlite3.connect(OUTPUT_PATH)
    cursor = connection.cursor()

    for game in games:
        week, home_team, away_team, neutral_flag, home_score, away_score = game

        # Calculate point differential from the home team's perspective
        home_point_diff = home_score - away_score

        if neutral_flag == 1:
            if home_point_diff > 0:
                home_point_diff = home_point_diff + 2.5
            else:
                home_point_diff = home_point_diff - 2.5

        # Get the ratings for both teams
        home_rating = team_ratings[home_team]
        away_rating = team_ratings[away_team]

        # Calculate rating differential from the home team's perspective
        home_rating_diff = home_rating - away_rating

        # Insert into model_data
        cursor.execute("""
            INSERT INTO model_data (
                Neutral_Flag,
                Home_Point_Diff,
                Home_Rating_Diff
            )
            VALUES (?, ?, ?)
        """, (
            neutral_flag,
            home_point_diff,
            home_rating_diff
        ))

    connection.commit()
    connection.close()
    



def main():
    input_model_data()

if __name__ == "__main__":
    main()
        

