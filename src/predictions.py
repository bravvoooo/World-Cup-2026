import json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from .scoring import score_prediction, DEFAULT_RULES
from .state import load_tournament

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

def save_predictions(predictions, path='data/predictions.json'):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as file:
        json.dump(predictions, file, indent=4)

def load_predictions(path: str = 'data/predictions.json'):
    if Path(path).exists():
        with open(path) as f:
            return json.load(f)
    return {'users': {}}

def get_leaderboard(predictions=None):
    if predictions is None:
        predictions = load_predictions()
    leaderboard = []
    for user_id, user_data in predictions['users'].items():
        total_points = _get_total_points(user_data)
        user_score =  {'username': user_data['username'], 'points_earned': total_points}
        leaderboard.append(user_score)
    return sorted(leaderboard, key=lambda x: x['points_earned'], reverse=True)

def _get_total_points(user_data):
    return sum(pick.get('points_earned', 0) for pick in user_data['predictions'].values())

def get_user_summary(user_id, predictions=None):
    if predictions is None:
        predictions = load_predictions()
    user_summary = {}
    user_data = predictions['users'][user_id]
    total_user_points = _get_total_points(user_data)
    user_summary.update(total_points=total_user_points)
    finished = 0
    hits = 0
    for pick in user_data['predictions'].values():
        if 'points_earned' in pick:
            finished += 1
            if pick['points_earned'] > 0:
                hits += 1
    if finished == 0:
        user_summary.update(accuracy=None)
    else:
        accuracy_rate = hits/finished
        user_summary.update(accuracy=accuracy_rate)
    return user_summary