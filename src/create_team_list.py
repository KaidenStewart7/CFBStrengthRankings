from fetch_api_data import FetchApiData
import os

YEAR = 2024

# Get path to the current script
base_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to txt/teams_list.txt (relative to project root)
output_path = os.path.join(base_dir, "..", "txt", f"{YEAR}_teams_list.txt")

# Creates a list of teams and there conferences to be printed to the file
def main():
    teams_info = FetchApiData().fetch_cfb_teams()
    for team in teams_info:
        if team['classification'] == 'fbs':
            with open(output_path, "a") as file:
                file.write(f"{team['school']},{team['conference']}\n")

if __name__ == "__main__":
    main()