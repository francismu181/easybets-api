from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import re
import time
import json
import requests
from bs4 import BeautifulSoup
from ml_predictions import predict_match_outcome

# Import Selenium conditionally - only used locally
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({"status": "ok", "message": "Service is running"})

@app.route('/api/odds', methods=['GET'])
def get_odds():
    """Endpoint to get all odds from SportPesa"""
    try:
        odds_data = scrape_sportpesa()
        return jsonify(odds_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/odds/<match_id>', methods=['GET'])
def get_match_odds(match_id):
    """Get odds for a specific match by ID"""
    try:
        odds_data = scrape_sportpesa()
        # Find match by ID (index in this case)
        try:
            match_id = int(match_id)
            if 0 <= match_id < len(odds_data):
                return jsonify(odds_data[match_id])
            else:
                return jsonify({"error": "Match not found"}), 404
        except ValueError:
            # If match_id is not an integer, try to find by match name
            for match in odds_data:
                if match_id.lower() in match["match"].lower():
                    return jsonify(match)
            return jsonify({"error": "Match not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/predictions', methods=['GET'])
def get_predictions():
    """Get ML predictions for upcoming matches"""
    try:
        odds_data = scrape_sportpesa()
        for match in odds_data:
            # Add predictions to each match
            prediction = predict_match_outcome(
                match["teams"][0],  # Home team
                match["teams"][1],  # Away team
                match["full_time_odds"]  # Using odds as features
            )
            match["prediction"] = prediction
        
        return jsonify(odds_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def scrape_sportpesa():
    """Scrape data from SportPesa website"""
    url = "https://www.ke.sportpesa.com/en/sports-betting/football-1/"
    
    # Check if running in cloud or Selenium is not available
    use_selenium = SELENIUM_AVAILABLE and os.environ.get('RUNNING_IN_CLOUD', 'false').lower() != 'true'
    
    if use_selenium:
        # Use Selenium for local development
        try:
            # Configure Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in headless mode
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            # For local development
            driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), 
                                    options=chrome_options)
                                    
            # Load SportPesa football page
            driver.get(url)
            time.sleep(3)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(6)  # Wait for JavaScript to load odds

            # Parse the HTML
            soup = BeautifulSoup(driver.page_source, "html.parser")
            driver.quit()
        except Exception as e:
            print(f"Selenium error: {e}. Falling back to requests.")
            use_selenium = False
    
    if not use_selenium:
        # Fallback to requests for cloud environments
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract match teams
        teams = [team.get_text(strip=True) for team in soup.select("div.event-team.ng-binding")]
        team_pairs = [(teams[i], teams[i+1]) for i in range(0, len(teams) - 1, 2)]
        matches = [f"{teams[i]} vs {teams[i+1]}" for i in range(0, len(teams) - 1, 2)]

        # Extract match dates
        raw_times = [el.get_text(strip=True) for el in soup.select("span.ng-binding")]
        match_times = [t for t in raw_times if re.match(r"\d{2}/\d{2}/\d{2} - \d{2}:\d{2}", t)]

        # Helper to extract odds by data-qa attribute
        def get_odds(selector):
            return [el.get_text(strip=True) for el in soup.select(f'div[data-qa="{selector}"] > div.ng-binding')]

        # Full time 1X2 odds
        full_time_raw = [
            el.get_text(strip=True)
            for el in soup.select('div.event-selection > div.ng-binding')
            if el.get_text(strip=True).replace('.', '', 1).isdigit()
        ]
        full_time_grouped = [full_time_raw[i:i+3] for i in range(0, len(full_time_raw), 3)]

        # Other market odds
        dc_1x = get_odds("prematch-event-selections-1x")
        dc_x2 = get_odds("prematch-event-selections-x2")
        dc_12 = get_odds("prematch-event-selections-12")

        ou_over = get_odds("prematch-event-selections-over")
        ou_under = get_odds("prematch-event-selections-under")

        btts_yes = get_odds("prematch-event-selections-yes")
        btts_no = get_odds("prematch-event-selections-no")

        # Structure the data
        results = []
        for i in range(min(len(matches), len(full_time_grouped), len(match_times))):
            match_data = {
                "id": i,
                "match": matches[i],
                "teams": team_pairs[i],
                "time": match_times[i] if i < len(match_times) else "",
                "full_time_odds": {
                    "home": float(full_time_grouped[i][0]) if i < len(full_time_grouped) and len(full_time_grouped[i]) >= 1 else None,
                    "draw": float(full_time_grouped[i][1]) if i < len(full_time_grouped) and len(full_time_grouped[i]) >= 2 else None,
                    "away": float(full_time_grouped[i][2]) if i < len(full_time_grouped) and len(full_time_grouped[i]) >= 3 else None
                },
                "double_chance": {
                    "1X": float(dc_1x[i]) if i < len(dc_1x) else None,
                    "X2": float(dc_x2[i]) if i < len(dc_x2) else None,
                    "12": float(dc_12[i]) if i < len(dc_12) else None
                },
                "over_under": {
                    "over": float(ou_over[i]) if i < len(ou_over) else None,
                    "under": float(ou_under[i]) if i < len(ou_under) else None
                },
                "btts": {
                    "yes": float(btts_yes[i]) if i < len(btts_yes) else None,
                    "no": float(btts_no[i]) if i < len(btts_no) else None
                }
            }
            results.append(match_data)

        return results

    except Exception as e:
        print(f"Error scraping odds: {e}")
        # Return mock data when scraping fails
        return generate_mock_data()
        
def generate_mock_data():
    """Generate mock data when scraping fails"""
    # This provides fallback data when the scraper encounters issues
    return [
        {
            "id": 0,
            "match": "Manchester United vs Liverpool",
            "teams": ["Manchester United", "Liverpool"],
            "time": "22/06/25 - 20:00",
            "full_time_odds": {"home": 2.45, "draw": 3.40, "away": 2.85},
            "double_chance": {"1X": 1.45, "X2": 1.50, "12": 1.30},
            "over_under": {"over": 1.85, "under": 1.95},
            "btts": {"yes": 1.70, "no": 2.10}
        },
        {
            "id": 1,
            "match": "Arsenal vs Chelsea",
            "teams": ["Arsenal", "Chelsea"],
            "time": "23/06/25 - 15:30",
            "full_time_odds": {"home": 2.20, "draw": 3.20, "away": 3.40},
            "double_chance": {"1X": 1.35, "X2": 1.65, "12": 1.40},
            "over_under": {"over": 1.90, "under": 1.90},
            "btts": {"yes": 1.75, "no": 2.05}
        },
        {
            "id": 2,
            "match": "Barcelona vs Real Madrid",
            "teams": ["Barcelona", "Real Madrid"],
            "time": "24/06/25 - 21:00",
            "full_time_odds": {"home": 2.30, "draw": 3.50, "away": 2.90},
            "double_chance": {"1X": 1.40, "X2": 1.55, "12": 1.30},
            "over_under": {"over": 1.80, "under": 2.00},
            "btts": {"yes": 1.65, "no": 2.20}
        }
    ]

if __name__ == "__main__":
    # Run the Flask app
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("DEBUG", "false").lower() == "true")
