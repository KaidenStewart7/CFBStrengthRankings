from fetch_api_data import FetchApiData
from database_queries import DatabaseQueries


# Week to load games of
WEEK = 15

# Regular or Postseason
SEASON_TYPE = "regular"

# This Class will load games from the College Football Data API into the database
class Load_Games:
    def import_games(self):
        api_data = FetchApiData()
        games = api_data.fetch_games(WEEK, SEASON_TYPE)

        if games is None:
            print("No games data fetched.")
            return
        
        
        for game in games:
            # Load only FBS vs FBS games
            if game["homeClassification"] == "fbs" and game["awayClassification"] == "fbs":
                
                # Gets data from the API response
                home_team = game["homeTeam"]
                away_team = game["awayTeam"]
                neutral_flag = game["neutralSite"]
                home_score = game["homePoints"]
                away_score = game["awayPoints"]

                db_queries = DatabaseQueries()
                if home_score is not None or away_score is not None:
                    if SEASON_TYPE == 'regular':
                        db_queries.insert_game(WEEK, home_team, away_team, neutral_flag, home_score, away_score)
                    else:
                        db_queries.insert_game(17, home_team, away_team, neutral_flag, home_score, away_score)
                else:
                    print (f"Skipping game between {home_team} and {away_team} due to missing scores.")

# Runs the script
# def main():
#     load_games = Load_Games()
#     load_games.import_games()

# if __name__ == "__main__":
#     main()

