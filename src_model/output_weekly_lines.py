import sqlite3
import os
from sklearn.linear_model import LinearRegression
from fetch_api_data import FetchApiData

# Season type
SEASON_TYPE = "regular"

# Week
DB_WEEK = 1

# Year
DB_YEAR = 2026

# Base directory of the current script
base_dir = os.path.dirname(os.path.abspath(__file__))

# Rankings path
RANKINGS_PATH = os.path.join(
    base_dir,
    "..",
    "txt",
    f"{DB_YEAR}_week{DB_WEEK - 1}_strength_ratings.txt"
)

# Input data path
INPUT_PATH = os.path.join(
    base_dir,
    "..",
    "db",
    "Model.db"
)

# HTML output directory
HTML_PATH = os.path.join(
    base_dir,
    "..",
    "docs"
)


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
                    "Ranking": int(ranking),
                    "Name": name,
                    "Rating": '{:.4f}'.format(float(rating))
                })

    return teams


def create_lines():

    # --------------------------------------------------
    # Create regression model
    # --------------------------------------------------

    model = create_model()

    # --------------------------------------------------
    # Get games from API
    # --------------------------------------------------

    api_data = FetchApiData()
    games = api_data.fetch_games(DB_WEEK, SEASON_TYPE)

    if games is None:
        print("No games data fetched.")
        return

    # --------------------------------------------------
    # Get team ratings and rankings
    # --------------------------------------------------

    teams = get_top_teams()

    # Create dictionaries for quick lookup
    team_ratings = {}
    team_rankings = {}

    for team in teams:
        team_ratings[team["Name"]] = float(team["Rating"])
        team_rankings[team["Name"]] = team["Ranking"]

    # --------------------------------------------------
    # Connect to Model.db
    # --------------------------------------------------

    connection = sqlite3.connect(INPUT_PATH)
    cursor = connection.cursor()

    # --------------------------------------------------
    # Delete existing lines for this week
    # --------------------------------------------------

    cursor.execute(f"""
        DELETE FROM lines_{DB_YEAR}
        WHERE Week = ?
    """, (DB_WEEK,))

    # Keep track of what happens
    added_games = 0
    skipped_games = 0

    # --------------------------------------------------
    # Go through API games
    # --------------------------------------------------

    for game in games:

        # Only use FBS vs FBS games
        if (
            game["homeClassification"] == "fbs"
            and game["awayClassification"] == "fbs"
        ):

            # Get game information
            home_team = game["homeTeam"]
            away_team = game["awayTeam"]
            neutral_flag = game["neutralSite"]

            # --------------------------------------------------
            # Get scores directly from API
            # --------------------------------------------------

            home_score = game["homePoints"]
            away_score = game["awayPoints"]

            # --------------------------------------------------
            # Skip completed games
            # --------------------------------------------------

            if home_score is not None and away_score is not None:

                print(
                    f"Skipping completed game: "
                    f"{home_team} vs {away_team} "
                    f"({home_score}-{away_score})"
                )

                skipped_games += 1
                continue

            # --------------------------------------------------
            # Make sure both teams have ratings
            # --------------------------------------------------

            if home_team not in team_ratings:
                print(
                    f"Skipping {home_team}: "
                    f"no rating found."
                )
                continue

            if away_team not in team_ratings:
                print(
                    f"Skipping {away_team}: "
                    f"no rating found."
                )
                continue

            # --------------------------------------------------
            # Get ratings
            # --------------------------------------------------

            home_rating = team_ratings[home_team]
            away_rating = team_ratings[away_team]

            # --------------------------------------------------
            # Calculate rating difference
            # --------------------------------------------------

            home_rating_diff = home_rating - away_rating

            # --------------------------------------------------
            # Predict point differential
            # --------------------------------------------------

            prediction = model.predict([
                [neutral_flag, home_rating_diff]
            ])[0]

            # --------------------------------------------------
            # Determine projected winner
            # --------------------------------------------------

            if prediction >= 0:
                projected_winner = home_team
            else:
                projected_winner = away_team

            # --------------------------------------------------
            # Make projected line positive
            # --------------------------------------------------

            projected_line = abs(prediction)

            # Round to nearest 0.5
            projected_line = round(projected_line * 2) / 2

            # --------------------------------------------------
            # Determine week
            # --------------------------------------------------

            if SEASON_TYPE == "postseason":
                week = 17
            else:
                week = DB_WEEK

            # --------------------------------------------------
            # Insert prediction into database
            # --------------------------------------------------

            cursor.execute(f"""
                INSERT INTO lines_{DB_YEAR} (
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

            print(
                f"Added: {home_team} vs {away_team} | "
                f"{projected_winner} -{projected_line}"
            )

            added_games += 1

    # --------------------------------------------------
    # Save database changes
    # --------------------------------------------------

    connection.commit()
    connection.close()

    print()
    print(
        f"Completed games skipped: "
        f"{skipped_games}"
    )

    print(
        f"New lines added: "
        f"{added_games}"
    )

    print(
        f"Successfully created lines "
        f"for Week {DB_WEEK}."
    )

    # --------------------------------------------------
    # Create HTML
    # --------------------------------------------------

    create_weekly_html()


def create_weekly_html():

    """
    Creates the HTML page for the current week's lines.

    Games are sorted by combined strength rating,
    highest to lowest.

    Format:

        (Rank) Home Team (-Line) vs (Rank) Away Team

    The line is only displayed next to the
    projected favorite.
    """

    # --------------------------------------------------
    # Connect to database
    # --------------------------------------------------

    connection = sqlite3.connect(INPUT_PATH)
    cursor = connection.cursor()

    cursor.execute(f"""
        SELECT
            Week,
            Home_Team,
            Away_Team,
            Neutral_Flag,
            Projected_Winner,
            Projected_Line,
            Home_Rating,
            Away_Rating
        FROM lines_{DB_YEAR}
        WHERE Week = ?
    """, (DB_WEEK,))

    games = cursor.fetchall()

    connection.close()

    # --------------------------------------------------
    # Get rankings
    # --------------------------------------------------

    teams = get_top_teams()

    team_rankings = {}

    for team in teams:
        team_rankings[team["Name"]] = team["Ranking"]

    # --------------------------------------------------
    # Sort games by combined strength rating
    # --------------------------------------------------

    games.sort(
        key=lambda game: game[6] + game[7],
        reverse=True
    )

    # --------------------------------------------------
    # Make sure docs directory exists
    # --------------------------------------------------

    os.makedirs(HTML_PATH, exist_ok=True)

    # --------------------------------------------------
    # HTML file path
    # --------------------------------------------------

    week_path = os.path.join(
        HTML_PATH,
        f"{DB_YEAR}week{DB_WEEK}lines.html"
    )

    # --------------------------------------------------
    # Create HTML file
    # --------------------------------------------------

    with open(
        week_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write("<!DOCTYPE html>\n")
        file.write("<html lang=\"en\">\n")

        # --------------------------------------------------
        # Head
        # --------------------------------------------------

        file.write("    <head>\n")

        file.write(
            "        <link rel=\"stylesheet\" "
            "href=\"styles.css\" media=\"screen\" />\n"
        )

        file.write(
            f"        <title>"
            f"College Football Lines - "
            f"{DB_YEAR} Week {DB_WEEK}"
            f"</title>\n"
        )

        file.write(
            "        <meta charset=\"UTF-8\">\n"
        )

        file.write("    </head>\n")

        # --------------------------------------------------
        # Body
        # --------------------------------------------------

        file.write("    <body>\n")

        file.write("        <div class=\"lines-page\">\n")

        file.write(
            f"            <h1>"
            f"College Football Lines - "
            f"Week {DB_WEEK}"
            f"</h1>\n"
        )

        file.write(
            "            <p class=\"lines-description\">\n"
        )

        file.write(
            "                Projected lines for this "
            "week's college football games. "
            "Games are ordered by team strength "
            "from highest to lowest.\n"
        )

        file.write(
            "            </p>\n"
        )

        # --------------------------------------------------
        # Week Header
        # --------------------------------------------------

        file.write(
            f"            <div class=\"lines-header\">"
            f"Week {DB_WEEK} Games"
            f"</div>\n"
        )

        # --------------------------------------------------
        # Game list
        # --------------------------------------------------

        file.write(
            "            <div class=\"lines-list\">\n"
        )

        for game in games:

            (
                week,
                home_team,
                away_team,
                neutral_flag,
                projected_winner,
                projected_line,
                home_rating,
                away_rating
            ) = game

            # --------------------------------------------------
            # Get team rankings
            # --------------------------------------------------

            home_rank = team_rankings.get(
                home_team,
                "?"
            )

            away_rank = team_rankings.get(
                away_team,
                "?"
            )

            # --------------------------------------------------
            # Format line with .0 for whole numbers
            # --------------------------------------------------

            line_text = f"{float(projected_line):.1f}"

            # --------------------------------------------------
            # Home team is favored
            # --------------------------------------------------

            if projected_winner == home_team:

                game_text = (
                    f"<span class=\"team-rank\">"
                    f"({home_rank})"
                    f"</span> "
                    f"{home_team} "
                    f"<span class=\"line\">"
                    f"(-{line_text})"
                    f"</span> "
                    f"vs "
                    f"<span class=\"team-rank\">"
                    f"({away_rank})"
                    f"</span> "
                    f"{away_team}"
                )

            # --------------------------------------------------
            # Away team is favored
            # --------------------------------------------------

            else:

                game_text = (
                    f"<span class=\"team-rank\">"
                    f"({home_rank})"
                    f"</span> "
                    f"{home_team} "
                    f"vs "
                    f"<span class=\"team-rank\">"
                    f"({away_rank})"
                    f"</span> "
                    f"{away_team} "
                    f"<span class=\"line\">"
                    f"(-{line_text})"
                    f"</span>"
                )

            # --------------------------------------------------
            # Write game row
            # --------------------------------------------------

            file.write(
                "                <div "
                "class=\"line-game\">\n"
            )

            file.write(
                f"                    "
                f"<span class=\"game\">"
                f"{game_text}"
                f"</span>\n"
            )

            file.write(
                "                </div>\n"
            )

        file.write(
            "            </div>\n"
        )

        # --------------------------------------------------
        # Back to Lines Home Page
        # Same HTML structure as the rankings page
        # --------------------------------------------------

        file.write("        <p>\n")

        file.write(
            "            <a href=\"lines_index.html\">"
            "Back to Lines Home Page"
            "</a>\n"
        )

        file.write("        </p>\n")

        file.write(
            "        </div>\n"
        )

        file.write("    </body>\n")
        file.write("</html>\n")

    print(
        f"Created HTML page: "
        f"{week_path}"
    )

    # --------------------------------------------------
    # Update Lines Index
    # --------------------------------------------------

    create_lines_index()


def create_lines_index():

    """
    Creates the main lines index page.

    Similar to the rankings index page.
    """

    index_path = os.path.join(
        HTML_PATH,
        "lines_index.html"
    )

    with open(
        index_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write("<!DOCTYPE html>\n")
        file.write("<html lang=\"en\">\n")

        # --------------------------------------------------
        # Head
        # --------------------------------------------------

        file.write("    <head>\n")

        file.write(
            "        <link rel=\"stylesheet\" "
            "href=\"styles.css\" media=\"screen\" />\n"
        )

        file.write(
            "        <title>"
            "College Football Weekly Lines"
            "</title>\n"
        )

        file.write(
            "        <meta charset=\"UTF-8\">\n"
        )

        file.write("    </head>\n")

        # --------------------------------------------------
        # Body
        # --------------------------------------------------

        file.write("    <body>\n")

        file.write(
            "        <h1>"
            "College Football Weekly Lines"
            "</h1>\n"
        )

        file.write("        <p>\n")

        file.write(
            "            Below you can find the "
            "weekly college football lines "
            "generated by the model. Games are "
            "ordered by the strength of the "
            "two teams.\n"
        )

        file.write("        </p>\n")

        # --------------------------------------------------
        # 2026 Weekly Lines
        # --------------------------------------------------

        file.write(
            f"        <h2>"
            f"{DB_YEAR} Weekly Lines"
            f"</h2>\n"
        )

        file.write("        <div>\n")

        week_count = DB_WEEK

        while week_count > 0:

            week_path = (
                f"{DB_YEAR}"
                f"week{week_count}"
                f"lines.html"
            )

            file.write(
                f"            <p>"
                f"<a href=\"{week_path}\">"
                f"Week {week_count} Lines"
                f"</a>"
                f"</p>\n"
            )

            week_count -= 1

        file.write("        </div>\n")

        # --------------------------------------------------
        # Back to Rankings
        # Same HTML structure as the rankings page
        # --------------------------------------------------

        file.write("        <p>\n")

        file.write(
            "            <a href=\"index.html\">"
            "Back to Rankings"
            "</a>\n"
        )

        file.write("        </p>\n")

        file.write("    </body>\n")
        file.write("</html>\n")

    print(
        f"Created lines index: "
        f"{index_path}"
    )


def main():
    create_lines()


if __name__ == "__main__":
    main()