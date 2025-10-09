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

    # # Method to insert teams into the database from the teams_list.txt file
    # def insert_teams(self):
    #     connection = sqlite3.connect(db_path)
    #     cursor = connection.cursor()

    #     with open(team_list_path, "r") as file:
    #         for line in file:
    #             school = "hi:"
        
def main():
    db = DatabaseQueries()
    db.insert_conferences()

if __name__ == "__main__":
    main()
        