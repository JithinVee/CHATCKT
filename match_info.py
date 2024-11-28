import os
import traceback
import mysql.connector
from mysql.connector import Error
import json

def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='12345678',
            database='cricket'
        )
        if connection.is_connected():
            print("Successfully connected to the database.")
        return connection
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None

def load_json_files(directory):
    connection = connect_to_database()
    if connection:
        cursor = connection.cursor()
        try:
            for filename in os.listdir(directory):
                if filename.endswith(".json"):
                    try:
                        with open(os.path.join(directory, filename), 'r') as f:
                            data = json.load(f)
                        match_info = data["info"]

                        # Extract the necessary details from the match_info
                        teams = match_info["teams"]
                        team_type = match_info["team_type"]
                        gender = match_info["gender"]
                        season = match_info["season"]
                        match_type = match_info["match_type"]
                        toss_info = match_info["toss"]
                        officials = match_info["officials"]
                        player_of_the_match = match_info.get("player_of_match", [""])[0]
                        filename = filename  # File name
                        try:
                            winner = match_info.get("outcome")["winner"]
                            draw = False  # Not a draw if there's a winner
                        except Exception as e:
                            winner = None
                            draw = True  # If no winner, it's a draw
                        team_1 = teams[0]  # Team 1
                        team_2 = teams[1]  # Team 2
                        toss_winner = toss_info.get('winner', 'unknown')
                        decision = toss_info.get("decision")
                        if toss_info.get("decision") == "bat":
                            first_bat = toss_winner
                        else:
                            first_bat = teams[0] if teams[1] == toss_winner else teams[1]
                        second_bat = teams[0] if teams[0] != first_bat else teams[1]
                        total_dates = len(match_info['dates'])
                        balls_per_over = match_info["balls_per_over"]
                        won_by_runs = 0
                        won_by_wickets = 0
                        try:
                            won_by_runs = match_info.get("outcome")["by"]["runs"]
                        except Exception as e:
                            try:
                                won_by_wickets = match_info.get("outcome")["by"]["wickets"]
                            except:
                                traceback.format_exc()
                        city = match_info["city"]
                        venue = match_info["venue"]
                        tournament_name = match_info.get("event", {}).get("name")
                        match_number = match_info.get("event", {}).get("match_number")

                        # Insert match data
                        match_id = insert_match(cursor, match_info, gender, season, winner, draw, team_1, team_2, first_bat, second_bat, toss_winner, decision, total_dates, balls_per_over, won_by_runs, won_by_wickets, city, venue, filename, team_type, tournament_name, match_number, match_type, player_of_the_match)

                        # Insert officials data
                        insert_officials(cursor, match_id, officials)

                        # Insert players data
                        insert_players(cursor, match_id, teams, match_info["players"])

                        connection.commit()

                    except Exception as e:
                        print(f"Error processing file {filename}: {e}")
                        connection.rollback()

        except Exception as e:
            print(f"Error while processing JSON files: {e}")
        finally:
            cursor.close()
            connection.close()

def insert_match(cursor, match_info, gender, season, winner, draw, team_1, team_2, first_bat, second_bat, toss_winner, decision, total_dates, balls_per_over, won_by_runs, won_by_wickets, city, venue, filename, team_type, tournament_name, match_number, match_type, player_of_the_match):
    cursor.execute(
        """INSERT INTO matches 
           (date, venue, match_type, gender, city, match_status, season, tournament_name, match_number, player_of_the_match, toss_won, decision, team_1, team_2, first_bat, second_bat, winner, draw, file_name, team_type, won_by_runs, won_by_wickets, total_dates, balls_per_over)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (
            match_info['dates'][0],
            venue,
            match_type,
            gender,
            city,
            match_info.get("outcome", {}).get("status", "completed"),
            season,
            tournament_name,
            match_number,
            player_of_the_match,
            toss_winner,
            decision,
            team_1,
            team_2,
            first_bat,
            second_bat,
            winner,
            draw,
            filename,
            team_type,
            won_by_runs,
            won_by_wickets,
            total_dates,
            balls_per_over
        )
    )
    match_id = cursor.lastrowid  # Get the last inserted match_id
    return match_id

def insert_officials(cursor, match_id, officials):
    for role, names in officials.items():
        for name in names:
            cursor.execute(
                "INSERT INTO officials (match_id, umpire_name, role) VALUES (%s, %s, %s)",
                (match_id, name, role[:-1])  # Removing plural suffix ('umpires' -> 'umpire')
            )

def insert_players(cursor, match_id, teams, players_data):
    for team in teams:
        players = players_data.get(team, [])
        for player in players:
            cursor.execute(
                "INSERT INTO players (match_id, team_name, player_name, played) VALUES (%s, %s, %s, %s)",
                (match_id, team, player, True)  # Assuming the player played in the match
            )

if __name__ == "__main__":
    json_directory = '/Users/aswin/Downloads/all_json_new/'
    load_json_files(json_directory)
