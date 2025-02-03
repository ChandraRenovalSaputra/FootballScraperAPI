'''cONFIG'''
DATABASE_NAME = 'scraped_data.db'

API_VERSION = 'api/v1'
API_HOST = '127.0.0.1'
API_PORT = 5000

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
