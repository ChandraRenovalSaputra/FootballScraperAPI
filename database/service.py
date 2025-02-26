"""service db"""
import sqlite3
from sqlite3 import Error
import pandas as pd
from database.model import create_all_table

class DatabaseManager():
    """db manager"""

    def __init__(self):
        create_all_table()

    def __insert_leagues_data(
        self,
        cursor: sqlite3.Cursor,
        results: pd.DataFrame,
        fixtures: pd.DataFrame
    ) -> dict:
        """insert leagues data"""

        leagues = pd.concat(
            [results["league"], fixtures["league"]], ignore_index=True
        ).unique()

        season = pd.concat(
            [results["season"], fixtures["season"]], ignore_index=True
        ).unique()

        records = []
        for league in leagues:

            record = (league, season.item())

            records.append(record)

        cursor.executemany(
            "INSERT OR IGNORE INTO leagues (name, season) VALUES (?, ?)", records
        )

        query = f"SELECT league_id, name FROM leagues WHERE season = '{season.item()}'"
        cursor.execute(query)
        raw_data = cursor.fetchall()

        leagues_data = {}
        for data in raw_data:
            league = data[1]
            leagues_data[league] = data[0]

        return leagues_data


    def __insert_teams_data(
        self,
        cursor: sqlite3.Cursor,
        df: pd.DataFrame,
        leagues_data: dict,
    ) -> dict:
        """insert teams data"""
        records = []

        for row in df.itertuples():

            if row.league in leagues_data.keys():
                record = (row.team, leagues_data[row.league])
                records.append(record)

        cursor.executemany(
            "INSERT OR IGNORE INTO teams (name, league_id) VALUES (?, ?)", records
        )

        lower = next(iter(leagues_data.values()))
        upper = leagues_data.popitem()[1]

        query = f"SELECT team_id, name FROM teams WHERE league_id BETWEEN {lower} AND {upper}"

        cursor.execute(query)
        raw_data = cursor.fetchall()

        teams_data = {}
        for data in raw_data:
            team = data[1]
            team_id = data[0]
            teams_data[team] = team_id

        return teams_data


    def __insert_fixtures_data(
        self,
        cursor: sqlite3.Cursor,
        fixtures: pd.DataFrame,
        teams_data: dict
    ) -> None:
        """insert fixtures data"""
        records = []

        for row in fixtures.itertuples():
            if row.home in teams_data.keys() and row.away in teams_data.keys():
                record = (
                    row.date,
                    row.time,
                    row.match_status,
                    teams_data[row.home],
                    teams_data[row.away],
                )
                records.append(record)

        cursor.executemany(
            """INSERT OR IGNORE INTO fixtures (
                    date,
                    time,
                    match_status,
                    home_team_id,
                    away_team_id
                ) VALUES (
                    ?,
                    ?,
                    ?,
                    ?,
                    ?
                )
            """,
            records
        )

    def __insert_results_data(
        self,
        cursor: sqlite3.Cursor,
        results: pd.DataFrame,
        teams_data: dict
    ) -> None:
        """insert results data"""
        records = []
        results.sort_index(ascending=False, inplace=True)
        for row in results.itertuples():
            if row.home in teams_data.keys() and row.away in teams_data.keys():
                record = (
                    row.date,
                    row.time,
                    teams_data[row.home],
                    teams_data[row.away],
                    row.home_scores,
                    row.away_scores,
                )
                records.append(record)

        cursor.executemany(
            """
            INSERT OR IGNORE INTO results (
                date,
                time,
                home_team_id,
                away_team_id,
                home_score,
                away_score
            ) VALUES (
                ?,
                ?,
                ?,
                ?,
                ?,
                ?
            )
            """, records,
        )

    def __insert_standings_data(
        self,
        cursor: sqlite3.Cursor,
        standings: pd.DataFrame,
        teams_data: dict
    ) -> None:
        """insert standings data"""

        records = []
        for row in standings.itertuples():
            if row.team in teams_data.keys():
                record = (
                    teams_data[row.team],
                    row.MP,
                    row.W,
                    row.D,
                    row.L,
                    row.GF,
                    row.GA,
                    row.GD,
                    row.PTS,
                )

                records.append(record)

        cursor.executemany(
            """
            INSERT OR IGNORE INTO standings (
                team_id,
                MP,
                W,
                D,
                L,
                GF,
                GA,
                GD,
                PTS
            ) VALUES (
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?
            )
            """, records,
        )

    def insert_data(
        self,
        db: str,
        results: pd.DataFrame,
        fixtures: pd.DataFrame,
        standings: pd.DataFrame
    ) -> None:
        """insert all data"""
        try:
            conn = sqlite3.connect(db)
            cursor = conn.cursor()

            leagues_data = self.__insert_leagues_data(
                cursor,
                results.loc[:, ["league", "season"]],
                fixtures.loc[:, ["league", "season"]],
            )

            teams_data = self.__insert_teams_data(
                cursor, standings.loc[:, ["league", "team"]], leagues_data
            )

            self.__insert_fixtures_data(
                cursor,
                fixtures.loc[:, ["match_status", "home", "away", "date", "time"]],
                teams_data,
            )

            self.__insert_results_data(
                cursor,
                results.loc[
                    :, ["date", "time", "home", "away", "home_scores", "away_scores"]
                ],
                teams_data,
            )

            self.__insert_standings_data(
                cursor,
                standings.loc[:, ["team", "MP", "W", "D", "L", "GF", "GA", "GD", "PTS"]],
                teams_data,
            )

            conn.commit()

        except Error as e:
            print(f"SQLite Error occurred: {e}")
            print(f"{db} rollback!")
            conn.rollback()

        finally:
            cursor.close()
            conn.close()

    def get_teams(self, league_name: str, db: str):
        """get teams data by league"""
        conn = sqlite3.connect(db)
        query = """
            SELECT leagues.name, teams.name, teams.team_id
            FROM teams
            INNER JOIN leagues ON teams.league_id = leagues.league_id
            WHERE leagues.name = ?
        """
        data = conn.execute(query, (league_name.replace("-", " "),)).fetchall()
        conn.close()

        return data

    def get_results(self, league_name: str, db: str):
        """get results data by league"""
        conn = sqlite3.connect(db)
        query = """
            SELECT
                results.result_id,
                results.date, 
                results.time, 
                home.name,
                away.name, 
                results.home_score, 
                results.away_score
            FROM results
            INNER JOIN teams AS home ON results.home_team_id = home.team_id
            INNER JOIN teams AS away ON results.away_team_id = away.team_id
            INNER JOIN leagues ON home.league_id = leagues.league_id
            WHERE leagues.name = ?
        """
        data = conn.execute(query, (league_name.replace("-", " "),)).fetchall()
        conn.close()

        return data

    def get_fixtures(self, league_name: str, db: str):
        """get fixtures data by league"""
        conn = sqlite3.connect(db)
        query = """
            SELECT
                fixtures.fixture_id,
                fixtures.date,
                fixtures.time,
                fixtures.match_status,
                home.name,
                away.name
            FROM fixtures
            INNER JOIN teams AS home ON fixtures.home_team_id = home.team_id
            INNER JOIN teams AS away ON fixtures.away_team_id = away.team_id
            INNER JOIN leagues ON home.league_id = leagues.league_id
            WHERE leagues.name = ?
        """
        data = conn.execute(query, (league_name.replace("-", " "),)).fetchall()
        conn.close()

        return data

    def get_standings(self, league_name: str, db: str):
        """get standiings data by league"""
        conn = sqlite3.connect(db)
        query = """
            SELECT
                standings.standing_id,
                teams.name,
                standings.MP,
                standings.W,
                standings.D,
                standings.L,
                standings.GF,
                standings.GA,
                standings.GD,
                standings.PTS
            FROM standings
            INNER JOIN teams ON standings.team_id = teams.team_id
            INNER JOIN leagues ON teams.league_id = leagues.league_id
            WHERE leagues.name = ?
            ORDER BY standings.PTS DESC, standings.GD DESC, standings.GF DESC
        """
        data = conn.execute(query, (league_name.replace("-", " "),)).fetchall()
        conn.close()

        return data
