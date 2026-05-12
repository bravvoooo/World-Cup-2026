from api_client import get_matches

def parse_matches(rawlist):
    matches_key = {}
    for match in rawlist:
        matches_key[match['id']] = {
            'home': match['homeTeam']['tla'] if match['homeTeam'] else None,
            'away': match['awayTeam']['tla'] if match['awayTeam'] else None,
            'kickoff': match['utcDate'], 
            'status': match['status'],
            'score': {"home": match['score']['fullTime']['home'], "away": match['score']['fullTime']['away']},
            'stage': match['stage'],
            'group': match['group'][6:] if match['group'] else None,
            'matchday': match['matchday']
        }
    return matches_key

def print_group_matches(parsed_matches, group_letter: str):
    for match_id, match in parsed_matches.items():
        if match['group'] == group_letter:
            print(match['home'], match['away'], match['kickoff'], match['score'], match['matchday'])

if __name__ == "__main__":
