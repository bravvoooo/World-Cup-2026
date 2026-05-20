from src.scoring import score_prediction

def test_score_prediction():
    predicted = {"home": 2, "away": 0}
    actual = {"home": 2, "away": 0}

    result = score_prediction(predicted, actual)
    assert result['points'] == 5
    assert result['breakdown'] == {"exact": True, "result": True, "gd": True, "tier_awarded": "exact"}

def test_score_prediction_gd():
    predicted = {"home": 2, "away": 1}
    actual = {"home": 5, "away": 4}

    result = score_prediction(predicted, actual)
    assert result['points'] == 3
    assert result['breakdown'] == {"exact": False, "result": False, "gd": True, "tier_awarded": "correct_gd"}

def test_score_prediction_result():
    predicted = {"home": 2, "away": 1}
    actual = {"home": 3, "away": 0}

    result = score_prediction(predicted, actual)
    assert result['points'] == 2 
    assert result['breakdown'] == {"exact": False, "result": True, "gd": False, "tier_awarded": "correct_result"}

def test_score_prediction_nothing():
    predicted = {"home": 5, "away": 8}
    actual = {"home": 4, "away": 0}

    result = score_prediction(predicted, actual)
    assert result['points'] == 0
    assert result['breakdown'] == {"exact": False, "result": False, "gd": False, "tier_awarded": "nothing"}

def test_draw():
    predicted = {"home": 0, "away": 0}
    actual = {"home": 0, "away": 0}

    result = score_prediction(predicted, actual)
    assert result['points'] == 5
    assert result['breakdown'] == {"exact": True, "result": True, "gd": True, "tier_awarded": "exact"}

def test_exact_score_but_flipped():
    predicted = {"home": 2, "away": 1}
    actual = {"home": 1, "away": 2}

    result = score_prediction(predicted, actual)
    assert result['points'] == 3
    assert result['breakdown'] == {"exact": False, "result": False, "gd": True, "tier_awarded": "correct_gd"}

def test_correct_winner_but_wrong_score():
    predicted = {"home": 3, "away": 0}
    actual = {"home": 2, "away": 0}

    result = score_prediction(predicted, actual)
    assert result['points'] == 2 
    assert result['breakdown'] == {"exact": False, "result": True, "gd": False, "tier_awarded": "correct_result"}

