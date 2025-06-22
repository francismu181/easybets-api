"""
Simple ML predictions for match outcomes.
This module provides a basic implementation for predicting match outcomes.
In a real-world scenario, you would use historical data and a trained model.
"""
import random
import numpy as np

# Placeholder for a trained model
# In a real implementation, you would load a trained model here
# model = load_model('model.h5')

# Simulated team strengths (in a real implementation, this would be based on historical data)
team_strengths = {
    # Premier League teams
    "Manchester United": 0.85,
    "Manchester City": 0.9,
    "Chelsea": 0.85,
    "Arsenal": 0.82,
    "Liverpool": 0.87,
    "Tottenham": 0.8,
    "Leicester": 0.75,
    "Wolves": 0.7,
    "Everton": 0.72,
    "West Ham": 0.71,
    
    # La Liga teams
    "Barcelona": 0.89,
    "Real Madrid": 0.9,
    "Atletico Madrid": 0.86,
    "Sevilla": 0.78,
    "Valencia": 0.75,
    
    # Generic strengths for unrecognized teams
    "UNKNOWN": 0.5
}

def predict_match_outcome(home_team, away_team, odds=None):
    """
    Predict the outcome of a match between two teams.
    
    Args:
        home_team (str): Name of the home team
        away_team (str): Name of the away team
        odds (dict): Betting odds (optional)
        
    Returns:
        dict: Prediction results with probabilities for home win, draw, and away win
    """
    # Get team strengths (defaulting to UNKNOWN if not in our dictionary)
    home_strength = team_strengths.get(home_team, team_strengths["UNKNOWN"])
    away_strength = team_strengths.get(away_team, team_strengths["UNKNOWN"])
    
    # Home advantage factor
    home_advantage = 0.1
    
    # Calculate basic probabilities
    base_home_prob = home_strength + home_advantage
    base_away_prob = away_strength
    
    # Normalize to ensure no probability is greater than 1
    max_prob = max(base_home_prob, base_away_prob)
    if max_prob > 1:
        base_home_prob /= max_prob
        base_away_prob /= max_prob
    
    # Calculate draw probability (higher when teams are evenly matched)
    draw_factor = 1 - abs(base_home_prob - base_away_prob)
    
    # Adjust probabilities based on odds if available
    if odds and all(odds.get(k) is not None for k in ["home", "draw", "away"]):
        # Inverse of odds correlates with expected probability
        odds_home_prob = 1 / odds["home"]
        odds_draw_prob = 1 / odds["draw"]
        odds_away_prob = 1 / odds["away"]
        
        # Normalize odds-based probabilities
        total_odds_prob = odds_home_prob + odds_draw_prob + odds_away_prob
        odds_home_prob /= total_odds_prob
        odds_draw_prob /= total_odds_prob
        odds_away_prob /= total_odds_prob
        
        # Blend model probabilities with odds probabilities (70% model, 30% odds)
        home_win_prob = 0.7 * base_home_prob + 0.3 * odds_home_prob
        draw_prob = 0.7 * (draw_factor * 0.5) + 0.3 * odds_draw_prob
        away_win_prob = 0.7 * base_away_prob + 0.3 * odds_away_prob
    else:
        # Without odds, use only our model probabilities
        home_win_prob = base_home_prob
        draw_prob = draw_factor * 0.5  # Reduce draw probability
        away_win_prob = base_away_prob
    
    # Normalize final probabilities
    total_prob = home_win_prob + draw_prob + away_win_prob
    home_win_prob /= total_prob
    draw_prob /= total_prob
    away_win_prob /= total_prob
    
    # Add a small random variation (±5%) to make predictions less deterministic
    home_win_prob = max(0, min(1, home_win_prob + random.uniform(-0.05, 0.05)))
    draw_prob = max(0, min(1, draw_prob + random.uniform(-0.05, 0.05)))
    away_win_prob = max(0, min(1, away_win_prob + random.uniform(-0.05, 0.05)))
    
    # Re-normalize after adding random variations
    total_prob = home_win_prob + draw_prob + away_win_prob
    home_win_prob /= total_prob
    draw_prob /= total_prob
    away_win_prob /= total_prob
    
    # Determine most likely outcome
    probabilities = {
        "home_win": round(home_win_prob, 3),
        "draw": round(draw_prob, 3),
        "away_win": round(away_win_prob, 3)
    }
    
    most_likely = max(probabilities, key=probabilities.get)
    
    # Generate prediction with confidence score
    confidence = probabilities[most_likely]
    
    # Translate to user-friendly text
    outcome_text = {
        "home_win": f"{home_team} Win",
        "draw": "Draw",
        "away_win": f"{away_team} Win"
    }
    
    prediction = {
        "most_likely_outcome": most_likely,
        "outcome_text": outcome_text[most_likely],
        "confidence": round(confidence * 100, 1),
        "probabilities": probabilities
    }
    
    return prediction

# Example usage
if __name__ == "__main__":
    prediction = predict_match_outcome("Manchester United", "Liverpool")
    print(prediction)
