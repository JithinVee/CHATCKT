import os
import traceback
import mysql.connector
from mysql.connector import Error
import json
import re


# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '12345678',
    'database': 'crickshopalyst'
}
team_id_map = {} 
player_id_map = {}

def create_connection():
    """Establish a database connection."""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print("Successfully connected to the database.")
        return connection
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None


def insert_team(cursor, team_name, team_type):
    # Update the query to include the team_type column
    query = "INSERT INTO teams (team_name, team_type) VALUES (%s, %s)"

    cursor.execute(query, (team_name, team_type))

    return cursor.lastrowid


def insert_player(cursor, player_name, gender):
    query = """
        INSERT INTO players (player_name, gender)
        VALUES (%s,%s)
    """
    cursor.execute(query, (player_name, gender))
    return cursor.lastrowid


def insert_match(cursor, match_data):
    expected_keys = [
        'match_id', 'date', 'venue', 'match_type', 'gender', 'city', 'match_status',
        'season', 'tournament_name', 'match_number', 'player_of_the_match', 'toss_won',
        'decision', 'team_1', 'team_2', 'first_bat', 'second_bat', 'winner', 'balls_per_over', 'draw'
    ]

    # Check if all keys are present
    missing_keys = [key for key in expected_keys if key not in match_data]
    if missing_keys:
        print(f"Missing keys in match_data: {missing_keys}")
        return  # Exit function if any keys are missing

    # Proceed with the insert if all keys are present
    query = """
        INSERT INTO matches (match_id, date, venue, match_type, gender, city, match_status,
                             season, tournament_name, match_number, player_of_the_match,
                             toss_won, decision, team_1, team_2, first_bat, second_bat,
                             winner, balls_per_over, draw)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        match_data['match_id'], match_data['date'], match_data['venue'], match_data['match_type'],
        match_data['gender'], match_data['city'], match_data['match_status'], match_data['season'],
        match_data['tournament_name'], match_data['match_number'], match_data['player_of_the_match'],
        match_data['toss_won'], match_data['decision'], match_data['team_1'], match_data['team_2'],
        match_data['first_bat'], match_data['second_bat'], match_data['winner'],
        match_data['balls_per_over'], match_data['draw']
    )

    cursor.execute(query, values)


def insert_player_team_history(cursor, player_id, team_id, match_id, team_type):
    # Prepare the SQL query to insert into the player_team_history table
    query = """
    INSERT INTO player_team_history (player_id, team_id, match_id, team_type)
    VALUES (%s, %s, %s, %s)
    """

    # Execute the query with the provided data
    cursor.execute(query, (player_id, team_id, match_id, team_type))




def insert_official(cursor, match_id, official_name, role):
    # Prepare the SQL query to insert into the officials table
    query = """
    INSERT INTO officials (match_id, official_name, role)
    VALUES (%s, %s, %s)
    """
    cursor.execute(query, (match_id, official_name, role))

def insert_officials_from_data(cursor, match_id, officials_data):
    """
    Insert match officials (referees, reserve umpires, umpires) into the officials table.

    Parameters:
    - cursor: Database cursor object
    - match_id: ID of the match in which the officials participated
    - officials_data: Dictionary containing 'match_referees', 'reserve_umpires', and 'umpires'
    """
    # Extract the official roles from the dictionary
    match_referees = officials_data.get('match_referees', [])
    reserve_umpires = officials_data.get('reserve_umpires', [])
    umpires = officials_data.get('umpires', [])

    # Insert referees
    for official_name in match_referees:
        insert_official(cursor, match_id, official_name, "Referee")

    # Insert reserve umpires
    for official_name in reserve_umpires:
        insert_official(cursor, match_id, official_name, "Reserve Umpire")

    # Insert umpires
    for official_name in umpires:
        insert_official(cursor, match_id, official_name, "Umpire")


# Function to insert player statistics into the player_statistics table
def insert_player_statistics(cursor, match_id, player_id, innings_id, runs, balls_faced, wickets, fours, sixes, maiden_overs):
    try:
        cursor.execute("""
            INSERT INTO player_statistics (match_id, player_id, innings_id, runs, balls_faced, wickets, fours, sixes, maiden_overs)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (match_id, player_id, innings_id, runs, balls_faced, wickets, fours, sixes, maiden_overs))
    except Error as e:
        print(f"Error inserting player statistics: {e}")



def insert_innings_and_deliveries(cursor, innings_data, match_id):
    """
    Inserts innings, deliveries, and player statistics data into the MySQL database.

    :param innings_data: A list of innings data containing overs and deliveries details.
    :param match_id: The match ID to associate the innings with.
    """
    innings_ids = []

    # Insert innings data and retrieve the innings_id
    innings_counter = 1
    for innings in innings_data:
        team_id = team_id_map.get(innings.get('team'))
        innings_id =int(f"{innings_counter}{match_id}")
        innings_counter +=1
        # Aggregate innings statistics before inserting into the database
        total_runs = 0
        total_wickets = 0
        total_overs = 0.0
        total_extras = 0
        player_stats = {}  # Dictionary to accumulate player statistics per player
        delivery_data = []  # List to hold deliveries data to insert into the deliveries table

        # Iterate over each over and its deliveries to calculate totals and prepare delivery data
        for over in innings['overs']:
            total_overs += 1
            ball_count = 0
            for delivery in over['deliveries']:
                ball_count+=1
                runs_batsman = delivery['runs']['batter']
                total_runs += runs_batsman
                total_extras += delivery['runs']['extras']

                # Accumulate player statistics (for batter)
                batter_id = player_id_map.get(delivery['batter'])
                if batter_id not in player_stats:
                    player_stats[batter_id] = {
                        'runs': 0,
                        'balls_faced': 0,
                        'wickets': 0,
                        'fours': 0,
                        'sixes': 0,
                        'maiden_overs': 0
                    }
                player_stats[batter_id]['runs'] += runs_batsman
                player_stats[batter_id]['balls_faced'] += 1

                # Count fours, sixes
                if runs_batsman == 4:
                    player_stats[batter_id]['fours'] += 1
                elif runs_batsman == 6:
                    player_stats[batter_id]['sixes'] += 1

                # Count wickets (for bowler)
                if 'wickets' in delivery:
                    total_wickets += len(delivery['wickets'])  # Count number of wickets in the delivery
                    for wicket in delivery['wickets']:
                        bowler_id = player_id_map.get(delivery['bowler'])
                        if bowler_id not in player_stats:
                            player_stats[bowler_id] = {
                                'runs': 0,
                                'balls_faced': 0,
                                'wickets': 0,
                                'fours': 0,
                                'sixes': 0,
                                'maiden_overs': 0
                            }
                        player_stats[bowler_id]['wickets'] += 1
                        player_stats[bowler_id]['balls_faced'] += 1  # Each delivery is a ball faced for the bowler

                # Count maiden overs for bowler
                if runs_batsman == 0 and 'bowler' in delivery:
                    bowler_id = player_id_map.get(delivery['bowler'])
                    if player_stats.get('bowler_id'):
                        player_stats[bowler_id]['maiden_overs'] += 1
                    else:
                        player_stats[bowler_id] = {
                            'runs': 0,
                            'balls_faced': 0,
                            'wickets': 0,
                            'fours': 0,
                            'sixes': 0,
                            'maiden_overs': 1
                        }

                # Prepare data for insertion into the deliveries table
                bowler_id = player_id_map.get(delivery['bowler'])
                non_striker_id = player_id_map.get(delivery['non_striker'])  # Non-striker player ID (if needed)


                extras_type = None  # Default to NULL if there are no extras
                if 'extras' in delivery:
                    if 'legbyes' in delivery['extras'] and delivery['extras']['legbyes'] > 0:
                        extras_type = 'leg-bye'
                    elif 'wides' in delivery['extras'] and delivery['extras']['wides'] > 0:
                        extras_type = 'wide'
                    elif 'noballs' in delivery['extras'] and delivery['extras']['noballs'] > 0:
                        extras_type = 'no-ball'
                    elif 'byes' in delivery['extras'] and delivery['extras']['byes'] > 0:
                        extras_type = 'bye'

                wicket_type = None  # Default to NULL if there is no dismissal or invalid type
                dismissed_player_id = None

                if 'wickets' in delivery:
                    for wicket in delivery['wickets']:
                        wicket_type = wicket.get('kind', None)

                        # Validate wicket_type against ENUM values
                        valid_wicket_types = {'bowled', 'caught', 'run-out', 'lbw', 'stumped', 'hit-wicket'}
                        if wicket_type not in valid_wicket_types:
                            wicket_type = None  # Default to NULL if invalid

                        # Get the dismissed player's ID
                        dismissed_player_id = player_id_map.get(wicket.get('player_out'), None)

                delivery_data.append((
                    innings_id, over['over'], ball_count, batter_id, bowler_id,
                    runs_batsman, delivery['runs']['extras'], delivery['runs']['total'], extras_type, wicket_type, dismissed_player_id
                ))

        # Insert the aggregated innings data into the `innings` table
        cursor.execute("""
            INSERT INTO innings (innings_id,match_id, team_id, total_runs, total_wickets, total_overs, extras)
            VALUES (%s,%s, %s, %s, %s, %s, %s)
        """, (innings_id,match_id, team_id, total_runs, total_wickets, total_overs, total_extras))

        # Get the last inserted innings_id
        # innings_ids.append(cursor.lastrowid)

        # Insert player statistics (batter and bowler statistics)
        for player_id, stats in player_stats.items():
            runs = stats['runs']
            balls_faced = stats['balls_faced']
            wickets = stats['wickets']
            fours = stats['fours']
            sixes = stats['sixes']
            maiden_overs = stats['maiden_overs']

            # Insert player statistics for the aggregated innings
            insert_player_statistics(cursor, match_id, player_id, innings_id, runs, balls_faced, wickets, fours, sixes, maiden_overs)

        # Insert all deliveries data into the `deliveries` table at once
        for delivery in delivery_data:
            cursor.execute("""
                INSERT INTO deliveries (innings_id, over_number, ball_number, batsman_id, bowler_id, runs_batsman,
                                        runs_extras, runs_total, extras_type, wicket_type, dismissed_player_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, delivery)

    print("Innings, Deliveries, and Player Statistics data inserted successfully.")



def load_json_files(directory):
    global team_id_map
    global player_id_map
    """Processes and inserts data from JSON files into the database."""
    connection = create_connection()
    if not connection:
        return
    team_id_map = {}

    player_id_map = {}

    cursor = connection.cursor()
    try:
        for filename in os.listdir(directory):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(directory, filename), 'r') as f:
                        data = json.load(f)
                    match_info = data["info"]


                    # Extract match-related details
                    match_data = extract_match_data(match_info, filename)

                    match_id = match_data['match_id']
                    try:
                        match_data['match_id'] = int(match_id)
                    except:
                        match_id = re.search(r'\d+', match_id).group()
                        match_data['match_id'] = match_id


                    team1 = match_data['team_1']
                    team2 = match_data['team_2']

                    gender = match_data.get('gender')
                    team_type = match_data.get('team_type')

                    if team_id_map.get(team1):
                        team1_id = team_id_map[team1]
                    else:
                        team1_id = insert_team(cursor,team1,team_type)
                        team_id_map[team1] = team1_id
                    if team_id_map.get(team2):
                        team2_id = team_id_map[team2]
                    else:
                        team2_id = insert_team(cursor,team2,team_type)
                        team_id_map[team2] = team2_id

                    if match_data.get('team_1'):
                        match_data['team_1'] = int(team1_id)
                    if match_data.get('team_2'):
                        match_data['team_2'] = int(team2_id)

                    if match_data.get('first_bat'):
                        match_data['first_bat'] = team_id_map.get(match_data['first_bat'])
                    if match_data.get('second_bat'):
                        match_data['second_bat'] = team_id_map.get(match_data['second_bat'])
                    if match_data.get('winner'):
                        match_data['winner'] = team_id_map.get(match_data['winner'],0)

                    if match_data.get('toss_won'):
                        match_data['toss_won'] = team_id_map.get(match_data['toss_won'],0)



                    # players loading
                    players = match_info.get('players')
                    if players:
                        for team_name, team_players in players.items():
                            team_id = team_id_map[team_name]
                            for player_name in team_players:
                                if not player_id_map.get(player_name):
                                    player_id = insert_player(cursor, player_name, gender)
                                    player_id_map[player_name] = player_id


                    # player of the match mapping to index
                    player_of_the_match = match_data.get('player_of_the_match')
                    if player_of_the_match:
                        player_id = player_id_map.get(player_of_the_match,None)
                    else:
                        player_id = None
                    match_data['player_of_the_match'] = player_id



                    insert_match(cursor, match_data)

                    if match_info.get('officials'):
                        officials = match_info.get("officials")
                        insert_officials_from_data(cursor,match_id,officials)



                    # player history adding
                    if players:
                        for team_name, team_players in players.items():
                            team_id = team_id_map[team_name]
                            for player_name in team_players:
                                player_id = player_id_map.get(player_name)
                                insert_player_team_history(cursor, player_id, team_id, match_id, gender)

                    # Insert players


                    insert_innings_and_deliveries(cursor,innings_data=data['innings'],match_id=match_id)

                    connection.commit()
                except Exception as e:
                    print(f"Error processing file {filename}: {e}")
                    traceback.print_exc()
                    connection.rollback()

    except Exception as e:
        print(f"Error while processing JSON files: {e}")
    finally:
        cursor.close()
        connection.close()




def extract_match_data(match_info, filename):
    """Extracts and formats match data from JSON."""
    teams = match_info["teams"]
    toss_info = match_info["toss"]

    # Determine first and second batting teams
    toss_winner = toss_info.get('winner', 'missing')
    decision = toss_info.get("decision")
    first_bat = toss_winner if decision == "bat" else (teams[0] if teams[1] == toss_winner else teams[1])
    second_bat = teams[0] if teams[0] != first_bat else teams[1]

    # Extract outcome details
    outcome = match_info.get("outcome", {})
    winner = outcome.get("winner")
    draw = outcome.get("status", "") == "draw"

    # Extract other details

    return {
        'match_id': filename.replace('.json', ''),
        'date': match_info['dates'][0],
        'venue': match_info.get("venue", "Unknown"),
        'match_type': match_info.get("match_type", "Unknown"),
        'gender': match_info.get("gender", "Unknown"),
        'city': match_info.get("city", "Unknown"),
        'match_status': outcome.get("status", "completed"),
        'season': match_info.get("season", "Unknown"),
        'tournament_name': match_info.get("event", {}).get("name", "Unknown"),
        'match_number': match_info.get("event", {}).get("match_number", None),
        'player_of_the_match': match_info.get("player_of_match", [""])[0],
        'toss_won': toss_winner,
        'decision': decision,
        'team_1': teams[0],
        'team_2': teams[1],
        'first_bat': first_bat,
        'second_bat': second_bat,
        'winner': winner,
        'file_name': filename,
        'team_type': match_info.get("team_type", "Unknown"),
        'won_by_runs': outcome.get("by", {}).get("runs", 0),
        'won_by_wickets': outcome.get("by", {}).get("wickets", 0),
        'total_dates': len(match_info.get('dates', [])),
        'balls_per_over': match_info.get("balls_per_over", 6),
        'draw': draw
    }


if __name__ == "__main__":
    json_directory = '/Users/sajid.hassan/Downloads/all_json/'
    load_json_files(json_directory)
