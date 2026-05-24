from datetime import datetime
from zoneinfo import ZoneInfo
from scoring import score_prediction, DEFAULT_RULES
from state import load_tournament

def submit_prediction(user_id, match_id, home, away, tournament, prediction, now=None):
    # Setup
    if now is None:
        now = datetime.now(ZoneInfo('America/New_York'))
    if match_id not in tournament['matches']:
        raise KeyError('The match/match id couldn\'t be found. Please check your match id.')
    match = tournament['matches'][match_id]
    kickoff = datetime.fromisoformat(match['kickoff'])
    if now >= kickoff:
        raise ValueError('Sorry, but you have missed the window to submit your prediction!')
    if home < 0 or away < 0:
        raise ValueError('The numbers you inputted could not be submitted')
    
    # Decision
    pred = {
            'home_score': home, 'away_score': away,
            'submitted_at': now.isoformat(),
            'locked': False
            }
    prediction['users'].setdefault(user_id, {'predictions': {}})
    prediction['users'][user_id]['predictions'][match_id] = pred 
    return prediction

def lock_predictions_for_match(match_id: str, predictions: dict):
    users = predictions.get('users', {})
    for _, user_data in users.items():
        preds = user_data.get('predictions', {})
        if match_id in preds:
            preds[match_id]['locked'] = True
    return predictions

def score_match_predictions(match_id, predictions, tournament, rules=DEFAULT_RULES):
    match = tournament['matches'][match_id]
    if match['status'] != 'FINISHED':
        return predictions
    actual = match['score']
    users = predictions.get('users', {})
    for _, user_data in users.items():
        preds = user_data.get('predictions', {})
        if match_id in preds:
            pred = preds[match_id]
            predicted = {'home': pred['home_score'], 'away': pred['away_score']}
            result = score_prediction(predicted, actual, rules)
            pred.update(points_earned=result['points'], scoring_breakdown=result['breakdown'])
    return predictions

