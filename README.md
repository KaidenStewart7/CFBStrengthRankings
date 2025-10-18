# CFB Strength Rankings

## Description
 - The goal of this project was to create a web page to provide college football power rankings each week. These are power rankings that take into account team performance, conference strength, and the talent of the team determined by their 247 Sports Talent Composite Ranking. Each week, new rankings will be added. Early in the season, the main factor weighting the strength ratings will be their talent rating; however, as the season progresses and more games are played, each team’s rankings will factor in their "resume rating" more than their talent rating. Eventually, after each team plays 12 games against FBS opponents, their strength rating will be comprised only of their resume rating. A team's resume rating factors in their performance as well as the strength of the conference they are in.
 - Additionally, you can find each teams record versus teams in each quadrant. This is based on the college basketball Quad Wins and Losses found on [NET Rankings and Quad Wins](https://bballnet.com). Here is the break down of quadrants I used that are proportional to the number of teams in each quadrant in college basketball:
   - Quad 1: Home (1-11), Neutral (1-19), Away(1-28)
   - Quad 2: Home (12-28), Neutral (20-37), Away(29-50)
   - Quad 3: Home (29-60), Neutral (38-75), Away(51-89)
   - Quad 4: Home (61-136), Neutral (76-136), Away(90-136)

 ## Methodology
 - Pulled data from the api created by [College Football Data API](https://api.collegefootballdata.com).
 - Designed and created database using SQLite to store data pulled from API and retrieve it later via SQL queries.
 - Used pandas dataframes to calculate and orginize the data needed to calculate the final strength ratings as well as find each teams quad wins and losses.
 - Created website by using HTML and CSS to display the weekly strength rankings.

 ## To Update Webpage
 - For each file make sure the year and week are updated at the top of each file.
 - First, run the load_games.py file to load the latest games into the database.
 - Then, run the calculate_strength_ratings.py file to calculate the strength ratings.
 - Finally, run the create_html.py to generate the html.
