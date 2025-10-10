import sqlite3
import os

# Class to interact with the database
# Get path to the current script
base_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to txt/teams_list.txt (relative to project root)
team_list_path = os.path.join(base_dir, "..", "txt", "teams_list.txt")

# Construct the path to db/cfb_game_results.db (relative to project root)
db_path = os.path.join(base_dir, "..", "db", "cfb_game_results.db")

# Class to handle database queries
class DatabaseQueries:
    # Method to insert conferences into the database
    def insert_conferences(self):
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        conferences = ["Mountain West", "Mid-American", "SEC", "Sun Belt", "Big 12", "American Athletic", "ACC", "Conference USA", "Big Ten"]

        for conference in conferences:
            cursor.execute("INSERT INTO CONFERENCE (Name) VALUES (?)", (conference,))

        connection.commit()
        connection.close()

    # Method to insert teams into the database from the teams_list.txt file
    def insert_teams(self):
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        with open(team_list_path, "r") as file:
            for line in file:
                split_line = line.strip().split(",")
                team_name = split_line[0]
                conference_name = split_line[1]
                talent_rating = split_line[2]

                cursor.execute("INSERT INTO TEAM(Name, Conference, Team_Composite_Rating) VALUES (?, ?, ?)", (team_name, conference_name, talent_rating))
            
            connection.commit()
            connection.close()

    # Method to insert a game into the database
    def insert_game(self, week, home_team, away_team, neutral_flag, home_score, away_score):
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        cursor.execute("INSERT INTO GAME(Week, Home_Team, Away_Team, Neutral_Flag, Home_Score, Away_Score) VALUES (?, ?, ?, ?, ?, ?)", (week, home_team, away_team, neutral_flag, home_score, away_score))

        connection.commit()
        connection.close()

    # Method to select all conferences from the database 
    def select_conferences(self):
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        cursor.execute("SELECT Name FROM CONFERENCE")
        conferences = cursor.fetchall()

        connection.close()
        return conferences
    
    # Method to select all teams from the database
    def select_teams(self):
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM TEAM")
        teams = cursor.fetchall()

        connection.close()
        return teams
    
    # Method to select all games from the database
    def select_games(self):
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM GAME")
        games = cursor.fetchall()

        connection.close()
        return games


def main():
    db_queries = DatabaseQueries()
    teams = db_queries.select_games()
    print(teams)

if __name__ == "__main__":
    main()
        
        