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
```bash
git clone https://github.com/ChandraRenovalSaputra/FootballScraperAPI.git
cd FootballScraperAPI
pip install -r requirements.txt
```

### Running the API
Untuk menjalankan API, gunakan perintah berikut:

    ```
    python app.py
    ```
API will be available at http://localhost:5000

### 🔍 API Endpoints 

* GET /api/<league-name>/fxtures: Mendapatkan daftar pertandingan terbaru.
* GET /api/<league-name>/standings: Mendapatkan klasemen liga.
* GET /api/<league-name>/results: Mendapatkan hasil pertandingan liga.
* GET /api/<league-name>/teams: Mendapatkan team berdasarkan lga.

### 📬 Contact
📧 Email: chandrarenovalsaputra03@gmail.com
