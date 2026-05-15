import sys
from state import get_group_table, load_tournament, get_todays_matches

USAGE = """Usage:
    python main.py standings <group_letter>
    python main.py today"""

loaded = load_tournament('data/tournament.json')

if len(sys.argv) < 2: 
    print(USAGE)
    sys.exit(1)

command = sys.argv[1]

if command == 'standings':
    if len(sys.argv) >= 3:
        letter = sys.argv[2]
        try:
            table = get_group_table(loaded, letter)
        except KeyError:
            first_char = min(loaded['groups'])
            last_char = max(loaded['groups'])
            print(f"No group '{letter}' found. Try something from {first_char}-{last_char}.")
            sys.exit(1)
        print(f'Group {letter}')
        for team in table:
            print(f"{team['tla']} Played: {team['played']} W: {team['W']} D: {team['D']} L: {team['L']} GF: {team['GF']} GA: {team['GA']} GD: {team['GD']:+d} PTS: {team['pts']}")
    else:
        print(USAGE)
        sys.exit(1)
elif command == 'today':
    matches = get_todays_matches(loaded)
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
else:
    print(f"Unknown command: {command}")
    print(USAGE)
    sys.exit(1)