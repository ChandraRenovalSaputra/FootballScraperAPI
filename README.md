# ⚽ FootballScraperAPI 

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://python.org)

A powerful API to scrape real-time football data from trusted sources. Built for developers who need live match stats, fixtures, standings, and team details across top leagues.

---

## 🌟 Features

- **Simple Endpoints** - Intuitive RESTful API design.
- **Top League Coverage** - Supports 6 major football leagues:
  - **Premier League** (England)
  - **Bundesliga** (Germany)
  - **Serie A** (Italy)
  - **Ligue 1** (France)
  - **Eredivisie** (Netherlands)
  - **LaLiga** (Spain)

---

## � Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation
1. clone this repo and go to dir:
```bash
git clone https://github.com/ChandraRenovalSaputra/FootballScraperAPI.git
cd FootballScraperAPI
```

2. Create venv:
```bash
python -m venv venv_name
```

3. Activate venv:
```bash
source venv_name/Scripts/activate
```

4. Install dependencies
```bash
pip install -r requirements.txt
```

### Running the API
```bash
python app.py
```
API will be available at http://localhost:5000 or https://chandrarenovalsaputra.pythonanywhere.com/

### 🔍 API Endpoints 

* GET /api/(league-name)/fxtures: Upcoming matches.
* GET /api/(league-name)/standings: League table.
* GET /api/(league-name)/results: Match results.
* GET /api/(league-name)/teams: Team details.

### 📬 Contact
📧 Email: chandrarenovalsaputra03@gmail.com
