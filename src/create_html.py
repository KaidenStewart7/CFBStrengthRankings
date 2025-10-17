import os

# Current Year
YEAR = 2025

# Current Week
WEEK = 7
# Get path to the current script
base_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to txt/teams_list.txt (relative to project root)
strength_ratings_path = os.path.join(base_dir, "..", "txt", f"{YEAR}_week{WEEK}_strength_ratings.txt")

# Construct the path to docs/index.html (relative to project root)
index_path = os.path.join(base_dir, "..", "docs", "index.html")

# Class to create HTML output
class CreateHTML():
    def initialize(self):
        self.teams = []

    # Method to get the top teams
    def get_top_teams(self):
        with open(strength_ratings_path, "r") as file:
            count = 0
            lines = file.readlines()
            count = 0
            for line in lines:
                if count > 0:
                    ranking = line[0:line.index(".")]
                    name = line[line.index(".") + 2:line.index(":")]
                    rating = line[line.index(":") + 2:line.rfind('(') - 1]
                    self.teams.append({"Ranking": ranking, "Name": name, "Rating": '  {:.4f}'.format(float(rating).__round__(4))})
                else:
                    count+=1

    def print_index_file(self):
        with open(index_path, "w") as file:
            file.write("<!DOCTYPE html>\n")
            file.write("<html lang=\"en\">\n")
            file.write("    <head>\n")
            file.write("        <link rel=\"stylesheet\" href=\"styles.css\" media=\"screen\" />\n")
            file.write("        <title>College Football Strength Rankings</title>\n")
            file.write("        <meta charset=\"UTF-8\" >\n")
            file.write("    </head>\n")
            file.write("    <body>\n")
            file.write("        <h1>College Football Strength Rankings</h1>\n")
            file.write("        <p>\n")
            file.write("            Below you can find the weekly rankings of college football teams according to their strength rankings. These are power rankings that take into account team performance, conference strength, and the talent of the team determined by their <a href=\"https://247sports.com/season/2025-football/collegeteamtalentcomposite/\"> 247 Sports Talent Composite Ranking</a>. Each week, new rankings will be added. Early in the season, the main factor weighting the strength ratings will be their talent rating; however, as the season progresses and more games are played, each team’s rankings will factor in their \"resume rating\" more than their talent rating. Eventually, after each team plays 12 games against FBS opponents, their strength rating will be comprised only of their resume rating. A team's resume rating factors in their performance as well as the strength of the conference they are in. \n")
            file.write("        </p>\n")
            file.write("        <h2> Weekly Rankings </h2>\n")
            file.write("        <div>\n")
            week_count = WEEK
            while week_count > 0:
                week_path = f"{YEAR}week{week_count}.html"
                file.write(f"            <p><a href=\"{week_path}\">Week {week_count} Rankings</a></p>\n")
                week_count -= 1
            file.write("        </div>\n")
            file.write("    </body>\n")
            file.write("</html>\n")

    # method to print the weekly files
    def print_weekly_files(self):
        week_count = WEEK
        week_path = os.path.join(base_dir, "..", "docs", f"{YEAR}week{week_count}.html")
        with open(week_path, "w") as file:
            file.write("<!DOCTYPE html>\n")
            file.write("<html lang=\"en\">\n")
            file.write("    <head>\n")
            file.write("        <link rel=\"stylesheet\" href=\"styles.css\" media=\"screen\" />\n")
            file.write(f"        <title>College Football Strength Rankings - Week {week_count}</title>\n")
            file.write("        <meta charset=\"UTF-8\" >\n")
            file.write("    </head>\n")
            file.write("    <body>\n")
            file.write(f"        <h1>College Football Strength Rankings - Week {week_count}</h1>\n")
            file.write("        <ol>\n")
            file.write(f"            <li><span class=\"header\">Rank</span><span class=\"header\">Team Name</span> <span class=\"header\">Rating</span></li>\n")
            for row in self.teams:
                file.write(f"            <li><span class=\"ranking\">{row['Ranking']}.</span><span class=\"team\">{row['Name']}</span> <span class=\"rating\">{row['Rating']}</span></li>\n")
                
            file.write("        </ol>\n")
            file.write("        <p>\n")
            file.write("            <a href=\"index.html\">Back to Home Page</a>\n")
            file.write("        </p>\n")
            file.write("    </body>\n")
            file.write("</html>\n")
                
                


                


    # method to print the html files
    def print_HTML_files(self):
        self.get_top_teams()
        self.print_index_file()
        self.print_weekly_files()


# Scripts to create the HTML files
def main():
    html = CreateHTML()
    html.initialize()
    html.print_HTML_files()

if __name__ == "__main__":
    main()