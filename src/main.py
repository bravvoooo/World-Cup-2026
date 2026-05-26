import sys
from .state import get_group_table, load_tournament, get_todays_matches
from .predictions import get_leaderboard, load_predictions, submit_prediction, save_predictions, lock_predictions_for_match

USAGE = """Usage:
    python -m src.main standings <group_letter>
    python -m src.main today
    python -m src.main predict <match_id> <prediction score>"""

USER_ID = 'isaac'

loaded_tournament = load_tournament('data/tournament.json')
loaded_predictions = load_predictions()

if len(sys.argv) < 2: 
    print(USAGE)
    sys.exit(1)

command = sys.argv[1]

if command == 'standings':
    if len(sys.argv) >= 3:
        letter = sys.argv[2]
        try:
            table = get_group_table(loaded_tournament, letter)
        except KeyError:
            first_char = min(loaded_tournament['groups'])
            last_char = max(loaded_tournament['groups'])
            print(f"No group '{letter}' found. Try something from {first_char}-{last_char}.")
            sys.exit(1)
        print(f'Group {letter}')
        for team in table:
            print(f"{team['tla']} Played: {team['played']} W: {team['W']} D: {team['D']} L: {team['L']} GF: {team['GF']} GA: {team['GA']} GD: {team['GD']:+d} PTS: {team['pts']}")
    else:
        print(USAGE)
        sys.exit(1)
elif command == 'today':
    matches = get_todays_matches(loaded_tournament)
    if not matches:
        print('No matches are playing today :(')
        sys.exit(0)
    print('Today\'s matches (America/New_York):')
    for match_id, local_kickoff, match_data in matches:
        if match_data['status'] == 'FINISHED':
            score_str = f"FT {match_data['score']['home']} : {match_data['score']['away']}"
        else:
            score_str = '(scheduled)'
        print(f"{match_id}  {match_data['home']} vs {match_data['away']}  {local_kickoff.strftime('%I:%M %p')}  {score_str}  Stage: {match_data['stage']}  Matchday: {match_data['matchday']}")
elif command == 'leaderboard':
    leaderboard = get_leaderboard()
    for user in leaderboard:
        print(f"{user['username']} Total Points: {user['points_earned']}")
elif command == 'predict': 
    if len(sys.argv) >= 4:
        match_id = sys.argv[2]
        score = sys.argv[3]
        score = score.split('-')
        if len(score) != 2:
            print('Need exactly two values, like 1-2')
            sys.exit(1)
        if not (score[0].isdigit() and score[1].isdigit()):
            print('Both values must be digits')
            sys.exit(1)
        home = int(score[0])
        away = int(score[1])
        if home > 9 or away > 9:
            print('Values should be 10 or less')
            sys.exit(1)
        try:
            submitting_pred = submit_prediction(USER_ID, match_id, home, away, loaded_tournament, loaded_predictions)
        except (KeyError, ValueError) as e:
            print(e)
            sys.exit(1)
        save_predictions(submitting_pred)
        print("Prediction saved.")
    else:
        print(USAGE)
        sys.exit(1)
else:
    print(f"Unknown command: {command}")
    print(USAGE)
    sys.exit(1)

