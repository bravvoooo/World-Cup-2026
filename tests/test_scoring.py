from src.scoring import score_prediction
from src.predictions import save_predictions, load_predictions, get_leaderboard, get_user_summary

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

def test_save_load_round_trip(tmp_path):
    fixture = {
        "users": {
            "456": {
                "username": "isaac",
                "joined_at": "2026-05-20T10:00:00Z",
                "total_points": 5,
                "predictions": {
                    "match_id_12345": {
                        "home_score": 2,
                        "away_score": 1,
                        "submitted_at": "2026-06-12T19:45:00Z",
                        "locked": True,
                        "points_earned": 5,
                        "scoring_breakdown": {"exact": True, "result": True, "gd": True},
                    }
                },
            }
        }
    }
    path = tmp_path / "predictions.json"
    save_predictions(fixture, path)
    loaded = load_predictions(path)
    assert loaded == fixture

def test_leaderboard_orders_by_points(predictions=None):
    fixture = {"users": {
        "1": {"username": "alice", "predictions": {
            "m1": {"points_earned": 5}, "m2": {"points_earned": 2}}},   # 7
        "2": {"username": "bob", "predictions": {
            "m1": {"points_earned": 5}, "m2": {"points_earned": 5}}},   # 10
    }}
    result = get_leaderboard(predictions=fixture)
    assert result[0]['username'] == 'bob'   # highest first
    assert result[0]['points_earned'] == 10
    assert result[1]['points_earned'] == 7

def test_user_summary():
    fixture = {"users": {
        "1": {"username": "isaac", "predictions": {
            "m1": {"points_earned": 5},   # finished, hit
            "m2": {"points_earned": 0},   # finished, wrong
            "m3": {"home_score": 1, "away_score": 0},  # unscored, no points_earned key
        }},
        "2": {"username": "newbie", "predictions": {
            "m1": {"home_score": 2, "away_score": 1},  # unscored only
        }},
    }}
    isaac = get_user_summary("1", predictions=fixture)
    assert isaac['total_points'] == 5        # 5 + 0, unscored contributes 0
    assert isaac['accuracy'] == 0.5          # 1 hit / 2 finished

    newbie = get_user_summary("2", predictions=fixture)
    assert newbie['total_points'] == 0
    assert newbie['accuracy'] is None        # zero finished → guard fires