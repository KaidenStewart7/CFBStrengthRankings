import sqlite3
import os

# Current Year
DB_YEAR = 2025

# Base directory
base_dir = os.path.dirname(os.path.abspath(__file__))

# Model database
MODEL_DB_PATH = os.path.join(
    base_dir,
    "..",
    "db",
    "Model.db"
)

# Game results database
GAME_DB_PATH = os.path.join(
    base_dir,
    "..",
    "db",
    f"{DB_YEAR}_cfb_game_results.db"
)

# Analytics directory
ANALYTICS_DIR = os.path.join(
    base_dir,
    "..",
    "model_analytics"
)


def get_predictions():
    """
    Get every prediction that has been generated
    during the 2025 season.
    """

    connection = sqlite3.connect(MODEL_DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            Week,
            Home_Team,
            Away_Team,
            Neutral_Flag,
            Projected_Winner,
            Projected_Line
        FROM lines_2025
        ORDER BY Week
    """)

    predictions = cursor.fetchall()

    connection.close()

    return predictions


def get_actual_results():
    """
    Get every game result from the 2025 season.
    """

    connection = sqlite3.connect(GAME_DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            Week,
            Home_Team,
            Away_Team,
            Neutral_Flag,
            Home_Score,
            Away_Score
        FROM GAME
        ORDER BY Week
    """)

    results = cursor.fetchall()

    connection.close()

    return results


def create_analytics():

    predictions = get_predictions()
    actual_results = get_actual_results()

    # ---------------------------------------------------------
    # Create dictionary of actual games
    # ---------------------------------------------------------

    actual_games = {}

    for game in actual_results:

        week, home_team, away_team, neutral_flag, home_score, away_score = game

        # Game isn't complete yet
        if home_score is None or away_score is None:
            continue

        key = (week, home_team, away_team)

        actual_games[key] = {
            "home_score": home_score,
            "away_score": away_score
        }

    # ---------------------------------------------------------
    # Season statistics
    # ---------------------------------------------------------

    total_games = 0
    correct_winners = 0

    total_absolute_error = 0
    total_error = 0

    total_predicted_margin = 0
    total_actual_margin = 0

    # Statistics by week
    weekly_stats = {}

    # Game-by-game information
    game_results = []

    # ---------------------------------------------------------
    # Compare predictions to actual results
    # ---------------------------------------------------------

    for prediction in predictions:

        (
            week,
            home_team,
            away_team,
            neutral_flag,
            projected_winner,
            projected_line
        ) = prediction

        key = (week, home_team, away_team)

        # No completed result for this game
        if key not in actual_games:
            continue

        actual = actual_games[key]

        home_score = actual["home_score"]
        away_score = actual["away_score"]

        # -----------------------------------------------------
        # Determine actual winner
        # -----------------------------------------------------

        if home_score > away_score:
            actual_winner = home_team

        elif away_score > home_score:
            actual_winner = away_team

        else:
            actual_winner = "Tie"

        # -----------------------------------------------------
        # Actual point differential
        # From projected winner's perspective
        # -----------------------------------------------------

        home_margin = home_score - away_score

        if projected_winner == home_team:
            actual_margin = home_margin
        else:
            actual_margin = -home_margin

        # -----------------------------------------------------
        # Winner prediction
        # -----------------------------------------------------

        winner_correct = projected_winner == actual_winner

        if winner_correct:
            correct_winners += 1

        # -----------------------------------------------------
        # Prediction error
        # -----------------------------------------------------

        error = projected_line - actual_margin

        absolute_error = abs(error)

        total_absolute_error += absolute_error
        total_error += error

        total_predicted_margin += projected_line
        total_actual_margin += actual_margin

        total_games += 1

        # -----------------------------------------------------
        # Initialize weekly statistics
        # -----------------------------------------------------

        if week not in weekly_stats:

            weekly_stats[week] = {
                "games": 0,
                "correct": 0,
                "absolute_error": 0
            }

        weekly_stats[week]["games"] += 1

        if winner_correct:
            weekly_stats[week]["correct"] += 1

        weekly_stats[week]["absolute_error"] += absolute_error

        # -----------------------------------------------------
        # Store individual game result
        # -----------------------------------------------------

        game_results.append({
            "week": week,
            "home_team": home_team,
            "away_team": away_team,
            "projected_winner": projected_winner,
            "projected_line": projected_line,
            "actual_winner": actual_winner,
            "actual_margin": actual_margin,
            "winner_correct": winner_correct,
            "error": error,
            "absolute_error": absolute_error
        })

    # ---------------------------------------------------------
    # Calculate season statistics
    # ---------------------------------------------------------

    if total_games > 0:

        winner_percentage = (
            correct_winners / total_games
        ) * 100

        mean_absolute_error = (
            total_absolute_error / total_games
        )

        average_prediction_error = (
            total_error / total_games
        )

        average_predicted_margin = (
            total_predicted_margin / total_games
        )

        average_actual_margin = (
            total_actual_margin / total_games
        )

    else:

        winner_percentage = 0
        mean_absolute_error = 0
        average_prediction_error = 0
        average_predicted_margin = 0
        average_actual_margin = 0

    # ---------------------------------------------------------
    # Create analytics directory
    # ---------------------------------------------------------

    os.makedirs(ANALYTICS_DIR, exist_ok=True)

    output_path = os.path.join(
        ANALYTICS_DIR,
        f"{DB_YEAR}_season_analytics.txt"
    )

    # ---------------------------------------------------------
    # Write TXT file
    # ---------------------------------------------------------

    with open(output_path, "w") as file:

        file.write(
            f"{DB_YEAR} CFB MODEL SEASON ANALYTICS\n"
        )

        file.write("=" * 70 + "\n\n")

        # =====================================================
        # SEASON SUMMARY
        # =====================================================

        file.write("SEASON SUMMARY\n")
        file.write("-" * 70 + "\n")

        file.write(
            f"Games Evaluated:          {total_games}\n"
        )

        file.write(
            f"Correct Winner Picks:     {correct_winners}\n"
        )

        file.write(
            f"Incorrect Winner Picks:   "
            f"{total_games - correct_winners}\n"
        )

        file.write(
            f"Winner Prediction %:      "
            f"{winner_percentage:.2f}%\n"
        )

        file.write(
            f"Mean Absolute Error:      "
            f"{mean_absolute_error:.2f} points\n"
        )

        file.write(
            f"Average Prediction Error: "
            f"{average_prediction_error:+.2f} points\n"
        )

        file.write(
            f"Average Predicted Margin: "
            f"{average_predicted_margin:.2f} points\n"
        )

        file.write(
            f"Average Actual Margin:    "
            f"{average_actual_margin:.2f} points\n"
        )

        file.write("\n\n")

        # =====================================================
        # WEEKLY PERFORMANCE
        # =====================================================

        file.write("WEEKLY PERFORMANCE\n")
        file.write("-" * 70 + "\n")

        for week in sorted(weekly_stats):

            stats = weekly_stats[week]

            games = stats["games"]
            correct = stats["correct"]
            mae = stats["absolute_error"] / games

            percentage = (correct / games) * 100

            file.write(
                f"Week {week}: "
                f"{correct}/{games} correct "
                f"({percentage:.2f}%) | "
                f"MAE: {mae:.2f}\n"
            )

        file.write("\n\n")

        # =====================================================
        # GAME-BY-GAME RESULTS
        # =====================================================

        file.write("COMPLETED GAME RESULTS\n")
        file.write("=" * 70 + "\n\n")

        for result in game_results:

            file.write(
                f"Week {result['week']}: "
                f"{result['home_team']} vs "
                f"{result['away_team']}\n"
            )

            file.write(
                f"Projected Winner: "
                f"{result['projected_winner']}\n"
            )

            file.write(
                f"Projected Line: "
                f"{result['projected_line']:.1f}\n"
            )

            file.write(
                f"Actual Winner: "
                f"{result['actual_winner']}\n"
            )

            file.write(
                f"Actual Margin: "
                f"{result['actual_margin']:+.1f}\n"
            )

            if result["winner_correct"]:
                file.write(
                    "Winner Prediction: CORRECT\n"
                )
            else:
                file.write(
                    "Winner Prediction: INCORRECT\n"
                )

            file.write(
                f"Prediction Error: "
                f"{result['error']:+.1f}\n"
            )

            file.write(
                f"Absolute Error: "
                f"{result['absolute_error']:.1f}\n"
            )

            file.write("-" * 70 + "\n")

    print(
        f"Season analytics created: {output_path}"
    )


def main():
    create_analytics()


if __name__ == "__main__":
    main()