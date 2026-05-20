DEFAULT_RULES = {
    'exact_score': 5,
    'correct_result': 2,
    'correct_gd': 3,
    'nothing': 0
    }

def score_prediction(prediction, actual, rules=DEFAULT_RULES):
    actual_gd = abs(actual['home'] - actual['away'])
    pred_gd = abs(prediction['home'] - prediction['away'])
    pred_outcome = _outcome(prediction)
    actual_outcome = _outcome(actual)
    if prediction['home'] == actual['home'] and prediction['away'] == actual['away']:
        return {"points": rules['exact_score'], "breakdown": {"exact": True, "result": True, "gd": True, "tier_awarded": "exact"}}
    
    if pred_gd == actual_gd:
        return {"points": rules['correct_gd'], "breakdown": {"exact": False, "result": False, "gd": True, "tier_awarded": "correct_gd"}}
    
    if pred_outcome == actual_outcome:
        return {"points": rules['correct_result'], "breakdown": {"exact": False, "result": True, "gd": False, "tier_awarded": "correct_result"}}
    
    return {'points': rules['nothing'], 'breakdown': {"exact": False, "result": False, "gd": False, "tier_awarded": "nothing"}}

def _outcome(score):
    if score['home'] > score['away']:
        return 'home'
    elif score['away'] > score['home']:
        return 'away'
    else:
        return 'draw'