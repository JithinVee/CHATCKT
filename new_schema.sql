




CREATE DATABASE crickshopalyst;
USE crickshopalyst;


-- Table to store teams
CREATE TABLE teams (
    team_id INT AUTO_INCREMENT PRIMARY KEY,       -- Unique ID for each team
    team_name VARCHAR(255) NOT NULL UNIQUE,        -- Unique name of the team
    team_type VARCHAR(50)                         -- Type of team (e.g., Home, Away)
);

-- Table to store players
CREATE TABLE players (
    player_id INT AUTO_INCREMENT PRIMARY KEY,     -- Unique ID for each player
    player_name VARCHAR(255) NOT NULL,            -- Name of the player
    gender VARCHAR(20)                            -- Gender of the player (male/female)
);

-- Table to store match information
CREATE TABLE matches (
    match_id INT PRIMARY KEY,                     -- Unique match ID
    date DATE NOT NULL,                            -- Match date
    venue VARCHAR(255),                            -- Match venue
    match_type VARCHAR(50),                       -- Match type (e.g., ODI, Test, T20)
    gender VARCHAR(20),                           -- Gender (male/female)
    city VARCHAR(100),                            -- City of the match
    match_status VARCHAR(50),                     -- Status (e.g., ongoing, completed)
    season VARCHAR(100),                          -- Season (e.g., year, tournament)
    tournament_name VARCHAR(255),                 -- Tournament name
    match_number INT,                             -- Match number in the tournament
    player_of_the_match INT,                      -- Foreign key referencing players
    toss_won INT,                                 -- Foreign key referencing teams
    decision ENUM('bat', 'field') NOT NULL,       -- Toss decision
    team_1 INT,                                   -- Foreign key referencing teams
    team_2 INT,                                   -- Foreign key referencing teams
    first_bat INT,                                -- Foreign key referencing teams (batting first)
    second_bat INT,                               -- Foreign key referencing teams (batting second)
    winner INT,                                   -- Foreign key referencing teams
    balls_per_over INT DEFAULT 6,                 -- Number of balls per over
    draw BOOLEAN DEFAULT FALSE,                   -- Whether the match ended in a draw
    FOREIGN KEY (player_of_the_match) REFERENCES players(player_id) ON DELETE SET NULL,
    FOREIGN KEY (toss_won) REFERENCES teams(team_id) ON DELETE SET NULL,
    FOREIGN KEY (team_1) REFERENCES teams(team_id) ON DELETE SET NULL,
    FOREIGN KEY (team_2) REFERENCES teams(team_id) ON DELETE SET NULL,
    FOREIGN KEY (first_bat) REFERENCES teams(team_id) ON DELETE SET NULL,
    FOREIGN KEY (second_bat) REFERENCES teams(team_id) ON DELETE SET NULL,
    FOREIGN KEY (winner) REFERENCES teams(team_id) ON DELETE SET NULL
);

-- Table to store match officials (umpires, referees)
CREATE TABLE officials (
    official_id INT AUTO_INCREMENT PRIMARY KEY,   -- Unique ID for each official
    match_id INT NOT NULL,                        -- Foreign key referencing matches
    official_name VARCHAR(255) NOT NULL,          -- Name of the umpire or official
    role VARCHAR(50) NOT NULL,                    -- Role of the official (e.g., umpire, referee)
    FOREIGN KEY (match_id) REFERENCES matches(match_id) ON DELETE CASCADE
);

-- Table to store innings details
CREATE TABLE innings (
    innings_id INT PRIMARY KEY,   				  -- Unique ID for the innings
    match_id INT NOT NULL,                        -- Foreign key referencing matches
    team_id INT NOT NULL,                         -- Foreign key referencing teams
    total_runs INT DEFAULT 0,                     -- Total runs scored in the innings
    total_wickets INT DEFAULT 0,                  -- Total wickets fallen in the innings
    total_overs DECIMAL(5,2) DEFAULT 0,           -- Total overs played (e.g., 19.5)
    extras INT DEFAULT 0,                         -- Extras scored in the innings
    FOREIGN KEY (match_id) REFERENCES matches(match_id) ON DELETE CASCADE,
    FOREIGN KEY (team_id) REFERENCES teams(team_id) ON DELETE CASCADE
);


-- Table to store player statistics for each match
CREATE TABLE player_statistics (
    stat_id INT AUTO_INCREMENT PRIMARY KEY,       -- Unique ID for each stat record
    match_id INT NOT NULL,                        -- Foreign key referencing matches
    player_id INT NOT NULL,                       -- Foreign key referencing players
    innings_id INT NOT NULL,                      -- Foreign key referencing innings
    runs INT DEFAULT 0,                           -- Runs scored by the player
    balls_faced INT DEFAULT 0,                    -- Balls faced by the player
    wickets INT DEFAULT 0,                        -- Wickets taken by the player
    fours INT DEFAULT 0,                          -- Number of boundaries (4s)
    sixes INT DEFAULT 0,                          -- Number of sixes
    maiden_overs INT DEFAULT 0,                   -- Maiden overs bowled
    FOREIGN KEY (match_id) REFERENCES matches(match_id) ON DELETE CASCADE,
    FOREIGN KEY (player_id) REFERENCES players(player_id) ON DELETE CASCADE,
    FOREIGN KEY (innings_id) REFERENCES innings(innings_id) ON DELETE CASCADE
);






-- Table to store delivery (ball-by-ball) information
CREATE TABLE deliveries (
    delivery_id INT AUTO_INCREMENT PRIMARY KEY,   -- Unique ID for each delivery
    innings_id INT NOT NULL,                      -- Foreign key referencing innings
    over_number INT NOT NULL,                     -- Over number
    ball_number INT NOT NULL,                     -- Ball number within the over
    batsman_id INT NOT NULL,                      -- Foreign key referencing players (batsman)
    bowler_id INT NOT NULL,                       -- Foreign key referencing players (bowler)
    runs_batsman INT DEFAULT 0,                   -- Runs scored by the batsman
    runs_extras INT DEFAULT 0,                    -- Extras scored on this ball
    runs_total INT DEFAULT 0,                     -- Total runs for the delivery
    extras_type ENUM('no-ball', 'wide', 'bye', 'leg-bye') DEFAULT NULL, -- Type of extras
    wicket_type ENUM('bowled', 'caught', 'run-out', 'lbw', 'stumped', 'hit-wicket') DEFAULT NULL, -- Type of dismissal
    dismissed_player_id INT,                      -- Player dismissed on this ball (if any)
    FOREIGN KEY (innings_id) REFERENCES innings(innings_id) ON DELETE CASCADE,
    FOREIGN KEY (batsman_id) REFERENCES players(player_id) ON DELETE CASCADE,
    FOREIGN KEY (bowler_id) REFERENCES players(player_id) ON DELETE CASCADE,
    FOREIGN KEY (dismissed_player_id) REFERENCES players(player_id) ON DELETE CASCADE
);

-- Table to store player-team history based on match participation
CREATE TABLE player_team_history (
    player_id INT NOT NULL,        -- Foreign key referencing players
    team_id INT NOT NULL,          -- Foreign key referencing teams
    match_id INT NOT NULL,         -- Foreign key referencing matches (match the player played in)
    team_type VARCHAR(50),         -- Team type for this match (e.g., Home, Away)
    PRIMARY KEY (player_id, team_id, match_id),   -- Composite primary key
    FOREIGN KEY (player_id) REFERENCES players(player_id) ON DELETE CASCADE,
    FOREIGN KEY (team_id) REFERENCES teams(team_id) ON DELETE CASCADE,
    FOREIGN KEY (match_id) REFERENCES matches(match_id) ON DELETE CASCADE
);
