"""
model db
"""
import sqlite3

conn = sqlite3.connect("testing.db")
cursor = conn.cursor()

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS leagues (
        league_id INTEGER PRIMARY KEY AUTOINCREMENT ,
        name TEXT NOT NULL,
        season TEXT NOT NULL,
        UNIQUE (name, season)
    )
    """
)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS teams (
        team_id INTEGER PRIMARY KEY AUTOINCREMENT ,
        name TEXT NOT NULL,
        league_id Integer NOT NULL,
        FOREIGN KEY (league_id) REFERENCES leagues(league_id),
        UNIQUE (name, league_id)
    )
    """
)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS fixtures (
        fixture_id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        match_status TEXT NOT NULL,
        home_team_id INTEGER NOT NULL,
        away_team_id INTEGER NOT NULL,
        FOREIGN KEY (home_team_id) REFERENCES teams(team_id),
        FOREIGN KEY (away_team_id) REFERENCES teams(team_id),
        CHECK (home_team_id != away_team_id),
        UNIQUE (date, time, home_team_id, away_team_id)
    )
    """
)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS results (
        result_id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        home_team_id INTEGER NOT NULL,
        away_team_id INTEGER NOT NULL,
        home_score INTEGER NOT NULL,
        away_score INTEGER NOT NULL,
        FOREIGN KEY (home_team_id) REFERENCES teams(team_id)
        FOREIGN KEY (away_team_id) REFERENCES teams(team_id)
        CHECK (home_team_id != away_team_id)
        UNIQUE (date, time, home_team_id, away_team_id)
    )
    """
)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS standings (
        standing_id INTEGER PRIMARY KEY AUTOINCREMENT,
        team_id INTEGER NOT NULL UNIQUE,
        MP INTEGER NOT NULL,
        W INTEGER NOT NULL,
        D INTEGER NOT NULL,
        L INTEGER NOT NULL,
        GF INTEGER NOT NULL,
        GA INTEGER NOT NULL,
        GD INTEGER NOT NULL,
        PTS INTEGER NOT NULL,
        FOREIGN KEY (team_id) REFERENCES teams(team_id)
    )
    """
)

conn.commit()
cursor.close()
conn.close()
