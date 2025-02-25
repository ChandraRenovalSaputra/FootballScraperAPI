'''Config'''
from pathlib import Path
from flask import Blueprint

DB_NAME = 'football.db'
FOLDER_PATH = Path('database')
DB_PATH = FOLDER_PATH / DB_NAME


API_BP = Blueprint("api", __name__, url_prefix="/api")

URLS = [
    'https://www.flashscore.com/football/england/premier-league/results/',
    'https://www.flashscore.com/football/france/ligue-1/results/',
    'https://www.flashscore.com/football/germany/bundesliga/results/',
    'https://www.flashscore.com/football/spain/laliga/results/',
    'https://www.flashscore.com/football/netherlands/eredivisie/results/',
    'https://www.flashscore.com/football/italy/serie-a/results/',
    'https://www.flashscore.com/football/england/premier-league/fixtures/',
    'https://www.flashscore.com/football/france/ligue-1/fixtures/',
    'https://www.flashscore.com/football/germany/bundesliga/fixtures/',
    'https://www.flashscore.com/football/spain/laliga/fixtures/',
    'https://www.flashscore.com/football/netherlands/eredivisie/fixtures/',
    'https://www.flashscore.com/football/italy/serie-a/fixtures/',
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/115.0.0.0'
}
