"""main app"""

from sqlite3 import Error
from json import dumps, JSONDecodeError
from flask import Flask, Response
from selenium.common.exceptions import WebDriverException
from scraper.scraper import FootballScraper
from cleaned_data.cleaner import Preprocessing
from database.service import DatabaseManager
from config import DB_PATH, API_BP

app = Flask(__name__)
scraper = FootballScraper()
db_manager = DatabaseManager()

@API_BP.route("/scrape-and-save", methods=["GET"])
def scrape_and_save():
    """scraping and save the data"""
    try:
        raw_data = scraper.start()

        clean_data = Preprocessing(raw_data)

        db_manager.insert_data(
            DB_PATH,
            clean_data.results,
            clean_data.fixtures,
            clean_data.standings
        )

        return dumps({"message": "Data scraped and saved successfully!"})

    except WebDriverException as e:
        return dumps({"error": str(e)}, indent=2), 500
    except Error as e:
        return dumps({"error": str(e)}, indent=2), 500
    except KeyboardInterrupt as e:
        return dumps({"error": str(e)}, indent=2), 500
    except JSONDecodeError as e:
        return dumps({"error": str(e)}, indent=2), 500

@API_BP.route("/<league_name>/teams", methods=["GET"])
def get_teams_data(league_name: str):
    """get teams data"""
    try:
        teams = [
            {"id": data[2], "name": data[1]} for data in db_manager.get_teams(league_name, DB_PATH)
        ]

        data = {
            "league": league_name,
            "teams": teams
        }

        response_data = dumps(data, indent=2)
    except Error as e:
        response_data = dumps({"error": str(e)}, indent=2)
    except JSONDecodeError as e:
        response_data = dumps({"error": str(e)}, indent=2)
    return Response(response_data, mimetype="application/json")

@API_BP.route("/<league_name>/results", methods=["GET"])
def get_results_data(league_name: str):
    """get results data"""
    try:
        results = []
        for data in db_manager.get_results(league_name, DB_PATH):
            record = {
                "id": data[0],
                "date": data[1],
                "time": data[2],
                "home": data[3],
                "away": data[4],
                "home_score": data[5],
                "away_score": data[6]
            }

            results.append(record)

        data = {
            "league": league_name,
            "results": results
        }

        response_data = dumps(data, indent=2)
    except Error as e:
        response_data = dumps({"error": str(e)})
    except JSONDecodeError as e:
        response_data = dumps({"error": str(e)})
    return Response(response_data, mimetype="application/json")

@API_BP.route("/<league_name>/fixtures", methods=["GET"])
def get_fixtures_data(league_name: str):
    """get fixtures data"""
    try:
        fixtures = []
        for data in db_manager.get_fixtures(league_name, DB_PATH):
            record = {
                "id": data[0],
                "date": data[1],
                "time": data[2],
                "match_status": data[3],
                "home": data[4],
                "away": data[5]
            }

            fixtures.append(record)

        data = {
            "league": league_name,
            "fixtures": fixtures
        }

        response_data = dumps(data, indent=2)
    except Error as e:
        response_data = dumps({"error": str(e)})
    except JSONDecodeError as e:
        response_data = dumps({"error": str(e)})
    return Response(response_data, mimetype="application/json")

@API_BP.route("/<league_name>/standings", methods=["GET"])
def get_standings_data(league_name: str):
    """get standings data"""
    try:
        standings = []
        position = 1
        for data in db_manager.get_standings(league_name, DB_PATH):
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

            standings.append(record)

        data = {
            "league": league_name,
            "standings": standings
        }

        response_data = dumps(data, indent=2)
    except Error as e:
        response_data = dumps({"error": str(e)})
    except JSONDecodeError as e:
        response_data = dumps({"error": str(e)})
    return Response(response_data, mimetype="application/json")

app.register_blueprint(API_BP)
