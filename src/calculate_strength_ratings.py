import pandas as pd
from database_queries import DatabaseQueries as db
import math
import os

# Current Year
YEAR = 2025
# Week Number for the strength ratings
WEEK = 8

# Get path to the current script
base_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to txt/teams_list.txt (relative to project root)
strength_ratings_path = os.path.join(base_dir, "..", "txt", f"{YEAR}_week{WEEK}_strength_ratings.txt")

# Class to calculate the strength ratings
class CalculateStrengthRatings:
    # Initialize the class with empty DataFrames for conferences and teams
    def __init__(self):
        # Creates conferences data frame
        self.conferences = pd.DataFrame(columns=['Name', 'OOC_Wins', 'OOC_Games', 'OOC_Win_Pct', 'OOC_Win_Pct_Standardized'])
        conferences = db().select_conferences()
        for conference in conferences:
            self.conferences.loc[len(self.conferences)] = [conference[0], 0, 0, 0.0, 0.0]

        # Creates teams data frame
        self.teams = pd.DataFrame(columns=['Name', 'Conference', 'Team_Composite_Rating', 'Team_Composite_Rating_Standardized', 'Wins', 'Games', 'Win_Pct', 'Conf_Wins', 'Conf_Games', 'Conf_Win_Pct', 'Point_Diff', 'Point_Diff_Standardized', 'Resume_Rating', 'Strength_Rating', 'Ranking', 'Home_Wins', 'Home_Losses', 'Neutral_Wins', 'Neutral_Losses', 'Away_Wins', 'Away_Losses', 'Quad1_Wins', 'Quad1_Losses', 'Quad2_Wins', 'Quad2_Losses', 'Quad3_Wins', 'Quad3_Losses', 'Quad4_Wins', 'Quad4_Losses'])
        teams = db().select_teams()
        for team in teams:
            self.teams.loc[len(self.teams)] = [team[0], team[1], float(team[2]), 0, 0, 0, 0.0, 0, 0, 0.0, 0, 0.0, 0.0, 0.0, 0, [], [], [], [], [], [], 0, 0, 0, 0, 0, 0, 0, 0]

    # Method to standardize the composite rating
    def standardize_composite_rating(self):
        max_rating = self.teams['Team_Composite_Rating'].max()
        min_rating = self.teams['Team_Composite_Rating'].min()
        self.teams['Team_Composite_Rating_Standardized'] = (self.teams['Team_Composite_Rating'] - min_rating) / (max_rating - min_rating)

    # Method to update conference out-of-conference totals
    def update_conference_ooc_totals(self, home_conf, away_conf, home_score, away_score):
        # Update games played
        self.conferences.loc[self.conferences['Name'] == home_conf, 'OOC_Games'] += 1
        self.conferences.loc[self.conferences['Name'] == away_conf, 'OOC_Games'] += 1

        # Update wins
        if home_score > away_score:
            self.conferences.loc[self.conferences['Name'] == home_conf, 'OOC_Wins'] += 1
        else:
            self.conferences.loc[self.conferences['Name'] == away_conf, 'OOC_Wins'] += 1

    # Method to update team conference wins
    def update_team_conf_wins(self, home_team, away_team, home_score, away_score):
        self.teams.loc[self.teams['Name'] == home_team, 'Conf_Games'] += 1
        self.teams.loc[self.teams['Name'] == away_team, 'Conf_Games'] += 1

        # Update wins and point differnentials
        if home_score > away_score:
            self.teams.loc[self.teams['Name'] == home_team, 'Conf_Wins'] += 1
        else:
            self.teams.loc[self.teams['Name'] == away_team, 'Conf_Wins'] += 1

    # Method to update team totals
    def update_team_totals(self, home_team, away_team, home_score, away_score, neutral_flag):
        # Update games played
        self.teams.loc[self.teams['Name'] == home_team, 'Games'] += 1
        self.teams.loc[self.teams['Name'] == away_team, 'Games'] += 1

        # Update wins and point differnentials
        if home_score > away_score:
            self.teams.loc[self.teams['Name'] == home_team, 'Wins'] += 1
            point_diff = home_score - away_score
            self.teams.loc[self.teams['Name'] == home_team, 'Point_Diff'] += point_diff
            self.teams.loc[self.teams['Name'] == away_team, 'Point_Diff'] -= point_diff

            if neutral_flag == 1:
                self.teams.loc[self.teams['Name'] == home_team, 'Neutral_Wins'] = self.teams.loc[self.teams['Name'] == home_team, 'Neutral_Wins'].apply(lambda x: x + [away_team] if isinstance(x, list) else [away_team])
                self.teams.loc[self.teams['Name'] == away_team, 'Neutral_Losses'] = self.teams.loc[self.teams['Name'] == away_team, 'Neutral_Losses'].apply(lambda x: x + [home_team] if isinstance(x, list) else [home_team])
            
            else:
                self.teams.loc[self.teams['Name'] == home_team, 'Home_Wins'] = self.teams.loc[self.teams['Name'] == home_team, 'Home_Wins'].apply(lambda x: x + [away_team] if isinstance(x, list) else [away_team])
                self.teams.loc[self.teams['Name'] == away_team, 'Away_Losses'] = self.teams.loc[self.teams['Name'] == away_team, 'Away_Losses'].apply(lambda x: x + [home_team] if isinstance(x, list) else [home_team])
                

        else:
            self.teams.loc[self.teams['Name'] == away_team, 'Wins'] += 1
            point_diff = away_score - home_score
            self.teams.loc[self.teams['Name'] == away_team, 'Point_Diff'] += point_diff
            self.teams.loc[self.teams['Name'] == home_team, 'Point_Diff'] -= point_diff

            if neutral_flag == 1:
                self.teams.loc[self.teams['Name'] == away_team, 'Neutral_Wins'] = self.teams.loc[self.teams['Name'] == away_team, 'Neutral_Wins'].apply(lambda x: x + [home_team] if isinstance(x, list) else [home_team])
                self.teams.loc[self.teams['Name'] == home_team, 'Neutral_Losses'] = self.teams.loc[self.teams['Name'] == home_team, 'Neutral_Losses'].apply(lambda x: x + [away_team] if isinstance(x, list) else [away_team])

            else:
                self.teams.loc[self.teams['Name'] == away_team, 'Away_Wins'] = self.teams.loc[self.teams['Name'] == away_team, 'Away_Wins'].apply(lambda x: x + [home_team] if isinstance(x, list) else [home_team])
                self.teams.loc[self.teams['Name'] == home_team, 'Home_Losses'] = self.teams.loc[self.teams['Name'] == home_team, 'Home_Losses'].apply(lambda x: x + [away_team] if isinstance(x, list) else [away_team])
            

    # Method to parse games and update team and conference records
    def parse_games(self):
        games = db().select_games()
        for game in games:
            if game[0] > WEEK:
                break
            # Gets essential information
            home_team = game[1]
            home_conference = self.teams[self.teams['Name'] == home_team]['Conference'].values[0]
            home_score = game[4]
            away_team = game[2]
            away_conference = self.teams[self.teams['Name'] == away_team]['Conference'].values[0]
            away_score = game[5]

            # Updates conference's record if it's an out-of-conference game
            if home_conference != away_conference:
                self.update_conference_ooc_totals(home_conference, away_conference, home_score, away_score)
            
            # Updated's teams' conference records if it's a conference game
            else:
                self.update_team_conf_wins(home_team, away_team, home_score, away_score)

            # Updates teams' records
            self.update_team_totals(home_team, away_team, home_score, away_score, game[3])

    # Calculates the out of conference win percentages
    def calculate_ooc_win_pct(self):
        for row in self.conferences.itertuples():
            if row.OOC_Games > 0:
                self.conferences.loc[self.conferences['Name'] == row.Name, 'OOC_Win_Pct'] = row.OOC_Wins / row.OOC_Games
            else:
                self.conferences.loc[self.conferences['Name'] == row.Name, 'OOC_Win_Pct'] = 0.0
        
    # Standardizes the out of conference win percentages
    def standardize_ooc_win_pct(self):
        max_pct = self.conferences['OOC_Win_Pct'].max()
        min_pct = self.conferences['OOC_Win_Pct'].min()
        self.conferences['OOC_Win_Pct_Standardized'] = (self.conferences['OOC_Win_Pct'] - min_pct) / (max_pct - min_pct)

    # Calculates each team's win percentage
    def calculate_team_win_pct(self):
        for row in self.teams.itertuples():
            if row.Games > 0:
                self.teams.loc[self.teams['Name'] == row.Name, 'Win_Pct'] = float(row.Wins) / row.Games
            else:
                self.teams.loc[self.teams['Name'] == row.Name, 'Win_Pct'] = 0.0
    
    # Calculates each team's conference win percentage
    def calculate_team_conf_win_pct(self):
        for row in self.teams.itertuples():
            if row.Conf_Games > 0:
                self.teams.loc[self.teams['Name'] == row.Name, 'Conf_Win_Pct'] = float(row.Conf_Wins) / row.Conf_Games
            else:
                self.teams.loc[self.teams['Name'] == row.Name, 'Conf_Win_Pct'] = 0.0

    # Standardizes each team's point differential
    def standardize_point_diff(self):
        max_diff = self.teams['Point_Diff'].max()
        min_diff = self.teams['Point_Diff'].min()
        self.teams['Point_Diff_Standardized'] = (self.teams['Point_Diff'] - min_diff) / (max_diff - min_diff)

    # Calculates logrithmic factor
    def log_factor(self, games_played, game_threshold):
        return math.log(games_played + 1) / math.log(game_threshold)

    # Gets a team's resume rating
    def get_team_resume_rating(self, win_pct, conf_win_pct, standardize_point_diff, ooc_win_pct_standardized, conf_games_played):
        final_avg = (win_pct + conf_win_pct + standardize_point_diff + ooc_win_pct_standardized)/4
        before_enough_conf_games = (win_pct + standardize_point_diff + ooc_win_pct_standardized)/3
        if conf_games_played >= 3:
            return final_avg
        else:   
            return before_enough_conf_games

    # Calculates each team's resume rating
    def calculate_strength_rating(self):
        for row in self.teams.itertuples():
            # Gets resume rating and compostie rating
            resume_rating = self.get_team_resume_rating(row.Win_Pct, row.Conf_Win_Pct, row.Point_Diff_Standardized, self.conferences.loc[self.conferences['Name'] == row.Conference, 'OOC_Win_Pct_Standardized'].values[0], row.Conf_Games)
            self.teams.loc[self.teams['Name'] == row.Name, 'Resume_Rating'] = resume_rating
            standardized_comp = row.Team_Composite_Rating_Standardized

            # Checks if game threshold is met before calculating strength rating
            if row.Games < 12:
                strength_rating = resume_rating * self.log_factor(row.Games, 13) + standardized_comp * (1 - self.log_factor(row.Games, 13))
            else: 
                strength_rating = resume_rating
            self.teams.loc[self.teams['Name'] == row.Name, 'Strength_Rating'] = strength_rating

    # Order teams by strength rating
    def order_teams_by_strength_rating(self):
        self.teams.sort_values(by='Strength_Rating', inplace=True, ascending=False)

        rank = 1
        for row in self.teams.itertuples():
            self.teams.loc[self.teams['Name'] == row.Name, 'Ranking'] = rank
            rank += 1

    # Prints rankings to file
    def print_strength_ratings(self):
        with open(strength_ratings_path, 'w') as file:
            file.write(f"{YEAR} Week {WEEK} Strength Ratings\n")
            for row in self.teams.itertuples():
                file.write(f"{row.Ranking}. {row.Name}: {row.Strength_Rating} ({row.Quad1_Wins}-{row.Quad1_Losses},{row.Quad2_Wins}-{row.Quad2_Losses},{row.Quad3_Wins}-{row.Quad3_Losses},{row.Quad4_Wins}-{row.Quad4_Losses})\n")


    # Calculates the team's quad
    def calculate_team_quad(self, opp_team, location):
        team_ranking = self.teams.loc[self.teams['Name'] == opp_team, 'Ranking'].iloc[0]
    
        if location == "H":
            if team_ranking < 12:
                return 1
            elif team_ranking < 29:
                return 2
            elif team_ranking < 61:
                return 3
            else:
                return 4
        
        elif location == "N":
            if team_ranking < 20:
                return 1
            elif team_ranking < 28:
                return 2
            elif team_ranking < 76:
                return 3
            else:
                return 4
            
        else:
            if team_ranking < 29:
                return 1
            elif team_ranking < 51:
                return 2
            elif team_ranking < 90:
                return 3
            else:
                return 4
            

    # Calculates quad home wins
    def calculate_quad_home_wins(self, row):
        team_list = self.teams.loc[self.teams['Name'] == row.Name, 'Home_Wins'].iloc[0]
        for opp_team in team_list:
            quad = self.calculate_team_quad(opp_team, "H")

            if quad == 1:
                self.teams.loc[self.teams['Name'] == row.Name, 'Quad1_Wins'] += 1
            elif quad == 2:
                self.teams.loc[self.teams['Name'] == row.Name, 'Quad2_Wins'] += 1
            elif quad == 3:
                self.teams.loc[self.teams['Name'] == row.Name, 'Quad3_Wins'] += 1
            else:
                self.teams.loc[self.teams['Name'] == row.Name, 'Quad4_Wins'] += 1

    # Calculates quad home losses
    def calculate_quad_home_losses(self, row):
        team_list = self.teams.loc[self.teams['Name'] == row.Name, 'Home_Losses'].iloc[0]
        for opp_team in team_list:
            quad = self.calculate_team_quad(opp_team, "H")

            if quad == 1:
                self.teams.loc[self.teams['Name'] == row.Name, 'Quad1_Losses'] += 1
            elif quad == 2:
                self.teams.loc[self.teams['Name'] == row.Name, 'Quad2_Losses'] += 1
            elif quad == 3:
                self.teams.loc[self.teams['Name'] == row.Name, 'Quad3_Losses'] += 1
            else:
                self.teams.loc[self.teams['Name'] == row.Name, 'Quad4_Losses'] += 1

    # Calculates quad neutral wins
    def calculate_quad_neutral_wins(self, row):
        team_list = self.teams.loc[self.teams['Name'] == row.Name, 'Neutral_Wins'].iloc[0]
        for opp_team in team_list:
            quad = self.calculate_team_quad(opp_team, "N")

            if quad == 1:
                self.teams.loc[self.teams['Name'] == row.Name, 'Quad1_Wins'] += 1
            if quad == 2:
                self.teams.loc[self.teams['Name'] == row.Name, 'Quad2_Wins'] += 1
            if quad == 3:
                self.teams.loc[self.teams['Name'] == row.Name, 'Quad3_Wins'] += 1
            if quad == 4:
                self.teams.loc[self.teams['Name'] == row.Name, 'Quad4_Wins'] += 1

    # Calculates quad neutral losses
    def calculate_quad_neutral_losses(self, row):
        team_list = self.teams.loc[self.teams['Name'] == row.Name, 'Neutral_Losses'].iloc[0]
        for opp_team in team_list:
            quad = self.calculate_team_quad(opp_team, "N")

            if quad == 1:
                self.teams.loc[self.teams['Name'] == row.Name, 'Quad1_Losses'] += 1
            if quad == 2:
                self.teams.loc[self.teams['Name'] == row.Name, 'Quad2_Losses'] += 1
            if quad == 3:
                self.teams.loc[self.teams['Name'] == row.Name, 'Quad3_Losses'] += 1
            if quad == 4:
                self.teams.loc[self.teams['Name'] == row.Name, 'Quad4_Losses'] += 1

    # Calculates quad away wins
    def calculate_quad_away_wins(self, row):
        team_list = self.teams.loc[self.teams['Name'] == row.Name, 'Away_Wins'].iloc[0]
        for opp_team in team_list:
            quad = self.calculate_team_quad(opp_team, "A")

            if quad == 1:
                self.teams.loc[self.teams['Name'] == row.Name, 'Quad1_Wins'] += 1
            elif quad == 2:
                self.teams.loc[self.teams['Name'] == row.Name, 'Quad2_Wins'] += 1
            elif quad == 3:
                self.teams.loc[self.teams['Name'] == row.Name, 'Quad3_Wins'] += 1
            else:
                self.teams.loc[self.teams['Name'] == row.Name, 'Quad4_Wins'] += 1

    # Calculates quad away losses
    def calculate_quad_away_losses(self, row):
        team_list = self.teams.loc[self.teams['Name'] == row.Name, 'Away_Losses'].iloc[0]
        for opp_team in team_list:
            quad = self.calculate_team_quad(opp_team, "A")

            if quad == 1:
                self.teams.loc[self.teams['Name'] == row.Name, 'Quad1_Losses'] += 1
            elif quad == 2:
                self.teams.loc[self.teams['Name'] == row.Name, 'Quad2_Losses'] += 1
            elif quad == 3:
                self.teams.loc[self.teams['Name'] == row.Name, 'Quad3_Losses'] += 1
            else:
                self.teams.loc[self.teams['Name'] == row.Name, 'Quad4_Losses'] += 1



    # Calculates the quad wins and losses
    def calculate_quad_results(self):
        for row in self.teams.itertuples():
            self.calculate_quad_home_wins(row)
            self.calculate_quad_home_losses(row)
            self.calculate_quad_neutral_wins(row)
            self.calculate_quad_neutral_losses(row)
            self.calculate_quad_away_wins(row)
            self.calculate_quad_away_losses(row)
            


# Run scripts to calculate and output strength ratings            
def main():
    calc = CalculateStrengthRatings()
    calc.standardize_composite_rating()
    calc.parse_games()
    calc.calculate_ooc_win_pct()
    calc.standardize_ooc_win_pct()
    calc.calculate_team_win_pct()
    calc.calculate_team_conf_win_pct()
    calc.standardize_point_diff()
    calc.calculate_strength_rating()
    calc.order_teams_by_strength_rating()
    calc.calculate_quad_results()
    calc.print_strength_ratings()

    


if __name__ == "__main__":
    main()



        


