"""main app"""

import sqlite3
from json import dumps
from flask import Flask, Response
from selenium.common.exceptions import WebDriverException
from scraper.scraper import FootballScraper
from cleaned_data.cleaner import Preprocessing
from database.service import DatabaseManager
from config import DB_PATH, API_BP

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

@API_BP.route("/scrape-and-save", methods=["GET"])
def scrape_and_save():
    """scraping and save the data"""

    try:
        scraper = FootballScraper()
        raw_data = scraper.start()

        clean_data = Preprocessing(raw_data)

        db_manager = DatabaseManager()
        db_manager.insert_data(
            DB_PATH,
            clean_data.results,
            clean_data.fixtures,
            clean_data.standings
        )

        return dumps({"message": "Data scraped and saved successfully!"})

    except WebDriverException as e:
        return dumps({"error": str(e)}, indent=2), 500

    except sqlite3.Error as e:
        return dumps({"error": str(e)}, indent=2), 500
    except KeyboardInterrupt as e:
        return dumps({"error": "Process stopped by user."}, indent=2), 500

@API_BP.route("/<league_name>/teams", methods=["GET"])
def get_teams_data(league_name: str):
    """get teams data"""
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT leagues.name, teams.name, teams.team_id
        FROM teams
        INNER JOIN leagues ON teams.league_id = leagues.league_id
        WHERE leagues.name = ?
    """
    raw_data = conn.execute(query, (league_name.replace("-", " "),))

    format_data = [{"id": data[2], "name": data[1]} for data in raw_data]

    conn.close()
    json_data = dumps(format_data, indent=2)
    return Response(json_data, mimetype="application/json")

@API_BP.route("/<league_name>/results", methods=["GET"])
def get_results_data(league_name: str):
    """get results data"""
    conn = sqlite3.connect(DB_PATH)
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
    raw_data = conn.execute(query, (league_name.replace("-", " "),))

    format_data = []
    for data in raw_data:
        record = {
            "id": data[0],
            "date": data[1],
            "time": data[2],
            "home": data[3],
            "away": data[4],
            "home_score": data[5],
            "away_score": data[6]
        }

        format_data.append(record)

    conn.close()
    json_data = dumps(format_data, indent=2)
    return Response(json_data, mimetype="application/json")

@API_BP.route("/<league_name>/fixtures", methods=["GET"])
def get_fixtures_data(league_name: str):
    """get fixtures data"""
    conn = sqlite3.connect(DB_PATH)
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
    raw_data = conn.execute(query, (league_name.replace("-", " "),))

    format_data = []
    for data in raw_data:
        record = {
            "id": data[0],
            "date": data[1],
            "time": data[2],
            "match_status": data[3],
            "home": data[4],
            "away": data[5]
        }

        format_data.append(record)

    conn.close()
    json_data = dumps(format_data, indent=2)
    return Response(json_data, mimetype="application/json")

@API_BP.route("/<league_name>/standings", methods=["GET"])
def get_standings_data(league_name: str):
    """get standings data"""
    conn = sqlite3.connect(DB_PATH)
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
    raw_data = conn.execute(query, (league_name.replace("-", " "),))

    format_data = []
    position = 1
    for data in raw_data:
        record = {
            "id": data[0],
            "team": data[1],
            "match_played": data[2],
            "won": data[3],
            "drawn": data[4],
            "loses": data[5],
            "goals_for": data[6],
            "goals_against": data[7],
            "goals_difference": data[8],
            "points": data[9],
            "position": position
        }

        position += 1

        format_data.append(record)

    conn.close()
    json_data = dumps(format_data, indent=2)
    return Response(json_data, mimetype="application/json")

app.register_blueprint(API_BP)
